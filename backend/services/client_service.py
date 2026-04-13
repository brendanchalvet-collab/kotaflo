from backend.models import client_model

VALID_PIPELINE = ("new", "contacted", "quoted", "won", "lost")


def list_clients(tenant_id, page=1, contact_type=None):
    return client_model.get_all(tenant_id, page=page, contact_type=contact_type), None


def get_client(tenant_id, client_id):
    client = client_model.get_by_id(tenant_id, client_id)
    if not client:
        return None, "Contact introuvable"
    return client, None


def create_client(tenant_id, data):
    if not data.get("name"):
        return None, "Le nom est requis"
    return client_model.create(tenant_id, data), None


def update_client(tenant_id, client_id, data):
    if not data.get("name"):
        return None, "Le nom est requis"
    client = client_model.update(tenant_id, client_id, data)
    if not client:
        return None, "Contact introuvable"
    return client, None


def update_pipeline_status(tenant_id, client_id, pipeline_status):
    if pipeline_status not in VALID_PIPELINE:
        return None, f"Statut invalide. Valeurs possibles : {VALID_PIPELINE}"
    client = client_model.update_pipeline_status(tenant_id, client_id, pipeline_status)
    if not client:
        return None, "Contact introuvable"
    return client, None


def delete_client(tenant_id, client_id):
    deleted = client_model.delete(tenant_id, client_id)
    if not deleted:
        return False, "Contact introuvable"
    return True, None
