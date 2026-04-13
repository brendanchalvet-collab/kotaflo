from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, page=1, per_page=20, contact_type=None):
    offset = (page - 1) * per_page
    conn = get_client_conn()
    if contact_type:
        cur = conn.execute(
            """SELECT * FROM clients WHERE tenant_id = ? AND contact_type = ?
               ORDER BY created_at DESC LIMIT ? OFFSET ?""",
            (tenant_id, contact_type, per_page, offset)
        )
    else:
        cur = conn.execute(
            "SELECT * FROM clients WHERE tenant_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (tenant_id, per_page, offset)
        )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, client_id):
    conn = get_client_conn()
    cur = conn.execute(
        "SELECT * FROM clients WHERE id = ? AND tenant_id = ?",
        (client_id, tenant_id)
    )
    result = row(cur.fetchone())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO clients
               (tenant_id, name, phone, email, address, notes, acquisition_source,
                contact_type, pipeline_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tenant_id, data["name"], data.get("phone"), data.get("email"),
             data.get("address"), data.get("notes"), data.get("acquisition_source"),
             data.get("contact_type", "client"), data.get("pipeline_status", "new"))
        )
        conn.commit()
        return row(conn.execute("SELECT * FROM clients WHERE id = ?", (cur.lastrowid,)).fetchone())
    finally:
        conn.close()


def update(tenant_id, client_id, data):
    conn = get_client_conn()
    try:
        conn.execute(
            """UPDATE clients SET name=?, phone=?, email=?, address=?, notes=?,
               acquisition_source=?, contact_type=?, pipeline_status=?
               WHERE id=? AND tenant_id=?""",
            (data["name"], data.get("phone"), data.get("email"), data.get("address"),
             data.get("notes"), data.get("acquisition_source"),
             data.get("contact_type", "client"), data.get("pipeline_status", "new"),
             client_id, tenant_id)
        )
        conn.commit()
        return row(conn.execute(
            "SELECT * FROM clients WHERE id=? AND tenant_id=?", (client_id, tenant_id)
        ).fetchone())
    finally:
        conn.close()


def update_pipeline_status(tenant_id, client_id, pipeline_status):
    conn = get_client_conn()
    try:
        conn.execute(
            "UPDATE clients SET pipeline_status=? WHERE id=? AND tenant_id=?",
            (pipeline_status, client_id, tenant_id)
        )
        conn.commit()
        return row(conn.execute(
            "SELECT * FROM clients WHERE id=? AND tenant_id=?", (client_id, tenant_id)
        ).fetchone())
    finally:
        conn.close()


def delete(tenant_id, client_id):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "DELETE FROM clients WHERE id = ? AND tenant_id = ?", (client_id, tenant_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
