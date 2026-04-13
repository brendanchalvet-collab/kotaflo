# ===== GMAIL API — Création de brouillons =====
import base64
import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import Config

log    = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _build_service(token_json):
    data  = json.loads(token_json)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds, cache_discovery=False), creds


def create_draft(token_json, company, client, quote, pdf_bytes):
    """
    Crée un brouillon Gmail avec le devis PDF en pièce jointe.
    Retourne (draft_url, updated_token_json, error_message).
    """
    try:
        service, creds = _build_service(token_json)

        company_name = str(company.get("company_name") or company.get("name") or "")
        client_name  = str(client.get("name") or "")
        client_email = str(client.get("email") or "")
        tenant_id    = quote.get("tenant_id", "")
        quote_id     = quote.get("id", "")
        quote_ref    = f"DEV-{tenant_id}-{quote_id}"
        title        = quote.get("title") or ""

        # ── Corps du message ──
        msg = MIMEMultipart()
        msg["To"]      = client_email
        msg["Subject"] = f"Votre devis {quote_ref}" + (f" — {title}" if title else "")

        body_text = (
            f"Bonjour{(' ' + client_name) if client_name else ''},\n\n"
            f"Veuillez trouver ci-joint votre devis {quote_ref}"
            f"{(' — ' + title) if title else ''}.\n\n"
            f"N'hésitez pas à nous contacter pour toute question.\n"
            f"Pour accepter ce devis, retournez-le signé avec la mention "
            f"\"Lu et approuvé, bon pour accord\".\n\n"
            f"Cordialement,\n{company_name}"
        )
        msg.attach(MIMEText(body_text, "plain", "utf-8"))

        # ── Pièce jointe PDF ──
        part = MIMEBase("application", "pdf")
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f'attachment; filename="{quote_ref}.pdf"')
        msg.attach(part)

        raw   = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        draft = service.users().drafts().create(
            userId="me",
            body={"message": {"raw": raw}}
        ).execute()

        thread_id = draft.get("message", {}).get("threadId", "")
        draft_url = (
            f"https://mail.google.com/mail/u/0/#drafts/{thread_id}"
            if thread_id else "https://mail.google.com/mail/#drafts"
        )

        # ── Sauvegarder le token rafraîchi ──
        updated = json.dumps({
            "token":         creds.token,
            "refresh_token": creds.refresh_token,
        })

        return draft_url, updated, None

    except Exception as exc:
        log.error("Gmail draft error: %s", exc)
        return None, token_json, str(exc)
