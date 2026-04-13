from backend.utils.db import get_saas_conn, row


def get_by_id(tenant_id):
    conn = get_saas_conn()
    cur = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    result = row(cur.fetchone())
    conn.close()
    return result


def get_google_token(tenant_id):
    conn = get_saas_conn()
    cur  = conn.execute("SELECT google_token FROM tenants WHERE id = ?", (tenant_id,))
    r    = cur.fetchone()
    conn.close()
    return r[0] if r else None


def save_google_token(tenant_id, token_json):
    conn = get_saas_conn()
    try:
        conn.execute("UPDATE tenants SET google_token = ? WHERE id = ?", (token_json, tenant_id))
        conn.commit()
    finally:
        conn.close()


def update_profile(tenant_id, data):
    fields = ["company_name", "address", "city", "zip_code", "country",
              "phone", "email", "website", "siret", "tva_number",
              "iban", "bic", "rge_number", "insurance_info"]
    sets   = ", ".join(f"{f} = ?" for f in fields)
    values = [data.get(f) for f in fields] + [tenant_id]

    conn = get_saas_conn()
    try:
        conn.execute(f"UPDATE tenants SET {sets} WHERE id = ?", values)
        conn.commit()
        result = row(conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone())
        return result
    finally:
        conn.close()
