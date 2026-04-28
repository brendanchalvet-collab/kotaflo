# 🏗️ ARCHITECTURE — Kotaflo

> Documentation complète de l'architecture, arborescence et patterns de code de Kotaflo.

---

## 📊 Vue d'Ensemble

**Kotaflo** est un SaaS multi-tenant pour artisans (plombiers, électriciens, etc.) bâti sur :

- **Backend** : Flask 3.0.3 (Python) + Flask-JWT-Extended + Flask-CORS
- **Frontend** : HTML5 + CSS3 + JavaScript vanilla + Jinja2
- **Base de données** : SQLite — **2 bases séparées** (architecture critique)
- **PDF** : fpdf2
- **Email** : SMTP (configurable)

**Objectif** : Outil de poche ultra-simple pour gérer clients, devis et factures sans friction.

---

## 🗂️ Arborescence Complète

```
kotaflo/
│
├── 🔧 Fichiers Core
│   ├── app.py                  # Point d'entrée Flask — routes HTML + blueprints API (⚠️ RESTREINT)
│   ├── config.py               # Configuration globale — clés, BDD, SMTP (⚠️ RESTREINT)
│   ├── init_db.py              # Initialisation + migrations BDD (⚠️ RESTREINT)
│   └── requirements.txt        # Dépendances Python
│
├── 📁 backend/ (⚠️ RESTREINT — Brendan)
│   ├── routes/                 # Blueprints API (endpoints HTTP uniquement, pas de logique)
│   │   ├── auth.py             # POST /api/auth/login, /register, /firebase-login
│   │   ├── clients.py          # CRUD /api/clients
│   │   ├── quotes.py           # CRUD /api/quotes
│   │   ├── invoices.py         # CRUD /api/invoices
│   │   ├── jobs.py             # CRUD /api/jobs (chantiers)
│   │   ├── tasks.py            # CRUD /api/tasks
│   │   ├── leads.py            # CRUD /api/leads
│   │   ├── profile.py          # GET/PATCH /api/profile
│   │   ├── google_auth.py      # OAuth Google /api/google
│   │   ├── quote_access.py     # Accès public devis /api/quote-access
│   │   └── __init__.py
│   │
│   ├── services/               # Logique métier
│   │   ├── auth_service.py     # Authentification bcrypt + Firebase
│   │   ├── client_service.py   # Logique clients
│   │   ├── quote_service.py    # Logique devis (calculs, statuts)
│   │   ├── invoice_service.py  # Logique factures
│   │   ├── job_service.py      # Logique chantiers
│   │   ├── lead_service.py     # Logique leads/prospects
│   │   ├── signature_service.py # Signature électronique
│   │   └── __init__.py
│   │
│   ├── models/                 # Accès base de données (SQLite raw)
│   │   ├── user_model.py       # users — SaaS DB
│   │   ├── tenant_model.py     # tenants — SaaS DB
│   │   ├── client_model.py     # clients — Client DB
│   │   ├── lead_model.py       # leads — Client DB
│   │   ├── quote_model.py      # quotes + quote_lines — Client DB
│   │   ├── quote_token_model.py # quote_tokens — Client DB
│   │   ├── invoice_model.py    # invoices — Client DB
│   │   ├── job_model.py        # jobs — Client DB
│   │   ├── task_model.py       # tasks — Client DB
│   │   ├── interaction_model.py # interactions — Client DB
│   │   ├── signature_model.py  # signature_events — Client DB
│   │   └── __init__.py
│   │
│   └── utils/                  # Helpers
│       ├── auth_utils.py       # JWT helpers, get_tenant_id
│       ├── db.py               # Connexions SQLite (get_saas_conn, get_client_conn)
│       ├── email_utils.py      # Envoi SMTP
│       ├── firebase_utils.py   # Firebase Admin SDK (init + verify token)
│       ├── gmail_api.py        # API Gmail OAuth
│       ├── pdf_generator.py    # Génération PDF devis/factures (fpdf2)
│       └── __init__.py
│
├── 📄 templates/ (✅ EDITABLE — Adrien)
│   │   ⚠️ Pas de base.html — chaque template est autonome (sidebar embarquée)
│   │
│   ├── landing.html            # / — Landing page publique (sans sidebar)
│   ├── login.html              # /login — Connexion + inscription
│   ├── dashboard.html          # /dashboard — KPIs, chantiers kanban
│   ├── clients.html            # /clients — Liste clients + modal CRUD
│   ├── contact_history.html    # /contacts/<id> — Fiche client + timeline
│   ├── quotes.html             # /quotes — Liste devis
│   ├── invoices.html           # /invoices — Liste factures
│   ├── projects.html           # /projects — Chantiers kanban
│   ├── project_detail.html     # /projects/<id> — Détail chantier + timeline
│   ├── tasks.html              # /tasks — Tâches kanban
│   ├── leads.html              # /leads — Pipeline prospects (→ redirect /clients)
│   ├── profile.html            # /profile — Profil utilisateur
│   ├── quote_sign.html         # /quote/<token> — Signature publique (sans auth)
│   ├── pricing.html            # /pricing — Plans + packs tokens
│   ├── trial.html              # /trial — Formulaire essai 14 jours
│   ├── checkout_packs.html     # /checkout-packs — Achat jetons (Stripe placeholder)
│   └── checkout_pro.html       # /checkout-pro — Abonnement Pro (Stripe placeholder)
│
├── 🎨 static/ (✅ EDITABLE — Adrien)
│   ├── css/
│   │   ├── base.css            # Variables CSS, reset, typographie, utilitaires
│   │   ├── layout.css          # App shell — sidebar, topbar, content, responsive
│   │   ├── components.css      # Boutons, cartes, tableaux, badges, modals, toasts
│   │   └── landing.css         # Styles spécifiques landing page publique
│   │
│   └── js/
│       ├── api.js              # fetch wrapper centralisé + gestion JWT 401
│       ├── dashboard.js        # KPIs, kanban projets, modal projet
│       ├── clients.js          # CRUD clients, modal, filtres
│       ├── contact_history.js  # Timeline client, projets liés
│       ├── quotes.js           # Liste devis, filtres
│       ├── invoices.js         # Liste factures, filtres
│       ├── projects.js         # Kanban chantiers, modal
│       ├── project_detail.js   # Détail chantier — timeline, devis, tâches
│       ├── project_detail_quotes.js # Gestion devis dans détail chantier
│       ├── tasks.js            # Kanban tâches, modal
│       ├── leads.js            # Pipeline prospects
│       └── profile.js          # Profil — lecture/update tenant
│
├── 🧩 components/
│   └── sidebar.html            # Sidebar de référence (non chargée auto — chaque template l'embarque)
│
├── 📊 BDD (racine — générées par init_db.py)
│   ├── artisans_saas.db        # users, tenants, user_tenants, subscriptions
│   └── artisans_client.db      # clients, leads, quotes, quote_lines, invoices,
│                               # jobs, tasks, interactions, quote_tokens,
│                               # signature_events, appointments, reminders
│
├── 🐍 Environnement Python
│   └── .venv/                  # Virtualenv (Arch Linux — `source .venv/bin/activate`)
│
├── 📚 Documentation
│   ├── README.md               # Vue d'ensemble + lancement rapide
│   ├── ARCHITECTURE.md         # ✅ CE FICHIER
│   ├── BACKLOG.md              # Priorisation MoSCoW + sprints
│   ├── RECAP_SESSION.md        # Log des sessions Adrien
│   ├── DEV_NOTES.md            # Notes techniques ponctuelles
│   ├── claude.md               # Règles assistant Brendan
│   └── claude_adrien.md        # Règles assistant Adrien
│
└── 📁 Autres
    └── veille_concurrentielle/ # Analyse 6 concurrents + stratégie tarifaire
```

