from backend.utils.db import get_client_conn, row, rows


def get_for_client(tenant_id, client_id):
    conn = get_client_conn()
    cur = conn.execute(
        "SELECT * FROM interactions WHERE tenant_id = ? AND client_id = ? ORDER BY date DESC",
        (tenant_id, client_id)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def create(tenant_id, client_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO interactions (tenant_id, client_id, type, title, notes, date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (tenant_id, client_id, data.get("type", "note"),
             data.get("title"), data.get("notes"), data.get("date"))
        )
        conn.commit()
        return row(conn.execute("SELECT * FROM interactions WHERE id = ?", (cur.lastrowid,)).fetchone())
    finally:
        conn.close()


def delete(tenant_id, interaction_id):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "DELETE FROM interactions WHERE id = ? AND tenant_id = ?",
            (interaction_id, tenant_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_timeline(tenant_id, client_id):
    """Fusionne interactions, devis et factures pour un contact donné."""
    conn = get_client_conn()
    events = []

    # Interactions manuelles
    for r in conn.execute(
        "SELECT id, type, title, notes, date FROM interactions WHERE tenant_id=? AND client_id=?",
        (tenant_id, client_id)
    ).fetchall():
        events.append({
            "kind":  "interaction",
            "id":    r["id"],
            "type":  r["type"],
            "title": r["title"] or "",
            "notes": r["notes"] or "",
            "date":  r["date"],
        })

    # Devis
    for r in conn.execute(
        """SELECT q.id, q.title, q.amount, q.status, q.created_at, j.title as job_title
           FROM quotes q LEFT JOIN jobs j ON j.id = q.job_id
           WHERE q.tenant_id=? AND q.client_id=?""",
        (tenant_id, client_id)
    ).fetchall():
        events.append({
            "kind":      "quote",
            "id":        r["id"],
            "title":     r["title"] or f"Devis #{r['id']}",
            "job_title": r["job_title"],
            "amount":    r["amount"],
            "status":    r["status"],
            "date":      r["created_at"],
        })

    # Factures
    for r in conn.execute(
        """SELECT i.id, i.amount, i.status, i.due_date, i.created_at, j.title as job_title
           FROM invoices i LEFT JOIN jobs j ON j.id = i.job_id
           WHERE i.tenant_id=? AND i.client_id=?""",
        (tenant_id, client_id)
    ).fetchall():
        events.append({
            "kind":      "invoice",
            "id":        r["id"],
            "title":     f"Facture #{r['id']}",
            "job_title": r["job_title"],
            "amount":    r["amount"],
            "status":    r["status"],
            "due_date":  r["due_date"],
            "date":      r["created_at"],
        })

    conn.close()
    events.sort(key=lambda e: e["date"] or "", reverse=True)
    return events
