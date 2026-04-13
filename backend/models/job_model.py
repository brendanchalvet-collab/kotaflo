from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, client_id=None, page=1, per_page=50):
    offset = (page - 1) * per_page
    conn = get_client_conn()
    if client_id:
        cur = conn.execute(
            """SELECT j.*, c.name as client_name FROM jobs j
               LEFT JOIN clients c ON c.id = j.client_id
               WHERE j.tenant_id = ? AND j.client_id = ?
               ORDER BY j.start_date DESC LIMIT ? OFFSET ?""",
            (tenant_id, client_id, per_page, offset)
        )
    else:
        cur = conn.execute(
            """SELECT j.*, c.name as client_name FROM jobs j
               LEFT JOIN clients c ON c.id = j.client_id
               WHERE j.tenant_id = ?
               ORDER BY j.start_date DESC LIMIT ? OFFSET ?""",
            (tenant_id, per_page, offset)
        )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, job_id):
    conn = get_client_conn()
    cur = conn.execute(
        """SELECT j.*, c.name as client_name FROM jobs j
           LEFT JOIN clients c ON c.id = j.client_id
           WHERE j.id = ? AND j.tenant_id = ?""",
        (job_id, tenant_id)
    )
    result = row(cur.fetchone())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO jobs (tenant_id, client_id, title, status, start_date, end_date, address, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (tenant_id, data.get("client_id"), data["title"],
             data.get("status", "planned"), data.get("start_date"),
             data.get("end_date"), data.get("address"), data.get("notes"))
        )
        conn.commit()
        return row(conn.execute(
            """SELECT j.*, c.name as client_name FROM jobs j
               LEFT JOIN clients c ON c.id = j.client_id WHERE j.id = ?""",
            (cur.lastrowid,)
        ).fetchone())
    finally:
        conn.close()


def update(tenant_id, job_id, data):
    conn = get_client_conn()
    try:
        conn.execute(
            """UPDATE jobs SET title=?, status=?, start_date=?, end_date=?, address=?, notes=?
               WHERE id=? AND tenant_id=?""",
            (data["title"], data.get("status", "planned"),
             data.get("start_date"), data.get("end_date"),
             data.get("address"), data.get("notes"), job_id, tenant_id)
        )
        conn.commit()
        return row(conn.execute(
            """SELECT j.*, c.name as client_name FROM jobs j
               LEFT JOIN clients c ON c.id = j.client_id WHERE j.id = ? AND j.tenant_id = ?""",
            (job_id, tenant_id)
        ).fetchone())
    finally:
        conn.close()


def delete(tenant_id, job_id):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "DELETE FROM jobs WHERE id = ? AND tenant_id = ?", (job_id, tenant_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
