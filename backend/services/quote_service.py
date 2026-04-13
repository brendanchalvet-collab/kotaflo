import logging
from backend.models import quote_model

log = logging.getLogger(__name__)
VALID_STATUSES = ("draft", "sent", "accepted", "refused")


def list_quotes(tenant_id, page=1):
    return quote_model.get_all(tenant_id, page=page), None


def get_quote(tenant_id, quote_id):
    quote = quote_model.get_by_id(tenant_id, quote_id)
    if not quote:
        return None, "Devis introuvable"
    return quote, None


def create_quote(tenant_id, data):
    if not data.get("client_id"):
        return None, "client_id requis"
    if not data.get("job_id"):
        return None, "Un projet est obligatoire"
    return quote_model.create(tenant_id, data), None


def update_quote_status(tenant_id, quote_id, status):
    if status not in VALID_STATUSES:
        return None, f"Statut invalide. Valeurs possibles : {VALID_STATUSES}"
    quote = quote_model.update_status(tenant_id, quote_id, status)
    if not quote:
        return None, "Devis introuvable"

    result = dict(quote)
    if status == "sent":
        result["draft_url"] = _try_create_gmail_draft(tenant_id, quote)

    return result, None


def _try_create_gmail_draft(tenant_id, quote):
    """Crée un brouillon Gmail avec le PDF. Retourne l'URL ou None si non connecté."""
    try:
        from backend.models import tenant_model, client_model, job_model
        from backend.utils.pdf_generator import generate_quote_pdf
        from backend.utils.gmail_api import create_draft

        token_json = tenant_model.get_google_token(tenant_id)
        if not token_json:
            return None  # Gmail non connecté, pas d'erreur

        company = tenant_model.get_by_id(tenant_id) or {}
        client  = client_model.get_by_id(tenant_id, quote.get("client_id")) or {}
        job     = job_model.get_by_id(tenant_id, quote.get("job_id")) if quote.get("job_id") else {}
        lines   = quote_model.get_lines(quote.get("id"))
        pdf     = generate_quote_pdf(company, client, quote, lines, job=job or {})

        draft_url, updated_token, error = create_draft(token_json, company, client, quote, pdf)

        if error:
            log.error("Gmail draft: %s", error)
            return None

        # Sauvegarder le token si rafraîchi
        if updated_token != token_json:
            tenant_model.save_google_token(tenant_id, updated_token)

        return draft_url

    except Exception as exc:
        log.error("Gmail draft exception: %s", exc)
        return None


def delete_quote(tenant_id, quote_id):
    deleted = quote_model.delete(tenant_id, quote_id)
    if not deleted:
        return False, "Devis introuvable"
    return True, None
