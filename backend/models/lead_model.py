from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, page=1, per_page=20):
    offset = (page - 1) * per_page
    conn = get_client_conn()
    cur = conn.execute(
        """SELECT l.*, c.name as client_name FROM leads l
           LEFT JOIN clients c ON c.id = l.client_id
           WHERE l.tenant_id = ? ORDER BY l.created_at DESC LIMIT ? OFFSET ?""",
        (tenant_id, per_page, offset)
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, lead_id):
    conn = get_client_conn()
    cur = conn.execute("SELECT * FROM leads WHERE id = ? AND tenant_id = ?", (lead_id, tenant_id))
    result = row(cur.fetchone())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO leads (tenant_id, client_id, name, phone, email, address,
               acquisition_source, source, status, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tenant_id, data.get("client_id"), data.get("name"), data.get("phone"),
             data.get("email"), data.get("address"), data.get("acquisition_source"),
             data.get("source"), data.get("status", "new"), data.get("notes"))
        )
        conn.commit()
        result = row(conn.execute("SELECT * FROM leads WHERE id = ?", (cur.lastrowid,)).fetchone())
        return result
    finally:
        conn.close()


def update(tenant_id, lead_id, data):
    conn = get_client_conn()
    try:
        conn.execute(
            """UPDATE leads SET name=?, phone=?, email=?, address=?,
               acquisition_source=?, source=?, notes=?
               WHERE id=? AND tenant_id=?""",
            (data.get("name"), data.get("phone"), data.get("email"), data.get("address"),
             data.get("acquisition_source"), data.get("source"), data.get("notes"),
             lead_id, tenant_id)
        )
        conn.commit()
        result = row(conn.execute("SELECT * FROM leads WHERE id = ? AND tenant_id = ?", (lead_id, tenant_id)).fetchone())
        return result
    finally:
        conn.close()


def update_status(tenant_id, lead_id, status):
    conn = get_client_conn()
    try:
        conn.execute(
            "UPDATE leads SET status = ? WHERE id = ? AND tenant_id = ?",
            (status, lead_id, tenant_id)
        )
        conn.commit()
        result = row(conn.execute("SELECT * FROM leads WHERE id = ? AND tenant_id = ?", (lead_id, tenant_id)).fetchone())
        return result
    finally:
        conn.close()


def delete(tenant_id, lead_id):
    conn = get_client_conn()
    try:
        cur = conn.execute("DELETE FROM leads WHERE id = ? AND tenant_id = ?", (lead_id, tenant_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
