# Kotaflo - Documentation Technique

Ce document regroupe les informations techniques pour le développement de Kotaflo. Pour la vision stratégique et le pilotage du projet, voir le [README.md](../README.md).

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
│   ├── routes/                 # Endpoints API REST
│   ├── services/               # Logique métier
│   └── utils/                  # Utilitaires
│   └── DOCS_TECH.md            # Ce fichier
│
├── templates/                  # Templates HTML (Jinja2)
├── static/                     # Ressources statiques
│   ├── css/                    # Feuilles de style
│   └── js/                     # Scripts JavaScript
│
├── components/                 # Composants HTML réutilisables
└── database/                   # Schémas SQL
```

---

## 🔌 API Endpoints

Tous les endpoints API sont préfixés par `/api`. Voir le code source pour les détails des paramètres.

---

## 🔐 Authentification

L'application utilise **Flask-JWT-Extended** pour l'authentification. Le token est stocké dans le `localStorage` et doit être envoyé dans le header `Authorization: Bearer <token>`.

---

## 👨‍💻 Développement

### Conventions de Code
- **Python** : Suivre PEP 8
- **JavaScript** : Utiliser `async/await` pour les requêtes API
- **Nommage** : snake_case pour Python, camelCase pour JavaScript

---

## 🚀 Déploiement (Production)

1. **Serveur WSGI** : Utiliser **Gunicorn**.
2. **Reverse Proxy** : Configurer **Nginx**.
3. **HTTPS** : Obligatoire pour OAuth/JWT.
4. **Base de Données** : Migrer vers **PostgreSQL** pour une utilisation réelle.

---

## 📝 Licence

Ce projet est la propriété de ses auteurs. Tous droits réservés.
