// ===== CONTACT_HISTORY.JS — Suivi du contact =====

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

const clientId  = parseInt(window.location.pathname.split('/').pop());
let contactData = null;

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function formatDate(str) {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
}

function formatDateTime(str) {
    if (!str) return '—';
    const d = new Date(str);
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
        + ' · ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function formatAmount(n) {
    return Number(n || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadContact();
    await Promise.all([loadTimeline(), loadProjects(), loadTasks()]);
    const now = new Date(); now.setSeconds(0, 0);
    document.getElementById('int-date').value = now.toISOString().slice(0, 16);
});

// ===== CONTACT =====
async function loadContact() {
    const res = await apiFetch(`/api/clients/${clientId}`);
    if (!res) return;
    contactData = await res.json();
    renderContactHeader(contactData);
}

function renderContactHeader(c) {
    document.title = `${c.name} — Suivi · Kotaflo`;
    document.getElementById('topbar-name').textContent  = c.name;
    document.getElementById('contact-name').textContent = c.name;

    const typeBadge = c.contact_type === 'prospect'
        ? '<span class="badge badge--draft">Prospect</span>'
        : '<span class="badge badge--accepted">Client</span>';

    const parts = [typeBadge];
    if (c.phone)              parts.push(`📞 ${c.phone}`);
    if (c.email)              parts.push(`📧 ${c.email}`);
    if (c.address)            parts.push(`📍 ${c.address}`);
    if (c.acquisition_source) parts.push(`Via : ${c.acquisition_source}`);
    if (c.notes)              parts.push(`<em style="color:var(--color-gray-400)">${c.notes}</em>`);
    document.getElementById('contact-info').innerHTML = parts.join('&emsp;');
}

// ===== TIMELINE =====
async function loadTimeline() {
    const res = await apiFetch(`/api/clients/${clientId}/timeline`);
    if (!res) return;
    const events = await res.json();
    renderTimeline(events);
    renderKPIs(events);
}

const TYPE_META = {
    call:     { icon: '📞', label: 'Appel' },
    sms:      { icon: '💬', label: 'SMS' },
    whatsapp: { icon: '🟢', label: 'WhatsApp' },
    email:    { icon: '📧', label: 'Email' },
    visit:    { icon: '🏠', label: 'Visite' },
    note:     { icon: '📝', label: 'Note' },
    other:    { icon: '•',  label: 'Autre' },
};
const QUOTE_STATUS   = { draft: 'Brouillon', sent: 'Envoyé', accepted: 'Accepté', refused: 'Refusé' };
const INVOICE_STATUS = { pending: 'En attente', paid: 'Payée', late: 'En retard' };

function renderTimeline(events) {
    const artisan = document.getElementById('timeline-artisan');
    const client  = document.getElementById('timeline-client');
    const empty   = document.getElementById('timeline-empty');

    artisan.innerHTML = '';
    client.innerHTML  = '';

    const artisanEvents = events.filter(e => e.kind === 'interaction');
    const clientEvents  = events.filter(e => e.kind === 'quote' || e.kind === 'invoice');

    if (!artisanEvents.length && !clientEvents.length) {
        empty.classList.remove('hidden');
        return;
    }
    empty.classList.add('hidden');

    // ===== CÔTÉ ARTISAN : interactions =====
    artisanEvents.forEach(ev => {
        const meta = TYPE_META[ev.type] || TYPE_META.other;
        const card = document.createElement('div');
        card.className = 'tl-card tl-card--artisan';
        card.innerHTML = `
            <div class="tl-card__title">${meta.icon} ${ev.title || meta.label}</div>
            <div class="tl-card__meta">${meta.label} · ${formatDateTime(ev.date)}</div>
            ${ev.notes ? `<div class="tl-card__notes">${ev.notes}</div>` : ''}
            <button class="tl-delete" onclick="deleteInteraction(${ev.id})">✕</button>`;
        artisan.appendChild(card);
    });

    // ===== CÔTÉ CLIENT : devis & factures =====
    clientEvents.forEach(ev => {
        const card = document.createElement('div');

        if (ev.kind === 'quote') {
            card.className = 'tl-card tl-card--quote';
            card.innerHTML = `
                <div class="tl-card__title">📄 ${ev.title}</div>
                <div class="tl-card__meta">Devis · ${formatDateTime(ev.date)}${ev.job_title ? ` · ${ev.job_title}` : ''}</div>
                <div style="margin-top:.3rem;font-size:.82rem">
                    ${formatAmount(ev.amount)}&nbsp;
                    <span class="badge badge--${ev.status}">${QUOTE_STATUS[ev.status] || ev.status}</span>
                </div>`;
        } else if (ev.kind === 'invoice') {
            card.className = 'tl-card tl-card--invoice';
            card.innerHTML = `
                <div class="tl-card__title">💰 ${ev.title}</div>
                <div class="tl-card__meta">Facture · ${formatDateTime(ev.date)}${ev.job_title ? ` · ${ev.job_title}` : ''}</div>
                <div style="margin-top:.3rem;font-size:.82rem">
                    ${formatAmount(ev.amount)}&nbsp;
                    <span class="badge badge--${ev.status}">${INVOICE_STATUS[ev.status] || ev.status}</span>
                </div>`;
        }

        client.appendChild(card);
    });
}

