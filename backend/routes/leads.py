from flask import Blueprint, request, jsonify
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.services import lead_service

leads_bp = Blueprint("leads", __name__)


# ===== GET /api/leads =====
@leads_bp.route("/", methods=["GET"])
@require_auth
def list_leads():
    page = request.args.get("page", 1, type=int)
    leads, _ = lead_service.list_leads(get_tenant_id(), page)
    return jsonify(leads), 200


# ===== POST /api/leads =====
@leads_bp.route("/", methods=["POST"])
@require_auth
def create_lead():
    data = request.get_json()
    lead, error = lead_service.create_lead(get_tenant_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(lead), 201


# ===== PUT /api/leads/<id> =====
@leads_bp.route("/<int:lead_id>", methods=["PUT"])
@require_auth
def update_lead(lead_id):
    data = request.get_json()
    lead, error = lead_service.update_lead(get_tenant_id(), lead_id, data)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(lead), 200


# ===== PATCH /api/leads/<id>/status =====
@leads_bp.route("/<int:lead_id>/status", methods=["PATCH"])
@require_auth
def update_status(lead_id):
    data = request.get_json()
    lead, error = lead_service.update_lead_status(get_tenant_id(), lead_id, data.get("status"))
    if error:
        return jsonify({"error": error}), 400
    return jsonify(lead), 200


# ===== DELETE /api/leads/<id> =====
@leads_bp.route("/<int:lead_id>", methods=["DELETE"])
@require_auth
def delete_lead(lead_id):
    success, error = lead_service.delete_lead(get_tenant_id(), lead_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Lead supprimé"}), 200
