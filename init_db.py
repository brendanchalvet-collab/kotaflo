"""
Script d'initialisation des bases de données SQLite.
Lancer une seule fois : python init_db.py
"""
import sqlite3
from config import Config


# ===== BDD SAAS =====
def init_saas():
    conn = sqlite3.connect(Config.SAAS_DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tenants (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT NOT NULL,
            company_name    TEXT,
            address         TEXT,
            city            TEXT,
            zip_code        TEXT,
            country         TEXT DEFAULT 'FRANCE',
            phone           TEXT,
            email           TEXT,
            website         TEXT,
            siret           TEXT,
            tva_number      TEXT,
            iban            TEXT,
            bic             TEXT,
            rge_number      TEXT,
            insurance_info  TEXT,
            created_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS user_tenants (
            user_id   INTEGER REFERENCES users(id) ON DELETE CASCADE,
            tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
            role      TEXT DEFAULT 'user' CHECK(role IN ('admin','user')),
            PRIMARY KEY (user_id, tenant_id)
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
            plan       TEXT DEFAULT 'free' CHECK(plan IN ('free','pro','enterprise')),
            status     TEXT DEFAULT 'active' CHECK(status IN ('active','inactive','cancelled')),
            start_date TEXT DEFAULT (date('now')),
            end_date   TEXT
        );
    """)
    conn.commit()
    conn.close()
    print(f"[OK] BDD SaaS initialisee : {Config.SAAS_DB_PATH}")


# ===== BDD CLIENT =====
def init_client():
    conn = sqlite3.connect(Config.CLIENT_DB_PATH)
    conn.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS clients (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL,
            name       TEXT NOT NULL,
            phone      TEXT,
            email      TEXT,
            address    TEXT,
            city       TEXT,
            zip_code   TEXT,
            country    TEXT DEFAULT 'FRANCE',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS leads (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL,
            client_id  INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            source     TEXT,
            status     TEXT DEFAULT 'new' CHECK(status IN ('new','contacted','quoted','won','lost')),
            notes      TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS quotes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id    INTEGER NOT NULL,
            client_id    INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            title        TEXT,
            amount       REAL DEFAULT 0,
            status       TEXT DEFAULT 'draft' CHECK(status IN ('draft','sent','accepted','refused')),
            notes        TEXT,
            payment_terms TEXT DEFAULT 'Comptant',
            expiry_date  TEXT,
            created_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS quote_lines (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id     INTEGER NOT NULL REFERENCES quotes(id) ON DELETE CASCADE,
            tenant_id    INTEGER NOT NULL,
            designation  TEXT NOT NULL,
            description  TEXT,
            tva_rate     REAL DEFAULT 10,
            quantity     REAL DEFAULT 1,
            unit_price   REAL DEFAULT 0,
            sort_order   INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS invoices (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL,
            client_id  INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            quote_id   INTEGER REFERENCES quotes(id) ON DELETE SET NULL,
            amount     REAL DEFAULT 0,
            status     TEXT DEFAULT 'pending' CHECK(status IN ('pending','paid','late')),
            due_date   TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS jobs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL,
            client_id  INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            title      TEXT NOT NULL,
            status     TEXT DEFAULT 'planned' CHECK(status IN ('planned','ongoing','done')),
            start_date TEXT,
            end_date   TEXT,
            notes      TEXT
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            job_id    INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
            date      TEXT NOT NULL,
            status    TEXT DEFAULT 'planned' CHECK(status IN ('planned','done','cancelled')),
            notes     TEXT
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id    INTEGER NOT NULL,
            type         TEXT CHECK(type IN ('quote','invoice')),
            target_id    INTEGER NOT NULL,
            scheduled_at TEXT NOT NULL,
            sent         INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id  INTEGER NOT NULL,
            client_id  INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            type       TEXT NOT NULL DEFAULT 'note',
            title      TEXT,
            notes      TEXT,
            date       TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_clients_tenant      ON clients(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_leads_tenant        ON leads(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_quotes_tenant       ON quotes(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_quote_lines_quote   ON quote_lines(quote_id);
        CREATE INDEX IF NOT EXISTS idx_invoices_tenant     ON invoices(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_jobs_tenant         ON jobs(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_appointments_tenant ON appointments(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_reminders_tenant    ON reminders(tenant_id);
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id   INTEGER NOT NULL,
            client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
            job_id      INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
            title       TEXT NOT NULL,
            description TEXT,
            due_date    TEXT,
            priority    TEXT DEFAULT 'normal' CHECK(priority IN ('high','normal','low')),
            status      TEXT DEFAULT 'todo'   CHECK(status IN ('todo','in_progress','done')),
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_interactions_client ON interactions(client_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_tenant ON interactions(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_tenant        ON tasks(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_client        ON tasks(client_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_job           ON tasks(job_id);

        CREATE TABLE IF NOT EXISTS quote_tokens (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id          INTEGER NOT NULL,
            quote_id           INTEGER NOT NULL UNIQUE,
            access_token       TEXT UNIQUE NOT NULL,
            view_code          TEXT,
            view_code_expires  TEXT,
            view_attempts      INTEGER DEFAULT 0,
            view_verified      INTEGER DEFAULT 0,
            sign_code          TEXT,
            sign_code_expires  TEXT,
            sign_attempts      INTEGER DEFAULT 0,
            signed_at          TEXT,
            created_at         TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_quote_tokens_token    ON quote_tokens(access_token);
        CREATE INDEX IF NOT EXISTS idx_quote_tokens_quote_id ON quote_tokens(quote_id);

        -- Historique de chaque événement de signature (envoi code, vérif, échec, succès)
        CREATE TABLE IF NOT EXISTS signature_events (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id    INTEGER NOT NULL,
            quote_id     INTEGER NOT NULL,
            token_id     INTEGER REFERENCES quote_tokens(id) ON DELETE CASCADE,
            event_type   TEXT NOT NULL,   -- view_code_sent | view_verified | view_failed
                                          -- sign_code_sent | signed | sign_failed
            ip_address   TEXT,
            user_agent   TEXT,
            details      TEXT,            -- info complémentaire (ex: nb tentatives)
            created_at   TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_sig_events_quote  ON signature_events(quote_id);
        CREATE INDEX IF NOT EXISTS idx_sig_events_tenant ON signature_events(tenant_id);
    """)
    conn.commit()
    conn.close()
    print(f"[OK] BDD Client initialisee : {Config.CLIENT_DB_PATH}")


# ===== MIGRATIONS (colonnes ajoutées après la création initiale) =====
def migrate():
    """Ajoute les colonnes manquantes sans casser les données existantes."""
    saas = sqlite3.connect(Config.SAAS_DB_PATH)
    client = sqlite3.connect(Config.CLIENT_DB_PATH)

    saas_cols = [
        "company_name TEXT", "address TEXT", "city TEXT", "zip_code TEXT",
        "country TEXT", "phone TEXT", "email TEXT", "website TEXT",
        "siret TEXT", "tva_number TEXT", "iban TEXT", "bic TEXT",
        "rge_number TEXT", "insurance_info TEXT",
        "google_token TEXT",
    ]
    for col in saas_cols:
        try:
            saas.execute(f"ALTER TABLE tenants ADD COLUMN {col}")
        except Exception:
            pass
    saas.commit()
    saas.close()

    client_cols = [
        ("quotes",  "payment_terms TEXT DEFAULT 'Comptant'"),
        ("quotes",  "expiry_date TEXT"),
        ("clients", "city TEXT"),
        ("clients", "zip_code TEXT"),
        ("clients", "country TEXT"),
        ("clients", "notes TEXT"),
        ("clients", "acquisition_source TEXT"),
        ("clients",  "contact_type TEXT DEFAULT 'client'"),
        ("clients",  "pipeline_status TEXT DEFAULT 'new'"),
        ("quotes",   "job_id INTEGER"),
        ("quotes",   "parent_quote_id INTEGER"),
        ("quotes",   "avenant_number INTEGER"),
        ("invoices", "job_id INTEGER"),
        ("invoices", "invoice_type TEXT DEFAULT 'standard'"),
        ("invoices", "deposit_percent REAL"),
        ("invoices", "deposit_invoice_id INTEGER"),
        ("invoices", "notes TEXT"),
        ("jobs",          "address TEXT"),
        ("quote_tokens",  "signed_pdf_path TEXT"),
    ]
    for table, col in client_cols:
        try:
            client.execute(f"ALTER TABLE {table} ADD COLUMN {col}")
        except Exception:
            pass
    # Recréer interactions sans CHECK pour permettre tous les types futurs
    try:
        client.executescript("""
            CREATE TABLE IF NOT EXISTS interactions_new (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id  INTEGER NOT NULL,
                client_id  INTEGER NOT NULL,
                type       TEXT NOT NULL DEFAULT 'note',
                title      TEXT,
                notes      TEXT,
                date       TEXT DEFAULT (datetime('now')),
                created_at TEXT DEFAULT (datetime('now'))
            );
            INSERT OR IGNORE INTO interactions_new SELECT * FROM interactions;
            DROP TABLE interactions;
            ALTER TABLE interactions_new RENAME TO interactions;
        """)
    except Exception:
        pass

    client.commit()
    client.close()
    print("[OK] Migrations appliquees")


if __name__ == "__main__":
    init_saas()
    init_client()
    migrate()
    print("\nTout est pret ! Lance maintenant : python app.py")