// ===== KPI =====
function renderKPIs(events) {
    const interactions = events.filter(e => e.kind === 'interaction').length;
    const quotes       = events.filter(e => e.kind === 'quote').length;
    const invoices     = events.filter(e => e.kind === 'invoice');

    const caFacture  = invoices.reduce((sum, e) => sum + (e.amount || 0), 0);
    const caEncaisse = invoices
        .filter(e => e.status === 'paid')
        .reduce((sum, e) => sum + (e.amount || 0), 0);

    document.getElementById('kpi-interactions').textContent  = interactions;
    document.getElementById('kpi-quotes').textContent        = quotes;
    document.getElementById('kpi-ca-facture').textContent    = formatAmount(caFacture);
    document.getElementById('kpi-ca').textContent            = formatAmount(caEncaisse);
}

// ===== PROJETS =====
const STATUS_PROJECT = {
    planned: { label: 'Planifié', cls: 'draft'    },
    ongoing: { label: 'En cours', cls: 'sent'     },
    done:    { label: 'Terminé',  cls: 'accepted' },
};

async function loadProjects() {
    const res = await apiFetch(`/api/jobs/?client_id=${clientId}`);
    if (!res) return;
    const projects = await res.json();
    renderProjects(projects);
    document.getElementById('kpi-projects').textContent = projects.length;
}

function renderProjects(projects) {
    const list  = document.getElementById('projects-list');
    const empty = document.getElementById('projects-empty');
    list.innerHTML = '';

    if (!projects.length) { empty.style.display = ''; return; }
    empty.style.display = 'none';

    projects.forEach(p => {
        const st   = STATUS_PROJECT[p.status] || STATUS_PROJECT.planned;
        const card = document.createElement('div');
        card.className = 'project-card';
        card.innerHTML = `
            <div class="project-card__title">${p.title}</div>
            <div class="project-card__meta">
                <span class="badge badge--${st.cls}">${st.label}</span>
                ${p.start_date ? `&nbsp;· Du ${formatDate(p.start_date)}` : ''}
                ${p.end_date   ? ` au ${formatDate(p.end_date)}` : ''}
            </div>`;
        card.addEventListener('click', () => window.location.href = `/projects/${p.id}`);
        list.appendChild(card);
    });
}

// ===== MODAL PROJET =====
function openProjectModal(project = null) {
    document.getElementById('project-modal-title').textContent = project ? 'Modifier le projet' : 'Nouveau projet';
    document.getElementById('proj-id').value      = project ? project.id : '';
    document.getElementById('proj-title').value   = project ? project.title : '';
    document.getElementById('proj-status').value  = project ? project.status : 'planned';
    document.getElementById('proj-start').value   = project?.start_date?.slice(0, 10) || '';
    document.getElementById('proj-end').value     = project?.end_date?.slice(0, 10) || '';
    document.getElementById('proj-address').value = project ? (project.address || '') : '';
    document.getElementById('proj-notes').value   = project ? (project.notes || '') : '';
    document.getElementById('modal-project').classList.remove('hidden');
}

