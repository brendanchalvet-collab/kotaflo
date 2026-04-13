# ===== QUOTE_ACCESS.PY — Routes publiques de signature en ligne =====
# Aucun JWT requis — accès client externe via token UUID.
# Toute la logique est déléguée à signature_service.

import io
from flask import Blueprint, request, jsonify, send_file

from backend.services import signature_service
from backend.models import quote_token_model

quote_access_bp = Blueprint("quote_access", __name__)


def _ip() -> str:
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def _ua() -> str:
    return request.headers.get("User-Agent", "")


# ───── GET /api/quote-access/<token> ─────
# Infos publiques du devis
@quote_access_bp.route("/<access_token>", methods=["GET"])
def get_info(access_token):
    data, err = signature_service.get_public_info(access_token)
    if err:
        return jsonify({"error": err["error"]}), err["code"]
    return jsonify(data), 200


# ───── POST /api/quote-access/<token>/request-view-code ─────
# Génère + envoie le code de consultation
@quote_access_bp.route("/<access_token>/request-view-code", methods=["POST"])
def request_view_code(access_token):
    body, status = signature_service.request_view_code(access_token, ip=_ip(), ua=_ua())
    return jsonify(body), status


# ───── POST /api/quote-access/<token>/verify-view ─────
# Vérifie le code de consultation
@quote_access_bp.route("/<access_token>/verify-view", methods=["POST"])
def verify_view(access_token):
    code = str(request.get_json(force=True).get("code", ""))
    body, status = signature_service.verify_view_code(access_token, code, ip=_ip(), ua=_ua())
    return jsonify(body), status


# ───── GET /api/quote-access/<token>/pdf ─────
# Sert le PDF en lecture (seulement si consultation vérifiée)
@quote_access_bp.route("/<access_token>/pdf", methods=["GET"])
def serve_pdf(access_token):
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return jsonify({"error": "Lien invalide"}), 404
    if not token["view_verified"]:
        return jsonify({"error": "Accès non autorisé"}), 403

    # Si le devis est déjà signé, servir le PDF signé stocké
    signed_bytes = signature_service.get_signed_pdf(token["tenant_id"], token["quote_id"])
    if signed_bytes:
        return send_file(
            io.BytesIO(signed_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"DEV-{token['tenant_id']}-{token['quote_id']}-signe.pdf",
        )

    # Sinon, générer le PDF à la volée
    from backend.models import quote_model, client_model, job_model
    from backend.models.tenant_model import get_by_id as get_tenant
    from backend.utils.pdf_generator import generate_quote_pdf

    tid      = token["tenant_id"]
    quote_id = token["quote_id"]
    q        = quote_model.get_by_id(tid, quote_id)
    if not q:
        return jsonify({"error": "Devis introuvable"}), 404

    lines   = quote_model.get_lines(quote_id)
    company = get_tenant(tid) or {}
    client  = client_model.get_by_id(tid, q.get("client_id")) or {}
    job     = job_model.get_by_id(tid, q.get("job_id")) if q.get("job_id") else {}

    pdf_bytes = generate_quote_pdf(company, client, q, lines, job=job or {})
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"DEV-{tid}-{quote_id}.pdf",
    )


# ───── POST /api/quote-access/<token>/request-sign-code ─────
# Génère + envoie le code de signature
@quote_access_bp.route("/<access_token>/request-sign-code", methods=["POST"])
def request_sign_code(access_token):
    body, status = signature_service.request_sign_code(access_token, ip=_ip(), ua=_ua())
    return jsonify(body), status


# ───── POST /api/quote-access/<token>/sign ─────
# Vérifie le code de signature, finalise (statut accepté + PDF stocké)
@quote_access_bp.route("/<access_token>/sign", methods=["POST"])
def sign_quote(access_token):
    code = str(request.get_json(force=True).get("code", ""))
    body, status = signature_service.finalize_signature(access_token, code, ip=_ip(), ua=_ua())
    return jsonify(body), status


# ───── GET /api/quote-access/<token>/history ─────
# Historique des événements (usage artisan, protégé)
@quote_access_bp.route("/<access_token>/history", methods=["GET"])
def get_history(access_token):
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return jsonify({"error": "Lien invalide"}), 404
    history = signature_service.get_signature_history(token["tenant_id"], token["quote_id"])
    return jsonify(history), 200
