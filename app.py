from flask import Flask, request, jsonify, send_from_directory
import joblib
import numpy as np
import os

# Load model and encoders
MODEL_PATH = "disease_model_small.joblib"
ENCODER_PATH = "label_encoder_small.joblib"
SYMPTOM_LIST_PATH = "symptoms_list.joblib"

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
symptom_list = joblib.load(SYMPTOM_LIST_PATH)

# Example medicine mapping; replace with your real mapping
medicine_mapping = {
    "panic disorder": [
        "Xanax (Alprazolam)",
        "Cognitive Behavioral Therapy (CBT)",
        "Sertraline",
        "Clonazepam",
        "Paroxetine"
    ],
    "flu": [
        "Oseltamivir",
        "Rest",
        "Fluids",
        "Acetaminophen"
    ],
    # Add more disease: [medicines...] as needed
}

app = Flask(__name__, static_folder="frontend/build", static_url_path="")

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    symptoms = data.get('symptoms', [])
    # Create input vector
    input_vector = np.zeros(len(symptom_list))
    for symptom in symptoms:
        if symptom in symptom_list:
            idx = symptom_list.index(symptom)
            input_vector[idx] = 1
    # Predict
    prediction = model.predict([input_vector])[0]
    disease = label_encoder.inverse_transform([prediction])[0]
    recommended_medicines = medicine_mapping.get(disease, ["No recommendation available"])
    return jsonify({
        "disease": disease,
        "recommended_medicines": recommended_medicines
    })

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))