async function editProject(id) {
    const res = await apiFetch(`/api/jobs/${id}`);
    if (!res) return;
    openProjectModal(await res.json());
}

async function handleProjectSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('proj-id').value;
    const body = {
        client_id:  clientId,
        title:      document.getElementById('proj-title').value,
        status:     document.getElementById('proj-status').value,
        start_date: document.getElementById('proj-start').value  || null,
        end_date:   document.getElementById('proj-end').value    || null,
        address:    document.getElementById('proj-address').value || null,
        notes:      document.getElementById('proj-notes').value,
    };
    const url    = id ? `/api/jobs/${id}` : '/api/jobs/';
    const method = id ? 'PUT' : 'POST';
    const res    = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (res?.ok) {
        closeModal('modal-project');
        showToast(id ? 'Projet mis à jour' : 'Projet créé', 'success');
        loadProjects();
    } else { showToast('Erreur', 'danger'); }
}

// ===== INTERACTION =====
async function deleteInteraction(id) {
    if (!confirm('Supprimer cette interaction ?')) return;
    const res = await apiFetch(`/api/clients/interactions/${id}`, { method: 'DELETE' });
    if (res?.ok) { showToast('Supprimé'); loadTimeline(); }
    else showToast('Erreur', 'danger');
}

function openInteractionModal() {
    document.getElementById('interaction-form').reset();
    const now = new Date(); now.setSeconds(0, 0);
    document.getElementById('int-date').value = now.toISOString().slice(0, 16);
    document.getElementById('modal-interaction').classList.remove('hidden');
}

async function handleInteractionSubmit(e) {
    e.preventDefault();
    const dateVal = document.getElementById('int-date').value;
    const body = {
        type:  document.getElementById('int-type').value,
        title: document.getElementById('int-title').value,
        notes: document.getElementById('int-notes').value,
        date:  dateVal ? dateVal.replace('T', ' ') + ':00' : null,
    };
    const res = await apiFetch(`/api/clients/${clientId}/interactions`, {
        method: 'POST', body: JSON.stringify(body),
    });
    if (res?.ok) {
        closeModal('modal-interaction');
        showToast('Interaction ajoutée', 'success');
        loadTimeline();
    } else { showToast('Erreur', 'danger'); }
}

// ===== MODIFIER CONTACT =====
function openEditModal() {
    if (!contactData) return;
    const c = contactData;
    document.getElementById('edit-name').value        = c.name || '';
    document.getElementById('edit-phone').value       = c.phone || '';
    document.getElementById('edit-email').value       = c.email || '';
    document.getElementById('edit-address').value     = c.address || '';

    document.getElementById('edit-notes').value       = c.notes || '';
    document.querySelector(`input[name="edit-type"][value="${c.contact_type || 'client'}"]`).checked = true;
    document.getElementById('modal-edit').classList.remove('hidden');
}

async function handleEditSubmit(e) {
    e.preventDefault();
    const body = {
        name:               document.getElementById('edit-name').value,
        phone:              document.getElementById('edit-phone').value,
        email:              document.getElementById('edit-email').value,
        address:            document.getElementById('edit-address').value,

        notes:              document.getElementById('edit-notes').value,
        contact_type:       document.querySelector('input[name="edit-type"]:checked').value,
        pipeline_status:    contactData.pipeline_status || 'new',
    };
    const res = await apiFetch(`/api/clients/${clientId}`, {
        method: 'PUT', body: JSON.stringify(body),
    });
    if (res?.ok) {
        contactData = await res.json();
        closeModal('modal-edit');
        showToast('Contact mis à jour', 'success');
        renderContactHeader(contactData);
    } else { showToast('Erreur', 'danger'); }
}

// ===== TÂCHES =====
const TASK_PRIORITY = { high: '🔴 Haute', normal: '🔵 Normale', low: '⚪ Basse' };
const TASK_STATUS   = { todo: 'À faire', in_progress: 'En cours', done: 'Terminée' };

