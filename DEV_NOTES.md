# DEV NOTES — Kotaflo

## 🚨 Dev Bypass Active

Routes temporaires pour contourner bug auth Firebase (Brendan en train de fix) :

- `GET /dev-login` → génère un JWT et pose un cookie, te log automatiquement
- `GET /dev-dashboard` → redirige vers `/dashboard` (protégé JWT, sert à vérifier que le token fonctionne)

**À SUPPRIMER dès que `backend/services/auth_service.py` est réparé.**

Date ajout : 2026-04-28

### Comment utiliser

1. Lance le serveur : `python app.py`
2. Ouvre `http://localhost:5000/dev-login` dans le navigateur
3. Copie le `access_token` de la réponse JSON
4. Dans la console du navigateur : `localStorage.setItem('access_token', '<token>')`
5. Va sur `http://localhost:5000/dashboard`
