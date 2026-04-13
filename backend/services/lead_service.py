from backend.models import lead_model

VALID_STATUSES = ("new", "contacted", "quoted", "won", "lost")


def list_leads(tenant_id, page=1):
    return lead_model.get_all(tenant_id, page=page), None


def get_lead(tenant_id, lead_id):
    lead = lead_model.get_by_id(tenant_id, lead_id)
    if not lead:
        return None, "Lead introuvable"
    return lead, None


def create_lead(tenant_id, data):
    return lead_model.create(tenant_id, data), None


def update_lead(tenant_id, lead_id, data):
    lead = lead_model.update(tenant_id, lead_id, data)
    if not lead:
        return None, "Lead introuvable"
    return lead, None


def update_lead_status(tenant_id, lead_id, status):
    if status not in VALID_STATUSES:
        return None, f"Statut invalide. Valeurs possibles : {VALID_STATUSES}"
    lead = lead_model.update_status(tenant_id, lead_id, status)
    if not lead:
        return None, "Lead introuvable"
    return lead, None


def delete_lead(tenant_id, lead_id):
    deleted = lead_model.delete(tenant_id, lead_id)
    if not deleted:
        return False, "Lead introuvable"
    return True, None
