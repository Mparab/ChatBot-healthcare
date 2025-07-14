from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, History, User
from datetime import datetime

history_bp = Blueprint("history", __name__)

@history_bp.route("/api/history", methods=["POST"])
@jwt_required()
def save_history():
    user_id = get_jwt_identity()
    data = request.get_json()
    symptoms = data.get("symptoms", "")
    prediction = data.get("prediction", "")
    
    if not symptoms or not prediction:
        return jsonify({"msg": "Missing data"}), 400

    new_entry = History(user_id=user_id, symptoms=symptoms, prediction=prediction)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"msg": "History saved"}), 201

@history_bp.route("/api/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = History.query.filter_by(user_id=user_id).order_by(History.timestamp.desc()).all()

    output = [
        {
            "symptoms": h.symptoms,
            "prediction": h.prediction,
            "timestamp": h.timestamp.isoformat(),
        } for h in history
    ]
    return jsonify(output), 200
