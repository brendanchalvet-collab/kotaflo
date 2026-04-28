# 📝 RECAP — Session Log Kotaflo (Adrien)

> Journal des sessions côté Adrien (design, UI/UX, pricing, marketing, docs).
> Après chaque session: ajouter entrée datée (format: "## 📅 DD/MM/YYYY à HH:MM")

## 📅 28/04/2026 — Session complète UI/Pricing/Landing

### Pages créées

- **`templates/pricing.html`** — Page tarifs complète (3 plans Free/Pro/Enterprise + packs tokens à l'unité). Sidebar intégrée, mobile-first, CSS variables existantes. Lien ajouté dans les 9 sidebars de l'app.
- **`templates/trial.html`** — Page d'essai gratuit 14 jours. Hero + 4 features incluses + formulaire (email, entreprise, CGU). Stub JS pour Brendan.
- **`templates/checkout_packs.html`** — Achat jetons. 3 packs radio cliquables, résumé dynamique, `<div id="stripe-card-element">` vide, pré-sélection via `?pack=10|50|100`.
- **`templates/checkout_pro.html`** — Abonnement Pro 29€/mois. Récap 6 features, form email, `<div id="stripe-card-element">` vide.
- **`templates/landing.html`** — Landing page publique complète (sans sidebar) : hero + stats visuelles, 4 feature cards grid 2×2, tableau comparaison 5 lignes, 3 témoignages fictifs, CTA final dark, footer. Redirige vers /dashboard si token valide.
- **`static/css/landing.css`** — CSS dédié landing (header sticky, hero, features, compare table, testimonials, CTA dark).

### Routes ajoutées dans `app.py`

| Route | Template | Note |
|-------|----------|------|
| `/` | `landing.html` | Séparée de `/login` |
| `/pricing` | `pricing.html` | `render_template` |
| `/trial` | `trial.html` | `render_template` |
| `/checkout-packs` | `checkout_packs.html` | `render_template` |
| `/checkout-pro` | `checkout_pro.html` | `render_template` |

### Liens pricing.html

- "Démarrer l'essai gratuit" → `/trial`
- "Passer au Pro" → `/checkout-pro`
- "Acheter" Pack 10/50/100 → `/checkout-packs?pack=10|50|100`

### Bug fixes

- **Moyen d'acquisition supprimé** : `form-group` retiré de `clients.html`, `contact_history.html`, `leads.html`. Refs JS nettoyées dans `clients.js`, `leads.js`, `contact_history.js` (reset, populate, envoi API).
- **Validation dates projet** : `onchange="validateProjDates()"` ajouté sur `proj-end` dans `projects.html`, `dashboard.html`, `contact_history.html`. Fonction ajoutée dans les 3 JS correspondants.

### Auth fix

- **Diagnostic** : La DB `artisans_saas.db` avait été créée avec un ancien schéma (`firebase_uid`) alors que le code actuel utilise `password_hash`. Login bcrypt impossible.
- **Fix** : Suppression de l'ancienne DB + réinit via `python init_db.py` → schéma correct restauré.
- **Venv créé** : `.venv/` à la racine pour les installations pip sous Arch Linux.
- **Dev bypass supprimé** : Routes `/dev-login` et `/dev-dashboard` créées puis retirées (non nécessaires après le fix DB).

### Mise à jour stratégique des prix — Proposition 2

- **Rationale** : Avant, les packs avaient un meilleur rapport €/token que Pro (0.39€ vs 0.97€). Ça poussait les users à acheter des gros packs plutôt que passer à l'abonnement.
- **Changement** : Augmentation des packs pour les rendre moins attractifs. Pro devient le meilleur ratio.
  - **Rationale** : Avant, les packs avaient un meilleur rapport €/token que Pro (0.39€ vs 0.97€). Ça poussait les users à acheter des gros packs plutôt que passer à l'abonnement.
  - **Changement** : Augmentation des packs pour les rendre moins attractifs. Pro devient le meilleur ratio.

  | Plan | Ancien | Nouveau | €/Token |
  |------|--------|---------|---------|
  | Pack 10 | 6€ | 15€ | 1.50€ |
  | Pack 50 | 24€ | 50€ | 1.00€ |
  | Pack 100 | 39€ | 80€ | 0.80€ |
  | Pro | 29€ | 29€ | 0.97€ ← Meilleur |

  - **Résultat attendu** : Free users achètent 1-2 petits packs (urgence), puis réalisent que Pro est plus rentable et basculent naturellement.
  - **Modèle** : Option A confirmée (Free → Packs → Pro).

---

## 📅 18/04/2026 à 16:09

- **Exploration design — 3 variantes parallèles** : Création du dossier `design_variants/` avec 3 directions stylistiques en maquettes HTML statiques navigables, **sans toucher au code actuel** (templates Flask et CSS de production intacts).
  - **V1 — Atelier Chaleureux** (`v1_atelier/`) : papier crème, terracotta, Fraunces serif. Ambiance carnet d'artisan, fait-main, rassurant.
  - **V2 — Nordique Épuré** (`v2_nordique/`) : blanc cassé, sauge, Manrope. Minimal scandinave, UI qui respire, positionnement premium.
  - **V3 — Chantier Confiant** (`v3_chantier/`) : graphite, safety orange, Space Grotesk. Gros chiffres, boutons francs, inspiration outils pros chantier.
- **4 pages par variante** : Dashboard, Login/Onboarding, Liste clients, Devis/Factures — soit 12 maquettes + 1 index central (`design_variants/index.html`) qui compare les 3 directions côte à côte avec swatches de palette.
- **Contenu réaliste** : persona "Marc Arnaud, plombier Lyon", 6 clients fictifs, devis rénovation SDB à 4 932 € TTC pour évaluer les écrans avec des vraies données.
- **Prochaine étape** : choisir la direction (ou combinaison) puis extraire les tokens dans `static/css/` pour brancher sur les templates Jinja2 actuels.

---

## 📅 18/04/2026 à 15:50

- **Commit 903f22d** : "docs: consolidation documentaire et création ARCHITECTURE.md"
  - 246 fichiers changés (27K insertions, 9K deletions)
  - Branche: `feature-adrien-fondations` (prête pour Claude design + GitHub)
  - Tous les changements de la session documentés et versionés

---

## 📅 18/04/2026 à 15:45

- **Création ARCHITECTURE.md** : Nouvelle source unique pour architecture du projet :
  - Arborescence complète (backend/, templates/, static/, components/, database/)
  - Architecture multi-tenant détaillée (2 BDD séparées, isolation par tenant_id)
  - Patterns de code (3-couches, décorateurs, validations centralisées)
  - Responsabilités par dossier (qui touche quoi)
  - Points d'intégration clés (Frontend ↔ Backend, JWT, PDF, Email)
  - Flux utilisateur & lancement app
- **Centralisation docs** : ARCHITECTURE.md complète claude.md et claude_adrien.md (architecture distribuée auparavant)

---

## 📅 18/04/2026 à 15:40

- **Centralisation Backlog** : Ajout des 5 tâches manquantes à `BACKLOG.md` depuis `z - taches adrien.md` :
  - SHOULD HAVE: Landing Page (6), Script de Prospection (7), Tests Utilisateurs (8)
  - COULD HAVE: Plan Réseaux Sociaux (5), Captures d'écran (6)
- **Suppression du doublon** : `z - taches adrien.md` supprimé — toutes les tâches sont maintenant centralisées dans `BACKLOG.md`.
- **Structure Backlog** : Backlog utilise la méthode MoSCoW (MUST, SHOULD, COULD, WON'T) pour une priorisation claire.

---

## 📅 18/04/2026 à 15:35

- **Consolidation documentaire** : Suppression de `antigravity.md` et `agents.md` — toutes les infos sont consolidées dans `claude_adrien.md`.
- **Vérification effectuée** : `claude_adrien.md` contient l'ensemble des règles, permissions, stack, protocoles et priorités des deux fichiers supprimés.
- **Source unique** : `claude_adrien.md` devient la référence unique pour les sessions Adrien (design, marketing, pricing, UI/UX).

---

## 📅 18/04/2026 à 15:31

- **Gouvernance assistant** : Création de `claude_adrien.md` — règles de travail dédiées à Adrien, synthétisées depuis `AGENTS.md` et `antigravity.md` (périmètre, zones restreintes/libres, stack, protocole, priorités Phase 1).
- **Séparation des rôles** : Le fichier `claude.md` reste réservé à Brendan (technique). `claude_adrien.md` devient la référence pour les sessions côté Adrien.
- **Renommage** : `RECAP_SESSION.md` → `RECAP_SESSION_Adrien.md` pour un journal dédié.

---

## 📅 17/04/2026 à 16:22

- **Gouvernance assistant** : Création de `AGENTS.md` (règles de permissions, architecture Flask, protocole de communication).
- **Simplification doc** : Fusion de `ROADMAP.md` dans `BACKLOG.md` pour une source de vérité unique.
- **Stratégie tarifaire** : Mise à jour du Backlog (Sprint 1-2) avec les Options A (Packs) et B (Freemium) issues de la veille concurrentielle.
- **Protocole** : Validation de la règle de datation systématique des entrées de log.
- **Révision contextuelle** : Migration de `qwen.md` vers `antigravity.md`.

---

## 📅 17/04/2026 à 15:48

- **Documentation** : Refonte du `README.md` en "Cockpit de Vision Globale".
- **Technique** : Déplacement de la documentation technique vers `backend/DOCS_TECH.md`.

---

## 📅 17/04/2026 à 15:10

- **Étude concurrence** : Analyse terminée de 6 concurrents majeurs.
- **Initialisation** : Création du `BACKLOG.md` et de la structure du dossier `veille_concurrentielle/`.
