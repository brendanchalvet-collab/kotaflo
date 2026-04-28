# 🔧 BRENDAN TODO — Backend à brancher sur l'UI existante

> Adrien a livré toute la couche UI de la session du 28/04/2026.
> Ce fichier liste **tout ce que Brendan doit implémenter** côté backend
> pour que le produit soit fonctionnel.
>
> **Pages UI prêtes et qui attendent le backend** :
> - `/trial` → formulaire essai 14j
> - `/checkout-packs` → achat jetons (Stripe placeholder présent)
> - `/checkout-pro` → abonnement Pro (Stripe placeholder présent)
> - `/pricing` → page tarifs (liens actifs vers les pages ci-dessus)
> - `/` → landing page publique

---

## 🚨 CRITIQUE — Bloque tout le reste

### 1. Authentification — Fix ou Migration

**Status** : ⚠️ Partiellement fixé (Adrien a réinitialisé la DB avec le bon schéma `password_hash`)
**Restant** :

- [ ] Vérifier que login bcrypt fonctionne end-to-end en local
- [ ] Décider si Firebase Auth est maintenu ou abandonné
  - Si **bcrypt uniquement** : retirer `firebase_login` et `firebase_utils` des imports dans `app.py`
  - Si **Firebase** : brancher le SDK Firebase Admin correctement + intégrer `firebase_login` dans `login.html`
- [ ] Tester : créer un user via `/login` (onglet Register), se connecter, JWT valide, accès dashboard

> **Note** : La DB `artisans_saas.db` a été réinitialisée avec le bon schéma
> (`password_hash TEXT NOT NULL`). Les 3 anciens users (brendan, admin, test)
> ont été perdus — recréer un compte via le formulaire Register.

---

### 2. Système de Tokens Backend

**Status** : ❌ N'existe pas côté backend — la sidebar affiche `— / —`

**À faire** :

- [ ] Ajouter table `user_tokens` dans `artisans_saas.db` :
  ```sql
  CREATE TABLE user_tokens (
      id         INTEGER PRIMARY KEY AUTOINCREMENT,
      tenant_id  INTEGER NOT NULL REFERENCES tenants(id),
      balance    INTEGER DEFAULT 0,
      consumed   INTEGER DEFAULT 0,
      updated_at TEXT DEFAULT (datetime('now'))
  );
  ```
- [ ] Créer `backend/services/token_service.py` :
  - `get_balance(tenant_id)` → retourne balance actuelle
  - `add_tokens(tenant_id, amount)` → crédite des tokens
  - `deduct_token(tenant_id)` → décrémente 1 token, lève exception si solde = 0
- [ ] Endpoint `GET /api/tokens/balance` → retourne `{ balance, consumed, plan }`
- [ ] Brancher `deduct_token` dans `quote_service.py` lors de l'envoi d'un devis
- [ ] Bloquer l'envoi si solde = 0 (retourner 402 Payment Required)
- [ ] Brancher l'affichage dans le widget sidebar (JS lit `/api/tokens/balance` au chargement)

**Le widget sidebar est déjà codé** — il attend juste l'endpoint :
```javascript
// Dans chaque template, le widget sidebar :
<div class="sidebar__tokens-count">— / —</div>  // ← à peupler via API
```

---

## 🔴 HAUTE PRIORITÉ

### 3. Période d'Essai — Backend

**Status** : ❌ Page `/trial` existe (HTML + formulaire), pas de backend

**À faire** :

- [ ] Ajouter table `trials` dans `artisans_saas.db` :
  ```sql
  CREATE TABLE trials (
      id                  INTEGER PRIMARY KEY AUTOINCREMENT,
      tenant_id           INTEGER NOT NULL REFERENCES tenants(id),
      email               TEXT NOT NULL,
      company_name        TEXT,
      started_at          TEXT DEFAULT (datetime('now')),
      expires_at          TEXT,         -- started_at + 14 jours
      converted_to_paid   INTEGER DEFAULT 0,
      trial_tokens_bonus  INTEGER DEFAULT 100
  );
  ```
- [ ] Endpoint `POST /api/trial/start` :
  ```
  Body : { email, company_name }
  → Crée user + tenant + trial record
  → Crédite 100 tokens bonus
  → Envoie email de confirmation
  → Retourne JWT pour connexion directe
  ```
- [ ] Endpoint `GET /api/trial/status` → jours restants + tokens restants
- [ ] Brancher le `<form>` dans `templates/trial.html` :
  ```javascript
  // Dans trial.html — la fonction handleTrial() est déjà présente :
  function handleTrial(e) {
      e.preventDefault();
      // → Brendan branche ici POST /api/trial/start
  }
  ```

---

### 4. Stripe — Intégration Webhooks

**Status** : ❌ Pages UI prêtes avec `<div id="stripe-card-element">` vide

**À faire dans l'ordre** :

