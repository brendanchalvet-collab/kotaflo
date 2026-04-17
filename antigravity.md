# 🧠 Antigravity Context — Adrien (Design & Business)

Je suis le co-fondateur en charge du design, du marketing et du pricing.
Mon objectif est d'améliorer l'UI/UX et la stratégie sans casser le backend de Brendan.

## 🎯 CONTEXTE DU PROJET

**Nom** : Kotaflo — SaaS de gestion pour artisans
**Stack technique** : Flask (Python) + SQLite + Vanilla JS + Jinja2
**Phase actuelle** : Phase 1 — Fondations (voir `ROADMAP.md`)
**Architecture** : Multi-tenant (chaque entreprise a ses données isolées via `tenant_id`)
**Base de données** : 
- `artisans_saas.db` — Tenants, Users, Subscriptions
- `artisans_client.db` — Clients, Leads, Quotes, Invoices, Jobs, Tasks, etc.

## 🚫 RÈGLES DE SÉCURITÉ (NE PAS TRANSGRESSER)

1. **NE JAMAIS** modifier les fichiers dans `backend/routes/` ou `backend/models/` sans demande explicite d'Adrien.
2. **NE JAMAIS** modifier la logique du `tenant_id` ou de l'authentification JWT.
3. **NE JAMAIS** toucher aux fichiers Python dans `backend/services/` sans autorisation.
4. Toute modification de style doit se faire en priorité dans `static/css/`.
5. **NE JAMAIS** suggérer de bibliothèques externes sans d'abord vérifier qu'elles sont dans `requirements.txt`.
6. **NE JAMAIS** modifier `app.py`, `config.py` ou `init_db.py` sans demande explicite.

## ✅ PERMISSIONS AUTOMATIQUES (pas besoin de demander)

- Modifier les templates HTML dans `templates/`
- Modifier les fichiers CSS dans `static/css/`
- Modifier les fichiers JavaScript dans `static/js/`
- Créer/éditer des fichiers markdown (README, ROADMAP, docs, scripts marketing)
- Travailler sur le design des PDF via `fpdf2` (uniquement le visuel, pas la logique)
- Optimiser le copywriting sur toutes les pages

## 🎨 TON PÉRIMÈTRE D'ACTION

### UI/UX
- Améliorer les templates HTML (`templates/*.html`)
- Travailler le CSS dans `static/css/`
- Rendre l'interface responsive et mobile-first
- Moderniser les tableaux, formulaires, boutons, badges

### Copywriting
- Optimiser les textes pour qu'ils parlent aux artisans (ton simple, direct, professionnel)
- Rédiger les titres, sous-titres, descriptions, tooltips
- Créer le contenu pour la landing page, FAQ, onboarding

### Business
- Aide à la rédaction de documents (Pricing, Landing Page, Scripts de vente)
- Stratégie de pricing et plans d'abonnement
- Analyse concurrentielle et positionnement
- Plans réseaux sociaux et contenu marketing

### PDF (Design uniquement)
- Améliorer le design des modèles de factures/devis via `fpdf2`
- Travailler sur : logo placement, couleurs, mise en page, mentions légales
- **Ne pas modifier** la logique de génération (noms de fichiers, chemins, etc.)

## 🛠️ MÉTHODE DE TRAVAIL

1. **Stratégie d'abord** : Avant de proposer un changement de code, explique d'abord la stratégie et le pourquoi.
2. **CSS pure** : Privilégie le "CSS pur" plutôt que d'ajouter des bibliothèques JS complexes.
3. **Mobile-first** : Reste toujours dans une philosophie "Ultra simple / Mobile-first".
4. **Pas de breaking changes** : Si une modification risque de casser quelque chose, demande avant.
5. **Propose des alternatives** : Si une approche est risquée, propose 2-3 options avec les trade-offs.

## 💻 BONNES PRATIQUES TECHNIQUES

