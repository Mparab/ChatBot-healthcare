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
CORS(app)

# === Config ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

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
with app.app_context():
    db.create_all()

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
except Exception as e:
    raise RuntimeError(f"Error loading model files: {e}")

# === Prediction Route ===
@app.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        data = request.get_json(force=True)  # ✅ Ensures JSON is parsed even on Render
        user_input = data.get("symptoms", "")

        # ✅ Validate it's a string
        if not isinstance(user_input, str) or not user_input.strip():
            return jsonify({"msg": "Subject must be a string"}), 422

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
            "medicines": medicines
        })
    
    except Exception as e:
        return jsonify({"msg": f"Prediction error: {str(e)}"}), 500

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
    app.run(host="0.0.0.0", port=5050)
