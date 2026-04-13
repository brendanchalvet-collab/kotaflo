from flask import Blueprint, request, jsonify, send_file
import io

from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.services import quote_service
from backend.utils.pdf_generator import generate_quote_pdf
from backend.models import quote_model, tenant_model, client_model, job_model
import logging
log = logging.getLogger(__name__)

quotes_bp = Blueprint("quotes", __name__)


# ===== GET /api/quotes =====
@quotes_bp.route("/", methods=["GET"])
@require_auth
def list_quotes():
    page = request.args.get("page", 1, type=int)
    quotes, _ = quote_service.list_quotes(get_tenant_id(), page)
    return jsonify(quotes), 200


# ===== POST /api/quotes =====
@quotes_bp.route("/", methods=["POST"])
@require_auth
def create_quote():
    data = request.get_json()
    quote, error = quote_service.create_quote(get_tenant_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(quote), 201


# ===== GET /api/quotes/<id>/full =====
# Devis + lignes + token d'accès + historique signature (usage artisan)
@quotes_bp.route("/<int:quote_id>/full", methods=["GET"])
@require_auth
def get_quote_full(quote_id):
    from backend.services.signature_service import get_quote_full
    data = get_quote_full(get_tenant_id(), quote_id)
    if not data:
        return jsonify({"error": "Devis introuvable"}), 404
    return jsonify(data), 200


# ===== GET /api/quotes/<id>/signature-history =====
@quotes_bp.route("/<int:quote_id>/signature-history", methods=["GET"])
@require_auth
def get_signature_history(quote_id):
    from backend.services.signature_service import get_signature_history
    history = get_signature_history(get_tenant_id(), quote_id)
    return jsonify(history), 200


# ===== GET /api/quotes/<id>/lines =====
@quotes_bp.route("/<int:quote_id>/lines", methods=["GET"])
@require_auth
def get_lines(quote_id):
    quote = quote_model.get_by_id(get_tenant_id(), quote_id)
    if not quote:
        return jsonify({"error": "Devis introuvable"}), 404
    return jsonify(quote_model.get_lines(quote_id)), 200


# ===== GET /api/quotes/<id> =====
@quotes_bp.route("/<int:quote_id>", methods=["GET"])
@require_auth
def get_quote(quote_id):
    quote, error = quote_service.get_quote(get_tenant_id(), quote_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(quote), 200


# ===== PUT /api/quotes/<id> (brouillon uniquement) =====
@quotes_bp.route("/<int:quote_id>", methods=["PUT"])
@require_auth
def update_quote(quote_id):
    data  = request.get_json()
    quote = quote_model.update(get_tenant_id(), quote_id, data)
    if not quote:
        return jsonify({"error": "Devis introuvable ou non modifiable (statut != brouillon)"}), 400
    return jsonify(quote), 200


# ===== PATCH /api/quotes/<id>/status =====
@quotes_bp.route("/<int:quote_id>/status", methods=["PATCH"])
@require_auth
def update_status(quote_id):
    from backend.models import quote_token_model
    from backend.utils.email_utils import send_quote_email
    import os

    data      = request.get_json()
    status    = data.get("status")
    tenant_id = get_tenant_id()

    quote, error = quote_service.update_quote_status(tenant_id, quote_id, status)
    if error:
        return jsonify({"error": error}), 400

    result = dict(quote)

    # Générer le lien de signature + envoyer l'email automatiquement
    if status == "sent":
        token    = quote_token_model.create_or_get(tenant_id, quote_id)
        base_url = os.getenv("APP_BASE_URL", request.host_url.rstrip("/"))
        sign_link = f"{base_url}/quote/{token['access_token']}"
        result["sign_link"] = sign_link

        # Récupérer les données nécessaires pour le PDF et l'email
        try:
            company = tenant_model.get_by_id(tenant_id) or {}
            client  = client_model.get_by_id(tenant_id, quote["client_id"]) if quote.get("client_id") else {}
            lines   = quote_model.get_lines(quote_id)
            job     = job_model.get_by_id(tenant_id, quote["job_id"]) if quote.get("job_id") else None

            pdf_bytes = generate_quote_pdf(company, client, dict(quote), lines, job)

            ok, err = send_quote_email(
                company   = company,
                client    = client,
                quote     = dict(quote),
                pdf_bytes = pdf_bytes,
                sign_link = sign_link,
            )
            if ok:
                log.info("Email devis %s envoyé à %s", quote_id, (client or {}).get("email"))
            else:
                log.warning("Email devis %s non envoyé : %s", quote_id, err)
                result["email_warning"] = err
        except Exception as exc:
            log.error("Erreur envoi email devis %s : %s", quote_id, exc)
            result["email_warning"] = str(exc)

    return jsonify(result), 200


# ===== DELETE /api/quotes/<id> =====
@quotes_bp.route("/<int:quote_id>", methods=["DELETE"])
@require_auth
def delete_quote(quote_id):
    success, error = quote_service.delete_quote(get_tenant_id(), quote_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Devis supprime"}), 200


# ===== POST /api/quotes/<id>/avenant =====
@quotes_bp.route("/<int:quote_id>/avenant", methods=["POST"])
@require_auth
def create_avenant(quote_id):
    data    = request.get_json()
    avenant = quote_model.create_avenant(get_tenant_id(), quote_id, data)
    if not avenant:
        return jsonify({"error": "Devis parent introuvable"}), 404
    return jsonify(avenant), 201


# ===== GET /api/quotes/<id>/avenants =====
@quotes_bp.route("/<int:quote_id>/avenants", methods=["GET"])
@require_auth
def list_avenants(quote_id):
    avenants = quote_model.get_avenants(get_tenant_id(), quote_id)
    return jsonify(avenants), 200


# ===== GET /api/quotes/<id>/pdf =====
@quotes_bp.route("/<int:quote_id>/pdf", methods=["GET"])
@require_auth
def download_pdf(quote_id):
    tenant_id = get_tenant_id()

    quote = quote_model.get_by_id(tenant_id, quote_id)
    if not quote:
        return jsonify({"error": "Devis introuvable"}), 404

    lines   = quote_model.get_lines(quote_id)
    company = tenant_model.get_by_id(tenant_id) or {}
    client  = client_model.get_by_id(tenant_id, quote.get("client_id")) or {}
    job     = job_model.get_by_id(tenant_id, quote.get("job_id")) if quote.get("job_id") else {}

    pdf_bytes = generate_quote_pdf(company, client, quote, lines, job=job or {})

    prefix   = "AVN" if quote.get("parent_quote_id") else "DEV"
    filename = f"{prefix}-{tenant_id}-{quote_id}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )
