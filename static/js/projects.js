// ===== PROJECTS.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

function validateProjDates() {
    const start = document.getElementById('proj-start').value;
    const end   = document.getElementById('proj-end').value;
    if (end && start && end < start) {
        alert('La date de fin doit être après la date de début');
        document.getElementById('proj-end').value = '';
    }
}

let allProjects = [];

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function formatDate(str) {
    if (!str) return null;
    return new Date(str).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadClients();
    loadProjects();
});

// ===== CLIENTS (pour le select) =====
async function loadClients() {
    const res = await apiFetch('/api/clients/?page=1');
    if (!res) return;
    const clients = await res.json();
    const select  = document.getElementById('proj-client');
    clients.forEach(c => {
        const opt = document.createElement('option');
        opt.value       = c.id;
        opt.textContent = c.name;
        select.appendChild(opt);
    });
}

// ===== CHARGEMENT PROJETS =====
async function loadProjects() {
    const res = await apiFetch('/api/jobs/');
    if (!res) return;
    allProjects = await res.json();
    renderKanban(allProjects);
    renderKPIs(allProjects);
}

// ===== KPI =====
function renderKPIs(projects) {
    const counts = { planned: 0, ongoing: 0, done: 0 };
    projects.forEach(p => { if (counts[p.status] !== undefined) counts[p.status]++; });

    document.getElementById('kpi-planned').innerHTML =
        `<span style="font-weight:700;font-size:1.2rem">${counts.planned}</span>
         <span style="font-size:.78rem;color:var(--color-gray-400);margin-left:.35rem">Planifiés</span>`;
    document.getElementById('kpi-ongoing').innerHTML =
        `<span style="font-weight:700;font-size:1.2rem;color:var(--color-primary)">${counts.ongoing}</span>
         <span style="font-size:.78rem;color:var(--color-gray-400);margin-left:.35rem">En cours</span>`;
    document.getElementById('kpi-done').innerHTML =
        `<span style="font-weight:700;font-size:1.2rem;color:var(--color-success)">${counts.done}</span>
         <span style="font-size:.78rem;color:var(--color-gray-400);margin-left:.35rem">Terminés</span>`;
}

// ===== KANBAN =====
function renderKanban(projects) {
    ['planned', 'ongoing', 'done'].forEach(s => {
        document.getElementById(`col-${s}`).innerHTML = '';
    });

    const counts = { planned: 0, ongoing: 0, done: 0 };

    projects.forEach(p => {
        const col = document.getElementById(`col-${p.status}`);
        if (!col) return;
        counts[p.status] = (counts[p.status] || 0) + 1;

        const dates = [];
        if (p.start_date) dates.push(`Du ${formatDate(p.start_date)}`);
        if (p.end_date)   dates.push(`au ${formatDate(p.end_date)}`);

        const card = document.createElement('div');
        card.className = 'proj-card';
        const notesHtml = p.notes ? `
            <div class="proj-card__notes-toggle" onclick="event.stopPropagation(); toggleProjNotes(this)">
                <span>💬 Notes</span><span class="toggle-arrow">▼</span>
            </div>
            <div class="proj-card__notes-body">${p.notes.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
        ` : '';

        card.innerHTML = `
            <div class="proj-card__main" style="cursor:pointer">
                <div class="proj-card__title">${p.title}</div>
                ${p.client_name ? `<div class="proj-card__client">👤 <a href="/contacts/${p.client_id}" onclick="event.stopPropagation()">${p.client_name}</a></div>` : ''}
                ${dates.length  ? `<div class="proj-card__dates">📅 ${dates.join(' ')}</div>` : ''}
            </div>
            ${notesHtml}
        `;
        card.querySelector('.proj-card__main').onclick = () => window.location.href = `/projects/${p.id}`;
        col.appendChild(card);
    });

    // Afficher/masquer les "Aucun"
    ['planned', 'ongoing', 'done'].forEach(s => {
        document.getElementById(`empty-${s}`).style.display =
            counts[s] ? 'none' : '';
    });
}

// ===== MODAL =====
function openModal(project = null) {
    document.getElementById('modal-title').textContent  = project ? 'Modifier le projet' : 'Nouveau projet';
    document.getElementById('proj-id').value            = project ? project.id : '';
    document.getElementById('proj-title').value         = project ? project.title : '';
    document.getElementById('proj-client').value        = project?.client_id || '';
    document.getElementById('proj-status').value        = project ? project.status : 'planned';
    document.getElementById('proj-start').value         = project?.start_date?.slice(0, 10) || '';
    document.getElementById('proj-end').value           = project?.end_date?.slice(0, 10)   || '';
    document.getElementById('proj-address').value       = project ? (project.address || '') : '';
    document.getElementById('proj-notes').value         = project ? (project.notes || '') : '';
    document.getElementById('btn-delete').style.display = project ? '' : 'none';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION =====
async function handleSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('proj-id').value;
    const body = {
        client_id:  document.getElementById('proj-client').value  || null,
        title:      document.getElementById('proj-title').value,
        status:     document.getElementById('proj-status').value,
        start_date: document.getElementById('proj-start').value   || null,
        end_date:   document.getElementById('proj-end').value     || null,
        address:    document.getElementById('proj-address').value  || null,
        notes:      document.getElementById('proj-notes').value,
    };

    const url    = id ? `/api/jobs/${id}` : '/api/jobs/';
    const method = id ? 'PUT' : 'POST';
    const res    = await apiFetch(url, { method, body: JSON.stringify(body) });

    if (res?.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast(id ? 'Projet mis à jour' : 'Projet créé', 'success');
        loadProjects();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== SUPPRESSION =====
async function deleteProject() {
    const id = document.getElementById('proj-id').value;
    if (!id || !confirm('Supprimer ce projet ?')) return;
    const res = await apiFetch(`/api/jobs/${id}`, { method: 'DELETE' });
    if (res?.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast('Projet supprimé');
        loadProjects();
    } else { showToast('Erreur', 'danger'); }
}

// ===== TOGGLE NOTES PROJET =====
function toggleProjNotes(toggleEl) {
    const body  = toggleEl.nextElementSibling;
    const arrow = toggleEl.querySelector('.toggle-arrow');
    const open  = body.classList.toggle('open');
    arrow.textContent = open ? '▲' : '▼';
}
