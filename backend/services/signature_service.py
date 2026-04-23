# ===== SIGNATURE_SERVICE.PY =====
# Service central pour le flux de signature en ligne des devis.
#
# Responsabilités :
#   1. Génération du lien d'accès unique (token UUID)
#   2. Envoi et validation des codes OTP (consultation + signature)
#   3. Mise à jour du statut du devis après signature
#   4. Génération et stockage du PDF signé
#   5. Journalisation de chaque événement dans signature_events
#
# Utilisé par : backend/routes/quote_access.py

import logging
import os

from backend.models import quote_token_model, quote_model, signature_model
from backend.models import client_model, job_model
from backend.models.tenant_model import get_by_id as get_tenant
from backend.utils.email_utils import send_otp_email, send_signed_quote_email
from backend.utils.pdf_generator import generate_quote_pdf

log = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════
# 1. LIEN D'ACCÈS
# ═══════════════════════════════════════════════════════

def generate_access_link(tenant_id: int, quote_id: int, base_url: str) -> dict:
    """
    Crée (ou retourne) le token UUID pour ce devis.
    Retourne { token, sign_link }.
    """
    token = quote_token_model.create_or_get(tenant_id, quote_id)
    sign_link = f"{base_url.rstrip('/')}/quote/{token['access_token']}"
    return {"token": token, "sign_link": sign_link}


def get_public_info(access_token: str) -> tuple[dict | None, dict | None]:
    """
    Retourne les infos publiques du devis pour l'affichage initial.
    Retourne (data, error_response) — l'un des deux est None.
    """
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return None, {"error": "Lien invalide ou expiré", "code": 404}

    from backend.utils.db import get_client_conn, row
    conn = get_client_conn()
    q = row(conn.execute(
        """SELECT q.*, c.name as client_name, c.email as client_email
           FROM quotes q LEFT JOIN clients c ON c.id = q.client_id
           WHERE q.tenant_id=? AND q.id=?""",
        (token["tenant_id"], token["quote_id"]),
    ).fetchone())
    conn.close()

    if not q:
        return None, {"error": "Devis introuvable", "code": 404}

    company = get_tenant(token["tenant_id"]) or {}

    return {
        "token_id":      token["id"],
        "quote_ref":     f"DEV-{token['tenant_id']}-{token['quote_id']}",
        "quote_title":   q.get("title") or "Devis",
        "quote_amount":  q.get("amount", 0),
        "client_name":   q.get("client_name") or "",
        "client_email":  q.get("client_email") or "",
        "company_name":  company.get("company_name") or company.get("name") or "",
        "view_verified": bool(token["view_verified"]),
        "signed":        bool(token["signed_at"]),
        "signed_at":     token.get("signed_at"),
    }, None


# ═══════════════════════════════════════════════════════
# 2. CODE OTP — CONSULTATION
# ═══════════════════════════════════════════════════════

def request_view_code(
    access_token: str,
    ip: str | None = None,
    ua: str | None = None,
) -> tuple[dict, int]:
    """
    Génère et envoie le code de consultation.
    Retourne (body_dict, http_status).
    """
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return {"error": "Lien invalide"}, 404

    if token["view_verified"]:
        return {"message": "Déjà vérifié"}, 200

    code = quote_token_model.request_view_code(token["id"])

    # Récupérer l'email client
    info, _ = get_public_info(access_token)
    client_email = (info or {}).get("client_email", "")

    sent, send_err = (
        send_otp_email(client_email, code, purpose="consultation")
        if client_email
        else (False, "Aucun email client renseigné")
    )

    # Journal
    signature_model.log_event(
        token["tenant_id"], token["quote_id"], token["id"],
        signature_model.VIEW_CODE_SENT,
        ip=ip, ua=ua,
        details=f"email_sent={sent}" + (f" err={send_err}" if send_err else ""),
    )

    body = {"message": "Code envoyé", "email_sent": sent}
    if not sent:
        body["dev_code"]    = code      # visible en dev uniquement
        body["email_error"] = send_err
    return body, 200


def verify_view_code(
    access_token: str,
    code: str,
    ip: str | None = None,
    ua: str | None = None,
) -> tuple[dict, int]:
    """
    Vérifie le code de consultation.
    Retourne (body_dict, http_status).
    """
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return {"error": "Lien invalide"}, 404

    ok, msg = quote_token_model.verify_view_code(token["id"], code)

    event_type = signature_model.VIEW_VERIFIED if ok else signature_model.VIEW_FAILED
    signature_model.log_event(
        token["tenant_id"], token["quote_id"], token["id"],
        event_type, ip=ip, ua=ua, details=msg,
    )

    if not ok:
        return {"error": msg}, 400
    return {"message": "Accès autorisé"}, 200


# ═══════════════════════════════════════════════════════
# 3. CODE OTP — SIGNATURE
# ═══════════════════════════════════════════════════════

