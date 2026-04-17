# 🛠️ Stratégie Kotaflo : Options de Monétisation & Architecture

## 1. Principe Technique : "Local-First, Cloud-Smart"

L'objectif est de réduire nos coûts serveurs à presque 0€ pour maximiser la marge sur les tokens.

### Traitement Local (Gratuit / 0€ API)
- **Dictée vocale** : Utilisation des API natives du téléphone (iOS/Android).
- **OCR (Photo)** : Extraction de texte via Google ML Kit ou Apple Vision (en local).
- **Stockage** : SQLite local (Zéro perte de données en zone blanche).

### Traitement Cloud (Payant / API Bas coût)
- **Moteur de Structure** : Envoi du texte brut (souvent mal orthographié/mal formé) à une API type Gemini Flash (via Groq pour la vitesse) pour transformer le brouillon en devis structuré (Lignes, TVA, Totaux).
- **Services Connectés** : Envoi mail (SMTP), Signature électronique, Relances.

---

## 2. Options de Monétisation (À trancher avec Brendan)

L'idée est d'éviter les micro-paiements polluants (30 centimes par-ci par-là) et de simplifier la compréhension. **1 Devis Complet = 1 Token.**

### Option A : Le modèle "Pack de Crédits" (Recommandé)
- **Fonctionnement** : L'artisan achète des packs (10, 50 ou 100 tokens).
- **Consommation** : 1 token débité uniquement quand le devis est "Généré par l'IA + Envoyé".
- **Avantages** : Une seule transaction bancaire pour l'artisan. Trésorerie d'avance pour nous.

### Option B : Le modèle "Seuil Freemium"
- **Fonctionnement** : 5 devis gratuits par mois (pour les petits artisans).
- **Au-delà** : Passage obligatoire à un pack de tokens ou un abonnement léger.
- **Avantages** : On capte tout le marché des débutants, mais on monétise dès qu'ils ont une vraie activité.

---

## 3. Parcours Utilisateur Automatisé (Le "Flow")

- **Capture** : L'artisan parle ou prend une photo (Local).
- **Sync** : Dès qu'il y a du réseau, les données montent au serveur (Zero Loss).
- **Magie IA** : L'API structure le document proprement.
- **Action** : Envoi automatique pour signature + programmation des relances si pas signé sous 48h.

---

## 4. Priorités de Développement (MVP)

- **Moteur Offline** : Sauvegarde locale prioritaire.
- **Connecteur API** : Liaison avec Gemini Flash/Groq pour le nettoyage de texte.
- **Système de Tokens** : Gestion du solde et blocage des fonctions Cloud si solde = 0.