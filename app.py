from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from flask_cors import CORS
import os
import joblib
import numpy as np

# === App Setup ===
app = Flask(__name__, static_folder="frontend/build", static_url_path="")

# === FORCE NEW DEPLOYMENT - VERSION 2025-07-17 ===
print("="*50)
print("FLASK APP STARTING - VERSION 2025-07-17-LATEST")
print("="*50)

# === Environment Detection ===
is_production = os.environ.get("RENDER") is not None

# === CORS Configuration ===
if is_production:
    # In production, allow requests from the deployed domain
    # Render automatically provides HTTPS, so we configure for that
    CORS(app, origins=["https://*.onrender.com"], supports_credentials=True)
else:
    # In development, allow all origins for easier testing
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# === Config ===
if is_production:
    # Production database configuration - use in-memory SQLite for Render
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    # Production-specific settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
else:
    # Development database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/users.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Use environment variable for JWT secret in production, fallback for development
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')

# Additional production configurations
if is_production:
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['JSON_SORT_KEYS'] = False

# === Extensions ===
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# === User Model ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# === Initialize DB ===
try:
    with app.app_context():
        db.create_all()
        if is_production:
            print("Database tables created successfully in production")
        else:
            print("Database tables created successfully in development")
except Exception as e:
    print(f"Database initialization error: {e}")
    if is_production:
        print("Continuing with database initialization error in production")
    else:
        raise

# === Test Route for Debugging ===
@app.route("/api/test", methods=["GET", "POST"])
def test():
    if request.method == "GET":
        return jsonify({
            "msg": "API is working", 
            "environment": "production" if is_production else "development",
            "version": "LATEST_VERSION_2025_07_17",
            "endpoints": ["predict", "predict_v3"]
        })
    else:
        data = request.get_json()
        return jsonify({"received": data, "msg": "POST test successful"})

# === Debug Route to Check What's Running ===
@app.route("/api/debug", methods=["GET"])
def debug():
    return jsonify({
        "message": "Debug endpoint working",
        "version": "2025-07-17-LATEST",
        "predict_v3_exists": True,
        "environment": "production" if is_production else "development"
    })

# === Authentication Routes ===
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "user": {"id": user.id, "username": user.username}
        }), 200

    return jsonify({"msg": "Wrong username or password"}), 401

# === Load ML Model Files ===
try:
    model = joblib.load("model/model_compatible.joblib")
    label_encoder = joblib.load("model/label_encoder.joblib")
    symptoms_list = joblib.load("model/symptoms_list.joblib")
    if is_production:
        print("Successfully loaded ML model files in production")
    else:
        print("Successfully loaded ML model files in development")
except Exception as e:
    error_msg = f"Error loading model files: {e}"
    print(error_msg)
    if is_production:
        print("Model loading failed in production environment")
    raise RuntimeError(error_msg)

# === New Prediction Route - Version 3.0 ===
@app.route("/api/predict_v3", methods=["POST"])
def predict_v3():
    # TEMPORARY TEST - Return immediately to confirm function is called
    return jsonify({"msg": "PREDICT_V3 FUNCTION IS WORKING - TEST MESSAGE"}), 200
    
    try:
        print("=== NEW PREDICTION API v3.0 CALLED ===")
        data = request.get_json(force=True)
        print("Received data:", data)
        
        user_input = data.get("symptoms", "") if data else ""
        print("User input:", user_input)

        # Simple validation - COMPLETELY NEW APPROACH
        if not user_input:
            print("Validation failed: no symptoms provided")  # Debug line
            return jsonify({"msg": "V3: No symptoms provided"}), 422
        
        # Convert to string and clean up
        user_input = str(user_input).strip()
        
        # Check if empty after cleaning
        if not user_input:
            print("Validation failed: empty symptoms after cleaning")  # Debug line
            return jsonify({"msg": "V3: Empty symptoms"}), 422

        user_input = user_input.lower().strip()
        input_symptoms = [sym.strip() for sym in user_input.split(",")]

        # Convert symptoms to binary vector
        input_vector = [1 if symptom in input_symptoms else 0 for symptom in symptoms_list]
        input_array = np.array([input_vector])

        prediction_index = model.predict(input_array)[0]
        predicted_disease = label_encoder.inverse_transform([prediction_index])[0]

        medicine_mapping = {
            "flu": ["Paracetamol", "Rest", "Hydration"],
            "cold": ["Antihistamines", "Decongestant"],
            "diabetes": ["Insulin", "Metformin"],
            "panic disorder": ["Xanax", "CBT"],
            "migraine": ["Ibuprofen", "Sumatriptan"],
            "covid-19": ["Rest", "Antivirals", "Consult doctor"]
        }

        medicines = medicine_mapping.get(predicted_disease.lower(), ["Consult a physician"])

        return jsonify({
            "disease": predicted_disease,
            "medicines": medicines,
            "version": "3.0"
        })
    
    except Exception as e:
        return jsonify({"msg": f"Error v3.0: {str(e)}"}), 500

