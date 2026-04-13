from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def require_auth(f):
    """Décorateur : vérifie le JWT et injecte tenant_id dans la requête."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("tenant_id"):
            return jsonify({"error": "tenant_id manquant dans le token"}), 403
        return f(*args, **kwargs)
    return decorated


def get_tenant_id():
    """Récupère le tenant_id depuis le JWT courant."""
    claims = get_jwt()
    return claims.get("tenant_id")