#### 4a. Stripe Elements (Frontend — côté Adrien après que Brendan donne la clé publique)
- Brendan fournit `STRIPE_PUBLIC_KEY`
- Adrien injecte Stripe.js dans `checkout_packs.html` et `checkout_pro.html`

#### 4b. Backend Packs (simple)
- [ ] Endpoint `POST /api/checkout/packs/create-intent` :
  ```
  Body : { pack_size: 10|50|100, email }
  → Crée PaymentIntent Stripe
  → Retourne client_secret pour Stripe Elements
  ```
- [ ] Webhook `POST /webhooks/stripe` — écoute `payment_intent.succeeded` :
  ```
  → Récupère metadata.tenant_id + metadata.pack_size
  → Appelle token_service.add_tokens(tenant_id, pack_size)
  → Envoie email confirmation
  ```

#### 4c. Backend Abonnement Pro
- [ ] Endpoint `POST /api/checkout/pro/create-subscription` :
  ```
  Body : { email }
  → Crée Customer Stripe
  → Crée Subscription au price_id Pro
  → Retourne client_secret
  ```
- [ ] Webhook `customer.subscription.created` :
  ```
  → Update subscriptions table : plan = 'pro'
  → Crédite 30 tokens
  ```
- [ ] Webhook `invoice.payment_succeeded` (renouvellement mensuel) :
  ```
  → Crédite 30 tokens chaque mois
  ```

**Formulaires prêts dans** :
- `templates/checkout_packs.html` → `handleCheckout()` à brancher
- `templates/checkout_pro.html` → `handleCheckoutPro()` à brancher

---

### 5. Emails Transactionnels

**Status** : ⚠️ SMTP config existe dans `config.py`, templates non faits

**À faire** :

- [ ] Configurer SMTP ou SendGrid (éviter gmail direct — auth complexe)
- [ ] Templates emails :
  - [ ] Confirmation trial — lien de connexion + tokens offerts
  - [ ] Confirmation achat pack — reçu + nb tokens crédités
  - [ ] Confirmation abonnement Pro — bienvenue
  - [ ] Rappel expiration trial J-3 et J-1
  - [ ] Relances factures (J+3, J+7, J+15)
- [ ] Tester en local : envoyer un email réel

---

## 🟡 MOYENNE PRIORITÉ

### 6. Audit Multi-Tenant

**Status** : ⚠️ Isolation tenant_id existe dans les modèles, non audité

**À faire** :

- [ ] Vérifier que **chaque** endpoint filtre par `tenant_id`
- [ ] Tester isolation : créer 2 comptes, vérifier qu'un user ne voit pas les données de l'autre
- [ ] Chercher les routes sans `@jwt_required()` qui exposent des données

---

### 7. Relances Automatiques — Job Cron

**Status** : ❌ UI leads.html existe, pas de cron côté backend

**À faire** :

- [ ] Job cron quotidien : parcourir factures `status = 'pending'` + `due_date` dépassée
- [ ] Envoyer email relance selon délai (J+3, J+7, J+15)
- [ ] Logger chaque relance dans `interactions` (type = 'reminder')
- [ ] Toggle on/off par facture (champ à ajouter en DB ?)

---

### 8. Saisie Vocale / IA (Future)

**Status** : ❌ Non commencé — basse priorité

**À faire (plus tard)** :

- [ ] Endpoint `POST /api/quotes/structure-with-ai` :
  - Reçoit texte brut
  - Appelle Groq/Claude API pour structurer en JSON
  - Retourne lignes de devis structurées
  - Débit : 1 token par appel

---

## 📋 Récap Priorités

| # | Tâche | Criticité | Temps Est. | Bloquant |
|---|-------|-----------|-----------|----------|
| 1 | Auth fix | 🚨 URGENT | 1-2h | Tout |
| 2 | Tokens system | 🚨 URGENT | 3-4h | Pricing/monétisation |
| 3 | Trial backend | 🔴 HIGH | 2h | Acquisition beta |
| 4 | Stripe webhooks | 🔴 HIGH | 4-5h | Paiements |
| 5 | Email setup | 🔴 HIGH | 1-2h | UX |
| 6 | Tenant audit | 🟡 MED | 2h | Sécurité prod |
| 7 | Relances auto | 🟡 MED | 1.5h | Feature |
| 8 | IA structuration | 🟢 LOW | 3h | Différenciation |

---

## 🗓️ Ordre Recommandé

```
Semaine 1 :
  → Auth fix (BLOCKER ABSOLU)
  → Tokens system (CŒUR ÉCONOMIQUE)
  → Trial backend (ACQUISITION)

Semaine 2 :
  → Stripe webhooks (PAIEMENTS)
  → Email setup (UX)

Semaine 3 :
  → Tenant audit (SÉCURITÉ)
  → Relances automatiques (FEATURE)
```

---

*Créé le 28/04/2026 — Session Adrien*
*À mettre à jour au fur et à mesure que Brendan complète les tâches.*
