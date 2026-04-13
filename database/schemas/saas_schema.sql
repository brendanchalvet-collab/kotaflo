-- ============================================================
-- BDD SAAS — Plateforme (gestion utilisateurs, tenants, abonnements)
-- ============================================================

-- Table des tenants (artisans/entreprises)
CREATE TABLE IF NOT EXISTS tenants (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Table de liaison user <-> tenant (avec rôle)
CREATE TABLE IF NOT EXISTS user_tenants (
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tenant_id   INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    role        VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    PRIMARY KEY (user_id, tenant_id)
);

-- Table des abonnements
CREATE TABLE IF NOT EXISTS subscriptions (
    id          SERIAL PRIMARY KEY,
    tenant_id   INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    plan        VARCHAR(100) NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    status      VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'cancelled')),
    start_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date    DATE
);

-- Index
CREATE INDEX IF NOT EXISTS idx_user_tenants_tenant ON user_tenants(tenant_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON subscriptions(tenant_id);
