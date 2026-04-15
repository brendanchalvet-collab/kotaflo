# 📋 Backlog Kotaflo — Priorisation MoSCoW

> Backlog produit basé sur l'étude de concurrence et la stratégie Kotaflo : **"L'outil de poche de l'artisan libre"**

---

## 📊 Méthode de Priorisation

| Priorité | Signification | Critère |
|----------|--------------|---------|
| 🔴 **MUST** | Indispensable | Sans ça, le produit ne fonctionne pas |
| 🟡 **SHOULD** | Important | Forte valeur ajoutée, mais pas bloquant au lancement |
| 🟢 **COULD** | Bonus | Amélioration significative, mais peut attendre |
| ⚪ **WON'T** | Écarté | Pas pour maintenant (trop lourd, pas aligné stratégie) |

---

## 🔴 MUST HAVE (Indispensable)

> Ces fonctionnalités sont **critiques** pour le lancement de la beta. Sans elles, Kotaflo ne tient pas sa promesse.

### 1. Mode Hors-Ligne Robuste
**Pourquoi** : Talon d'Achille de Costructor et Obat. Les artisans travaillent dans des zones blanches (sous-sols, zones rurales).

**Spécifications** :
- Stockage local des données (SQLite côté client ou IndexedDB)
- Synchronisation automatique quand réseau disponible
- Indicateur clair : 📴 Mode hors-ligne vs 📡 Connecté
- Conflits de sync gérés (dernière modification wins)

**Responsable** : Brendan (architecture) + Adrien (UX indicator)

---

### 2. Système de Tokens (Backend)
**Pourquoi** : Aucun concurrent ne propose de paiement à l'usage pur. C'est notre différenciation majeure.

**Spécifications** :
- 1 token = 1 devis envoyé
- Achat de packs de tokens (10, 50, 100)
- Dashboard : solde de tokens, historique conso
- Plan Pro : quota mensuel de tokens (ex: 30/mois)
- Pas d'engagement contractuel

**Responsable** : Brendan (backend + DB) + Adrien (UI dashboard)

---

### 3. Dashboard "Artisan Libre"
**Pourquoi** : Vue d'ensemble instantanée. L'artisan doit voir en 1 coup d'œil où il en est.

**Spécifications** :
- KPIs : clients actifs, devis en cours, factures impayées, chantiers en cours
- Graphique simple : revenus mensuels
- Alertes : factures en retard, devis à relancer
- Mobile-first, lisible en 5 secondes

**Responsable** : Brendan (API data) + Adrien (UI/UX templates)

---

### 4. Authentification & Multi-Tenant
**Pourquoi** : Base technique obligatoire. Isolation des données par entreprise.

**Spécifications** :
- Login/Register avec JWT
- Google OAuth (optionnel)
- Isolation par `tenant_id`
- Plans : Free, Pro, Enterprise

**Responsable** : Brendan

---

### 5. CRUD Clients & Prospects
**Pourquoi** : Fonctionnalité de base. Sans clients, pas de devis ni factures.

**Spécifications** :
- Créer, modifier, supprimer un client
- Coordonnées complètes (nom, tel, email, adresse)
- Type : client ou prospect
- Pipeline status : new → contacted → quoted → won/lost

**Responsable** : Brendan (backend) + Adrien (UI templates)

---

### 6. Création de Devis Simple
**Pourquoi** : Core métier. Objectif : premier devis en < 2 minutes.

**Spécifications** :
- Formulaire épuré (client, titre, lignes, total)
- Calcul auto (TVA, total HT/TTC)
- Statut : draft → sent → accepted/refused
- Export PDF basique
- **Onboarding** : exemple pré-rempli, skip tutorial

**Responsable** : Brendan (backend + fpdf2) + Adrien (UI + design PDF)

---

### 7. Facturation Basique
**Pourquoi** : Suite logique du devis. L'artisan doit pouvoir facturer.

**Spécifications** :
- Conversion devis → facture en 1 clic
- Statut : pending → paid → late
- Export PDF
- Mentions légales obligatoires