def request_sign_code(
    access_token: str,
    ip: str | None = None,
    ua: str | None = None,
) -> tuple[dict, int]:
    """
    Génère et envoie le code de signature.
    Retourne (body_dict, http_status).
    """
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return {"error": "Lien invalide"}, 404

    if not token["view_verified"]:
        return {"error": "Consultez d'abord le devis"}, 403

    if token["signed_at"]:
        return {"message": "Devis déjà signé"}, 200

    code = quote_token_model.request_sign_code(token["id"])

    info, _ = get_public_info(access_token)
    client_email = (info or {}).get("client_email", "")

    sent, send_err = (
        send_otp_email(client_email, code, purpose="signature")
        if client_email
        else (False, "Aucun email client renseigné")
    )

    signature_model.log_event(
        token["tenant_id"], token["quote_id"], token["id"],
        signature_model.SIGN_CODE_SENT,
        ip=ip, ua=ua,
        details=f"email_sent={sent}" + (f" err={send_err}" if send_err else ""),
    )

    body = {"message": "Code de signature envoyé", "email_sent": sent}
    if not sent:
        body["dev_code"]    = code
        body["email_error"] = send_err
    return body, 200


def finalize_signature(
    access_token: str,
    code: str,
    signer_name: str = "",
    ip: str | None = None,
    ua: str | None = None,
) -> tuple[dict, int]:
    """
    Vérifie le code de signature, marque le devis accepté,
    génère et stocke le PDF signé.
    Retourne (body_dict, http_status).
    """
    token = quote_token_model.get_by_token(access_token)
    if not token:
        return {"error": "Lien invalide"}, 404

    if not token["view_verified"]:
        return {"error": "Consultez d'abord le devis"}, 403

    if token["signed_at"]:
        return {"message": "Devis déjà signé"}, 200

    ok, signed_at_val = quote_token_model.verify_sign_code(token["id"], code)

    if not ok:
        signature_model.log_event(
            token["tenant_id"], token["quote_id"], token["id"],
            signature_model.SIGN_FAILED, ip=ip, ua=ua, details=signed_at_val,
        )
        return {"error": signed_at_val}, 400

    tid      = token["tenant_id"]
    quote_id = token["quote_id"]

    # ── Enregistrer le nom du signataire ──
    if signer_name:
        quote_token_model.save_signer_name(token["id"], signer_name)

    # ── Mettre le devis en "accepté" ──
    quote_model.update_status(tid, quote_id, "accepted")

    # ── Générer et stocker le PDF signé ──
    pdf_path, pdf_bytes = _generate_and_store_signed_pdf(
        tid, quote_id, token["id"],
        signer_name=signer_name, signed_at=signed_at_val,
    )

    # ── Envoyer le PDF aux deux parties ──
    if pdf_bytes:
        q       = quote_model.get_by_id(tid, quote_id)
        company = get_tenant(tid) or {}
        client  = client_model.get_by_id(tid, q.get("client_id")) or {}
        send_signed_quote_email(company, client, q, pdf_bytes, signer_name, signed_at_val)

    # ── Journal ──
    signature_model.log_event(
        tid, quote_id, token["id"],
        signature_model.SIGNED,
        ip=ip, ua=ua,
        details=f"signer={signer_name} pdf_path={pdf_path}",
    )

    log.info("Devis %s-%s signé par %s (%s)", tid, quote_id, signer_name, ip)
    return {"message": "Devis signé et accepté — merci !", "pdf_path": pdf_path}, 200


def _generate_and_store_signed_pdf(
    tid: int, quote_id: int, token_id: int,
    signer_name: str = "", signed_at: str = "",
) -> tuple[str | None, bytes | None]:
    """Génère le PDF du devis signé avec bloc de signature et le stocke sur disque."""
    try:
        q       = quote_model.get_by_id(tid, quote_id)
        lines   = quote_model.get_lines(quote_id)
        company = get_tenant(tid) or {}
        client  = client_model.get_by_id(tid, q.get("client_id")) or {}
        job     = job_model.get_by_id(tid, q.get("job_id")) if q.get("job_id") else {}

        pdf_bytes = generate_quote_pdf(
            company, client, q, lines, job=job or {},
            signer_name=signer_name, signed_at=signed_at,
        )
        pdf_path  = signature_model.save_signed_pdf(tid, quote_id, pdf_bytes)
        signature_model.link_pdf_to_token(token_id, pdf_path)
        return pdf_path, pdf_bytes

    except Exception as exc:
        log.error("Erreur génération PDF signé %s-%s : %s", tid, quote_id, exc)
        return None, None


# ═══════════════════════════════════════════════════════
# 4. HISTORIQUE & ACCÈS AUX DONNÉES ENRICHIES
# ═══════════════════════════════════════════════════════

def get_signature_history(tenant_id: int, quote_id: int) -> list[dict]:
    """Retourne l'historique complet des événements de signature."""
    return signature_model.get_history(tenant_id, quote_id)


def get_quote_full(tenant_id: int, quote_id: int) -> dict | None:
    """
    Retourne le devis avec lignes, token d'accès, et historique de signature.
    Utilisé par l'artisan pour voir l'état complet d'un devis.
    """
    return signature_model.get_quote_with_signature(tenant_id, quote_id)


def get_client_tree(tenant_id: int, client_id: int) -> dict:
    """
    Retourne la hiérarchie complète :
      client → projets → tâches par projet + tâches directes.
    """
    return signature_model.get_client_tree(tenant_id, client_id)


# ═══════════════════════════════════════════════════════
# 5. SERVE PDF SIGNÉ
# ═══════════════════════════════════════════════════════

def get_signed_pdf(tenant_id: int, quote_id: int) -> bytes | None:
    """
    Retourne les bytes du PDF signé stocké, ou None si inexistant.
    Utilisé pour permettre au client de re-télécharger après signature.
    """
    path = signature_model.get_signed_pdf_path(tenant_id, quote_id)
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()
