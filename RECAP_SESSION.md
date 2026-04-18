# 📝 RECAP — Session Log Kotaflo (Adrien)

> Journal des sessions côté Adrien (design, UI/UX, pricing, marketing, docs).
> Après chaque session: ajouter entrée datée (format: "## 📅 DD/MM/YYYY à HH:MM")

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
