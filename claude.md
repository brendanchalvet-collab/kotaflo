🧠 Claude Code Context — SaaS Artisans (Scalable)
🧑‍💻 Profil développeur

Je développe un SaaS métier destiné aux artisans (plombiers, électriciens, etc.).

Stack utilisée :

HTML
CSS
JavaScript
Python (backend)
SQL (PostgreSQL recommandé)

Objectif :
👉 Construire une solution SaaS clé en main, scalable, maintenable et performante

🏗️ Architecture globale

Le SaaS est structuré en 2 couches distinctes :

1. 🧾 BDD SaaS (admin plateforme)

Gère :

utilisateurs
abonnements
plans
facturation
accès
2. 🏢 BDD Client (multi-tenant)

Gère :

données métier artisan
clients
devis
factures
chantiers

👉 Séparation OBLIGATOIRE

🧱 Organisation des projets
/templates
/static/css
/static/js
/backend
    /routes
    /services
    /models
    /utils
/components
/database
    /migrations
    /schemas
📏 Règles de taille
300–400 lignes max par fichier
découper en modules si nécessaire
backend toujours séparé par responsabilité
🧠 Logique SaaS (CRITIQUE)
Multi-tenant obligatoire

Chaque requête doit être liée à :

tenant_id

👉 AUCUNE donnée ne doit fuiter entre clients

🗄️ BDD CLIENT (métier artisan)
Tables principales
👤 clients
id
tenant_id
name
phone
email
address
created_at
📄 leads (prospects)
id
tenant_id
client_id
source
status (new, contacted, quoted, won, lost)
notes
created_at
🧾 quotes (devis)
id
tenant_id
client_id
amount
status (draft, sent, accepted, refused)
created_at
💰 invoices (factures)
id
tenant_id
client_id
amount
status (pending, paid, late)
due_date
created_at
🏗️ jobs (chantiers)
id
tenant_id
client_id
title
status (planned, ongoing, done)
start_date
end_date
notes
📅 appointments
id
tenant_id
client_id
job_id
date
status
🔁 reminders (relances auto)
id
tenant_id
type (quote, invoice)
target_id
scheduled_at
sent
🧾 BDD SAAS (plateforme)
👤 users
id
email
password_hash
created_at
🏢 tenants
id
name
created_at
🔗 user_tenants
user_id
tenant_id
role (admin, user)
💳 subscriptions
id
tenant_id
plan
status
start_date
end_date
⚙️ Backend (Python)

Structure obligatoire :

/routes     → endpoints API
/services   → logique métier
/models     → accès BDD
/utils      → helpers
🔥 Règles critiques
Aucune logique dans les routes
Toute logique métier → services
Accès BDD → models uniquement
🔐 Sécurité
Auth obligatoire (JWT ou session)
Vérification du tenant_id à chaque requête
Hash des mots de passe (bcrypt)
🎨 Frontend
HTML
Sections commentées
Structure claire
composants réutilisables
CSS
base.css
layout.css
components.css
JS
1 fichier par feature :
leads.js
quotes.js
dashboard.js
🚀 Features MVP (priorité)
1. CRM simple
création client
fiche client
2. Gestion leads
pipeline simple
3. Devis
création rapide
statut
4. Factures
suivi paiement
5. Relances automatiques
devis non répondu
facture impayée
⚡ Philosophie produit

❌ Pas un CRM complexe type Salesforce
❌ Pas une usine à gaz comme HubSpot

✅ Ultra simple
✅ Ultra rapide
✅ Mobile-first

📱 UX règles
1 action = 1 écran
max 3 clics pour créer un devis
interface utilisable sur chantier
🧪 Tests
tester chaque endpoint
tester isolation tenant
tester création → facturation complète
📦 Scalabilité
DB indexée (tenant_id obligatoire)
pagination sur toutes les listes
aucune requête lourde
🚫 À éviter
mélange SaaS / client dans une même BDD
routes avec logique métier
fichiers trop longs
UI complexe
🎯 Objectif final

Construire :

Le CRM ultra simple pour artisans qui veulent bosser, pas gérer