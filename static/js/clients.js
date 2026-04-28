// ===== CLIENTS.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

let currentPage = 1;
let _allClients   = [];      // cache complet pour la recherche
let _jobsByClient = {};      // projets groupés par client_id

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function esc(val) {
    return (val || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

const STATUS_ICON = { planned: '📅', ongoing: '⚙️', done: '✅' };

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([loadJobs(), loadClients()]);

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const el = document.getElementById('sidebar-name');
        if (el) el.textContent = payload.sub || '';
        const av = document.getElementById('sidebar-avatar');
        if (av && payload.sub) av.textContent = payload.sub[0].toUpperCase();
    } catch (_) {}
});

// ===== CHARGEMENT DES PROJETS =====
async function loadJobs() {
    const res = await apiFetch('/api/jobs/');
    if (!res) return;
    const jobs = await res.json();
    _jobsByClient = {};
    jobs.forEach(j => {
        if (!j.client_id) return;
        if (!_jobsByClient[j.client_id]) _jobsByClient[j.client_id] = [];
        _jobsByClient[j.client_id].push(j);
    });
}

// ===== CHARGEMENT DES CLIENTS =====
async function loadClients(page = 1) {
    currentPage = page;
    const res = await apiFetch(`/api/clients/?page=${page}`);
    if (!res) return;
    _allClients = (await res.json()).sort((a, b) =>
        (a.name || '').localeCompare(b.name || '', 'fr', { sensitivity: 'base' })
    );
    renderCards(_allClients);
}

// ===== RECHERCHE =====
function filterClients(query) {
    const q = query.toLowerCase().trim();
    if (!q) {
        renderCards(_allClients);
        return;
    }
    const filtered = _allClients.filter(c =>
        (c.name  || '').toLowerCase().includes(q) ||
        (c.email || '').toLowerCase().includes(q) ||
        (c.phone || '').toLowerCase().includes(q)
    );
    renderCards(filtered);
}

// ===== RENDU CARTES =====
function renderCards(clients) {
    const list = document.getElementById('clients-list');

    if (!clients.length) {
        list.innerHTML = '<div class="text-muted">Aucun client.</div>';
        return;
    }

    list.innerHTML = '';

    clients.forEach(c => {
        const jobs = _jobsByClient[c.id] || [];

        // Ligne infos (phone / email / acquisition)
        const infoParts = [];
        if (c.phone)              infoParts.push(`<span><a href="tel:${esc(c.phone)}" onclick="event.stopPropagation()">${esc(c.phone)}</a></span>`);
        if (c.email)              infoParts.push(`<span>${esc(c.email)}</span>`);
        if (c.acquisition_source) infoParts.push(`<span>Via ${esc(c.acquisition_source)}</span>`);

        // Projets sous forme de pills
        const pillsHtml = jobs.map(j => `
            <a class="proj-pill proj-pill--${j.status}" href="/projects/${j.id}">
                ${esc(j.title)}
            </a>
        `).join('');

        const projectsBlock = jobs.length
            ? `<div class="client-card__projects">
                   <span class="client-card__projects-label">Projets</span>
                   ${pillsHtml}
               </div>`
            : '';

        // Section commentaires (masquée par défaut, toggle au clic)
        const notesBlock = c.notes
            ? `<div class="card-notes-toggle" onclick="toggleNotes(this)">
                   <span>💬 Commentaires</span><span class="toggle-arrow">▼</span>
               </div>
               <div class="card-notes-body">${esc(c.notes)}</div>`
            : '';

        const card = document.createElement('div');
        card.className = 'client-card';
        card.innerHTML = `
            <div class="client-card__main" onclick="window.location='/contacts/${c.id}'">
                <div style="flex:1;min-width:0">
                    <div class="client-card__name">${esc(c.name)}</div>
                    ${infoParts.length ? `<div class="client-card__info">${infoParts.join('')}</div>` : ''}
                </div>
                <div class="client-card__actions">
                    <button class="btn btn--ghost btn--sm" onclick="event.stopPropagation(); openEditModal(${c.id})">Modifier</button>
                    <span style="font-size:.82rem;color:var(--color-primary)">Voir →</span>
                </div>
            </div>
            ${projectsBlock}
            ${notesBlock}`;

        list.appendChild(card);
    });
}

// ===== MODAL CRÉATION =====
function openModal() {
    document.getElementById('modal-title').textContent   = 'Nouveau client';
    document.getElementById('client-id').value           = '';
    document.getElementById('client-name').value         = '';
    document.getElementById('client-phone').value        = '';
    document.getElementById('client-email').value        = '';
    document.getElementById('client-address').value      = '';

    document.getElementById('client-notes').value        = '';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// ===== MODAL MODIFICATION =====
async function openEditModal(clientId) {
    const res = await apiFetch(`/api/clients/${clientId}`);
    if (!res?.ok) return;
    const c = await res.json();

    document.getElementById('modal-title').textContent   = 'Modifier le client';
    document.getElementById('client-id').value           = c.id;
    document.getElementById('client-name').value         = c.name || '';
    document.getElementById('client-phone').value        = c.phone || '';
    document.getElementById('client-email').value        = c.email || '';
    document.getElementById('client-address').value      = c.address || '';

    document.getElementById('client-notes').value        = c.notes || '';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION =====
async function handleSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('client-id').value;
    const body = {
        name:               document.getElementById('client-name').value,
        phone:              document.getElementById('client-phone').value,
        email:              document.getElementById('client-email').value,
        address:            document.getElementById('client-address').value,

        notes:              document.getElementById('client-notes').value,
        contact_type:       'client',
    };

    const url    = id ? `/api/clients/${id}` : '/api/clients/';
    const method = id ? 'PUT' : 'POST';

    const res = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (!res) return;

    if (res.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast(id ? 'Client mis à jour' : 'Client créé', 'success');
        await loadJobs();
        loadClients(currentPage);
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== TOGGLE COMMENTAIRES =====
function toggleNotes(toggleEl) {
    const body  = toggleEl.nextElementSibling;
    const arrow = toggleEl.querySelector('.toggle-arrow');
    const open  = body.classList.toggle('open');
    arrow.textContent = open ? '▲' : '▼';
}

