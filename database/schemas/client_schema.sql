-- ============================================================
-- BDD CLIENT — Métier artisan (multi-tenant)
-- Chaque table inclut tenant_id pour l'isolation des données
-- ============================================================

-- Table clients
CREATE TABLE IF NOT EXISTS clients (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    name        VARCHAR(255) NOT NULL,
    phone       VARCHAR(50),
    email       VARCHAR(255),
    address     TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Table leads (prospects)
CREATE TABLE IF NOT EXISTS leads (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    source      VARCHAR(100),
    status      VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'quoted', 'won', 'lost')),
    notes       TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Table devis
CREATE TABLE IF NOT EXISTS quotes (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    title       VARCHAR(255),
    amount      NUMERIC(12, 2) DEFAULT 0,
    status      VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'accepted', 'refused')),
    notes       TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Table factures
CREATE TABLE IF NOT EXISTS invoices (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    quote_id    INTEGER REFERENCES quotes(id) ON DELETE SET NULL,
    amount      NUMERIC(12, 2) DEFAULT 0,
    status      VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'late')),
    due_date    DATE,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Table chantiers
CREATE TABLE IF NOT EXISTS jobs (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    title       VARCHAR(255) NOT NULL,
    status      VARCHAR(50) DEFAULT 'planned' CHECK (status IN ('planned', 'ongoing', 'done')),
    start_date  DATE,
    end_date    DATE,
    notes       TEXT
);

-- Table rendez-vous
CREATE TABLE IF NOT EXISTS appointments (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER NOT NULL,
    client_id   INTEGER REFERENCES clients(id) ON DELETE SET NULL,
    job_id      INTEGER REFERENCES jobs(id) ON DELETE SET NULL,
    date        TIMESTAMP NOT NULL,
    status      VARCHAR(50) DEFAULT 'planned' CHECK (status IN ('planned', 'done', 'cancelled')),
    notes       TEXT
);

-- Table relances automatiques
CREATE TABLE IF NOT EXISTS reminders (
    id              SERIAL PRIMARY KEY,
    tenant_id       INTEGER NOT NULL,
    type            VARCHAR(50) CHECK (type IN ('quote', 'invoice')),
    target_id       INTEGER NOT NULL,
    scheduled_at    TIMESTAMP NOT NULL,
    sent            BOOLEAN DEFAULT FALSE
);

-- Index obligatoires (performance multi-tenant)
CREATE INDEX IF NOT EXISTS idx_clients_tenant       ON clients(tenant_id);
CREATE INDEX IF NOT EXISTS idx_leads_tenant         ON leads(tenant_id);
CREATE INDEX IF NOT EXISTS idx_quotes_tenant        ON quotes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_invoices_tenant      ON invoices(tenant_id);
CREATE INDEX IF NOT EXISTS idx_jobs_tenant          ON jobs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_appointments_tenant  ON appointments(tenant_id);
CREATE INDEX IF NOT EXISTS idx_reminders_tenant     ON reminders(tenant_id);