async function loadTasks() {
    const res = await apiFetch(`/api/tasks/?client_id=${clientId}`);
    if (!res) return;
    renderTasks(await res.json());
}

function renderTasks(tasks) {
    const list  = document.getElementById('tasks-list');
    const empty = document.getElementById('tasks-empty');
    list.innerHTML = '';
    if (!tasks.length) { empty.style.display = ''; return; }
    empty.style.display = 'none';
    const today = new Date(); today.setHours(0,0,0,0);
    tasks.forEach(t => {
        const overdue  = t.due_date && new Date(t.due_date+'T00:00:00') < today && t.status !== 'done';
        const statusCls = { todo: 'draft', in_progress: 'sent', done: 'accepted' }[t.status] || 'draft';
        const div = document.createElement('div');
        div.style.cssText = 'background:var(--color-white);border-radius:var(--radius);box-shadow:var(--shadow);padding:.7rem 1rem;margin-bottom:.5rem;display:flex;align-items:center;gap:.75rem;cursor:pointer;border-left:3px solid ' + ({high:'var(--color-danger)',normal:'var(--color-primary)',low:'var(--color-gray-300)'}[t.priority]||'var(--color-gray-300)');
        div.innerHTML = `
            <div style="flex:1">
                <div style="font-weight:600;font-size:.9rem${t.status==='done'?';text-decoration:line-through;color:var(--color-gray-400)':''}">${t.title}</div>
                <div style="font-size:.75rem;color:var(--color-gray-400);margin-top:.2rem;display:flex;gap:.6rem;flex-wrap:wrap">
                    <span class="badge badge--${statusCls}">${TASK_STATUS[t.status]}</span>
                    <span>${TASK_PRIORITY[t.priority]}</span>
                    ${t.due_date ? `<span style="${overdue?'color:var(--color-danger);font-weight:600':''}">${overdue?'⚠️ ':'📅 '}${formatDate(t.due_date)}</span>` : ''}
                </div>
            </div>`;
        div.onclick = () => openTaskModal(t);
        list.appendChild(div);
    });
}

function openTaskModal(task = null) {
    document.getElementById('task-modal-title').textContent   = task ? 'Modifier la tâche' : 'Nouvelle tâche';
    document.getElementById('task-id').value                  = task?.id || '';
    document.getElementById('task-title').value               = task?.title || '';
    document.getElementById('task-desc').value                = task?.description || '';
    document.getElementById('task-priority').value            = task?.priority || 'normal';
    document.getElementById('task-due').value                 = task?.due_date?.slice(0,10) || '';
    document.getElementById('task-status').value              = task?.status || 'todo';
    document.getElementById('task-btn-delete').style.display  = task ? '' : 'none';
    document.getElementById('modal-task').classList.remove('hidden');
}

function closeTaskModal(event) {
    const overlay = document.getElementById('modal-task');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    const id   = document.getElementById('task-id').value;
    const body = {
        title:       document.getElementById('task-title').value,
        description: document.getElementById('task-desc').value    || null,
        priority:    document.getElementById('task-priority').value,
        due_date:    document.getElementById('task-due').value      || null,
        status:      document.getElementById('task-status').value,
        client_id:   clientId,
    };
    const url    = id ? `/api/tasks/${id}` : '/api/tasks/';
    const method = id ? 'PUT' : 'POST';
    const res    = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (res?.ok) { closeTaskModal(); showToast(id ? 'Tâche mise à jour' : 'Tâche créée', 'success'); loadTasks(); }
    else showToast('Erreur', 'danger');
}

async function deleteTask() {
    const id = document.getElementById('task-id').value;
    if (!id || !confirm('Supprimer cette tâche ?')) return;
    const res = await apiFetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (res?.ok) { closeTaskModal(); showToast('Tâche supprimée'); loadTasks(); }
}

// ===== UTILITAIRE MODAL =====
function closeModal(id, event) {
    const overlay = document.getElementById(id);
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}
