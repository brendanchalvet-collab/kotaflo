// ===== DASHBOARD.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadRecentClients();
    setUserEmail();
    loadProjectClients();
    loadProjects();
});

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

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// ===== USER EMAIL =====
function setUserEmail() {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const email = payload.sub || '';
        const nameEl = document.getElementById('sidebar-name');
        if (nameEl) nameEl.textContent = email;
        const av = document.getElementById('sidebar-avatar');
        if (av && email) av.textContent = email[0].toUpperCase();
        const subtitle = document.getElementById('topbar-subtitle');
        if (subtitle) subtitle.textContent = `Bonjour, ${email.split('@')[0]} !`;
    } catch (_) {}
}

// ===== STATS =====
async function loadStats() {
    try {
        const [clients, leads, quotes, invoices] = await Promise.all([
            apiFetch('/api/clients/').then(r => r.json()),
            apiFetch('/api/leads/').then(r => r.json()),
            apiFetch('/api/quotes/').then(r => r.json()),
            apiFetch('/api/invoices/').then(r => r.json()),
        ]);

        document.getElementById('stat-clients').textContent  = clients.length;
        document.getElementById('stat-leads').textContent    = leads.length;

        const openQuotes = quotes.filter(q => ['draft','sent'].includes(q.status)).length;
        document.getElementById('stat-quotes').textContent   = openQuotes;

        const unpaid = invoices.filter(i => ['pending','late'].includes(i.status)).length;
        document.getElementById('stat-invoices').textContent = unpaid;

    } catch (e) { console.error('Erreur stats', e); }
}

// ===== DERNIERS CLIENTS =====
async function loadRecentClients() {
    try {
        const clients = await apiFetch('/api/clients/').then(r => r.json());
        const tbody = document.getElementById('recent-clients');

        if (!clients.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="text-muted">Aucun client pour l\'instant</td></tr>';
            return;
        }

        tbody.innerHTML = clients.slice(0, 5).map(c => `
            <tr onclick="window.location='/contacts/${c.id}'">
                <td><b>${c.name}</b></td>
                <td class="font-mono" style="font-size:.85rem">${c.phone || '—'}</td>
                <td style="font-size:.85rem">${c.email || '—'}</td>
                <td><span class="badge badge--active">Actif</span></td>
            </tr>
        `).join('');

    } catch (e) { console.error('Erreur clients', e); }
}

// ===== PROJETS : CLIENTS SELECT =====
async function loadProjectClients() {
    const res = await apiFetch('/api/clients/?page=1');
    if (!res) return;
    const clients = await res.json();
    const select  = document.getElementById('proj-client');
    if (!select) return;
    clients.forEach(c => {
        const opt = document.createElement('option');
        opt.value       = c.id;
        opt.textContent = c.name;
        select.appendChild(opt);
    });
}

// ===== PROJETS : CHARGEMENT =====
async function loadProjects() {
    const res = await apiFetch('/api/jobs/');
    if (!res) return;
    const projects = await res.json();
    renderKPIs(projects);
    renderKanban(projects);
}

// ===== PROJETS : KPI =====
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
        `<span style="font-weight:700;font-size:1.2rem;color:var(--color-success,#22c55e)">${counts.done}</span>
         <span style="font-size:.78rem;color:var(--color-gray-400);margin-left:.35rem">Terminés</span>`;
}

// ===== PROJETS : KANBAN =====
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

        const esc = v => (v || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        const notesHtml = p.notes ? `
            <div class="proj-card__notes-toggle" onclick="event.stopPropagation(); toggleProjNotes(this)">
                <span>Notes</span><span class="toggle-arrow">▼</span>
            </div>
            <div class="proj-card__notes-body">${esc(p.notes)}</div>
        ` : '';

        const card = document.createElement('div');
        card.className = 'proj-card';
        card.innerHTML = `
            <div class="proj-card__main">
                <div class="proj-card__title">${esc(p.title)}</div>
                ${p.client_name ? `<div class="proj-card__client"><a href="/contacts/${p.client_id}" onclick="event.stopPropagation()">${esc(p.client_name)}</a></div>` : ''}
                ${dates.length  ? `<div class="proj-card__dates">${dates.join(' ')}</div>` : ''}
                <div style="margin-top:.5rem">
                    <button class="btn btn--ghost btn--sm" onclick="event.stopPropagation(); openProjectModal(${p.id})">Modifier</button>
                </div>
            </div>
            ${notesHtml}
        `;
        card.querySelector('.proj-card__main').addEventListener('click', () => window.location.href = `/projects/${p.id}`);
        col.appendChild(card);
    });

    ['planned', 'ongoing', 'done'].forEach(s => {
        document.getElementById(`empty-${s}`).style.display = counts[s] ? 'none' : '';
        const countEl = document.getElementById(`count-${s}`);
        if (countEl) countEl.textContent = counts[s] || 0;
    });
}

// ===== MODAL PROJET =====
async function openProjectModal(projectId = null) {
    document.getElementById('btn-delete').style.display = projectId ? '' : 'none';
    document.getElementById('proj-id').value = '';
    document.getElementById('proj-title').value = '';
    document.getElementById('proj-client').value = '';
    document.getElementById('proj-status').value = 'planned';
    document.getElementById('proj-start').value = '';
    document.getElementById('proj-end').value = '';
    document.getElementById('proj-address').value = '';
    document.getElementById('proj-notes').value = '';
    document.getElementById('modal-title').textContent = projectId ? 'Modifier le projet' : 'Nouveau projet';

    if (projectId) {
        const res = await apiFetch(`/api/jobs/${projectId}`);
        if (res?.ok) {
            const p = await res.json();
            document.getElementById('proj-id').value      = p.id;
            document.getElementById('proj-title').value   = p.title || '';
            document.getElementById('proj-client').value  = p.client_id || '';
            document.getElementById('proj-status').value  = p.status || 'planned';
            document.getElementById('proj-start').value   = p.start_date?.slice(0, 10) || '';
            document.getElementById('proj-end').value     = p.end_date?.slice(0, 10) || '';
            document.getElementById('proj-address').value = p.address || '';
            document.getElementById('proj-notes').value   = p.notes || '';
        }
    }

    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION PROJET =====
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
        const err = await res?.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== SUPPRESSION PROJET =====
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

// ===== TOGGLE NOTES =====
function toggleProjNotes(toggleEl) {
    const body  = toggleEl.nextElementSibling;
    const arrow = toggleEl.querySelector('.toggle-arrow');
    const open  = body.classList.toggle('open');
    arrow.textContent = open ? '▲' : '▼';
}
