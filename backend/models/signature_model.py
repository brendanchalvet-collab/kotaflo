# ===== SIGNATURE_MODEL.PY =====
# Gestion de l'historique des événements de signature et du stockage PDF signé.

import os
from datetime import datetime

from backend.utils.db import get_client_conn, rows, row


# ───── Constantes event_type ─────

VIEW_CODE_SENT  = "view_code_sent"
VIEW_VERIFIED   = "view_verified"
VIEW_FAILED     = "view_failed"
SIGN_CODE_SENT  = "sign_code_sent"
SIGNED          = "signed"
SIGN_FAILED     = "sign_failed"

SIGNED_PDF_DIR = "signed_pdfs"   # dossier relatif à la racine du projet


# ───── Historique ─────

def log_event(
    tenant_id: int,
    quote_id: int,
    token_id: int,
    event_type: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: str | None = None,
) -> None:
    """Enregistre un événement dans l'historique de signature."""
    conn = get_client_conn()
    conn.execute(
        """INSERT INTO signature_events
           (tenant_id, quote_id, token_id, event_type, ip_address, user_agent, details)
           VALUES (?,?,?,?,?,?,?)""",
        (tenant_id, quote_id, token_id, event_type, ip_address, user_agent, details),
    )
    conn.commit()
    conn.close()


def get_history(tenant_id: int, quote_id: int) -> list[dict]:
    """Retourne l'historique complet des événements pour un devis."""
    conn = get_client_conn()
    result = rows(conn.execute(
        """SELECT * FROM signature_events
           WHERE tenant_id=? AND quote_id=?
           ORDER BY created_at ASC""",
        (tenant_id, quote_id),
    ).fetchall())
    conn.close()
    return result


# ───── Stockage PDF signé ─────

def save_signed_pdf(tenant_id: int, quote_id: int, pdf_bytes: bytes) -> str:
    """
    Sauvegarde le PDF au moment de la signature.
    Retourne le chemin relatif du fichier.
    """
    os.makedirs(SIGNED_PDF_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename  = f"DEV-{tenant_id}-{quote_id}_signed_{timestamp}.pdf"
    filepath  = os.path.join(SIGNED_PDF_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    return filepath


def link_pdf_to_token(token_id: int, pdf_path: str) -> None:
    """Enregistre le chemin du PDF signé dans le token."""
    conn = get_client_conn()
    conn.execute(
        "UPDATE quote_tokens SET signed_pdf_path=? WHERE id=?",
        (pdf_path, token_id),
    )
    conn.commit()
    conn.close()


def get_signed_pdf_path(tenant_id: int, quote_id: int) -> str | None:
    """Retourne le chemin du PDF signé si disponible."""
    conn = get_client_conn()
    r = row(conn.execute(
        "SELECT signed_pdf_path FROM quote_tokens WHERE tenant_id=? AND quote_id=?",
        (tenant_id, quote_id),
    ).fetchone())
    conn.close()
    return r.get("signed_pdf_path") if r else None


# ───── Associations clients → projets → tâches ─────

def get_client_tree(tenant_id: int, client_id: int) -> dict:
    """
    Retourne un client avec tous ses projets et, pour chaque projet, ses tâches.
    Structure : { client, projects: [{ job, tasks: [...] }] }
    """
    conn = get_client_conn()

    client_row = row(conn.execute(
        "SELECT * FROM clients WHERE id=? AND tenant_id=?",
        (client_id, tenant_id),
    ).fetchone())

    if not client_row:
        conn.close()
        return {}

    jobs = rows(conn.execute(
        "SELECT * FROM jobs WHERE client_id=? AND tenant_id=? ORDER BY created_at DESC",
        (client_id, tenant_id),
    ).fetchall())

    projects = []
    for job in jobs:
        tasks = rows(conn.execute(
            "SELECT * FROM tasks WHERE job_id=? AND tenant_id=? ORDER BY priority DESC, due_date ASC",
            (job["id"], tenant_id),
        ).fetchall())
        projects.append({**job, "tasks": tasks})

    # Tâches directes sur le client (sans projet)
    loose_tasks = rows(conn.execute(
        "SELECT * FROM tasks WHERE client_id=? AND job_id IS NULL AND tenant_id=? ORDER BY priority DESC, due_date ASC",
        (client_id, tenant_id),
    ).fetchall())

    conn.close()
    return {
        **client_row,
        "projects":    projects,
        "loose_tasks": loose_tasks,
    }


def get_quote_with_signature(tenant_id: int, quote_id: int) -> dict | None:
    """
    Retourne un devis enrichi : lignes + token d'accès + historique de signature.
    """
    conn = get_client_conn()

    q = row(conn.execute(
        """SELECT q.*, c.name as client_name, j.title as job_title
           FROM quotes q
           LEFT JOIN clients c ON c.id = q.client_id
           LEFT JOIN jobs    j ON j.id = q.job_id
           WHERE q.id=? AND q.tenant_id=?""",
        (quote_id, tenant_id),
    ).fetchone())

    if not q:
        conn.close()
        return None

    lines = rows(conn.execute(
        "SELECT * FROM quote_lines WHERE quote_id=? ORDER BY sort_order",
        (quote_id,),
    ).fetchall())

    token = row(conn.execute(
        "SELECT * FROM quote_tokens WHERE quote_id=? AND tenant_id=?",
        (quote_id, tenant_id),
    ).fetchone())

    history = rows(conn.execute(
        "SELECT * FROM signature_events WHERE quote_id=? AND tenant_id=? ORDER BY created_at",
        (quote_id, tenant_id),
    ).fetchall())

    conn.close()

    return {
        **q,
        "lines":     lines,
        "token":     token,
        "signature_history": history,
    }
