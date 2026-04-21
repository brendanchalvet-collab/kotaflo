// ===== TASKS.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

let allTasks      = [];
let currentFilter = 'all';

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function formatDate(str) {
    if (!str) return null;
    return new Date(str + 'T00:00:00').toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

const PRIORITY_LABEL = { high: '🔴 Haute', normal: '🔵 Normale', low: '⚪ Basse' };

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    loadClients();
    loadJobs();
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const el = document.getElementById('sidebar-name');
        if (el) el.textContent = payload.sub || '';
        const av = document.getElementById('sidebar-avatar');
        if (av && payload.sub) av.textContent = payload.sub[0].toUpperCase();
    } catch (_) {}
});

// ===== CHARGEMENT =====
async function loadTasks() {
    const res = await apiFetch('/api/tasks/');
    if (!res) return;
    allTasks = await res.json();
    renderKanban(allTasks);
}

async function loadClients() {
    const res = await apiFetch('/api/clients/');
    if (!res) return;
    const clients = await res.json();
    const sel = document.getElementById('task-client');
    clients.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id; opt.textContent = c.name;
        sel.appendChild(opt);
    });
}

async function loadJobs() {
    const res = await apiFetch('/api/jobs/');
    if (!res) return;
    const jobs = await res.json();
    const sel  = document.getElementById('task-job');
    jobs.forEach(j => {
        const opt = document.createElement('option');
        opt.value = j.id; opt.textContent = j.title;
        sel.appendChild(opt);
    });
}

// ===== FILTRE PRIORITÉ =====
function setFilter(priority, btn) {
    currentFilter = priority;
    document.querySelectorAll('.filter-bar .btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filtered = priority === 'all' ? allTasks : allTasks.filter(t => t.priority === priority);
    renderKanban(filtered);
}

// ===== RENDU KANBAN =====
function renderKanban(tasks) {
    const cols   = ['todo', 'in_progress', 'done'];
    const counts = { todo: 0, in_progress: 0, done: 0 };

    cols.forEach(s => { document.getElementById(`col-${s}`).innerHTML = ''; });

    const today = new Date(); today.setHours(0, 0, 0, 0);

    tasks.forEach(t => {
        const col = document.getElementById(`col-${t.status}`);
        if (!col) return;
        counts[t.status]++;

        const isOverdue = t.due_date && new Date(t.due_date + 'T00:00:00') < today && t.status !== 'done';
        const dueStr    = t.due_date ? `📅 ${formatDate(t.due_date)}` : '';

        const card = document.createElement('div');
        card.className = `task-card priority-${t.priority}`;
        card.innerHTML = `
            <div class="task-card__title">${t.title}</div>
            ${t.description ? `<div class="task-card__desc">${t.description}</div>` : ''}
            <div class="task-card__meta">
                <span>${PRIORITY_LABEL[t.priority] || t.priority}</span>
                ${dueStr ? `<span class="task-card__due ${isOverdue ? 'overdue' : ''}">${isOverdue ? '⚠️ ' : ''}${dueStr}</span>` : ''}
                ${t.client_name ? `<span>👤 ${t.client_name}</span>` : ''}
                ${t.job_title   ? `<span>🔨 ${t.job_title}</span>`   : ''}
            </div>`;
        card.onclick = () => openModal(t);
        col.appendChild(card);
    });

    cols.forEach(s => {
        document.getElementById(`empty-${s}`).style.display = counts[s] ? 'none' : '';
        const countEl = document.getElementById(`count-${s}`);
        if (countEl) countEl.textContent = counts[s] ? `(${counts[s]})` : '';
    });
}

// ===== MODAL =====
function openModal(task = null) {
    document.getElementById('modal-title').textContent    = task ? 'Modifier la tâche' : 'Nouvelle tâche';
    document.getElementById('task-id').value             = task?.id || '';
    document.getElementById('task-title').value          = task?.title || '';
    document.getElementById('task-desc').value           = task?.description || '';
    document.getElementById('task-priority').value       = task?.priority || 'normal';
    document.getElementById('task-due').value            = task?.due_date?.slice(0, 10) || '';
    document.getElementById('task-client').value         = task?.client_id || '';
    document.getElementById('task-job').value            = task?.job_id || '';
    document.getElementById('task-status').value         = task?.status || 'todo';
    document.getElementById('btn-delete').style.display  = task ? '' : 'none';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION =====
async function handleSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('task-id').value;
    const body = {
        title:       document.getElementById('task-title').value,
        description: document.getElementById('task-desc').value     || null,
        priority:    document.getElementById('task-priority').value,
        due_date:    document.getElementById('task-due').value       || null,
        client_id:   document.getElementById('task-client').value   ? Number(document.getElementById('task-client').value) : null,
        job_id:      document.getElementById('task-job').value      ? Number(document.getElementById('task-job').value)    : null,
        status:      document.getElementById('task-status').value,
    };
    const url    = id ? `/api/tasks/${id}` : '/api/tasks/';
    const method = id ? 'PUT' : 'POST';
    const res    = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (res?.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast(id ? 'Tâche mise à jour' : 'Tâche créée', 'success');
        loadTasks();
    } else { showToast('Erreur', 'danger'); }
}

// ===== SUPPRESSION =====
async function deleteTask() {
    const id = document.getElementById('task-id').value;
    if (!id || !confirm('Supprimer cette tâche ?')) return;
    const res = await apiFetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (res?.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast('Tâche supprimée');
        loadTasks();
    } else { showToast('Erreur', 'danger'); }
}
