from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import joblib
import os

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Load model and label encoder
model = joblib.load("disease_model_small.joblib")
label_encoder = joblib.load("label_encoder_small.joblib")
symptom_list = joblib.load("symptoms_list.joblib")

@app.route("/api/predict", methods=["POST"])
def predict_disease():
    try:
        data = request.get_json()
        symptoms_input = data.get("symptoms", [])

        # Convert symptoms to binary feature vector
        input_vector = [1 if symptom in symptoms_input else 0 for symptom in symptom_list]

        prediction = model.predict([input_vector])[0]
        predicted_disease = label_encoder.inverse_transform([prediction])[0]

        # Dummy medicine mapping (you can update with real mappings)
        medicine_map = {
            "panic disorder": [
                "Xanax (Alprazolam)",
                "Cognitive Behavioral Therapy (CBT)",
                "Sertraline",
                "Clonazepam",
                "Paroxetine"
            ],
            "migraine": ["Ibuprofen", "Paracetamol", "Triptans"],
            "flu": ["Rest", "Fluids", "Paracetamol"]
            # Add more disease: medicine mappings as needed
        }

        recommended_medicines = medicine_map.get(predicted_disease.lower(), ["Consult a doctor"])

        return jsonify({
            "predicted_disease": predicted_disease,
            "recommended_medicines": recommended_medicines
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve React app from build folder
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# Run the app (development only)
if __name__ == "__main__":
    app.run(debug=True, port=5050)