### Quand tu modifies du code :
- Utilise `git status` et `git diff` pour voir l'impact des changements
- Commit fréquemment avec des messages clairs (convention : `type: description`, ex: `ui: improve client table styling`)
- Vérifie que les templates Jinja2 restent valides (pas de `{% %}` cassés)
- Teste le responsive (classes CSS adaptatives, pas de largeurs fixes)

### Stack à connaître :
- **Backend** : Flask 3.0.3, Flask-JWT-Extended, Flask-CORS
- **Frontend** : HTML5, CSS3, JavaScript vanilla (pas de framework)
- **API** : REST avec JWT authentication
- **DB** : SQLite (2 bases séparées)
- **PDF** : fpdf2
- **Emails** : SMTP (Gmail ou configurable)

### Ce qu'il faut ÉVITER de suggérer :
- ❌ React, Vue, Angular (on est en vanilla JS)
- ❌ Bootstrap, Tailwind (on a notre propre CSS)
- ❌ PostgreSQL, MySQL (on est sur SQLite)
- ❌ Nouvelles bibliothèques sans d'abord vérifier `requirements.txt`
- ❌ Webpack, Vite, npm (pas de build system, c'est du Flask pur)

## 🤝 PROTOCOLE DE COMMUNICATION

### Si tu dois toucher à une zone restreinte :
1. **Explique** pourquoi c'est nécessaire
2. **Propose** le changement exact que tu veux faire
3. **Attends** la validation d'Adrien avant d'exécuter

### Si tu ne sais pas :
- Demande plutôt que de deviner
- Propose plusieurs options si il y a des trade-offs
- Reference la documentation existante (`README.md`, `ROADMAP.md`)

### Format des réponses :
- Sois concis et direct (pas de fluff)
- Montre le code avant/après si c'est un changement
- Explique les impacts potentiels (performance, compatibilité, UX)
- **Systématiquement** ajouter la date et l'heure lors d'un ajout dans `RECAP_SESSION.md` (ex: 17/04/2026 à 15:10)

## 📁 STRUCTURE RAPIDE DU PROJET

```
kotaflo/
├── app.py                      # ⚠️ NE PAS TOUCHER sans permission
├── config.py                   # ⚠️ NE PAS TOUCHER sans permission
├── init_db.py                  # ⚠️ NE PAS TOUCHER sans permission
├── requirements.txt            # Dépendances Python
│
├── backend/
│   ├── routes/                 # ⚠️ RESTRICTED — Endpoints API
│   ├── models/                 # ⚠️ RESTRICTED — Modèles de données
│   ├── services/               # ⚠️ RESTRICTED — Logique métier
│   └── utils/                  # Utilitaires
│
├── templates/                  # ✅ EDITABLE — Templates HTML (Jinja2)
├── static/
│   ├── css/                    # ✅ EDITABLE — Feuilles de style
│   └── js/                     # ✅ EDITABLE — Scripts JavaScript
│
├── components/                 # ✅ EDITABLE — Composants réutilisables
├── database/schemas/           # ⚠️ RESTRICTED — Schémas BDD
│
├── README.md                   # ✅ EDITABLE — Documentation
├── ROADMAP.md                  # ✅ EDITABLE — Planification
└── antigravity.md              # ✅ CE FICHIER — Règles Antigravity
```

## 🎯 PRIORITÉS ACTUELLES (Phase 1 — Semaines 1-2)

1. **Définition des plans** — Free/Pro/Enterprise + matrice des features (Adrien) ✅ EN COURS
2. **Période d'essai** — Workflow et durée (Adrien)
3. **Modèle de tokens** — Logique de pricing à l'usage (Adrien)
4. **Charte graphique** — Couleurs et typographies (Adrien) — *après plans*
5. **Logo & Assets** — Identité visuelle (Adrien) — *après charte*
6. **Stabilisation auth** (Brendan) — Laisser Brendan finir l'auth

Voir `ROADMAP.md` pour le planning complet et les mises à jour.

---

*Dernière mise à jour : 17 Avril 2026 à 15:10*
*Ce fichier est vivant — à mettre à jour selon l'évolution du projet*
