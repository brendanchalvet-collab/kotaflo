# ===== TASK MODEL =====
from backend.utils.db import get_client_conn, row, rows


def get_all(tenant_id, client_id=None, job_id=None, status=None):
    conn   = get_client_conn()
    wheres = ["t.tenant_id = ?"]
    params = [tenant_id]
    if client_id: wheres.append("t.client_id = ?");  params.append(client_id)
    if job_id:    wheres.append("t.job_id = ?");      params.append(job_id)
    if status:    wheres.append("t.status = ?");      params.append(status)
    where = " AND ".join(wheres)
    cur = conn.execute(
        f"""SELECT t.*,
               c.name  as client_name,
               j.title as job_title
            FROM tasks t
            LEFT JOIN clients c ON c.id = t.client_id
            LEFT JOIN jobs    j ON j.id = t.job_id
            WHERE {where}
            ORDER BY
                CASE t.priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
                t.due_date ASC NULLS LAST,
                t.created_at DESC""",
        params
    )
    result = rows(cur.fetchall())
    conn.close()
    return result


def get_by_id(tenant_id, task_id):
    conn = get_client_conn()
    cur  = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND tenant_id = ?",
        (task_id, tenant_id)
    )
    result = row(cur.fetchone())
    conn.close()
    return result


def create(tenant_id, data):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            """INSERT INTO tasks
               (tenant_id, client_id, job_id, title, description, due_date, priority, status)
               VALUES (?,?,?,?,?,?,?,?)""",
            (tenant_id, data.get("client_id"), data.get("job_id"),
             data["title"], data.get("description"),
             data.get("due_date"), data.get("priority", "normal"),
             data.get("status", "todo"))
        )
        conn.commit()
        return row(conn.execute(
            """SELECT t.*, c.name as client_name, j.title as job_title
               FROM tasks t
               LEFT JOIN clients c ON c.id = t.client_id
               LEFT JOIN jobs    j ON j.id = t.job_id
               WHERE t.id = ?""", (cur.lastrowid,)
        ).fetchone())
    finally:
        conn.close()


def update(tenant_id, task_id, data):
    conn = get_client_conn()
    try:
        conn.execute(
            """UPDATE tasks SET client_id=?, job_id=?, title=?, description=?,
               due_date=?, priority=?, status=?
               WHERE id=? AND tenant_id=?""",
            (data.get("client_id"), data.get("job_id"), data["title"],
             data.get("description"), data.get("due_date"),
             data.get("priority", "normal"), data.get("status", "todo"),
             task_id, tenant_id)
        )
        conn.commit()
        return row(conn.execute(
            """SELECT t.*, c.name as client_name, j.title as job_title
               FROM tasks t
               LEFT JOIN clients c ON c.id = t.client_id
               LEFT JOIN jobs    j ON j.id = t.job_id
               WHERE t.id = ?""", (task_id,)
        ).fetchone())
    finally:
        conn.close()


def delete(tenant_id, task_id):
    conn = get_client_conn()
    try:
        cur = conn.execute(
            "DELETE FROM tasks WHERE id = ? AND tenant_id = ?", (task_id, tenant_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
