from flask import Blueprint, request, jsonify
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.models import tenant_model

profile_bp = Blueprint("profile", __name__)


# ===== GET /api/profile =====
@profile_bp.route("/", methods=["GET"])
@require_auth
def get_profile():
    tenant = tenant_model.get_by_id(get_tenant_id())
    if not tenant:
        return jsonify({"error": "Profil introuvable"}), 404
    data = dict(tenant)
    data["google_connected"] = bool(data.pop("google_token", None))  # ne pas exposer le token
    return jsonify(data), 200


# ===== PUT /api/profile =====
@profile_bp.route("/", methods=["PUT"])
@require_auth
def update_profile():
    data   = request.get_json()
    tenant = tenant_model.update_profile(get_tenant_id(), data)
    return jsonify(tenant), 200
