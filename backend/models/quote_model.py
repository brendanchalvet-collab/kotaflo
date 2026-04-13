from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_client_conn()
    cur = conn.execute(
        """SELECT q.*, c.name as client_name, j.title as job_title FROM quotes q
           LEFT JOIN clients c ON c.id = q.client_id
           LEFT JOIN jobs j ON j.id = q.job_id
           WHERE q.tenant_id = ? ORDER BY q.created_at DESC LIMIT ? OFFSET ?""",
        (tenant_id, per_page, offset)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, quote_id):
    conn = get_client_conn()
    cur = conn.execute("SELECT * FROM quotes WHERE id = ? AND tenant_id = ?", (quote_id, tenant_id))
    result = row(cur.fetchone())
    conn.close()
    return result


def update(tenant_id, quote_id, data):
    """Met à jour un devis brouillon (infos + lignes)."""
    lines  = data.get("lines", [])
    amount = sum(float(l.get("quantity", 1)) * float(l.get("unit_price", 0)) for l in lines)

    conn = get_client_conn()
    try:
        conn.execute(
            """UPDATE quotes SET client_id=?, job_id=?, title=?, amount=?, notes=?,
               payment_terms=?, expiry_date=?
               WHERE id=? AND tenant_id=? AND status='draft'""",
            (data.get("client_id"), data.get("job_id"), data.get("title"), amount, data.get("notes"),
             data.get("payment_terms", "Comptant"), data.get("expiry_date"),
             quote_id, tenant_id)
        )
        # Remplacer les lignes existantes
        conn.execute("DELETE FROM quote_lines WHERE quote_id = ?", (quote_id,))
        for i, line in enumerate(lines):
            conn.execute(
                """INSERT INTO quote_lines (quote_id, tenant_id, designation, description,
                   tva_rate, quantity, unit_price, sort_order) VALUES (?,?,?,?,?,?,?,?)""",
                (quote_id, tenant_id, line.get("designation"), line.get("description"),
                 line.get("tva_rate", 10), line.get("quantity", 1), line.get("unit_price", 0), i)
            )
        conn.commit()
        return row(conn.execute("SELECT * FROM quotes WHERE id=?", (quote_id,)).fetchone())
    finally:
        conn.close()


def get_lines(quote_id):
    conn = get_client_conn()
    cur = conn.execute(
        "SELECT * FROM quote_lines WHERE quote_id = ? ORDER BY sort_order",
        (quote_id,)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        # Calcul du montant total depuis les lignes
        lines = data.get("lines", [])
        amount = sum(float(l.get("quantity", 1)) * float(l.get("unit_price", 0)) for l in lines)

        cur = conn.execute(
            """INSERT INTO quotes (tenant_id, client_id, job_id, title, amount, status, notes, payment_terms, expiry_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tenant_id, data.get("client_id"), data.get("job_id"), data.get("title"), amount,
             data.get("status", "draft"), data.get("notes"),
             data.get("payment_terms", "Comptant"), data.get("expiry_date"))
        )
        quote_id = cur.lastrowid

        # Insérer les lignes
        for i, line in enumerate(lines):
            conn.execute(
                """INSERT INTO quote_lines (quote_id, tenant_id, designation, description, tva_rate, quantity, unit_price, sort_order)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (quote_id, tenant_id, line.get("designation"), line.get("description"),
                 line.get("tva_rate", 10), line.get("quantity", 1), line.get("unit_price", 0), i)
            )

        conn.commit()
        result = row(conn.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,)).fetchone())
        return result
    finally:
        conn.close()


def get_avenants(tenant_id, parent_quote_id):
    """Retourne tous les avenants d'un devis parent."""
    conn = get_client_conn()
    cur  = conn.execute(
        """SELECT q.*, c.name as client_name, j.title as job_title
           FROM quotes q
           LEFT JOIN clients c ON c.id = q.client_id
           LEFT JOIN jobs j ON j.id = q.job_id
           WHERE q.tenant_id = ? AND q.parent_quote_id = ?
           ORDER BY q.avenant_number""",
        (tenant_id, parent_quote_id)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def create_avenant(tenant_id, parent_quote_id, data):
    """Crée un avenant au devis parent."""
    conn = get_client_conn()
    try:
        # Numéro d'avenant = max existant + 1
        cur = conn.execute(
            "SELECT COALESCE(MAX(avenant_number), 0) FROM quotes WHERE tenant_id=? AND parent_quote_id=?",
            (tenant_id, parent_quote_id)
        )
        next_num = cur.fetchone()[0] + 1

        parent = row(conn.execute("SELECT * FROM quotes WHERE id=? AND tenant_id=?",
                                  (parent_quote_id, tenant_id)).fetchone())
        if not parent:
            return None

        lines  = data.get("lines", [])
        amount = sum(float(l.get("quantity", 1)) * float(l.get("unit_price", 0)) for l in lines)

        cur = conn.execute(
            """INSERT INTO quotes
               (tenant_id, client_id, job_id, title, amount, status, notes,
                payment_terms, expiry_date, parent_quote_id, avenant_number)
               VALUES (?,?,?,?,?,'draft',?,?,?,?,?)""",
            (tenant_id, parent["client_id"], parent.get("job_id"),
             data.get("title", f"Avenant n°{next_num}"),
             amount, data.get("notes"),
             parent.get("payment_terms", "Comptant"), data.get("expiry_date"),
             parent_quote_id, next_num)
        )
        avenant_id = cur.lastrowid
        for i, line in enumerate(lines):
            conn.execute(
                """INSERT INTO quote_lines
                   (quote_id, tenant_id, designation, description, tva_rate, quantity, unit_price, sort_order)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (avenant_id, tenant_id, line.get("designation"), line.get("description"),
                 line.get("tva_rate", 10), line.get("quantity", 1), line.get("unit_price", 0), i)
            )
        conn.commit()
        return row(conn.execute("SELECT * FROM quotes WHERE id=?", (avenant_id,)).fetchone())
    finally:
        conn.close()


def update_status(tenant_id, quote_id, status):
    conn = get_client_conn()
    try:
        conn.execute(
            "UPDATE quotes SET status = ? WHERE id = ? AND tenant_id = ?",
            (status, quote_id, tenant_id)
        )
        conn.commit()
        result = row(conn.execute("SELECT * FROM quotes WHERE id = ? AND tenant_id = ?", (quote_id, tenant_id)).fetchone())
        return result
    finally:
        conn.close()


def delete(tenant_id, quote_id):
    conn = get_client_conn()
    try:
        cur = conn.execute("DELETE FROM quotes WHERE id = ? AND tenant_id = ?", (quote_id, tenant_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
