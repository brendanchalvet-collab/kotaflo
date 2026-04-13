from flask import Blueprint, request, jsonify
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.services import job_service
from backend.models import job_model
from backend.utils.db import get_client_conn, rows

jobs_bp = Blueprint("jobs", __name__)


# ===== GET /api/jobs?client_id=X =====
@jobs_bp.route("/", methods=["GET"])
@require_auth
def list_jobs():
    client_id = request.args.get("client_id", None, type=int)
    page      = request.args.get("page", 1, type=int)
    jobs, _   = job_service.list_jobs(get_tenant_id(), client_id=client_id, page=page)
    return jsonify(jobs), 200


# ===== POST /api/jobs =====
@jobs_bp.route("/", methods=["POST"])
@require_auth
def create_job():
    data = request.get_json()
    job, error = job_service.create_job(get_tenant_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(job), 201


# ===== GET /api/jobs/<id> =====
@jobs_bp.route("/<int:job_id>", methods=["GET"])
@require_auth
def get_job(job_id):
    job, error = job_service.get_job(get_tenant_id(), job_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(job), 200


# ===== PUT /api/jobs/<id> =====
@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@require_auth
def update_job(job_id):
    data = request.get_json()
    job, error = job_service.update_job(get_tenant_id(), job_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(job), 200


# ===== GET /api/jobs/<id>/summary =====
@jobs_bp.route("/<int:job_id>/summary", methods=["GET"])
@require_auth
def job_summary(job_id):
    tenant_id = get_tenant_id()
    job = job_model.get_by_id(tenant_id, job_id)
    if not job:
        return jsonify({"error": "Projet introuvable"}), 404

    conn = get_client_conn()

    # Devis liés au projet (amount = HT, amount_ttc calculé depuis les lignes)
    quotes = rows(conn.execute(
        """SELECT q.*, c.name as client_name,
           COALESCE((SELECT SUM(ql.quantity * ql.unit_price * (1 + ql.tva_rate / 100.0))
                     FROM quote_lines ql WHERE ql.quote_id = q.id), q.amount) as amount_ttc
           FROM quotes q
           LEFT JOIN clients c ON c.id = q.client_id
           WHERE q.tenant_id = ? AND q.job_id = ?
           ORDER BY q.created_at DESC""",
        (tenant_id, job_id)
    ).fetchall())

    # Factures liées au projet
    invoices = rows(conn.execute(
        """SELECT i.*, c.name as client_name FROM invoices i
           LEFT JOIN clients c ON c.id = i.client_id
           WHERE i.tenant_id = ? AND i.job_id = ?
           ORDER BY i.created_at DESC""",
        (tenant_id, job_id)
    ).fetchall())

    # Interactions liées au client du projet
    interactions = rows(conn.execute(
        """SELECT * FROM interactions
           WHERE tenant_id = ? AND client_id = ?
           ORDER BY date DESC LIMIT 30""",
        (tenant_id, job.get("client_id"))
    ).fetchall()) if job.get("client_id") else []

    conn.close()
    return jsonify({
        "job":          dict(job),
        "quotes":       quotes,
        "invoices":     invoices,
        "interactions": interactions,
    }), 200


# ===== DELETE /api/jobs/<id> =====
@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@require_auth
def delete_job(job_id):
    success, error = job_service.delete_job(get_tenant_id(), job_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Projet supprimé"}), 200
