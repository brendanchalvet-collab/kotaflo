import bcrypt
from flask_jwt_extended import create_access_token

from backend.models import user_model


def register(email, password):
    """Inscrit un nouvel utilisateur et crée son tenant."""
    if not email or not password:
        return None, "Email et mot de passe requis"

    existing = user_model.get_by_email(email)
    if existing:
        return None, "Cet email est déjà utilisé"

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user, tenant_id = user_model.create(email, password_hash)

    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"tenant_id": tenant_id}
    )
    return {"token": token, "user": {"id": user["id"], "email": user["email"]}}, None


def login(email, password):
    """Authentifie un utilisateur, retourne un JWT."""
    if not email or not password:
        return None, "Email et mot de passe requis"

    user = user_model.get_by_email(email)
    if not user:
        return None, "Identifiants invalides"

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return None, "Identifiants invalides"

    tenant_id = user_model.get_tenant_id(user["id"])
    if not tenant_id:
        return None, "Aucun tenant associé"

    token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"tenant_id": tenant_id}
    )
    return {"token": token, "user": {"id": user["id"], "email": user["email"]}}, None
