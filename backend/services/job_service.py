from backend.models import job_model

VALID_STATUSES = ("planned", "ongoing", "done")


def list_jobs(tenant_id, client_id=None, page=1):
    return job_model.get_all(tenant_id, client_id=client_id, page=page), None


def get_job(tenant_id, job_id):
    job = job_model.get_by_id(tenant_id, job_id)
    if not job:
        return None, "Projet introuvable"
    return job, None


def create_job(tenant_id, data):
    if not data.get("title"):
        return None, "Le titre est requis"
    return job_model.create(tenant_id, data), None


def update_job(tenant_id, job_id, data):
    if not data.get("title"):
        return None, "Le titre est requis"
    job = job_model.update(tenant_id, job_id, data)
    if not job:
        return None, "Projet introuvable"
    return job, None


def delete_job(tenant_id, job_id):
    deleted = job_model.delete(tenant_id, job_id)
    if not deleted:
        return False, "Projet introuvable"
    return True, None