---

## 🔀 Architecture Multi-Tenant (CRITIQUE)

### Principe

**2 bases de données séparées** pour garantir l'isolation des données :

#### 1️⃣ **artisans_saas.db** — Base Plateforme

Gère la **couche SaaS** (tout le monde, pas de tenant_id) :

```sql
users              -- Comptes globaux
├── id (PK)
├── email (UNIQUE)
├── password_hash
└── created_at

tenants            -- Entreprises artisans
├── id (PK)
├── name
└── created_at

user_tenants       -- Association (qui a accès à quelle entreprise ?)
├── user_id (FK)
├── tenant_id (FK)
├── role (admin, user)
└── created_at

subscriptions      -- Abonnements
├── id (PK)
├── tenant_id (FK)
├── plan (free, pro, enterprise)
├── status (active, cancelled)
├── start_date
├── end_date
└── created_at
```

#### 2️⃣ **artisans_client.db** — Base Métier

Gère les **données métier** (toujours filtrées par tenant_id) :

```sql
clients            -- Clients artisan
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── name
├── phone
├── email
├── address
└── created_at

leads              -- Prospects
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── client_id (FK)
├── source
├── status (new, contacted, quoted, won, lost)
├── notes
└── created_at

quotes             -- Devis
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── client_id (FK)
├── amount
├── status (draft, sent, accepted, refused)
└── created_at

invoices           -- Factures
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── client_id (FK)
├── amount
├── status (pending, paid, late)
├── due_date
└── created_at

jobs               -- Chantiers
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── client_id (FK)
├── title
├── status (planned, ongoing, done)
├── start_date
├── end_date
└── notes

appointments       -- RDV
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── client_id (FK)
├── job_id (FK)
├── date
└── status

reminders          -- Relances automatiques
├── id (PK)
├── tenant_id (FK) ← ⚠️ OBLIGATOIRE
├── type (quote, invoice)
├── target_id
├── scheduled_at
└── sent
```

