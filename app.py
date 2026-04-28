from flask import Flask, redirect, render_template, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import Config
from init_db import migrate
from backend.utils.firebase_utils import init_firebase
from backend.routes.auth import auth_bp
from backend.routes.clients import clients_bp
from backend.routes.leads import leads_bp
from backend.routes.quotes import quotes_bp
from backend.routes.invoices import invoices_bp
from backend.routes.profile import profile_bp
from backend.routes.jobs import jobs_bp
from backend.routes.google_auth import google_auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.quote_access import quote_access_bp

# ===== MIGRATIONS =====
migrate()

# ===== FIREBASE =====
init_firebase()

# ===== INIT APP =====
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

CORS(app)
JWTManager(app)

# ===== ROUTES API =====
app.register_blueprint(auth_bp,    url_prefix="/api/auth")
app.register_blueprint(clients_bp, url_prefix="/api/clients")
app.register_blueprint(leads_bp,   url_prefix="/api/leads")
app.register_blueprint(quotes_bp,  url_prefix="/api/quotes")
app.register_blueprint(invoices_bp, url_prefix="/api/invoices")
app.register_blueprint(profile_bp,  url_prefix="/api/profile")
app.register_blueprint(jobs_bp,        url_prefix="/api/jobs")
app.register_blueprint(google_auth_bp, url_prefix="/api/google")
app.register_blueprint(tasks_bp,         url_prefix="/api/tasks")
app.register_blueprint(quote_access_bp,  url_prefix="/api/quote-access")


# ===== ROUTES FRONTEND (serve HTML) =====
@app.route("/")
def landing_page():
    return render_template("landing.html")


@app.route("/login")
def login_page():
    return send_from_directory("templates", "login.html")


@app.route("/dashboard")
def dashboard_page():
    return send_from_directory("templates", "dashboard.html")


@app.route("/clients")
def clients_page():
    return send_from_directory("templates", "clients.html")


@app.route("/contacts/<int:client_id>")
def contact_history_page(client_id):
    return send_from_directory("templates", "contact_history.html")


@app.route("/leads")
def leads_page():
    return redirect("/clients")


@app.route("/quotes")
def quotes_page():
    return send_from_directory("templates", "quotes.html")


@app.route("/invoices")
def invoices_page():
    return send_from_directory("templates", "invoices.html")


@app.route("/tasks")
def tasks_page():
    return send_from_directory("templates", "tasks.html")


@app.route("/projects")
def projects_page():
    return send_from_directory("templates", "projects.html")


@app.route("/projects/<int:job_id>")
def project_detail_page(job_id):
    return send_from_directory("templates", "project_detail.html")


@app.route("/pricing")
def pricing_page():
    return render_template("pricing.html")


@app.route("/trial")
def trial_page():
    return render_template("trial.html")


@app.route("/checkout-packs")
def checkout_packs_page():
    return render_template("checkout_packs.html")


@app.route("/checkout-pro")
def checkout_pro_page():
    return render_template("checkout_pro.html")


@app.route("/profile")
def profile_page():
    return send_from_directory("templates", "profile.html")


# Page publique de signature (aucune auth requise — token lu par le JS)
@app.route("/quote/<access_token>")
def quote_sign_page(access_token):  # noqa: ARG001
    return send_from_directory("templates", "quote_sign.html")


if __name__ == "__main__":
    app.run(debug=Config.DEBUG, port=5000)
