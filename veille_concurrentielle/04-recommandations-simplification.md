# 📱 Recommandations : Simplification Radicale pour Mobile

> Comment Kotaflo peut devenir l'outil le plus simple du marché sur smartphone en éliminant les frictions identifiées chez les concurrents.

---

## 📋 Sommaire

1. [Fonctionnalités à supprimer](#1-fonctionnalités-à-supprimer)
2. [Fonctionnalités à simplifier](#2-fonctionnalités-à-simplifier)
3. [Optimisations techniques critiques](#3-optimisations-techniques-critiques)
4. [Résumé des priorités](#résumé-des-priorités)

---

## 1. Fonctionnalités à Supprimer

Pour éviter l'effet **"usine à gaz"** — reproche majeur fait aux leaders internationaux.

### 🚫 Outils de Conception Lourds
- **Supprimer** : Plans 3D, scan LiDAR de pièces, marketing par e-mail
- **Pourquoi** : Présents chez Houzz Pro, ces fonctions sont perçues comme "lourdes"
- **Impact** : Ralentissent l'interface mobile et ne concernent qu'une niche premium

### 🚫 Modules "Hors-Métier"
- **Supprimer** : Création de site web, logos (comme le pack Booster d'Obat)
- **Pourquoi** : L'artisan sur smartphone veut **facturer, pas gérer son agence de communication**

### 🚫 Engagement Contractuel
- **Supprimer** : Contrats de 12 ou 24 mois (pratiqués par TrustUp Pro et Houzz Pro)
- **Pourquoi** : Source majeure de **détestation de la marque**

---

## 2. Fonctionnalités à Simplifier

### ✍️ La Saisie Textuelle

| Concurrent | Solution |
|------------|----------|
| **Obat** | Dictée vocale "Rita" |
| **Costructor** | Importation de devis papier par photo |

> **Objectif Kotaflo** : Que l'artisan n'ait quasiment rien à taper avec ses "mains sales ou occupées"

**Recommandation** : Intégrer saisie vocale + import photo dès le MVP.

---

### 🎯 L'Onboarding et le Paramétrage

| Concurrent | Problème |
|------------|----------|
| **Tolteck** | Démonstration obligatoire de 30 minutes |

> **Objectif Kotaflo** : Créer le **premier devis en moins de 2 minutes** sans formation.

**Recommandation** :
- Onboarding en 3 étapes max
- Pré-remplir un exemple de devis
- Skip tutorial, apprendre en faisant

---

### 💰 La Gestion des Impayés

| Concurrent | Problème |
|------------|----------|
| **Tolteck, Henrri** | Pointage manuel le soir, pas de synchro bancaire |

> **Objectif Kotaflo** : Automatiser les relances et la synchronisation bancaire.

**Recommandation** :
- Relances automatiques configurables (J+3, J+7, J+15)
- Sync bancaire optionnelle (type Bankin')
- Dashboard impayés en un coup d'œil

---

### 📊 La Grille Tarifaire

| Concurrent | Problème |
|------------|----------|
| **Obat** | Multiplication des paliers et options qui perdent l'artisan solo |

> **Objectif Kotaflo** : Système de tokens simple — pas de paliers complexes.

**Recommandation** :
- 3 plans max : Free, Pro, Enterprise
- Tokens clairs : 1 token = 1 devis envoyé
- Pas d'options cachées

---

## 3. Optimisations Techniques Critiques

### 📡 Mode Hors-Ligne

| Concurrent | Problème |
|------------|----------|
| **Obat, Costructor** | Inutilisables dans les zones blanches (sous-sols, zones rurales) |

> **Objectif Kotaflo** : Mode hors-ligne robuste et synchronisation automatique.

**Recommandation** :
- Stockage local (SQLite embarqué ou Indexed côté client)
- Sync auto quand réseau disponible
- Indicateur clair : "📴 Mode hors-ligne" vs "📡 Connecté"

---

### 📱 Application Native

| Concurrent | Problème |
|------------|----------|
| **Henrri** | Pas d'app native — navigateur peu adapté |
| **Tolteck** | Navigateur optimisé au lieu d'app (iOS) |

> **Objectif Kotaflo** : Application native indispensable pour la fluidité sur le terrain.

**Recommandation** :
- PWA (Progressive Web App) pour commencer
- Native iOS/Android si traction confirmée
- Accès offline, notifications push

---

## Résumé des Priorités

| Priorité | Action | Impact |
|----------|--------|--------|
| 🏆 **Mode hors-ligne** | Stockage local + sync auto | 🔴 Critique |
| 🏆 **App native** | PWA d'abord, native ensuite | 🔴 Critique |
| 🥈 **Saisie vocale** | Import photo + dictée | 🟡 Fort |
| 🥈 **Onboarding 2 min** | 3 étapes max, skip tutorial | 🟡 Fort |
| 🥉 **Relances auto** | Configurables, pas de pointage manuel | 🟢 Moyen |
| 🥉 **Grille simple** | 3 plans max, tokens clairs | 🟢 Moyen |

---

## 🎯 Positionnement Cible

> **Kotaflo = "L'outil de poche"**

**Supprimer** tout ce qui n'est pas lié à l'acte immédiat de chiffrage/facturation.

**Automatiser** tout ce qui nécessite une saisie manuelle.

---

## 📌 Key Takeaways

1. **La lourdeur est le reproche #1** aux leaders → rester minimaliste
2. **Le mobile est critique** → app native + mode offline obligatoires
3. **L'artisan veut facturer, pas gérer** → focus sur le core métier
4. **2 minutes max** pour créer un premier devis → onboarding radical

---

*Source : Analyse UX concurrentielle — Avril 2026*
