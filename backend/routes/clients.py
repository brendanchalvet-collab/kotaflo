from flask import Blueprint, request, jsonify
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.services import client_service
from backend.models import interaction_model

clients_bp = Blueprint("clients", __name__)


# ===== GET /api/clients?type=client|prospect =====
@clients_bp.route("/", methods=["GET"])
@require_auth
def list_clients():
    page         = request.args.get("page", 1, type=int)
    contact_type = request.args.get("type", None)
    clients, _   = client_service.list_clients(get_tenant_id(), page, contact_type=contact_type)
    return jsonify(clients), 200


# ===== POST /api/clients =====
@clients_bp.route("/", methods=["POST"])
@require_auth
def create_client():
    data = request.get_json()
    client, error = client_service.create_client(get_tenant_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(client), 201


# ===== GET /api/clients/<id> =====
@clients_bp.route("/<int:client_id>", methods=["GET"])
@require_auth
def get_client(client_id):
    client, error = client_service.get_client(get_tenant_id(), client_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(client), 200


# ===== PUT /api/clients/<id> =====
@clients_bp.route("/<int:client_id>", methods=["PUT"])
@require_auth
def update_client(client_id):
    data = request.get_json()
    client, error = client_service.update_client(get_tenant_id(), client_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(client), 200


# ===== PATCH /api/clients/<id>/pipeline =====
@clients_bp.route("/<int:client_id>/pipeline", methods=["PATCH"])
@require_auth
def update_pipeline(client_id):
    data = request.get_json()
    client, error = client_service.update_pipeline_status(
        get_tenant_id(), client_id, data.get("pipeline_status")
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(client), 200


# ===== GET /api/clients/<id>/tree =====
# Retourne client + projets + tâches (hiérarchie complète)
@clients_bp.route("/<int:client_id>/tree", methods=["GET"])
@require_auth
def get_tree(client_id):
    from backend.services.signature_service import get_client_tree
    tree = get_client_tree(get_tenant_id(), client_id)
    if not tree:
        return jsonify({"error": "Client introuvable"}), 404
    return jsonify(tree), 200


# ===== GET /api/clients/<id>/timeline =====
@clients_bp.route("/<int:client_id>/timeline", methods=["GET"])
@require_auth
def get_timeline(client_id):
    _, error = client_service.get_client(get_tenant_id(), client_id)
    if error:
        return jsonify({"error": error}), 404
    timeline = interaction_model.get_timeline(get_tenant_id(), client_id)
    return jsonify(timeline), 200


# ===== POST /api/clients/<id>/interactions =====
@clients_bp.route("/<int:client_id>/interactions", methods=["POST"])
@require_auth
def add_interaction(client_id):
    _, error = client_service.get_client(get_tenant_id(), client_id)
    if error:
        return jsonify({"error": error}), 404
    data = request.get_json()
    if not data.get("date"):
        from datetime import datetime
        data["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    interaction = interaction_model.create(get_tenant_id(), client_id, data)
    return jsonify(interaction), 201


# ===== DELETE /api/interactions/<id> =====
@clients_bp.route("/interactions/<int:interaction_id>", methods=["DELETE"])
@require_auth
def delete_interaction(interaction_id):
    deleted = interaction_model.delete(get_tenant_id(), interaction_id)
    if not deleted:
        return jsonify({"error": "Interaction introuvable"}), 404
    return jsonify({"message": "Supprimé"}), 200


# ===== DELETE /api/clients/<id> =====
@clients_bp.route("/<int:client_id>", methods=["DELETE"])
@require_auth
def delete_client(client_id):
    success, error = client_service.delete_client(get_tenant_id(), client_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Contact supprimé"}), 200
