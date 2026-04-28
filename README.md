# 🚀 Kotaflo — Vision Globale & Cockpit

> **Mantra** : "L'outil de poche de l'artisan libre."
> **Objectif** : Simplicité radicale, mobilité totale (offline), zéro engagement.

---

## 📌 Accès Rapides (Pilotage)

| Section | Lien | Description |
| :--- | :--- | :--- |
| **Analyse** | [📚 Veille Concurrentielle](veille_concurrentielle/INDEX.md) | Études de marché et stratégie de différenciation. |
| **Exécution** | [📋 Backlog Priorisé](BACKLOG.md) | Liste des fonctionnalités (Must, Should, Could). |
| **Historique** | [📝 Récapitulatifs de Session](RECAP_SESSION.md) | Journal de bord des avancées et décisions. |
| **Architecture** | [🏗️ Architecture](ARCHITECTURE.md) | Arborescence, patterns, BDD, lancement. |
| **Brendan** | [🔧 TODO Brendan](BRENDAN_TODO.md) | Liste priorisée des tâches backend à implémenter. |

---

## 🔥 Focus Actuel : Phase 1 — Sprint 1-2

### ✅ Livré côté Adrien (28/04/2026)

- [x] Stratégie tarifaire — Proposition 2 (Free → Packs → Pro)
- [x] Page `/pricing` — 3 plans + packs tokens
- [x] Page `/trial` — formulaire essai 14j sans CB
- [x] Page `/checkout-packs` — achat jetons (Stripe placeholder)
- [x] Page `/checkout-pro` — abonnement Pro (Stripe placeholder)
- [x] Page `/` — landing page publique complète
- [x] Fix auth DB (schéma `password_hash` restauré, login fonctionnel)
- [x] Bug fixes (champ acquisition supprimé, validation dates chantiers)
- [x] Lien Tarifs ajouté dans toutes les sidebars (9 templates)

### 🔴 En attente côté Brendan

- [ ] Auth : vérifier login bcrypt end-to-end (**BLOCKER**)
- [ ] Tokens system : table + service + `/api/tokens/balance`
- [ ] Trial backend : `POST /api/trial/start`
- [ ] Stripe webhooks : packs + abonnement Pro
- [ ] Emails transactionnels : confirmation trial/achat/Pro
- [ ] Audit multi-tenant isolation

> Voir [BRENDAN_TODO.md](BRENDAN_TODO.md) pour le détail complet + ordre recommandé.

---

## 🤔 Décisions Actées

| Sujet | Décision | Date |
| :--- | :--- | :--- |
| **Pricing** | Option A confirmée — Free → Packs → Pro | 28/04/2026 |
| **Packs** | Proposition 2 — Packs augmentés, Pro = meilleur ratio | 28/04/2026 |
| **Essai** | 14 jours sans CB | 28/04/2026 |
| **Auth** | bcrypt (DB réinitialisée) — Firebase à décider par Brendan | 28/04/2026 |

---

## 🤝 Guide de Collaboration

### Adrien — Produit & UX/UI
- Stratégie business, acquisition et pricing.
- Design de l'interface et des templates HTML/CSS.
- Expérience utilisateur (UX) et parcours clients.

### Brendan — Architecture & Backend
- Infrastructure, sécurité et base de données.
- Développement des APIs et logique métier complexe.
- Intégration Stripe, emails, tokens system.

---

## 🛠️ État de la Plateforme

- **Stack** : Flask (Python) + SQLite + Vanilla JS + Jinja2
- **Pages UI livrées** : 12 (dashboard, clients, devis, factures, chantiers, tâches, profil, pricing, trial, checkout×2, landing)
- **Lancement** :
  ```bash
  source .venv/bin/activate
  python init_db.py   # première fois seulement
  python app.py       # → http://localhost:5000
  ```
- **Créer un compte** : aller sur `/login` → onglet "Créer un compte"

---

*Dernière mise à jour : 28 Avril 2026*
*Ce README est l'outil de synchronisation cœur entre Adrien et Brendan.*