**Responsable** : Brendan (backend + fpdf2) + Adrien (design PDF)

---

## 🟡 SHOULD HAVE (Important)

> Forte valeur ajoutée. À implémenter avant la beta si possible.

### 1. Signature Électronique
**Pourquoi** : Différenciation vs Henrri et Tolteck. Processus sécurisé avec codes de vérification.

**Spécifications** :
- Lien public avec token unique
- Code de vérification pour visualisation
- Code de vérification pour signature
- Journal d'audit (signature_events)
- PDF signé généré

**Responsable** : Brendan (backend) + Adrien (UX flow)

---

### 2. Relances Automatiques
**Pourquoi** : Point faible de Tolteck et Henrri. L'artisan ne veut pas faire du pointage manuel le soir.

**Spécifications** :
- Relances configurables : J+3, J+7, J+15
- Templates d'emails professionnels
- Toggle on/off par facture
- Dashboard : relances à envoyer

**Responsable** : Brendan (backend + SMTP) + Adrien (templates emails)

---

### 3. Gestion des Chantiers (Jobs)
**Pourquoi** : Suivi des interventions. Associe clients, devis, factures, tâches.

**Spécifications** :
- CRUD chantiers avec statuts (planned, ongoing, done)
- Timeline des interventions
- Association client, devis, factures
- Notes et adresse du chantier

**Responsable** : Brendan (backend) + Adrien (UI)

---

### 4. Système de Tâches
**Pourquoi** : Organisation quotidienne. L'artisan doit savoir quoi faire.

**Spécifications** :
- Créer tâche avec priorité (high, normal, low)
- Statut : todo → in_progress → done
- Association facultative à client et/ou chantier
- Date limite optionnelle

**Responsable** : Brendan (backend) + Adrien (UI)

---

### 5. Synchronisation Bancaire (Basique)
**Pourquoi** : Tolteck et Henrri échouent sur le pointage manuel.

