# ===== QUOTE_TOKEN_MODEL.PY =====

import uuid
import random
from datetime import datetime, timedelta

from backend.utils.db import get_client_conn, row


# ───── Helpers ─────

def _gen_code() -> str:
    """Code OTP 5 chiffres."""
    return str(random.randint(10000, 99999))


def _expiry() -> str:
    """Timestamp d'expiration dans 10 minutes (UTC)."""
    return (datetime.utcnow() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# ───── Création / récupération ─────

def create_or_get(tenant_id: int, quote_id: int) -> dict:
    """Crée un token d'accès pour un devis ou retourne l'existant."""
    conn = get_client_conn()
    r = conn.execute(
        "SELECT * FROM quote_tokens WHERE tenant_id=? AND quote_id=?",
        (tenant_id, quote_id)
    ).fetchone()
    if r:
        conn.close()
        return row(r)

    token = uuid.uuid4().hex
    conn.execute(
        "INSERT INTO quote_tokens (tenant_id, quote_id, access_token) VALUES (?,?,?)",
        (tenant_id, quote_id, token)
    )
    conn.commit()
    r = conn.execute(
        "SELECT * FROM quote_tokens WHERE access_token=?", (token,)
    ).fetchone()
    conn.close()
    return row(r)


def save_signer_name(token_id: int, signer_name: str) -> None:
    """Enregistre le nom du signataire dans le token."""
    conn = get_client_conn()
    conn.execute("UPDATE quote_tokens SET signer_name=? WHERE id=?", (signer_name, token_id))
    conn.commit()
    conn.close()


def get_by_token(access_token: str) -> dict | None:
    conn = get_client_conn()
    r = conn.execute(
        "SELECT * FROM quote_tokens WHERE access_token=?", (access_token,)
    ).fetchone()
    conn.close()
    return row(r)


# ───── Consultation (view) ─────

def request_view_code(token_id: int) -> str:
    """Génère un nouveau code de consultation, réinitialise les tentatives."""
    code    = _gen_code()
    expires = _expiry()
    conn = get_client_conn()
    conn.execute(
        "UPDATE quote_tokens SET view_code=?, view_code_expires=?, view_attempts=0 WHERE id=?",
        (code, expires, token_id)
    )
    conn.commit()
    conn.close()
    return code


def verify_view_code(token_id: int, code: str) -> tuple[bool, str | None]:
    """Vérifie le code de consultation. Retourne (ok, erreur)."""
    conn = get_client_conn()
    r = conn.execute(
        "SELECT view_code, view_code_expires, view_attempts, view_verified FROM quote_tokens WHERE id=?",
        (token_id,)
    ).fetchone()
    conn.close()
    if not r:
        return False, "Token introuvable"

    if r["view_verified"]:
        return True, None  # déjà vérifié

    if r["view_attempts"] >= 5:
        return False, "Trop de tentatives — demandez un nouveau code"

    if not r["view_code_expires"] or _now() > r["view_code_expires"]:
        return False, "Code expiré — demandez un nouveau code"

    if r["view_code"] != str(code):
        conn = get_client_conn()
        conn.execute(
            "UPDATE quote_tokens SET view_attempts=view_attempts+1 WHERE id=?",
            (token_id,)
        )
        conn.commit()
        conn.close()
        remaining = max(0, 4 - r["view_attempts"])
        return False, f"Code incorrect — {remaining} essai(s) restant(s)"

    conn = get_client_conn()
    conn.execute("UPDATE quote_tokens SET view_verified=1 WHERE id=?", (token_id,))
    conn.commit()
    conn.close()
    return True, None


# ───── Signature (sign) ─────

def request_sign_code(token_id: int) -> str:
    """Génère un code de signature, réinitialise les tentatives."""
    code    = _gen_code()
    expires = _expiry()
    conn = get_client_conn()
    conn.execute(
        "UPDATE quote_tokens SET sign_code=?, sign_code_expires=?, sign_attempts=0 WHERE id=?",
        (code, expires, token_id)
    )
    conn.commit()
    conn.close()
    return code


def verify_sign_code(token_id: int, code: str) -> tuple[bool, str | None]:
    """Vérifie le code de signature. Retourne (ok, erreur)."""
    conn = get_client_conn()
    r = conn.execute(
        "SELECT sign_code, sign_code_expires, sign_attempts, signed_at FROM quote_tokens WHERE id=?",
        (token_id,)
    ).fetchone()
    conn.close()
    if not r:
        return False, "Token introuvable"

    if r["signed_at"]:
        return True, None  # déjà signé

    if r["sign_attempts"] >= 5:
        return False, "Trop de tentatives — demandez un nouveau code"

    if not r["sign_code_expires"] or _now() > r["sign_code_expires"]:
        return False, "Code expiré — demandez un nouveau code"

    if r["sign_code"] != str(code):
        conn = get_client_conn()
        conn.execute(
            "UPDATE quote_tokens SET sign_attempts=sign_attempts+1 WHERE id=?",
            (token_id,)
        )
        conn.commit()
        conn.close()
        remaining = max(0, 4 - r["sign_attempts"])
        return False, f"Code incorrect — {remaining} essai(s) restant(s)"

    signed_at = _now()
    conn = get_client_conn()
    conn.execute("UPDATE quote_tokens SET signed_at=? WHERE id=?", (signed_at, token_id))
    conn.commit()
    conn.close()
    return True, signed_at
