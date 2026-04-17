# Kotaflo — Agent Instructions

> Adrien (co-founder): Design, marketing, pricing. Objective: Improve UI/UX without breaking Brendan's backend.

## Architecture Essentials

- **Flask + SQLite** — No PostgreSQL yet, no build tools (npm, webpack)
- **Multi-tenant CRITICAL**: Every API request must filter by tenant_id. Zero data leakage between tenants.
- **Two databases**:
  - artisans_saas.db — tenants, users, subscriptions
  - artisans_client.db — clients, leads, quotes, invoices, jobs, tasks

## Code Organization

```
backend/
├── routes/     → HTTP endpoints ONLY (no logic)
├── services/   → Business logic
├── models/     → DB queries
```

Rule: Routes call services, services call models. Never put logic in routes.

## Running the App

```bash
pip install -r requirements.txt
python init_db.py    # Creates both DBs
python app.py       # Starts on localhost:5000
```

## Permission Structure (CRITICAL)

### RESTRICTED — Ask first before touching
- backend/routes/ — API endpoints
- backend/models/ — Database models
- backend/services/ — Business logic
- app.py, config.py, init_db.py — Core config
- tenant_id logic or JWT authentication
- database/schemas/

### EDITABLE — No need to ask
- templates/ — HTML templates (Jinja2)
- static/css/ — Stylesheets
- static/js/ — JavaScript
- Markdown files (README, ROADMAP, docs)
- PDF design via fpdf2 (visuals only, NOT logic)

## What to AVOID

- React, Vue, Angular — vanilla JS only
- Bootstrap, Tailwind — custom CSS only
- PostgreSQL, MySQL — SQLite only
- New libraries without checking requirements.txt first
- Webpack, Vite, npm — no build system (Flask pure)

## Action Scope

- UI/UX: Improve HTML templates, CSS, responsive design, tables, forms, buttons
- Copywriting: Optimize text for artisans (simple, direct, professional)
- Business docs: Pricing, landing page, sales scripts
- PDF design: Logo placement, colors, layout (visual only via fpdf2)

## Communication Protocol

If you MUST touch a restricted area:
1. Explain why it's necessary
2. Propose the exact change
3. Wait for validation before executing

If you don't know: Ask rather than guess. Reference existing docs (README.md, ROADMAP.md).

## Documentation Rules

- After EVERY modification: Add dated entry to RECAP_SESSION.md (format: "## 📅 [DD/MM/YYYY à HH:MM]")
- Backlog = tasks to do (MoSCoW priority)
- README = global overview

## References

- antigravity.md — Adrien's full context (design/business permissions)
- claude.md — Original architecture spec
- backend/DOCS_TECH.md — Full technical docs