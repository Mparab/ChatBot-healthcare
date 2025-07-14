from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.record
def init_app(setup_state):
    bcrypt.init_app(setup_state.app)

# === Register ===
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 409

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201

# === Login ===
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": token,
            "user": {
                "id": user.id,
                "username": user.username
            }
        }), 200

    return jsonify({"msg": "Wrong username or password"}), 401

# === Get Current User Info ===
@auth_bp.route("/api/user", methods=["GET"])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username
    })
