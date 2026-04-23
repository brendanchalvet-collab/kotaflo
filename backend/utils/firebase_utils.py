import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

_firebase_app = None


def init_firebase():
    """Initialise Firebase Admin SDK au démarrage de l'app Flask."""
    global _firebase_app
    if _firebase_app is not None:
        return

    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "firebase-service-account.json")

    if not os.path.exists(service_account_path):
        print(f"[WARN] Firebase service account introuvable : {service_account_path}")
        print("[WARN] Firebase Auth désactivé — utilisez les variables d'env.")
        return

    cred = credentials.Certificate(service_account_path)
    _firebase_app = firebase_admin.initialize_app(cred)
    print("[OK] Firebase Admin SDK initialisé")


def verify_firebase_token(id_token: str) -> dict:
    """
    Vérifie un Firebase ID token.
    Retourne {'uid': ..., 'email': ...} si valide.
    Lève ValueError si le token est invalide ou expiré.
    """
    if _firebase_app is None:
        raise ValueError("Firebase non initialisé — vérifiez FIREBASE_SERVICE_ACCOUNT")

    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return {
            "uid":   decoded["uid"],
            "email": decoded.get("email", ""),
        }
    except Exception as e:
        raise ValueError(f"Token Firebase invalide : {e}") from e
