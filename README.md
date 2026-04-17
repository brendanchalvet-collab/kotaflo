# 🚀 Kotaflo — Vision Globale & Cockpit

> **Mantra** : "L'outil de poche de l'artisan libre."
> **Objectif** : Simplicité radicale, mobilité totale (offline), zéro engagement.

---

## 📌 Accès Rapides (Pilotage)

| Section | Lien | Description |
| :--- | :--- | :--- |
| **Analyse** | [📚 Veille Concurrentielle](veille_concurrentielle/INDEX.md) | Études de marché et stratégie de différenciation. |
| **Planification** | [🗺️ Roadmap Projet](ROADMAP.md) | Phases de développement et timeline globale. |
| **Exécution** | [📋 Backlog Priorisé](BACKLOG.md) | Liste des fonctionnalités (Must, Should, Could). |
| **Historique** | [📝 Récapitulatifs de Session](RECAP_SESSION.md) | Journal de bord des avancées et décisions. |
| **Technique** | [🛠️ Documentation Technique](backend/DOCS_TECH.md) | Setup, architecture, API et base de données. |

---

## 🔥 Focus Actuel : Phase 1 — Fondations (En cours)

Nous sommes actuellement en train de stabiliser les bases stratégiques et techniques du SaaS.

### 🎯 Tâches Prioritaires (Sprint 1-2)
- [x] Étude de concurrence complète.
- [ ] **Définition des plans** (Free/Pro/Enterprise) — *Adrien*
- [ ] **Modèle de Tokens** (1 Token = 1 Devis) — *Adrien*
- [ ] **Période d'essai** (Workflow sans CB) — *Adrien*
- [ ] Stabilisation Auth & Audit Multi-tenant — *Brendan*

---

## 🤔 Décisions & Arbitrages (À trancher)

| Sujet | Options | Statut |
| :--- | :--- | :--- |
| **Pricing** | Option A (Packs de jetons) vs Option B (Seuil Freemium) | 🟡 **En attente de Brendan** |
| **Essai** | 14 jours ou 30 jours ? | ⚪ À discuter |
| **Offline** | Stockage SQLite local vs IndexedDB ? | ⚪ À arbitrer techniquement |

---

## 🤝 Guide de Collaboration

### Adrien — Produit & UX/UI
- Stratégie business, acquisition et pricing.
- Design de l'interface et des templates HTML/CSS.
- Expérience utilisateur (UX) et parcours clients.

### Brendan — Architecture & Backend
- Infrastructure, sécurité et base de données.
- Développement des APIs et logique métier complexe.
- Déploiement et performances.

---

## 🛠️ État de la Plateforme

- **Stack** : Flask (Python) + SQLite + Vanilla JS + Jinja2.
- **Dernière release** : Migration de l'assistant de contexte (Antigravity).
- **Setup rapide** : `pip install -r requirements.txt` && `python init_db.py`.
- **Détails techniques** : [Voir DOCS_TECH.md](backend/DOCS_TECH.md).

---

*Dernière mise à jour : 17 Avril 2026 à 15:48*
*Ce README est l'outil de synchronisation coeur entre Adrien et Brendan.*
