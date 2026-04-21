from flask import Blueprint, request, jsonify
from backend.services import auth_service

auth_bp = Blueprint("auth", __name__)


# ===== POST /api/auth/register =====
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    result, error = auth_service.register(data.get("email"), data.get("password"))
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 201


# ===== POST /api/auth/login =====
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    result, error = auth_service.login(data.get("email"), data.get("password"))
    if error:
        return jsonify({"error": error}), 401
    return jsonify(result), 200


# ===== POST /api/auth/firebase-login =====
@auth_bp.route("/firebase-login", methods=["POST"])
def firebase_login():
    data = request.get_json()
    result, error = auth_service.firebase_login(data.get("id_token"))
    if error:
        return jsonify({"error": error}), 401
    return jsonify(result), 200
