# 📋 Liste des Tâches - Hadrien

Ce document regroupe les missions prioritaires pour Hadrien afin de ne pas interférer avec le développement core (backend) de Brendan tout en faisant avancer le projet Kotaflo.

---

## 💰 1. Stratégie de Pricing & Business Model
*Objectif : Définir comment on gagne de l'argent et comment on attire les premiers clients.*

- [ ] **Étude de la concurrence** : Analyser les tarifs des logiciels existants (ex: Tolteck, Obat, Henrri) pour se positionner.
- [ ] **Définition des Tiers** : Préciser ce qu'il y a dans chaque plan (déjà mentionnés dans le README) :
    - **Free** : Limite de clients ? Limite de devis ?
    - **Pro** : Accès à la signature électronique ?
    - **Enterprise** : Multi-utilisateurs ?
- [ ] **Modèle de Tokens** : Réfléchir à la logique des jetons pour les devis (ex: 1 devis = 1 token, ou abonnement illimité).
- [ ] **Période d'essai** : Définir la durée (14 jours ?) et si on demande la CB au début.

---

## 🎨 2. Design & Identité Visuelle (UI/UX)
*Objectif : Rendre l'outil "sexy" et facile à utiliser pour un artisan qui n'a pas de temps à perdre.*

- [ ] **Charte Graphique** : Choisir une palette de couleurs (le "Bleu Artisan" rassure, le "Orange" dynamise).
- [ ] **Logo & Assets** : Créer un logo propre et des icônes pour l'interface.
- [ ] **Amélioration CSS** : Travailler dans `static/css/` pour rendre les tableaux et formulaires plus modernes (sans toucher aux fichiers Python).
- [ ] **Captures d'écran** : Réaliser des screenshots propres pour le README et le futur site vitrine.

---

## 📢 3. Marketing & Acquisition
*Objectif : Créer la "hype" et ramener les 10 premiers testeurs.*

- [ ] **Landing Page** : Concevoir le contenu de la page d'accueil (titres accrocheurs, bénéfices utilisateurs).
- [ ] **Plan Réseaux Sociaux** : 
    - Créer un compte Instagram/TikTok "Kotaflo".
    - Préparer une série de posts : "Comment gagner 2h par jour sur ses devis".
- [ ] **Script de Prospection** : Préparer un message type pour contacter des artisans sur Facebook ou LinkedIn pour leur proposer de tester la version Beta.

---

## 🛠️ 4. Améliorations Produit (Low-Code)
- [ ] **Modèles de Devis/Factures** : Améliorer le design des PDF générés par la bibliothèque `fpdf2` (dans `backend/services/`).
- [ ] **Tests Utilisateurs** : Utiliser l'app comme si tu étais un plombier et noter tous les "points de friction" ou bugs visuels.