**Spécifications** :
- Import CSV bancaire (pas d'API directe pour MVP)
- Rapprochement auto facture/paiement
- Marquer facture comme "paid" automatiquement

**Responsable** : Brendan

---

## 🟢 COULD HAVE (Bonus)

> Améliorations significatives mais peuvent attendre post-beta.

### 1. Saisie Vocale des Devis (IA)
**Pourquoi** : Dictée vocale comme Obat "Rita". L'artisan a les mains sales ou occupées.

**Spécifications** :
- Microphone dans l'interface
- Speech-to-text (Web Speech API ou API externe)
- Pré-remplissage du devis
- Correction manuelle possible

**Responsable** : Adrien (intégration API IA) + Brendan (backend processing)

---

### 2. Import Photo/OCR de Devis Papier
**Pourquoi** : Comme Costructor. L'artisan prend un devis papier en photo → import auto.

**Spécifications** :
- Upload photo devis papier
- OCR (Tesseract ou API cloud)
- Extraction lignes (désignation, quantité, prix)
- Vérification manuelle avant validation

**Responsable** : Adrien (intégration API IA) + Brendan (backend processing)

---

### 3. Application Mobile Native
**Pourquoi** : Henrri et Tolteck échouent sur mobile. UX optimale sur le terrain.

**Spécifications** :
- PWA (Progressive Web App) pour commencer
- Notifications push
- Accès offline amélioré
- Gesture-based UI

**Responsable** : Adrien (PWA) + Brendan (API optimisée)

---

### 4. Dashboard Analytics Avancés
**Pourquoi** : Pour les plans Pro/Enterprise. Visualisation business.

**Spécifications** :
- Graphiques : revenus mensuels, taux conversion devis
- Comparaison mois/mois
- Export données (CSV)
- KPIs personnalisables

**Responsable** : Brendan (API) + Adrien (UI charts)

---

### 5. Portail Client
**Pourquoi** : Le client final peut voir ses devis, factures, signer.

**Spécifications** :
- Lien public pour chaque client
- Vue de ses documents
- Signature en ligne
- Téléchargement PDF

**Responsable** : Brendan (backend) + Adrien (UI)

---

## ⚪ WON'T HAVE (Écarté pour Maintenant)

> Ces fonctionnalités sont **volontairement écartées** car trop lourdes ou pas alignées avec la stratégie "outil de poche".

### 1. Plans 3D et Scans LiDAR
**Pourquoi écarté** :
- Présent chez Houzz Pro (69€/mois) → niche premium
- Fonctionnalités perçues comme "lourdes"
- Ralentissent l'interface mobile
- Ne concernent qu'une minorité d'artisans

**Décision** : ❌ Pas dans Kotaflo. On reste sur du "chiffrage/facturation" pur.

---

### 2. Marketing par Email (Campagnes)
**Pourquoi écarté** :
- Présent chez Houzz Pro → usine à gaz
- Hors métier de l'artisan
- L'artisan veut facturer, pas faire du marketing

**Décision** : ❌ Pas dans Kotaflo. Les emails transactionnels uniquement (relances, devis).

---

### 3. Création de Site Web / Logo
**Pourquoi écarté** :
- Pack Booster d'Obat → hors métier
- L'artisan sur smartphone veut facturer, pas gérer son agence de communication

**Décision** : ❌ Pas dans Kotaflo. Focus core métier uniquement.

---

### 4. Engagement Contractuel (12-24 mois)
**Pourquoi écarté** :
- Source majeure de détestation de la marque (TrustUp Pro, Houzz Pro)
- Contre la philosophie "artisan libre"

**Décision** : ❌ Zéro engagement. Système de tokens = liberté totale.

---

### 5. Modules Comptables Avancés
**Pourquoi écarté** :
- Trop complexe pour MVP
- L'artisan a déjà un comptable ou un outil dédié

**Décision** : ❌ Export CSV pour le comptable suffit pour maintenant.

---

## 📅 Feuille de Route par Sprint

### Sprint 1-2 (Phase 1 — En cours)
- [x] Étude de concurrence ✅
- [ ] Stabilisation auth (Brendan)
- [ ] Audit multi-tenant (Brendan)
- [ ] Charte graphique + Logo (Adrien)

### Sprint 3-5 (Phase 2 — Core MUST)
- [ ] Système de tokens backend (Brendan) 🔴
- [ ] CRUD Clients (Brendan + Adrien) 🔴
- [ ] Création de devis simple (Brendan + Adrien) 🔴
- [ ] Facturation basique (Brendan + Adrien) 🔴
- [ ] Dashboard "Artisan Libre" (Brendan + Adrien) 🔴

### Sprint 6-7 (Phase 3 — SHOULD + Polish)
- [ ] Mode hors-ligne (Brendan) 🔴
- [ ] Signature électronique (Brendan + Adrien) 🟡
- [ ] Relances automatiques (Brendan + Adrien) 🟡
- [ ] Gestion chantiers (Brendan + Adrien) 🟡
- [ ] Système de tâches (Brendan + Adrien) 🟡

### Sprint 8-10 (Phase 4 — Beta)
- [ ] Lancement beta (10 testeurs)
- [ ] Collecte feedbacks
- [ ] Itérations rapides

### Sprint 11+ (Phase 5 — Scale)
- [ ] Saisie vocale IA (Adrien) 🟢
- [ ] Import photo/OCR (Adrien) 🟢
- [ ] PWA mobile (Adrien) 🟢
- [ ] Analytics avancés (Brendan + Adrien) 🟢

---

## 🎯 Métriques de Suivi du Backlog

| Métrique | Cible | Actuel |
|----------|-------|--------|
| MUST HAVE implémentés | 7/7 | 0/7 |
| SHOULD HAVE implémentés | 5/5 | 0/5 |
| Taux complétion Sprint 1-2 | 100% | En cours |
| Bugs critiques ouverts | < 5 | 0 |

---

*Dernière mise à jour : Avril 2026*
*Document vivant — à mettre à jour à chaque sprint*
