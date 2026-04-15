# 🚀 Stratégie Tarifaire Kotaflo

---

## 1. Principe : Local-First + IA Cloud pour les devis

### Local (on-device) — gratuit, 0 token
**OCR et reconnaissance vocale** → 100% dans le navigateur du téléphone.
- Zéro coût pour Kotaflo
- Zéro dépendance réseau (fonctionne en sous-sol / zones blanches)
- Données sensibles ne quittent pas l'appareil
- L'artisan dicte ou prend en photo → le texte apparaît localement

### Cloud (IA via API) — consomme des tokens
**L'IA cloud ne fait pas rien toute seule — elle génère le devis via API.**
- L'artisan dicte (voix on-device) → texte brut → envoyé à l'IA cloud → l'IA structure le devis suivant un modèle (lignes, désignation, quantités, prix, TVA) → devis complet généré
- Sans l'IA cloud, l'artisan peut quand même remplir son devis manuellement à partir du texte brut local
- **Modèle utilisé** : Gemini Flash (suffisant, pas cher, pas besoin de GPT-4)

**Cloud (serveur Kotaflo)** → utilisé pour :
- **Génération de devis via IA** (API Gemini Flash) — structure le texte brut en devis professionnel
- Synchronisation des données (devis, factures, clients) quand le réseau revient
- Signature électronique (vérification + envoi code SMS/email)
- Envoi de devis/factures par email (SMTP)
- Relances automatiques

---

## 2. Modèle de Tokens

### Principe
- **Usage local (OCR, saisie vocale, brouillon)** = **0 token** — gratuit, illimité
- **Usage cloud** = consomme des tokens :
  - **Génération de devis par IA** = **1 token** (l'IA structure le devis via API)
  - Signature électronique = **1 token**
  - Envoi devis/facture par email = **1 token**
  - Relance automatique = **0.5 token**

### Pourquoi ça marche
- L'artisan peut bosser **sans jamais dépenser** (brouillon local, saisie manuelle)
- S'il veut que l'IA génère le devis tout seul → **1 token**
- Les mois creux (congés, intempéries) = facture minimale
- Pas d'abonnement fixe injustifié

---

## 3. Architecture des Plans

| Plan | Cible | Modèle | Inclus |
|------|-------|--------|--------|
| **Free** | Découverte | Gratuit | Mode hors-ligne, gestion clients, 5 devis/mois (brouillon local uniquement — pas d'IA) |
| **Pack Tokens** | Artisans agiles | Pay-as-you-go | Achat de tokens pour IA devis, signature, envoi email, relances. OCR/voix = toujours gratuit |
| **Pro** | Volume constant | Mensuel fixe (~29-49€) | Tokens inclus (ex: 30/mois), génération IA de devis, signature, relances auto, exports comptables |
| **Enterprise** | Multi-utilisateurs | Mensuel (~79-99€) | Tout Pro + multi-users, API, support dédié, custom branding |

---

## 4. Comparatif vs Concurrents

| Critère | Leaders (Obat, Tolteck) | Kotaflo |
|---------|------------------------|---------|
| Connexion | Obligatoire (cloud-dependent) | **Optionnelle** — local-first, synchro quand réseau dispo |
| Engagement | 12-24 mois | **Zéro engagement** |
| Coût | Fixe (25-50€/mois) | **Variable** (tokens) ou fixe (Pro) |
| Onboarding | 30 min (formation) | **< 2 min** (intuitif) |
| OCR / Voix | Cloud (coûteux, besoin réseau) | **On-device** (gratuit, offline) |
| Génération devis | Manuelle ou IA cloud obligatoire | **Au choix** : manuelle (gratuit) ou IA cloud (1 token) |

---

## 5. Priorités Techniques (Backlog Brendan)

### 🛠️ Sync "Zero-Loss"
- Sauvegarde immédiate en base locale
- Sync automatique dès réseau disponible
- Résolution de conflits auto (dernière modif wins)

### 🪙 Moteur de Tokens
- **Usage local = 0 token** (OCR, voix, brouillon → tout on-device)
- **Usage cloud = décompte tokens** (IA génération devis, signature, envoi email, relances)
- Interface qui montre le solde en temps réel
- Blocage élégant des features cloud si solde = 0 (sans bloquer la saisie locale)

### 🤖 IA Génération Devis (API Gemini Flash)
- Texte brut (dicté ou OCR local) → envoyé à l'API → l'IA structure suivant un modèle de devis
- Champs générés : lignes de devis, désignation, quantités, prix unitaire, TVA, total HT/TTC
- L'artisan peut corriger/modifier avant validation
- Coût : ~$0.001-0.005 par appel Gemini Flash → on peut vendre 1 token pour ~0.10-0.30€

### 📱 Interface dynamique
- Features cloud grisées si pas de tokens / pas de réseau
- Indicateur clair : 📴 Hors-ligne vs 📡 Connecté
- Compteur de tokens visible en permanence

---

## 6. Argumentaire Marketing

| Message | Explication |
|---------|-------------|
| **"Vous ne travaillez pas ? Vous ne payez pas."** | Modèle tokens vs abonnements fixes |
| **"Zéro engagement"** | On ne retient pas par le contrat, mais par l'utilité |
| **"L'IA qui bosse partout, même sans réseau"** | OCR et voix on-device, IA cloud quand réseau dispo |
| **"Premier devis en < 2 min"** | Radical simplicity vs 30 min d'onboarding chez Tolteck |
| **"L'IA au service du devis, pas l'inverse"** | L'IA génère le devis via API, mais l'artisan garde le contrôle total |
