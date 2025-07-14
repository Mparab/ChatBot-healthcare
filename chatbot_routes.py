from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, History
import os
import joblib

chatbot_bp = Blueprint("chatbot", __name__)

# === Load Model & LabelEncoder ===
model = None
le = None
MODEL_PATH = "model.pkl"  # Replace when available
LE_PATH = "le.pkl"

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model loaded in chatbot_routes.")
    except Exception as e:
        print("❌ Model load error:", e)

if os.path.exists(LE_PATH):
    try:
        le = joblib.load(LE_PATH)
        print("✅ LabelEncoder loaded in chatbot_routes.")
    except Exception as e:
        print("❌ LabelEncoder load error:", e)

# === Dummy Medicine Mapping ===
medicine_mapping = {
    "panic disorder": [
        "Xanax (Alprazolam)",
        "Cognitive Behavioral Therapy (CBT)",
        "Sertraline",
        "Clonazepam",
        "Paroxetine"
    ]
}

# === Prediction Route ===
@chatbot_bp.route("/api/predict", methods=["POST"])
@jwt_required()
def predict():
    data = request.get_json()
    symptoms = data.get("symptoms", "")

    # Simulate prediction — replace this with model prediction if available
    disease = "panic disorder"

    # Save to history
    user_id = get_jwt_identity()
    new_entry = History(user_id=user_id, symptoms=symptoms, prediction=disease)
    db.session.add(new_entry)
    db.session.commit()

    # Medicine result
    medicines = medicine_mapping.get(disease, [])

    return jsonify({
        "disease": disease,
        "medicines": medicines
    })
