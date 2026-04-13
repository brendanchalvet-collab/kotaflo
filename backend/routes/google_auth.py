# ===== GOOGLE OAUTH — Connexion Gmail =====
import json
import secrets

from flask import Blueprint, jsonify, redirect, request, session
from google_auth_oauthlib.flow import Flow

from config import Config
from backend.utils.auth_utils import require_auth, get_tenant_id
from backend.models import tenant_model

google_auth_bp = Blueprint("google_auth", __name__)
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _make_flow():
    return Flow.from_client_config(
        {"web": {
            "client_id":     Config.GOOGLE_CLIENT_ID,
            "client_secret": Config.GOOGLE_CLIENT_SECRET,
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
            "redirect_uris": [Config.GOOGLE_REDIRECT_URI],
        }},
        scopes=SCOPES,
        redirect_uri=Config.GOOGLE_REDIRECT_URI,
    )


# ── GET /api/google/auth  (appelé en AJAX depuis le profil) ──
@google_auth_bp.route("/auth")
@require_auth
def google_auth():
    """Génère l'URL d'autorisation Google et la retourne en JSON."""
    state = secrets.token_urlsafe(16)
    session["google_state"]     = state
    session["google_tenant_id"] = get_tenant_id()

    flow = _make_flow()
    auth_url, _ = flow.authorization_url(
        state=state,
        access_type="offline",
        prompt="consent",
    )
    return jsonify({"auth_url": auth_url})


# ── GET /api/google/callback  (redirection navigateur depuis Google) ──
@google_auth_bp.route("/callback")
def google_callback():
    """Reçoit le code OAuth, stocke le token, redirige vers le profil."""
    state     = request.args.get("state")
    tenant_id = session.get("google_tenant_id")

    if not state or state != session.get("google_state") or not tenant_id:
        return redirect("/profile?gmail=error")

    flow = _make_flow()
    try:
        flow.fetch_token(code=request.args.get("code"))
        creds = flow.credentials
    except Exception:
        return redirect("/profile?gmail=error")

    token_json = json.dumps({
        "token":         creds.token,
        "refresh_token": creds.refresh_token,
    })
    tenant_model.save_google_token(tenant_id, token_json)

    return redirect("/profile?gmail=connected")


# ── DELETE /api/google/disconnect ──
@google_auth_bp.route("/disconnect", methods=["DELETE"])
@require_auth
def google_disconnect():
    """Supprime le token Google stocké."""
    tenant_model.save_google_token(get_tenant_id(), None)
    return jsonify({"message": "Gmail déconnecté"}), 200