### 🔐 Règle CRITIQUE : Isolation par tenant_id

**CHAQUE requête doit filtrer par tenant_id** :

```python
# ❌ INTERDIT
clients = Client.query.all()

# ✅ OBLIGATOIRE
current_user = get_jwt_identity()
tenant_id = get_user_tenant(current_user)
clients = Client.query.filter_by(tenant_id=tenant_id).all()
```

**Aucune donnée ne doit fuiter entre clients.**

---

## 🧠 Patterns de Code

### 1. Architecture 3-Couches (Routes → Services → Models)

```
Request
  ↓
[Route] — HTTP endpoint uniquement
  ↓
[Service] — Logique métier, validations
  ↓
[Model] — Requêtes BDD
  ↓
Response
```

**Exemple** : Créer un client

```python
# routes/clients.py
@app.post('/clients')
@login_required
def create_client():
    data = request.json
    current_user = get_jwt_identity()
    tenant_id = get_user_tenant(current_user)
    
    client = client_service.create(tenant_id, data)
    return jsonify(client), 201

# services/client_service.py
def create(tenant_id, data):
    validate_client_data(data)
    client = Client(tenant_id=tenant_id, **data)
    return client_model.save(client)

# models/client.py
def save(client):
    db_client.insert(table='clients', values=client.to_dict())
    return client
```

### 2. Décorateurs de Sécurité

```python
# @login_required — Vérifie JWT
# @tenant_check — Vérifie tenant_id dans les params
# @role_required('admin') — Vérifie rôle utilisateur

@app.delete('/clients/<id>')
@login_required
@tenant_check
def delete_client(id):
    # Garantit que l'utilisateur ne peut supprimer que ses clients
    pass
```

### 3. Validations Centralisées

```python
# utils/validators.py
def validate_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def validate_phone(phone):
    return re.match(r'^\+?[1-9]\d{1,14}$', phone)

# services/client_service.py
def create(tenant_id, data):
    if not validate_email(data['email']):
        raise ValueError("Invalid email")
    # ...
```

### 4. Pagination & Filtres

```python
# routes/clients.py
@app.get('/clients')
@login_required
def list_clients():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    status = request.args.get('status')  # Filter par statut
    
    tenant_id = get_user_tenant()
    clients = client_service.list(tenant_id, page, limit, status=status)
    
    return jsonify({
        'data': clients,
        'page': page,
        'total': count_total
    })
```

---

## 📋 Responsabilités par Dossier

