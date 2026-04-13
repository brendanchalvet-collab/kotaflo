from flask import Blueprint, request, jsonify, send_file
import io

from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.services import invoice_service
from backend.models import invoice_model, quote_model, tenant_model, client_model, job_model
from backend.utils.pdf_generator import generate_invoice_pdf

invoices_bp = Blueprint("invoices", __name__)


# ===== GET /api/invoices =====
@invoices_bp.route("/", methods=["GET"])
@require_auth
def list_invoices():
    page = request.args.get("page", 1, type=int)
    invoices, _ = invoice_service.list_invoices(get_tenant_id(), page)
    return jsonify(invoices), 200


# ===== POST /api/invoices (standard) =====
@invoices_bp.route("/", methods=["POST"])
@require_auth
def create_invoice():
    data = request.get_json()
    invoice, error = invoice_service.create_invoice(get_tenant_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(invoice), 201


# ===== POST /api/invoices/deposit =====
@invoices_bp.route("/deposit", methods=["POST"])
@require_auth
def create_deposit():
    data     = request.get_json()
    quote_id = data.get("quote_id")
    if not quote_id:
        return jsonify({"error": "quote_id requis"}), 400
    invoice, error = invoice_service.create_deposit_invoice(get_tenant_id(), quote_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(invoice), 201


# ===== POST /api/invoices/final =====
@invoices_bp.route("/final", methods=["POST"])
@require_auth
def create_final():
    data     = request.get_json()
    quote_id = data.get("quote_id")
    if not quote_id:
        return jsonify({"error": "quote_id requis"}), 400
    invoice, error = invoice_service.create_final_invoice(get_tenant_id(), quote_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(invoice), 201


# ===== GET /api/invoices/<id> =====
@invoices_bp.route("/<int:invoice_id>", methods=["GET"])
@require_auth
def get_invoice(invoice_id):
    invoice, error = invoice_service.get_invoice(get_tenant_id(), invoice_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(invoice), 200


# ===== GET /api/invoices/<id>/pdf =====
@invoices_bp.route("/<int:invoice_id>/pdf", methods=["GET"])
@require_auth
def get_pdf(invoice_id):
    tenant_id = get_tenant_id()
    invoice   = invoice_model.get_by_id(tenant_id, invoice_id)
    if not invoice:
        return jsonify({"error": "Facture introuvable"}), 404

    company = tenant_model.get_by_id(tenant_id) or {}
    client  = client_model.get_by_id(tenant_id, invoice.get("client_id")) or {}
    job     = job_model.get_by_id(tenant_id, invoice.get("job_id")) if invoice.get("job_id") else {}
    quote   = quote_model.get_by_id(tenant_id, invoice.get("quote_id")) if invoice.get("quote_id") else {}
    lines   = quote_model.get_lines(invoice.get("quote_id")) if invoice.get("quote_id") else []

    deposit_invoice = None
    if invoice.get("deposit_invoice_id"):
        deposit_invoice = invoice_model.get_by_id(tenant_id, invoice["deposit_invoice_id"])

    pdf_bytes = generate_invoice_pdf(
        company, client, invoice, quote, lines,
        deposit_invoice=deposit_invoice, job=job or {}
    )
    inv_type  = invoice.get("invoice_type", "standard")
    prefix    = {"deposit": "ACOMPTE", "final": "FINALE"}.get(inv_type, "FAC")
    filename  = f"{prefix}-{tenant_id}-{invoice_id}.pdf"

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


# ===== PATCH /api/invoices/<id>/status =====
@invoices_bp.route("/<int:invoice_id>/status", methods=["PATCH"])
@require_auth
def update_status(invoice_id):
    data = request.get_json()
    invoice, error = invoice_service.update_invoice_status(
        get_tenant_id(), invoice_id, data.get("status")
    )
    if error:
        return jsonify({"error": error}), 400
    return jsonify(invoice), 200


# ===== DELETE /api/invoices/<id> =====
@invoices_bp.route("/<int:invoice_id>", methods=["DELETE"])
@require_auth
def delete_invoice(invoice_id):
    success, error = invoice_service.delete_invoice(get_tenant_id(), invoice_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Facture supprimée"}), 200
