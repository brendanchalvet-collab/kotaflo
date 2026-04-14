# Kotaflo - SaaS de Gestion pour Artisans

**Kotaflo** est une application SaaS complète de gestion d'activité pour artisans, développée avec Flask (Python). Elle permet de gérer les clients, les prospects (leads), les devis, les factures, les chantiers (jobs), les tâches et les interactions clients, le tout dans un environnement multi-entreprise (multi-tenant).

---

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Technologies Utilisées](#-technologies-utilisées)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du Projet](#-structure-du-projet)
- [Base de Données](#-base-de-données)
- [API Endpoints](#-api-endpoints)
- [Authentification](#-authentification)
- [Développement](#-développement)
- [Variables d'Environnement](#-variables-denvironnement)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### Gestion Commerciale
- **Clients** : CRUD complet avec historique des interactions
- **Prospects (Leads)** : Suivi du pipeline de prospection (nouveau → contacté → devis → gagné/perdu)
- **Devis** : Création, envoi, suivi et signature électronique de devis
- **Factures** : Génération et suivi des factures (standard, acompte, acompte restant)
- **Chantiers (Jobs)** : Planification et suivi des interventions

### Gestion des Tâches
- Création et assignation de tâches avec priorités (haute, normale, basse)
- Suivi de statut (à faire, en cours, terminé)
- Association aux clients et chantiers

### Signature Électronique
- Signature sécurisée des devis avec code de vérification
- Tokens d'accès uniques pour les liens de signature publics
- Historique complet des événements de signature
- Génération de PDF signés

### Intégrations
- **Google OAuth** : Authentification via Google
- **Gmail API** : Envoi d'emails pour les devis et notifications
- **SMTP** : Envoi d'emails configurables (devis, OTP)

### Multi-Tenant
- Architecture SaaS multi-entreprise
- Isolation des données par tenant
- Système d'abonnement (free, pro, enterprise)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/JS/CSS)          │
│  Templates Jinja2 + JavaScript Vanilla  │
└────────────────┬────────────────────────┘
                 │ HTTP Requests
┌────────────────▼────────────────────────┐
│          Backend Flask (API)            │
│  ┌──────────┬──────────┬──────────┐    │
│  │  Routes  │ Services │  Models  │    │
│  └──────────┴──────────┴──────────┘    │
└────────────────┬────────────────────────┘
                 │ SQLite
┌────────────────▼────────────────────────┐
│         Bases de Données SQLite         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │ artisans_    │  │ artisans_    │    │
│  │ saas.db      │  │ client.db    │    │
│  │ (Tenants,    │  │ (Clients,    │    │
│  │  Users)      │  │  Devis, etc.)│    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

### Séparation des Bases de Données

**Base SaaS (`artisans_saas.db`)** :
- `tenants` : Entreprises/artisan·es
- `users` : Utilisateurs authentifiés
- `user_tenants` : Associations utilisateur/entreprise
- `subscriptions` : Abonnements

**Base Client (`artisans_client.db`)** :
- `clients` : Clients et prospects
- `leads` : Suivi des prospects
- `quotes` & `quote_lines` : Devis et lignes de devis
- `invoices` : Factures
- `jobs` : Chantiers/interventions
- `tasks` : Tâches
- `interactions` : Historique des interactions clients
- `appointments` : Rendez-vous
- `reminders` : Rappels automatiques
- `quote_tokens` : Tokens de signature électronique
- `signature_events` : Journal d'audit de signature

---

## 🛠️ Technologies Utilisées

### Backend
- **Flask 3.0.3** : Framework web Python
- **Flask-JWT-Extended 4.6.0** : Authentification JWT
- **Flask-CORS 4.0.1** : Support CORS
- **bcrypt 4.1.3** : Chiffrement des mots de passe
- **fpdf2 2.7.9** : Génération de PDF (devis, factures)

### Intégrations Google
- **google-auth-oauthlib 1.2.0** : Authentification OAuth2 Google
- **google-api-python-client 2.131.0** : API Gmail

### Configuration
- **python-dotenv 1.0.1** : Gestion des variables d'environnement

### Frontend
- **HTML5/CSS3** : Templates Jinja2
- **JavaScript Vanilla** : Pas de framework, interactions directes avec l'API
- **LocalStorage** : Stockage du token JWT

---

## 📦 Prérequis

- **Python** 3.8 ou supérieur
- **pip** (gestionnaire de paquets Python)
- **SQLite3** (généralement inclus avec Python)
- Un navigateur web moderne

---

## 🚀 Installation

### 1. Cloner le Repository

```bash
git clone <repository-url>
cd kotaflo
```

### 2. Créer un Environnement Virtuel (Recommandé)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 4. Initialiser la Base de Données

```bash
python init_db.py
```

Ce script va :
- Créer `artisans_saas.db` (gestion des entreprises et utilisateurs)
- Créer `artisans_client.db` (données métier : clients, devis, factures, etc.)
- Appliquer les migrations automatiques

### 5. Configurer les Variables d'Environnement

Créez un fichier `.env` à la racine du projet (voir [Configuration](#configuration)).

### 6. Lancer l'Application

```bash
python app.py
```

L'application sera disponible sur : **http://localhost:5000**

---

## ⚙️ Configuration

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# ===== Flask =====
SECRET_KEY=votre-secret-key-tres-securisee
DEBUG=true

# ===== JWT =====
JWT_SECRET_KEY=votre-jwt-secret-key-tres-securisee
# JWT_ACCESS_TOKEN_EXPIRES=28800  # 8 heures (défaut)

# ===== Bases de Données SQLite =====
SAAS_DB_PATH=artisans_saas.db
CLIENT_DB_PATH=artisans_client.db

# ===== Google OAuth2 (Optionnel) =====
GOOGLE_CLIENT_ID=votre-google-client-id
GOOGLE_CLIENT_SECRET=votre-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/google/callback

# ===== SMTP (Envoi d'emails) =====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-application
SMTP_FROM=votre-email@gmail.com
```

### Notes de Configuration

- **SECRET_KEY** et **JWT_SECRET_KEY** : Générez des clés aléatoires sécurisées pour la production
- **DEBUG** : Mettre `false` en production
- **Google OAuth** : Nécessite la configuration d'un projet dans Google Cloud Console
- **SMTP_PASSWORD** : Pour Gmail, utilisez un "mot de passe d'application" (pas votre mot de passe habituel)

---

## 📖 Utilisation

### Pages Disponibles

| Route | Description | Authentification |
|-------|-------------|------------------|
| `/` | Page de connexion | ❌ Publique |
| `/login` | Page de connexion | ❌ Publique |
| `/dashboard` | Tableau de bord | ✅ Requise |
| `/clients` | Liste des clients | ✅ Requise |
| `/contacts/<id>` | Historique des interactions | ✅ Requise |
| `/leads` | Prospects (redirige vers `/clients`) | ✅ Requise |
| `/quotes` | Gestion des devis | ✅ Requise |
| `/invoices` | Gestion des factures | ✅ Requise |
| `/tasks` | Gestion des tâches | ✅ Requise |
| `/projects` | Liste des chantiers | ✅ Requise |
| `/projects/<id>` | Détail d'un chantier | ✅ Requise |
| `/profile` | Profil entreprise | ✅ Requise |
| `/quote/<token>` | Page publique de signature | ❌ Publique (token) |

### Flux de Travail Typique

1. **Inscription/Connexion** : Créez un compte ou connectez-vous
2. **Configuration du Profil** : Complétez les informations de votre entreprise
3. **Gestion des Clients** : Ajoutez vos clients et prospects
4. **Création de Devis** : Générez des devis avec lignes de détail
5. **Envoi pour Signature** : Envoyez le lien de signature au client
6. **Signature** : Le client signe électroniquement avec un code de vérification
7. **Facturation** : Convertissez les devis acceptés en factures
8. **Suivi** : Gérez les chantiers et tâches associées

---

## 📁 Structure du Projet

```
kotaflo/
├── app.py                      # Point d'entrée Flask, routes frontend
├── config.py                   # Configuration de l'application
├── init_db.py                  # Script d'initialisation des BDD
├── requirements.txt            # Dépendances Python
├── artisans_saas.db           # Base SaaS (auto-généré)
├── artisans_client.db         # Base Client (auto-généré)
│
├── backend/
│   ├── __init__.py
│   ├── models/                 # Modèles de données
│   │   ├── client_model.py
│   │   ├── interaction_model.py
│   │   ├── invoice_model.py
│   │   ├── job_model.py
│   │   ├── lead_model.py
│   │   ├── quote_model.py
│   │   ├── quote_token_model.py
│   │   ├── signature_model.py
│   │   ├── task_model.py
│   │   ├── tenant_model.py
│   │   └── user_model.py
│   │
│   ├── routes/                 # Endpoints API REST
│   │   ├── auth.py             # Authentification (login, register)
│   │   ├── clients.py          # CRUD clients
│   │   ├── google_auth.py      # OAuth Google
│   │   ├── invoices.py         # Gestion factures
│   │   ├── jobs.py             # Gestion chantiers
│   │   ├── leads.py            # Gestion prospects
│   │   ├── profile.py          # Profil entreprise
│   │   ├── quote_access.py     # Accès public aux devis
│   │   ├── quotes.py           # Gestion devis
│   │   └── tasks.py            # Gestion tâches
│   │
│   ├── services/               # Logique métier
│   │   ├── auth_service.py
│   │   ├── client_service.py
│   │   ├── invoice_service.py
│   │   ├── job_service.py
│   │   ├── lead_service.py
│   │   ├── quote_service.py
│   │   └── signature_service.py
│   │
│   └── utils/                  # Utilitaires
│
├── templates/                  # Templates HTML (Jinja2)
│   ├── login.html
│   ├── dashboard.html
│   ├── clients.html
│   ├── contact_history.html
│   ├── quotes.html
│   ├── invoices.html
│   ├── tasks.html
│   ├── projects.html
│   ├── project_detail.html
│   ├── profile.html
│   └── quote_sign.html         # Page publique de signature
│
├── static/                     # Ressources statiques
│   ├── css/                    # Feuilles de style
│   └── js/                     # Scripts JavaScript
│       ├── api.js              # Helper fetch API + JWT
│       ├── dashboard.js
│       ├── clients.js
│       ├── contact_history.js
│       ├── invoices.js
│       ├── leads.js
│       ├── profile.js
│       ├── projects.js
│       ├── project_detail.js
│       ├── project_detail_quotes.js
│       ├── quotes.js
│       └── tasks.js
│
├── components/
│   └── sidebar.html            # Composant sidebar réutilisable
│
└── database/
    └── schemas/
        ├── saas_schema.sql     # Schéma BDD SaaS
        └── client_schema.sql   # Schéma BDD Client
```

---

## 🗄️ Base de Données

### Architecture Multi-tenant

Kotaflo utilise une architecture **multi-tenant** où chaque entreprise (artisan·e) a ses propres données isolées :

- Le **tenant_id** est présent dans toutes les tables métier
- Les requêtes filtrent automatiquement par `tenant_id`
- Un utilisateur peut appartenir à plusieurs entreprises (table `user_tenants`)

### Tables Principales

#### Base SaaS (`artisans_saas.db`)

**tenants** :
- Informations de l'entreprise (nom, SIRET, adresse, IBAN, etc.)
- Informations d'assurance et certifications (RGE)

**users** :
- Email et mot de passe hashé (bcrypt)
- Authentification JWT

**user_tenants** :
- Association utilisateur ↔ entreprise
- Rôle : `admin` ou `user`

**subscriptions** :
- Plan : `free`, `pro`, `enterprise`
- Statut : `active`, `inactive`, `cancelled`

#### Base Client (`artisans_client.db`)

**clients** :
- Coordonnées complètes (nom, téléphone, email, adresse)
- Type de contact : `client` ou `prospect`
- Source d'acquisition
- Statut dans le pipeline

**leads** :
- Statut : `new`, `contacted`, `quoted`, `won`, `lost`
- Source du prospect
- Notes

**quotes** & **quote_lines** :
- Devis avec lignes de détail (désignation, quantité, prix unitaire, TVA)
- Statut : `draft`, `sent`, `accepted`, `refused`
- Conditions de paiement, date d'expiration
- Support des avenants (parent_quote_id, avenant_number)

**invoices** :
- Types : `standard`, `deposit` (acompte), `deposit_balance` (acompte restant)
- Statut : `pending`, `paid`, `late`
- Lien avec devis et chantiers
- Gestion des acomptes (pourcentage, facture associée)

**jobs** :
- Chantiers/interventions
- Statut : `planned`, `ongoing`, `done`
- Dates de début/fin, adresse, notes

**tasks** :
- Statut : `todo`, `in_progress`, `done`
- Priorité : `high`, `normal`, `low`
- Association facultative à client et/ou chantier

**interactions** :
- Historique complet des interactions avec chaque client
- Types variés (note, appel, email, rendez-vous, etc.)

**quote_tokens** & **signature_events** :
- Tokens d'accès pour signature électronique
- Codes de vérification (visualisation et signature)
- Journal d'audit complet (tentatives, IP, user-agent)

### Migrations

Le système de migrations (`init_db.py` → `migrate()`) permet d'ajouter des colonnes sans perdre de données :

```python
# Ajoute automatiquement les nouvelles colonnes
# Ignore les colonnes déjà existantes
# Recrée les tables si nécessaire (ex: interactions)
```

---

## 🔌 API Endpoints

Tous les endpoints API sont préfixés par `/api`.

### Authentification (`/api/auth`)
- `POST /register` - Créer un compte
- `POST /login` - Se connecter (retourne token JWT)
- `GET /me` - Infos utilisateur courant

### Clients (`/api/clients`)
- `GET /` - Liste des clients
- `POST /` - Créer un client
- `GET /<id>` - Détails d'un client
- `PUT /<id>` - Modifier un client
- `DELETE /<id>` - Supprimer un client

### Leads (`/api/leads`)
- `GET /` - Liste des prospects
- `POST /` - Créer un prospect
- `PUT /<id>` - Modifier un prospect
- `DELETE /<id>` - Supprimer un prospect

### Devis (`/api/quotes`)
- `GET /` - Liste des devis
- `POST /` - Créer un devis
- `GET /<id>` - Détails d'un devis
- `PUT /<id>` - Modifier un devis
- `DELETE /<id>` - Supprimer un devis
- `POST /<id>/send` - Envoyer le devis par email

### Factures (`/api/invoices`)
- `GET /` - Liste des factures
- `POST /` - Créer une facture
- `GET /<id>` - Détails d'une facture
- `PUT /<id>` - Modifier une facture
- `DELETE /<id>` - Supprimer une facture
- `POST /<id>/mark-paid` - Marquer comme payée

### Chantiers (`/api/jobs`)
- `GET /` - Liste des chantiers
- `POST /` - Créer un chantier
- `GET /<id>` - Détails d'un chantier
- `PUT /<id>` - Modifier un chantier
- `DELETE /<id>` - Supprimer un chantier

### Tâches (`/api/tasks`)
- `GET /` - Liste des tâches
- `POST /` - Créer une tâche
- `GET /<id>` - Détails d'une tâche
- `PUT /<id>` - Modifier une tâche
- `DELETE /<id>` - Supprimer une tâche

### Profil (`/api/profile`)
- `GET /` - Informations entreprise
- `PUT /` - Modifier les informations

### Google OAuth (`/api/google`)
- `GET /login` - Initier l'authentification Google
- `GET /callback` - Callback OAuth

### Accès Devis Public (`/api/quote-access`)
- `GET /quote/<token>` - Récupérer les infos d'un devis (public)
- `POST /quote/<token>/view` - Vérifier le code de visualisation
- `POST /quote/<token>/sign` - Signer le devis

---

## 🔐 Authentification

### JWT (JSON Web Token)

L'application utilise **Flask-JWT-Extended** pour l'authentification :

1. **Login** : L'utilisateur envoie email + mot de passe → reçoit un token JWT
2. **Stockage** : Le token est stocké dans `localStorage` côté client
3. **Requêtes** : Le token est envoyé dans le header `Authorization: Bearer <token>`
4. **Expiration** : Le token expire après 8 heures (configurable)
5. **Refresh** : En cas d'expiration, redirection vers `/login`

### Google OAuth2

Authentification alternative via Google :
- Configuration requise dans Google Cloud Console
- Scopes nécessaires : Gmail API, userinfo
- Callback URL : `http://localhost:5000/api/google/callback`

### Signature Électronique

Processus sécurisé en deux étapes :
1. **Visualisation** : Code de vérification à 6 chiffres
2. **Signature** : Second code de vérification pour signer
3. **Audit** : Tous les événements sont journalisés (IP, user-agent, tentatives)

---

## 👨‍💻 Développement

### Ajouter une Nouvelle Fonctionnalité

1. **Modèle** : Créer le modèle dans `backend/models/`
2. **Service** : Implémenter la logique métier dans `backend/services/`
3. **Route** : Ajouter l'endpoint API dans `backend/routes/`
4. **Frontend** : Créer la page HTML dans `templates/` et le JS dans `static/js/`
5. **Registre** : Enregistrer le blueprint dans `app.py`

### Conventions de Code

- **Python** : Suivre PEP 8
- **JavaScript** : Utiliser `async/await` pour les requêtes API
- **Nommage** : snake_case pour Python, camelCase pour JavaScript
- **API** : Retourner du JSON avec des codes HTTP appropriés

### Helper API JavaScript

Le fichier `static/js/api.js` fournit :

```javascript
// Effectuer une requête avec token JWT automatique
const response = await apiFetch('/api/clients', {
    method: 'POST',
    body: JSON.stringify({ name: 'Nouveau Client' })
});

// Déconnexion
logout();
```

### Debugging

- Activer `DEBUG=true` dans `.env`
- Les erreurs Flask sont affichées dans le navigateur
- Console navigateur pour les erreurs JavaScript
- Logs Python dans le terminal

---

## 🔧 Variables d'Environnement

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clé secrète Flask | `change-me-in-production` |
| `DEBUG` | Mode debug | `true` |
| `JWT_SECRET_KEY` | Clé secrète JWT | `jwt-change-me-in-production` |
| `JWT_ACCESS_TOKEN_EXPIRES` | Expiration token (secondes) | `28800` (8h) |
| `SAAS_DB_PATH` | Chemin BDD SaaS | `artisans_saas.db` |
| `CLIENT_DB_PATH` | Chemin BDD Client | `artisans_client.db` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `""` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | `""` |
| `GOOGLE_REDIRECT_URI` | URL callback Google | `http://localhost:5000/api/google/callback` |
| `SMTP_HOST` | Serveur SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Port SMTP | `587` |
| `SMTP_USER` | Utilisateur SMTP | `""` |
| `SMTP_PASSWORD` | Mot de passe SMTP | `""` |
| `SMTP_FROM` | Adresse d'envoi | `""` |

---

## 🚀 Déploiement (Production)

### Recommandations

1. **Serveur WSGI** : Utiliser **Gunicorn** ou **uWSGI** au lieu du serveur de dev Flask
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Reverse Proxy** : Configurer **Nginx** devant Flask

3. **HTTPS** : Obligatoire pour JWT et OAuth (utiliser Let's Encrypt)

4. **Variables d'Environnement** :
   - `DEBUG=false`
   - Générer des `SECRET_KEY` et `JWT_SECRET_KEY` aléatoires
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

5. **Base de Données** : Pour une utilisation intensive, migrer vers **PostgreSQL**

6. **Sécurité** :
   - Rate limiting sur les endpoints d'authentification
   - Headers de sécurité (CSP, X-Frame-Options, etc.)
   - Backups réguliers des BDD SQLite

---

## 📝 Licence

Ce projet est la propriété de ses auteurs. Tous droits réservés.

---

## 🤝 Support

Pour toute question ou problème :
- Ouvrez une issue sur le repository
- Consultez la documentation des endpoints via l'auto-complétion du code

---

## 🎯 Roadmap

- [ ] Migration vers PostgreSQL pour production
- [ ] Dashboard avec graphiques et statistiques
- [ ] Export PDF des factures
- [ ] Notifications par email automatiques (rappels factures, etc.)
- [ ] Application mobile
- [ ] Module de paiement en ligne
- [ ] Gestion des stocks et matériaux
- [ ] Planning et calendrier intégré
- [ ] Import/Export CSV des clients
- [ ] API REST documentation avec Swagger

---

## 📸 Captures d'Écran

*À ajouter*

---

**Développé avec ❤️ pour les artisans**
