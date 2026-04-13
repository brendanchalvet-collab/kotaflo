import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Flask
    SECRET_KEY     = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG          = os.getenv("DEBUG", "true").lower() == "true"

    # JWT
    JWT_SECRET_KEY          = os.getenv("JWT_SECRET_KEY", "jwt-change-me-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 28800  # 8 heures

    # SQLite — fichiers locaux
    SAAS_DB_PATH   = os.getenv("SAAS_DB_PATH",   "artisans_saas.db")
    CLIENT_DB_PATH = os.getenv("CLIENT_DB_PATH", "artisans_client.db")

    # Gmail API — OAuth2
    GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID",     "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI",  "http://localhost:5000/api/google/callback")

    # SMTP — Envoi d'emails (devis + OTP)
    SMTP_HOST     = os.getenv("SMTP_HOST",     "smtp.gmail.com")
    SMTP_PORT     = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER     = os.getenv("SMTP_USER",     "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM     = os.getenv("SMTP_FROM",     "")