# === Original Prediction Route - FIXED VERSION ===
@app.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        print("=== PREDICTION API v2.0 CALLED ===")  # Version identifier
        data = request.get_json(force=True)
        print("Received data:", data)  # Debug line
        print("Data type:", type(data))  # Debug line
        
        user_input = data.get("symptoms", "") if data else ""
        print("User input:", user_input)  # Debug line
        print("User input type:", type(user_input))  # Debug line

        # Completely new validation approach
        if not user_input:
            print("VALIDATION FAILED: No symptoms provided")  # Debug line
            return jsonify({"msg": "NEW VERSION: Please provide symptoms"}), 422
        
        # Convert to string and clean up
        user_input = str(user_input).strip()
        
        # Check if empty after cleaning
        if not user_input:
            print("VALIDATION FAILED: Empty symptoms after cleaning")  # Debug line
            return jsonify({"msg": "NEW VERSION: Symptoms cannot be empty"}), 422

        print(f"PROCESSING SYMPTOMS: {user_input}")  # Debug line
        user_input = user_input.lower().strip()
        input_symptoms = [sym.strip() for sym in user_input.split(",")]
        print(f"PARSED SYMPTOMS: {input_symptoms}")  # Debug line

        # Convert symptoms to binary vector
        input_vector = [1 if symptom in input_symptoms else 0 for symptom in symptoms_list]
        input_array = np.array([input_vector])
        print(f"INPUT VECTOR LENGTH: {len(input_vector)}")  # Debug line

        prediction_index = model.predict(input_array)[0]
        predicted_disease = label_encoder.inverse_transform([prediction_index])[0]
        print(f"PREDICTED DISEASE: {predicted_disease}")  # Debug line

        medicine_mapping = {
            "flu": ["Paracetamol", "Rest", "Hydration"],
            "cold": ["Antihistamines", "Decongestant"],
            "diabetes": ["Insulin", "Metformin"],
            "panic disorder": ["Xanax", "CBT"],
            "migraine": ["Ibuprofen", "Sumatriptan"],
            "covid-19": ["Rest", "Antivirals", "Consult doctor"]
        }

        medicines = medicine_mapping.get(predicted_disease.lower(), ["Consult a physician"])
        print(f"RECOMMENDED MEDICINES: {medicines}")  # Debug line

        return jsonify({
            "disease": predicted_disease,
            "medicines": medicines,
            "version": "2.0"  # Version identifier in response
        })
    
    except Exception as e:
        print(f"PREDICTION ERROR: {str(e)}")  # Debug line
        return jsonify({"msg": f"Prediction error v2.0: {str(e)}"}), 500

# === Serve React Frontend ===
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

# === Run App ===
if __name__ == "__main__":
    # Use PORT environment variable from Render, fallback to 5050 for local development
    port = int(os.environ.get("PORT", 5050))
    
    if is_production:
        print(f"Starting Flask app in production mode on port {port}")
        print("Environment: Production (Render)")
        print(f"CORS configured for: https://*.onrender.com")
    else:
        print(f"Starting Flask app in development mode on port {port}")
        print("Environment: Development")
        print(f"CORS configured for: http://localhost:3000")
    
    # Additional production settings
    if is_production:
        # Disable debug mode and set production-optimized settings
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
    else:
        # Development mode with debug enabled
        app.run(host="0.0.0.0", port=port, debug=True)
