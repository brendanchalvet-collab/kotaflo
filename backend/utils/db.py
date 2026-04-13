import sqlite3
from config import Config


def _connect(path):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def get_saas_conn():
    """Connexion à la BDD SaaS (utilisateurs, tenants, abonnements)."""
    return _connect(Config.SAAS_DB_PATH)


def get_client_conn():
    """Connexion à la BDD Client (données métier artisan)."""
    return _connect(Config.CLIENT_DB_PATH)


def row(r):
    """Convertit un sqlite3.Row en dict (JSON-serializable)."""
    return dict(r) if r else None


def rows(rs):
    """Convertit une liste de sqlite3.Row en liste de dicts."""
    return [dict(r) for r in rs] if rs else []
