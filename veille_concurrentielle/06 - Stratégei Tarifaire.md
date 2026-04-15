# 🚀 Stratégie Tarifaire Kotaflo

---

## 1. Principe : Local-First + Cloud pour le reste

**OCR et reconnaissance vocale** → 100% on-device (on-device via le navigateur du téléphone).
- Zéro coût pour Kotaflo
- Zéro dépendance réseau (fonctionne en sous-sol / zones blanches)
- Données sensibles ne quittent pas l'appareil

**Cloud (serveur Kotaflo)** → utilisé uniquement pour :
- Synchronisation des données (devis, factures, clients) quand le réseau revient
- Signature électronique (vérification + envoi code SMS/email)
- Envoi de devis/factures par email (SMTP)
- Relances automatiques
- IA cloud si besoin ponctuel (ex: Gemini Flash pour analyse complexe)

---

## 2. Modèle de Tokens

### Principe
- **Usage local (OCR, saisie vocale)** = **0 token** — gratuit, illimité, aucun coût
- **Usage cloud** = consomme des tokens :
  - Signature électronique = **1 token**
  - Envoi devis/facture par email = **1 token**
  - Relance automatique = **0.5 token**
  - IA cloud (Gemini Flash, usage ponctuel) = **1-2 tokens**

### Pourquoi ça marche
- L'artisan paie **seulement quand il utilise** des services cloud
- Les mois creux (congés, intempéries) = facture minimale
- Pas d'abonnement fixe injustifié

---

## 3. Architecture des Plans

| Plan | Cible | Modèle | Inclus |
|------|-------|--------|--------|
| **Free** | Découverte | Gratuit | Mode hors-ligne, gestion clients, 5 devis/mois (brouillon local) |
| **Pack Tokens** | Artisans agiles | Pay-as-you-go | Signature élec, envoi email, relances auto. OCR/voix = toujours gratuit |
| **Pro** | Volume constant | Mensuel fixe (~29-49€) | Tokens inclus (ex: 30/mois), signature illimitée, relances auto, exports comptables |
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

---

## 5. Priorités Techniques (Backlog Brendan)

### 🛠️ Sync "Zero-Loss"
- Sauvegarde immédiate en base locale
- Sync automatique dès réseau disponible
- Résolution de conflits auto (dernière modif wins)

### 🪙 Moteur de Tokens
- **Usage local = 0 token** (OCR, voix → tout on-device)
- **Usage cloud = décompte tokens** (signature, envoi email, relances)
- Interface qui montre le solde en temps réel
- Blocage élégant des features cloud si solde = 0 (sans bloquer la saisie locale)

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
| **"L'IA qui n'a pas besoin de réseau"** | OCR et voix on-device, fonctionnent partout |
| **"Premier devis en < 2 min"** | Radical simplicity vs 30 min d'onboarding chez Tolteck |