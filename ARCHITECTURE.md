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
│   ├── app.py                  # Point d'entrée Flask (⚠️ RESTREINT)
│   ├── config.py               # Configuration globale (⚠️ RESTREINT)
│   ├── init_db.py              # Initialisation BDD (⚠️ RESTREINT)
│   └── requirements.txt         # Dépendances Python
│
├── 📁 backend/ (⚠️ RESTREINT)
│   ├── routes/                 # Endpoints API HTTP uniquement (pas de logique)
│   │   ├── auth.py             # POST /login, /register, /refresh
│   │   ├── clients.py          # CRUD clients
│   │   ├── quotes.py           # CRUD devis
│   │   ├── invoices.py         # CRUD factures
│   │   ├── jobs.py             # CRUD chantiers
│   │   ├── tasks.py            # CRUD tâches
│   │   ├── dashboard.py        # GET dashboard KPIs
│   │   └── __init__.py
│   │
│   ├── services/               # Logique métier (business rules)
│   │   ├── auth_service.py     # Authentification, JWT, hash pwd
│   │   ├── client_service.py   # Logique clients (validation, filters)
│   │   ├── quote_service.py    # Logique devis (calculs, statuts)
│   │   ├── invoice_service.py  # Logique factures (paiements, statuts)
│   │   ├── job_service.py      # Logique chantiers
│   │   ├── task_service.py     # Logique tâches
│   │   ├── token_service.py    # Système de tokens (pricing)
│   │   ├── email_service.py    # Envoi emails transactionnels
│   │   ├── pdf_service.py      # Génération PDF (factures, devis)
│   │   └── __init__.py
│   │
│   ├── models/                 # Accès à la base de données
│   │   ├── base.py             # Classe de base pour les modèles
│   │   ├── user.py             # Requêtes utilisateurs (SaaS DB)
│   │   ├── tenant.py           # Requêtes tenants (SaaS DB)
│   │   ├── subscription.py     # Requêtes abonnements (SaaS DB)
│   │   ├── client.py           # Requêtes clients (Client DB)
│   │   ├── lead.py             # Requêtes prospects (Client DB)
│   │   ├── quote.py            # Requêtes devis (Client DB)
│   │   ├── invoice.py          # Requêtes factures (Client DB)
│   │   ├── job.py              # Requêtes chantiers (Client DB)
│   │   ├── task.py             # Requêtes tâches (Client DB)
│   │   ├── appointment.py      # Requêtes RDV (Client DB)
│   │   ├── reminder.py         # Requêtes relances auto (Client DB)
│   │   └── __init__.py
│   │
│   └── utils/                  # Helpers & utilitaires
│       ├── decorators.py       # @login_required, @tenant_check, etc.
│       ├── validators.py       # Validation emails, téléphones, etc.
│       ├── pagination.py       # Pagination & filtres
│       ├── date_utils.py       # Gestion dates/heures
│       └── __init__.py
│
├── 📄 templates/ (✅ EDITABLE)
│   ├── base.html               # Template de base (layout, nav)
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── password_reset.html
│   ├── dashboard/
│   │   └── dashboard.html      # KPIs, vue d'ensemble
│   ├── clients/
│   │   ├── list.html           # Tableau clients
│   │   ├── detail.html         # Fiche client
│   │   ├── form.html           # Créer/éditer client
│   │   └── leads.html          # Pipeline prospects
│   ├── quotes/
│   │   ├── list.html           # Tableau devis
│   │   ├── form.html           # Créer/éditer devis
│   │   ├── detail.html         # Détail devis
│   │   └── signature.html      # Page signature publique
│   ├── invoices/
│   │   ├── list.html           # Tableau factures
│   │   ├── form.html           # Créer/éditer facture
│   │   └── detail.html         # Détail facture
│   ├── jobs/
│   │   ├── list.html           # Tableau chantiers
│   │   ├── form.html           # Créer/éditer chantier
│   │   └── detail.html         # Détail chantier
│   ├── settings/
│   │   ├── profile.html        # Profil utilisateur
│   │   ├── subscription.html   # Abonnement & facturation
│   │   ├── tokens.html         # Gestion tokens
│   │   └── team.html           # Gestion équipe (Enterprise)
│   └── errors/
│       ├── 403.html            # Accès refusé
│       ├── 404.html            # Page not found
│       └── 500.html            # Erreur serveur
│
├── 🎨 static/ (✅ EDITABLE)
│   ├── css/
│   │   ├── base.css            # Styles globaux
│   │   ├── layout.css          # Layout & grid
│   │   ├── components.css      # Boutons, formulaires, tableaux
│   │   ├── responsive.css      # Media queries (mobile-first)
│   │   ├── themes.css          # Thèmes couleurs
│   │   └── print.css           # Styles impression PDF
│   │
│   └── js/
│       ├── app.js              # App principale, routing
│       ├── auth.js             # Gestion JWT, localStorage auth
│       ├── clients.js          # Features clients (CRUD, filters)
│       ├── quotes.js           # Features devis (formulaire, calculs)
│       ├── invoices.js         # Features factures
│       ├── jobs.js             # Features chantiers
│       ├── dashboard.js        # Dashboard interactions
│       ├── api.js              # Client API helper (fetch wrapper)
│       ├── utils.js            # Helpers (dates, validation, etc.)
│       └── pdf.js              # Génération PDF côté client (optional)
│
├── 🧩 components/ (✅ EDITABLE)
│   ├── navbar.html             # Barre navigation réutilisable
│   ├── sidebar.html            # Sidebar réutilisable
│   ├── form_fields.html        # Composants input, textarea, select
│   ├── table.html              # Tableau générique avec pagination
│   ├── card.html               # Carte générique
│   ├── modal.html              # Modal générique
│   ├── alert.html              # Alerte générique
│   └── pagination.html         # Pagination réutilisable
│
├── 🗄️ database/ (⚠️ RESTREINT)
│   ├── schemas/
│   │   ├── saas.sql            # Schéma BDD SaaS (users, tenants, subscriptions)
│   │   └── client.sql          # Schéma BDD Client (clients, devis, factures, etc.)
│   │
│   └── migrations/ (future)
│       └── (migrations alembic ou custom)
│
├── 📊 BDD (racine)
│   ├── artisans_saas.db        # Base SaaS — tenants, users, subscriptions
│   └── artisans_client.db      # Base Client — données métier (multi-tenant)
│
├── 📚 Documentation
│   ├── README.md               # Vue d'ensemble projet & lancement
│   ├── ARCHITECTURE.md         # ✅ CE FICHIER — Architecture détaillée
│   ├── claude.md               # Règles Brendan (technique)
│   ├── claude_adrien.md        # Règles Adrien (design, marketing)
│   ├── BACKLOG.md              # Priorisation MoSCoW & sprints
│   └── RECAP_SESSION_Adrien.md # Log des sessions
│
└── 📁 Autres
    ├── veille_concurrentielle/ # Analyse concurrence
    └── style_preview.html      # Preview des composants CSS
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
# 1. Installer dépendances
pip install -r requirements.txt

# 2. Initialiser les BDD
python init_db.py

# 3. Lancer le serveur
python app.py
# → http://localhost:5000
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

*Dernière mise à jour : 18/04/2026*
*Document vivant — à mettre à jour à chaque évolution architecture*
