# kotaflo - SaaS de Gestion pour Artisans

**kotaflo** est une application SaaS complète conçue pour aider les artisans à gérer leur activité quotidienne. Elle offre une suite d'outils intégrés pour la gestion des clients, des devis, des factures, des projets et des tâches.

## 🚀 Fonctionnalités

### Gestion Commerciale
- **Clients** : CRM complet avec historique des contacts
- **Leads** : Suivi des prospects et opportunités
- **Devis (Quotes)** : Création, envoi et suivi des devis
  - Signature électronique des devis par les clients
  - Partage par lien sécurisé avec token d'accès
- **Factures (Invoices)** : Génération et gestion des factures

### Gestion de Projets
- **Projets/Chantiers** : Suivi complet des projets
- **Tâches** : Organisation et suivi des tâches par projet
- **Historique** : Traçabilité des actions et communications

### Authentification & Sécurité
- Authentification JWT avec tokens d'accès (8h)
- Connexion sécurisée avec hachage bcrypt
- Intégration Google OAuth2
- Système d'OTP pour la validation

### Communication
- Envoi d'emails via SMTP (devis, OTP)
- Intégration Gmail API
- Historique des contacts clients

## 🛠️ Technologies

- **Backend** : Flask (Python)
- **Base de données** : SQLite (dual database architecture)
  - `artisans_saas.db` : Données SaaS et utilisateurs
  - `artisans_client.db` : Données clients et métiers
- **Authentification** : Flask-JWT-Extended, bcrypt
- **API** : RESTful API avec CORS
- **Frontend** : HTML5, CSS3, JavaScript vanilla

## 📦 Installation

### Prérequis
- Python 3.8+
- pip

### 1. Cloner le repository
```bash
git clone <repository-url>
cd kotaflo
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer l'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Flask
SECRET_KEY=votre_clé_secrète_flask
DEBUG=true

# JWT
JWT_SECRET_KEY=votre_clé_secrète_jwt

# Bases de données
SAAS_DB_PATH=artisans_saas.db
CLIENT_DB_PATH=artisans_client.db

# Google OAuth2 (optionnel)
GOOGLE_CLIENT_ID=votre_client_id
GOOGLE_CLIENT_SECRET=votre_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/api/google/callback

# SMTP pour l'envoi d'emails
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app
SMTP_FROM=votre_email@gmail.com
```

### 4. Initialiser la base de données
```bash
python init_db.py
```

### 5. Lancer l'application
```bash
python app.py
```

L'application sera disponible sur : http://localhost:5000

## 📁 Structure du Projet

```
kotaflo/
├── app.py                 # Point d'entrée principal
├── config.py              # Configuration de l'application
├── init_db.py             # Script d'initialisation des bases de données
├── requirements.txt       # Dépendances Python
├── artisans_saas.db       # Base de données SaaS
├── artisans_client.db     # Base de données clients
│
├── backend/
│   └── routes/
│       ├── auth.py           # Authentification
│       ├── clients.py        # Gestion des clients
│       ├── leads.py          # Gestion des leads
│       ├── quotes.py         # Gestion des devis
│       ├── quote_access.py   # Accès public aux devis
│       ├── invoices.py       # Gestion des factures
│       ├── jobs.py           # Gestion des projets
│       ├── tasks.py          # Gestion des tâches
│       ├── profile.py        # Gestion du profil utilisateur
│       └── google_auth.py    # Authentification Google
│
├── templates/             # Pages HTML frontend
│   ├── login.html
│   ├── dashboard.html
│   ├── clients.html
│   ├── contact_history.html
│   ├── quotes.html
│   ├── quote_sign.html    # Page de signature publique
│   ├── invoices.html
│   ├── projects.html
│   ├── project_detail.html
│   ├── tasks.html
│   └── profile.html
│
├── static/                # Fichiers statiques (CSS, JS, images)
├── components/            # Composants réutilisables
└── database/              # Scripts et modèles de base de données
```

## 🔌 API Endpoints

### Authentification
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `GET /api/google/auth` - Authentification Google
- `GET /api/google/callback` - Callback Google OAuth

### Clients
- `GET /api/clients` - Liste des clients
- `POST /api/clients` - Créer un client
- `GET /api/clients/<id>` - Détails d'un client
- `PUT /api/clients/<id>` - Modifier un client
- `DELETE /api/clients/<id>` - Supprimer un client

### Devis
- `GET /api/quotes` - Liste des devis
- `POST /api/quotes` - Créer un devis
- `GET /api/quote-access/<token>` - Accès public à un devis

### Factures
- `GET /api/invoices` - Liste des factures
- `POST /api/invoices` - Créer une facture
- `GET /api/invoices/<id>/pdf` - Télécharger en PDF

### Projets & Tâches
- `GET /api/jobs` - Liste des projets
- `POST /api/jobs` - Créer un projet
- `GET /api/tasks` - Liste des tâches
- `POST /api/tasks` - Créer une tâche

## 🔐 Sécurité

- Mots de passe hachés avec bcrypt
- Tokens JWT avec expiration automatique (8 heures)
- CORS configuré pour les appels API
- Tokens d'accès uniques pour le partage de devis
- Validation des entrées utilisateur

## 📝 Licence

Ce projet est propriétaire. Tous droits réservés.

## 👥 Contact

Pour toute question ou support, contactez l'équipe kotaflo.

---

**kotaflo** - La solution tout-en-un pour les artisans qui souhaitent digitaliser et optimiser leur gestion commerciale.
