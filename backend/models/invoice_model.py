from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_client_conn()
    cur = conn.execute(
        """SELECT i.*, c.name as client_name, j.title as job_title FROM invoices i
           LEFT JOIN clients c ON c.id = i.client_id
           LEFT JOIN jobs j ON j.id = i.job_id
           WHERE i.tenant_id = ? ORDER BY i.created_at DESC LIMIT ? OFFSET ?""",
        (tenant_id, per_page, offset)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, invoice_id):
    conn = get_client_conn()
    cur = conn.execute(
        "SELECT * FROM invoices WHERE id = ? AND tenant_id = ?",
        (invoice_id, tenant_id)
    )
    result = row(cur.fetchone())
    conn.close()
    return result


def get_by_quote(tenant_id, quote_id):
    """Retourne toutes les factures liées à un devis."""
    conn = get_client_conn()
    cur = conn.execute(
        "SELECT * FROM invoices WHERE tenant_id = ? AND quote_id = ? ORDER BY created_at",
        (tenant_id, quote_id)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "INSERT INTO invoices (tenant_id, client_id, job_id, quote_id, amount, status, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tenant_id, data.get("client_id"), data.get("job_id"), data.get("quote_id"),
             data.get("amount", 0), data.get("status", "pending"), data.get("due_date"))
        )
        conn.commit()
        result = row(conn.execute("SELECT * FROM invoices WHERE id = ?", (cur.lastrowid,)).fetchone())
        return result
    finally:
        conn.close()


def create_deposit(tenant_id, quote, lines, data):
    """Crée une facture d'acompte à partir d'un devis."""
    quote_ht = float(quote.get("amount", 0))

    if data.get("deposit_type") == "amount":
        deposit_ht = float(data.get("deposit_value", 0))
        percent    = round(deposit_ht / quote_ht * 100, 2) if quote_ht else 0
    else:
        percent    = float(data.get("deposit_value", 30))
        deposit_ht = round(quote_ht * percent / 100, 2)

    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO invoices
               (tenant_id, client_id, job_id, quote_id, amount, status, due_date,
                invoice_type, deposit_percent, notes)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, 'deposit', ?, ?)""",
            (tenant_id, quote["client_id"], quote.get("job_id"), quote["id"],
             deposit_ht, data.get("due_date"), percent, data.get("notes"))
        )
        conn.commit()
        return row(conn.execute("SELECT * FROM invoices WHERE id = ?", (cur.lastrowid,)).fetchone())
    finally:
        conn.close()


def create_final(tenant_id, quote, deposit_invoice, data):
    """Crée une facture finale, déduisant l'acompte éventuel."""
    quote_ht   = float(quote.get("amount", 0))
    deposit_ht = float(deposit_invoice.get("amount", 0)) if deposit_invoice else 0
    final_ht   = max(0, round(quote_ht - deposit_ht, 2))

    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO invoices
               (tenant_id, client_id, job_id, quote_id, amount, status, due_date,
                invoice_type, deposit_invoice_id)
               VALUES (?, ?, ?, ?, ?, 'pending', ?, 'final', ?)""",
            (tenant_id, quote["client_id"], quote.get("job_id"), quote["id"],
             final_ht, data.get("due_date"),
             deposit_invoice["id"] if deposit_invoice else None)
        )
        conn.commit()
        return row(conn.execute("SELECT * FROM invoices WHERE id = ?", (cur.lastrowid,)).fetchone())
    finally:
        conn.close()


def update_status(tenant_id, invoice_id, status):
    conn = get_client_conn()
    try:
        conn.execute(
            "UPDATE invoices SET status = ? WHERE id = ? AND tenant_id = ?",
            (status, invoice_id, tenant_id)
        )
        conn.commit()
        result = row(conn.execute(
            "SELECT * FROM invoices WHERE id = ? AND tenant_id = ?", (invoice_id, tenant_id)
        ).fetchone())
        return result
    finally:
        conn.close()


def delete(tenant_id, invoice_id):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "DELETE FROM invoices WHERE id = ? AND tenant_id = ?", (invoice_id, tenant_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
