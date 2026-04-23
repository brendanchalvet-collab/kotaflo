# ===== EMAIL UTILS =====
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from config import Config

log = logging.getLogger(__name__)


def _smtp_configured():
    return bool(Config.SMTP_USER and Config.SMTP_PASSWORD and Config.SMTP_HOST)


def send_quote_email(company, client, quote, pdf_bytes, sign_link=None):
    """
    Envoie le devis par email au client avec le PDF en pièce jointe.
    Si sign_link est fourni, inclut le lien de signature électronique.
    Retourne (True, None) ou (False, message_erreur).
    """
    if not _smtp_configured():
        return False, "SMTP non configuré"

    to_email = (client or {}).get("email")
    if not to_email:
        return False, "Client sans adresse email"

    company_name = str(company.get("company_name") or company.get("name") or "Votre artisan")
    client_name  = str(client.get("name") or "")
    tenant_id    = quote.get("tenant_id", "")
    quote_id     = quote.get("id", "")
    quote_title  = quote.get("title") or ""
    quote_ref    = f"DEV-{tenant_id}-{quote_id}"

    # ── Bloc signature électronique (optionnel) ──
    sign_block = ""
    if sign_link:
        sign_block = f"""
      <div style="margin:24px 0;padding:16px;background:#f0fdf4;border-left:4px solid #16a34a;border-radius:4px">
        <p style="margin:0 0 8px;font-weight:bold;color:#15803d">Signature électronique</p>
        <p style="margin:0 0 12px">Vous pouvez signer ce devis directement en ligne (sans impression) :</p>
        <a href="{sign_link}" style="display:inline-block;padding:10px 20px;background:#16a34a;color:#fff;text-decoration:none;border-radius:6px;font-weight:bold">
          Signer le devis en ligne
        </a>
        <p style="margin:12px 0 0;font-size:12px;color:#6b7280">
          Un code de vérification vous sera envoyé par email pour confirmer votre identité.<br>
          Lien valable jusqu'à acceptation du devis.
        </p>
      </div>"""

    # ── Corps HTML ──
    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#1f2937;font-size:14px;line-height:1.6">
      <p>Bonjour{(' ' + client_name) if client_name else ''},</p>
      <p>
        Veuillez trouver ci-joint votre devis <strong>{quote_ref}</strong>
        {('&mdash; ' + quote_title) if quote_title else ''}.
      </p>
      {sign_block}
      <p>N'hésitez pas à nous contacter pour toute question.</p>
      <p>Cordialement,<br><strong>{company_name}</strong></p>
    </body></html>
    """

    # ── Construction du message ──
    msg = MIMEMultipart()
    msg["From"]    = Config.SMTP_FROM or Config.SMTP_USER
    msg["To"]      = to_email
    msg["Subject"] = f"Votre devis {quote_ref} — {company_name}"
    msg.attach(MIMEText(html, "html", "utf-8"))

    # ── Pièce jointe PDF ──
    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{quote_ref}.pdf"')
    msg.attach(part)

    # ── Envoi SMTP ──
    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())
        return True, None
    except Exception as exc:
        log.error("Erreur envoi email devis %s : %s", quote_ref, exc)
        return False, str(exc)


def send_signed_quote_email(
    company: dict,
    client: dict,
    quote: dict,
    pdf_bytes: bytes,
    signer_name: str,
    signed_at: str,
) -> tuple:
    """
    Envoie le devis signé en PDF aux deux parties (artisan + client) dans le même email.
    Retourne (True, None) ou (False, raison).
    """
    if not _smtp_configured():
        return False, "SMTP non configuré"

    client_email  = (client or {}).get("email", "")
    artisan_email = Config.SMTP_FROM or Config.SMTP_USER
    recipients    = list(filter(None, [client_email, artisan_email]))
    if not recipients:
        return False, "Aucun destinataire"

    company_name = str(company.get("company_name") or company.get("name") or "Votre artisan")
    client_name  = str(client.get("name") or signer_name or "")
    tenant_id    = quote.get("tenant_id", "")
    quote_id     = quote.get("id", "")
    quote_ref    = f"DEV-{tenant_id}-{quote_id}"
    quote_title  = quote.get("title") or ""

    # Formater la date de signature
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(str(signed_at).replace("Z", ""))
        signed_date = dt.strftime("%d/%m/%Y à %H:%M")
    except Exception:
        signed_date = str(signed_at or "")

    html = f"""
    <html><body style="font-family:Arial,sans-serif;color:#1f2937;font-size:14px;line-height:1.6">
      <p>Bonjour,</p>
      <p>
        Le devis <strong>{quote_ref}</strong>
        {('&mdash; ' + quote_title) if quote_title else ''}
        a été signé électroniquement par <strong>{signer_name or client_name}</strong>
        le {signed_date}.
      </p>
      <div style="margin:20px 0;padding:14px 16px;background:#f0fdf4;border-left:4px solid #16a34a;border-radius:4px">
        <p style="margin:0 0 4px;font-weight:bold;color:#15803d">Signature enregistrée</p>
        <p style="margin:0;font-size:13px">
          Signataire : <strong>{signer_name or client_name}</strong><br>
          Mention : <em>Lu et approuvé, bon pour accord</em><br>
          Date : {signed_date}
        </p>
      </div>
      <p>Le devis signé est joint en pièce attachée.</p>
      <p>Cordialement,<br><strong>{company_name}</strong></p>
    </body></html>
    """

    msg = MIMEMultipart()
    msg["From"]    = artisan_email
    msg["To"]      = ", ".join(recipients)
    msg["Subject"] = f"Devis signé {quote_ref} — {company_name}"
    msg.attach(MIMEText(html, "html", "utf-8"))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{quote_ref}-signe.pdf"')
    msg.attach(part)

    try:
        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(artisan_email, recipients, msg.as_string())
        return True, None
    except Exception as exc:
        log.error("Erreur envoi email devis signé %s : %s", quote_ref, exc)
        return False, str(exc)


def send_otp_email(to_email: str, code: str, purpose: str = "accès") -> tuple:
    """
    Envoie un code OTP 5 chiffres par email.
    Retourne (True, None) si succès, (False, raison) sinon.
    Fallback console si SMTP non configuré (dev).
    """
    subject = f"Votre code de {purpose} — Kotaflo"
    body    = (
        f"Bonjour,\n\n"
        f"Votre code de {purpose} est :\n\n"
        f"    {code}\n\n"
        f"Ce code est valable 10 minutes.\n"
        f"Ne le communiquez à personne.\n\n"
        f"— Kotaflo"
    )

    if not _smtp_configured():
        print(f"[EMAIL FALLBACK] → {to_email} | {subject} | Code : {code}")
        return False, "SMTP non configuré"

    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"]    = Config.SMTP_FROM or Config.SMTP_USER
        msg["To"]      = to_email

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        return True, None

    except Exception as exc:
        log.error("Erreur envoi OTP %s : %s", to_email, exc)
        return False, str(exc)
