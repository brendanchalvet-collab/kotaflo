// ===== LEADS.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

let currentLeadId  = null;
let currentLeadObj = null;

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => loadLeads());

// ===== CHARGEMENT PIPELINE =====
async function loadLeads() {
    const res = await apiFetch('/api/leads/');
    if (!res) return;
    const data = await res.json();
    renderPipeline(data);
}

// ===== RENDU KANBAN =====
function renderPipeline(leads) {
    ['new', 'contacted', 'quoted', 'won', 'lost'].forEach(status => {
        const col = document.getElementById(`col-${status}`);
        col.querySelectorAll('.pipeline__card').forEach(el => el.remove());
    });

    leads.forEach(lead => {
        const col = document.getElementById(`col-${lead.status}`);
        if (!col) return;

        const card = document.createElement('div');
        card.className = 'pipeline__card';
        card.innerHTML = `
            <div style="font-weight:600">${lead.name || lead.client_name || 'Sans nom'}</div>
            ${lead.phone ? `<div style="font-size:.8rem; color:var(--color-gray-500); margin-top:.1rem">${lead.phone}</div>` : ''}
            ${lead.acquisition_source ? `<div style="font-size:.75rem; color:var(--color-gray-400); margin-top:.1rem">${lead.acquisition_source}</div>` : ''}
        `;
        card.onclick = () => openDetailModal(lead);
        col.appendChild(card);
    });
}

// ===== MODAL CRÉATION =====
function openModal() {
    document.getElementById('lead-modal-title').textContent = 'Nouveau prospect';
    document.getElementById('lead-id').value          = '';
    document.getElementById('lead-name').value        = '';
    document.getElementById('lead-phone').value       = '';
    document.getElementById('lead-email').value       = '';
    document.getElementById('lead-address').value     = '';
    document.getElementById('lead-acquisition').value = '';
    document.getElementById('lead-notes').value       = '';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// ===== MODAL MODIFICATION =====
function editCurrentLead() {
    if (!currentLeadObj) return;
    closeDetailModal();

    const lead = currentLeadObj;
    document.getElementById('lead-modal-title').textContent = 'Modifier le prospect';
    document.getElementById('lead-id').value          = lead.id;
    document.getElementById('lead-name').value        = lead.name || '';
    document.getElementById('lead-phone').value       = lead.phone || '';
    document.getElementById('lead-email').value       = lead.email || '';
    document.getElementById('lead-address').value     = lead.address || '';
    document.getElementById('lead-acquisition').value = lead.acquisition_source || '';
    document.getElementById('lead-notes').value       = lead.notes || '';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION =====
async function handleSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('lead-id').value;
    const body = {
        name:               document.getElementById('lead-name').value,
        phone:              document.getElementById('lead-phone').value,
        email:              document.getElementById('lead-email').value,
        address:            document.getElementById('lead-address').value,
        acquisition_source: document.getElementById('lead-acquisition').value,
        notes:              document.getElementById('lead-notes').value,
        status:             'new',
    };

    const url    = id ? `/api/leads/${id}` : '/api/leads/';
    const method = id ? 'PUT' : 'POST';

    const res = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (!res) return;

    if (res.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast(id ? 'Prospect mis à jour' : 'Prospect ajouté', 'success');
        loadLeads();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== MODAL DETAIL (statut + infos) =====
function openDetailModal(lead) {
    currentLeadId  = lead.id;
    currentLeadObj = lead;

    document.getElementById('detail-name').textContent = lead.name || lead.client_name || 'Prospect';

    const parts = [];
    if (lead.phone)              parts.push(`Tél : ${lead.phone}`);
    if (lead.email)              parts.push(`Email : ${lead.email}`);
    if (lead.address)            parts.push(`Adresse : ${lead.address}`);
    if (lead.acquisition_source) parts.push(`Via : ${lead.acquisition_source}`);
    if (lead.notes)              parts.push(`Notes : ${lead.notes}`);
    document.getElementById('detail-info').innerHTML = parts.join('<br>');

    document.getElementById('detail-status').value = lead.status;
    document.getElementById('modal-detail-overlay').classList.remove('hidden');
}

function closeDetailModal(event) {
    if (event && event.target !== document.getElementById('modal-detail-overlay')) return;
    document.getElementById('modal-detail-overlay').classList.add('hidden');
}

async function saveStatus() {
    const status = document.getElementById('detail-status').value;
    const res = await apiFetch(`/api/leads/${currentLeadId}/status`, {
        method: 'PATCH', body: JSON.stringify({ status }),
    });
    if (res?.ok) {
        closeDetailModal();
        showToast('Statut mis à jour', 'success');
        loadLeads();
    } else {
        showToast('Erreur', 'danger');
    }
}

async function deleteLead() {
    if (!confirm('Supprimer ce prospect ?')) return;
    const res = await apiFetch(`/api/leads/${currentLeadId}`, { method: 'DELETE' });
    if (res?.ok) {
        closeDetailModal();
        showToast('Prospect supprimé');
        loadLeads();
    }
}
