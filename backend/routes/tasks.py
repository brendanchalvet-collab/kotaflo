# ===== ROUTES TÂCHES =====
from flask import Blueprint, request, jsonify
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.models import task_model

tasks_bp = Blueprint("tasks", __name__)


# ===== GET /api/tasks?client_id=&job_id=&status= =====
@tasks_bp.route("/", methods=["GET"])
@require_auth
def list_tasks():
    tid = get_tenant_id()
    tasks = task_model.get_all(
        tid,
        client_id=request.args.get("client_id", None, type=int),
        job_id=request.args.get("job_id",    None, type=int),
        status=request.args.get("status",    None),
    )
    return jsonify(tasks), 200


# ===== POST /api/tasks =====
@tasks_bp.route("/", methods=["POST"])
@require_auth
def create_task():
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "Titre requis"}), 400
    task = task_model.create(get_tenant_id(), data)
    return jsonify(task), 201


# ===== PUT /api/tasks/<id> =====
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@require_auth
def update_task(task_id):
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "Titre requis"}), 400
    task = task_model.update(get_tenant_id(), task_id, data)
    if not task:
        return jsonify({"error": "Tâche introuvable"}), 404
    return jsonify(task), 200


# ===== PATCH /api/tasks/<id>/status =====
@tasks_bp.route("/<int:task_id>/status", methods=["PATCH"])
@require_auth
def patch_status(task_id):
    data   = request.get_json()
    status = data.get("status")
    if status not in ("todo", "in_progress", "done"):
        return jsonify({"error": "Statut invalide"}), 400
    task = task_model.get_by_id(get_tenant_id(), task_id)
    if not task:
        return jsonify({"error": "Tâche introuvable"}), 404
    updated = task_model.update(get_tenant_id(), task_id, {**dict(task), "status": status})
    return jsonify(updated), 200


# ===== DELETE /api/tasks/<id> =====
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@require_auth
def delete_task(task_id):
    ok = task_model.delete(get_tenant_id(), task_id)
    if not ok:
        return jsonify({"error": "Tâche introuvable"}), 404
    return jsonify({"message": "Tâche supprimée"}), 200
