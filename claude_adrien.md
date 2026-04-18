# 🧠 claude_adrien — Règles de travail pour Adrien

> Fichier de règles dédié à Adrien (co-fondateur — Design, Marketing, Pricing).
> Synthèse issue de `AGENTS.md` et `antigravity.md`.
> **Ne pas confondre avec `claude.md`** qui est réservé à Brendan (technique).

---

## 🎯 1. Contexte & Rôle

- **Projet** : Kotaflo — SaaS de gestion multi-tenant pour artisans (plombiers, électriciens, etc.).
- **Mon rôle (Adrien)** : Design, UI/UX, marketing, pricing, stratégie, copywriting.
- **Rôle Brendan** : Backend, architecture technique, authentification, logique métier.
- **Objectif** : Améliorer l'interface et la stratégie **sans jamais casser le backend de Brendan**.

## 🏗️ 2. Stack & Architecture (à connaître, pas à modifier)

- **Backend** : Flask 3.0.3 (Python) + Flask-JWT-Extended + Flask-CORS
- **Frontend** : HTML5 + CSS3 + JavaScript **vanilla** + Jinja2
- **BDD** : SQLite — 2 bases séparées :
  - `artisans_saas.db` → tenants, users, subscriptions
  - `artisans_client.db` → clients, leads, quotes, invoices, jobs, tasks
- **PDF** : fpdf2
- **Multi-tenant** : chaque requête filtre par `tenant_id`. **Zéro fuite entre tenants.**

Organisation backend (à ne pas toucher sauf demande explicite) :

```
backend/
├── routes/     → endpoints HTTP uniquement (pas de logique)
├── services/   → logique métier
├── models/     → accès BDD
└── utils/      → helpers
```

## 🚫 3. Zones RESTREINTES (demander avant de toucher)

- `backend/routes/` — endpoints API
- `backend/models/` — modèles BDD
- `backend/services/` — logique métier
- `app.py`, `config.py`, `init_db.py` — configuration core
- Logique `tenant_id` ou authentification JWT
- `database/schemas/`

## ✅ 4. Zones LIBRES (permissions automatiques)

- `templates/` — templates HTML (Jinja2)
- `static/css/` — feuilles de style
- `static/js/` — scripts JavaScript
- Fichiers markdown (README, BACKLOG, docs, scripts marketing)
- Design PDF via `fpdf2` (visuel uniquement — **pas la logique**)
- Copywriting sur toutes les pages

## 🎨 5. Périmètre d'action

### UI/UX
- Moderniser templates HTML, tableaux, formulaires, boutons, badges
- CSS responsive, mobile-first
- Philosophie : **Ultra simple**, 1 action = 1 écran, max 3 clics pour créer un devis

### Copywriting
- Ton simple, direct, professionnel — qui parle aux artisans
- Titres, sous-titres, descriptions, tooltips, landing, FAQ, onboarding

### Business
- Pricing (plans Free/Pro/Enterprise, matrice features)
- Landing page, scripts de vente
- Analyse concurrentielle, positionnement
- Contenu marketing, réseaux sociaux

### PDF (design only)
- Logo, couleurs, mise en page, mentions légales
- **Ne pas modifier** les chemins, noms de fichiers, ou la logique de génération

## ❌ 6. À ÉVITER absolument

- React, Vue, Angular (on reste en **vanilla JS**)
- Bootstrap, Tailwind (on a **notre propre CSS**)
- PostgreSQL, MySQL (on est sur **SQLite**)
- Nouvelles bibliothèques sans vérifier `requirements.txt`
- Webpack, Vite, npm (**pas de build system** — Flask pur)
- Mélanger BDD SaaS et BDD Client
- Mettre de la logique métier dans les routes
- Fichiers trop longs (**max 300–400 lignes**, découper en modules sinon)

## 🛠️ 7. Méthode de travail

1. **Stratégie d'abord** — Expliquer le *pourquoi* avant le *quoi*.
2. **CSS pur** — Privilégier CSS plutôt qu'ajouter du JS complexe.
3. **Mobile-first** — Toujours tester le responsive (pas de largeurs fixes).
4. **Pas de breaking changes** — En cas de doute, demander.
5. **Alternatives** — Si risqué, proposer 2-3 options avec trade-offs.
6. **Git hygiène** — `git status` / `git diff` avant de valider. Commits clairs (`type: description`, ex: `ui: improve client table styling`).
7. **Jinja2** — Ne pas casser les `{% %}`.

## 🤝 8. Protocole de communication

Si je dois toucher à une zone restreinte :
1. **Expliquer** pourquoi c'est nécessaire
2. **Proposer** le changement exact
3. **Attendre** validation d'Adrien avant d'exécuter

Si je ne sais pas :
- Demander plutôt que deviner
- Référencer `README.md`, `BACKLOG.md`, `backend/DOCS_TECH.md`

Format des réponses :
- Concis, direct, pas de fluff
- Montrer avant/après pour un changement de code
- Expliquer les impacts (performance, compatibilité, UX)

## 📝 9. Documentation (OBLIGATOIRE)

- Après **CHAQUE** modification : ajouter une entrée datée dans `RECAP_SESSION_Adrien.md`
- **Format** : `## 📅 DD/MM/YYYY à HH:MM`
- `BACKLOG.md` = tâches à faire (priorité MoSCoW)
- `README.md` = vue d'ensemble

## 📁 10. Structure projet (rappel)

```
kotaflo/
├── app.py                      # ⚠️ NE PAS TOUCHER
├── config.py                   # ⚠️ NE PAS TOUCHER
├── init_db.py                  # ⚠️ NE PAS TOUCHER
├── requirements.txt
│
├── backend/
│   ├── routes/                 # ⚠️ RESTRICTED
│   ├── models/                 # ⚠️ RESTRICTED
│   ├── services/               # ⚠️ RESTRICTED
│   └── utils/
│
├── templates/                  # ✅ EDITABLE
├── static/{css,js}/            # ✅ EDITABLE
├── components/                 # ✅ EDITABLE
├── database/schemas/           # ⚠️ RESTRICTED
│
├── README.md                   # ✅ EDITABLE
├── BACKLOG.md                  # ✅ EDITABLE
├── AGENTS.md                   # Règles agents (lecture)
├── antigravity.md              # Contexte Adrien (lecture)
├── claude.md                   # Règles Brendan (ne pas modifier)
└── claude_adrien.md            # ✅ CE FICHIER — mes règles
```

## 🎯 11. Priorités actuelles (Phase 1)

1. Définition des plans (Free/Pro/Enterprise + matrice features) — *Adrien*
2. Période d'essai (workflow, durée) — *Adrien*
3. Modèle de tokens (pricing à l'usage) — *Adrien*
4. Charte graphique (couleurs, typographies) — *Adrien, après plans*
5. Logo & assets — *Adrien, après charte*
6. Stabilisation auth — *Brendan*

Voir `BACKLOG.md` pour le planning à jour.

---

*Fichier créé le 18/04/2026 — à faire vivre selon l'évolution du projet.*
*Source : synthèse de `AGENTS.md` + `antigravity.md`.*