| Dossier | Responsabilité | Qui touche ? | Règle |
|---------|----------------|------------|--------|
| `backend/routes/` | Endpoints HTTP uniquement | Brendan | ⚠️ Pas de logique |
| `backend/services/` | Logique métier, validations | Brendan | ⚠️ Pas d'accès BDD |
| `backend/models/` | Requêtes BDD, ORM | Brendan | ⚠️ Pas de logique |
| `backend/utils/` | Helpers, validations, décorateurs | Brendan | ✅ Ouvert |
| `templates/` | HTML Jinja2 | Adrien | ✅ Ouvert |
| `static/css/` | Stylesheets | Adrien | ✅ Ouvert |
| `static/js/` | JavaScript vanilla | Adrien | ✅ Ouvert |
| `components/` | Composants réutilisables | Adrien | ✅ Ouvert |
| `database/` | Schémas & migrations | Brendan | ⚠️ Critique |
| `app.py` | Point d'entrée | Brendan | ⚠️ Très restreint |

---

## 🔌 Points d'Intégration Clés

### 1. **Frontend ↔ Backend**

Le frontend communique via **API REST + JWT** :

```javascript
// static/js/api.js
const apiCall = async (method, endpoint, data = null) => {
    const token = localStorage.getItem('token');
    const response = await fetch(`/api${endpoint}`, {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: data ? JSON.stringify(data) : null
    });
    return response.json();
};

// Utilisation
const client = await apiCall('POST', '/clients', {
    name: 'Plomberie Martin',
    phone: '+33612345678'
});
```

### 2. **JWT Authentication**

```python
# routes/auth.py
@app.post('/auth/login')
def login():
    email = request.json['email']
    password = request.json['password']
    
    user = auth_service.authenticate(email, password)
    token = create_access_token(identity=user.id)
    
    return jsonify({'token': token})
```

### 3. **PDF Generation**

```python
# services/pdf_service.py
from fpdf import FPDF

def generate_quote_pdf(quote_id, tenant_id):
    quote = quote_model.get(quote_id, tenant_id)
    client = client_model.get(quote.client_id, tenant_id)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Devis #{quote.id}", ln=True)
    # ... design PDF
    
    pdf.output(f"devis_{quote.id}.pdf")
```

### 4. **Email Transactional**

```python
# services/email_service.py
def send_quote_reminder(quote_id, tenant_id):
    quote = quote_model.get(quote_id, tenant_id)
    client = client_model.get(quote.client_id, tenant_id)
    
    subject = f"Relance : Devis #{quote.id}"
    body = f"Bonjour {client.name},\n\nVoici votre devis..."
    
    send_smtp(client.email, subject, body)
```

---

## 📏 Règles de Taille & Code

| Règle | Valeur |
|-------|--------|
| **Max lignes par fichier** | 300–400 lignes |
| **Max lignes par fonction** | 50 lignes |
| **Max lignes per template** | 200 lignes |
| **Découpage obligatoire** | Si dépasse max |

---

## 🚀 Lancement de l'App

```bash
# 1. Créer et activer le virtualenv (Arch Linux)
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Initialiser les BDD (première fois seulement)
python init_db.py

# 4. Lancer le serveur
python app.py
# → http://localhost:5000
# → Landing : /
# → Login   : /login  (créer un compte via le formulaire Register)
```

---

## 🔄 Flux Utilisateur Typique

```
1. [Auth] Utilisateur se crée un compte → INSERT users + tenants + user_tenants
2. [Login] JWT token généré et stocké en localStorage
3. [Dashboard] GET /api/dashboard → KPIs affichés
4. [Create Client] POST /api/clients → client_service.create() → models.save()
5. [Create Quote] POST /api/quotes → calculs auto → PDF généré
6. [Send Quote] POST /api/quotes/<id>/send → email transactionnel + status update
7. [Invoice] POST /api/invoices → conversion auto du devis → facture générée
8. [Pay Invoice] PATCH /api/invoices/<id> → status = paid → relances désactivées
```

---

## 🎯 Évolutions Futures

- **Mode hors-ligne** : Sync local ↔ serveur (IndexedDB + Service Worker)
- **Système de tokens** : Paiement à l'usage (1 devis = 1 token)
- **Signature électronique** : Lien public + codes de vérification
- **PWA mobile** : Notifications push, offline access amélioré
- **Analytics avancés** : Graphiques revenus, taux conversion

---

*Dernière mise à jour : 28/04/2026*
*Document vivant — à mettre à jour à chaque évolution architecture*
