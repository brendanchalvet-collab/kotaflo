from backend.models import invoice_model, quote_model

VALID_STATUSES = ("pending", "paid", "late")


def list_invoices(tenant_id, page=1):
    return invoice_model.get_all(tenant_id, page=page), None


def get_invoice(tenant_id, invoice_id):
    invoice = invoice_model.get_by_id(tenant_id, invoice_id)
    if not invoice:
        return None, "Facture introuvable"
    return invoice, None


def create_invoice(tenant_id, data):
    if not data.get("client_id"):
        return None, "client_id requis"
    if not data.get("job_id"):
        return None, "Un projet est obligatoire"
    return invoice_model.create(tenant_id, data), None


def create_deposit_invoice(tenant_id, quote_id, data):
    """Crée une facture d'acompte à partir d'un devis accepté."""
    quote = quote_model.get_by_id(tenant_id, quote_id)
    if not quote:
        return None, "Devis introuvable"
    if quote.get("status") != "accepted":
        return None, "Le devis doit être accepté"

    # Vérifier qu'il n'existe pas déjà une facture d'acompte
    existing = invoice_model.get_by_quote(tenant_id, quote_id)
    if any(inv.get("invoice_type") == "deposit" for inv in existing):
        return None, "Une facture d'acompte existe déjà pour ce devis"

    lines = quote_model.get_lines(quote_id)
    invoice = invoice_model.create_deposit(tenant_id, quote, lines, data)
    return invoice, None


def create_final_invoice(tenant_id, quote_id, data):
    """Crée la facture finale à partir d'un devis, déduit l'acompte si existant."""
    quote = quote_model.get_by_id(tenant_id, quote_id)
    if not quote:
        return None, "Devis introuvable"
    if quote.get("status") != "accepted":
        return None, "Le devis doit être accepté"

    # Vérifier qu'il n'existe pas déjà une facture finale
    existing = invoice_model.get_by_quote(tenant_id, quote_id)
    if any(inv.get("invoice_type") == "final" for inv in existing):
        return None, "Une facture finale existe déjà pour ce devis"

    deposit_invoice = next(
        (inv for inv in existing if inv.get("invoice_type") == "deposit"), None
    )
    invoice = invoice_model.create_final(tenant_id, quote, deposit_invoice, data)
    return invoice, None


def update_invoice_status(tenant_id, invoice_id, status):
    if status not in VALID_STATUSES:
        return None, f"Statut invalide. Valeurs possibles : {VALID_STATUSES}"
    invoice = invoice_model.update_status(tenant_id, invoice_id, status)
    if not invoice:
        return None, "Facture introuvable"
    return invoice, None


def delete_invoice(tenant_id, invoice_id):
    deleted = invoice_model.delete(tenant_id, invoice_id)
    if not deleted:
        return False, "Facture introuvable"
    return True, None
