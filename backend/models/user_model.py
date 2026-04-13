from backend.utils.db import get_saas_conn, row


def get_by_email(email):
    conn = get_saas_conn()
    cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
    result = row(cur.fetchone())
    conn.close()
    return result


def create(email, password_hash):
    conn = get_saas_conn()
    try:
        # Créer le tenant associé
        cur = conn.execute("INSERT INTO tenants (name) VALUES (?)", (email.split("@")[0],))
        tenant_id = cur.lastrowid

        # Créer l'utilisateur
        cur = conn.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )
        user_id = cur.lastrowid

        # Lier user <-> tenant (admin)
        conn.execute(
            "INSERT INTO user_tenants (user_id, tenant_id, role) VALUES (?, ?, 'admin')",
            (user_id, tenant_id)
        )

        # Abonnement gratuit par défaut
        conn.execute(
            "INSERT INTO subscriptions (tenant_id, plan, status) VALUES (?, 'free', 'active')",
            (tenant_id,)
        )

        conn.commit()

        user = row(conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())
        return user, tenant_id
    finally:
        conn.close()


def get_tenant_id(user_id):
    conn = get_saas_conn()
    cur = conn.execute(
        "SELECT tenant_id FROM user_tenants WHERE user_id = ? LIMIT 1",
        (user_id,)
    )
    r = cur.fetchone()
    conn.close()
    return r["tenant_id"] if r else None
