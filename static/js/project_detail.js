// ===== PROJECT_DETAIL.JS — Suivi d'un projet =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

const jobId = parseInt(window.location.pathname.split('/').pop());
let jobData = null;

// Cache des devis pour les actions (PDF, acompte, etc.)
const _pjQuoteCache = {};

function esc(v) { return (v || '').replace(/'/g, "\\'"); }

// ===== HELPERS =====
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

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
    await loadSummary();
    // Email sidebar
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const el = document.getElementById('sidebar-name');
        if (el) el.textContent = payload.sub || '';
        const av = document.getElementById('sidebar-avatar');
        if (av && payload.sub) av.textContent = payload.sub[0].toUpperCase();
    } catch (_) {}
});

// ===== CHARGEMENT PRINCIPAL =====
async function loadSummary() {
    const res = await apiFetch(`/api/jobs/${jobId}/summary`);
    if (!res) return;
    const data = await res.json();

    jobData = data.job;
    renderHeader(data.job);
    renderKPIs(data.quotes, data.invoices);
    renderPipeline(data.job, data.quotes, data.invoices);
    renderDualTimeline(data.quotes, data.invoices, data.interactions);
    loadTasks();
}

// ===== EN-TÊTE =====
const STATUS_JOB = {
    planned: { label: 'Planifié',  cls: 'draft'    },
    ongoing: { label: 'En cours',  cls: 'sent'     },
    done:    { label: 'Terminé',   cls: 'accepted' },
};

function renderHeader(job) {
    document.title = `${job.title} — Suivi · Kotaflo`;
    document.getElementById('topbar-name').textContent  = job.title;
    document.getElementById('project-name').textContent = job.title;

    const st = STATUS_JOB[job.status] || STATUS_JOB.planned;
    const parts = [`<span class="badge badge--${st.cls}">${st.label}</span>`];
    if (job.client_name) parts.push(`👤 <a href="/contacts/${job.client_id}" style="color:var(--color-primary)">${job.client_name}</a>`);
    if (job.address)     parts.push(`📍 ${job.address}`);
    if (job.start_date)  parts.push(`📅 Du ${formatDate(job.start_date)}${job.end_date ? ' au ' + formatDate(job.end_date) : ''}`);
    document.getElementById('project-info').innerHTML = parts.join('&emsp;');

    const notesCard = document.getElementById('project-notes-card');
    if (job.notes) {
        notesCard.textContent = job.notes;
        notesCard.style.display = '';
    } else {
        notesCard.style.display = 'none';
    }
}

// ===== PIPELINE BAR =====
function renderPipeline(job, quotes, invoices) {
    const hasDepositInv = invoices.some(i => i.invoice_type === 'deposit');
    const hasFinalInv   = invoices.some(i => i.invoice_type === 'final' || i.invoice_type === 'standard');

    // Définition des étapes avec leur condition de complétion
    const STEPS = [
        { label: 'Projet créé',       done: () => true },
        { label: 'Devis envoyé',      done: () => quotes.some(q => ['sent','accepted','refused'].includes(q.status)) },
        { label: 'Devis signé',       done: () => quotes.some(q => q.status === 'accepted') },
        ...(hasDepositInv || quotes.some(q => q.status === 'accepted') ? [
            { label: 'Acompte émis',  done: () => hasDepositInv },
            { label: 'Acompte payé',  done: () => invoices.some(i => i.invoice_type === 'deposit' && i.status === 'paid') },
        ] : []),
        { label: 'Chantier terminé',  done: () => job.status === 'done' },
        ...(hasFinalInv || job.status === 'done' ? [
            { label: 'Facture finale', done: () => hasFinalInv },
            { label: 'Solde payé',    done: () => invoices.some(i => (i.invoice_type === 'final' || i.invoice_type === 'standard') && i.status === 'paid') },
        ] : []),
    ];

    // Calculer l'état de chaque étape
    const results = STEPS.map(s => s.done());
    // La première étape non complétée = active
    const firstPending = results.findIndex(r => !r);

    const container = document.getElementById('pipeline-inner');
    container.innerHTML = '';

    STEPS.forEach((step, i) => {
        const isDone   = results[i];
        const isActive = i === firstPending;
        const cls      = isDone ? 'done' : (isActive ? 'active' : '');

        // Étape
        const el = document.createElement('div');
        el.className = `pipeline-step${cls ? ' pipeline-step--' + cls : ''}`;
        el.innerHTML = `
            <div class="pipeline-step__dot"></div>
            <div class="pipeline-step__label">${step.label}</div>`;
        container.appendChild(el);

        // Ligne (sauf après le dernier)
        if (i < STEPS.length - 1) {
            const line = document.createElement('div');
            line.className = 'pipeline-line' + (isDone ? ' pipeline-line--done' : '');
            container.appendChild(line);
        }
    });
}

// ===== KPI MULTI-ANNEAUX =====
// Chaque anneau a sa propre circonférence (2π*r)
const KPI_CIRCS = { devise: 427.26, deviseAccepte: 339.29, facture: 251.33 };

function setArcKpi(id, ratio, circ) {
    const el = document.getElementById(id);
    if (!el) return;
    const filled = Math.max(0, Math.min(1, ratio || 0)) * circ;
    el.setAttribute('stroke-dasharray', `${filled.toFixed(2)} ${circ.toFixed(2)}`);
}

// Arc helper pour le cercle TVA (r=40, circ≈251.33)
const CIRC = 2 * Math.PI * 40;
function setArc(id, ratio) {
    const el = document.getElementById(id);
    if (!el) return;
    const filled = Math.max(0, Math.min(1, ratio || 0)) * CIRC;
    el.setAttribute('stroke-dasharray', `${filled.toFixed(2)} ${CIRC.toFixed(2)}`);
}

function renderKPIs(quotes, invoices) {
    const caDevise        = quotes.reduce((s, q) => s + (q.amount || 0), 0);
    const caDeviseAccepte = quotes.filter(q => q.status === 'accepted')
                                  .reduce((s, q) => s + (q.amount || 0), 0);
    const caFacture       = invoices.reduce((s, i) => s + (i.amount || 0), 0);
    const caPaye          = invoices.filter(i => i.status === 'paid').reduce((s, i) => s + (i.amount || 0), 0);

    const base = caDevise || 1;

    document.getElementById('kpi-ca-devise').textContent         = formatAmount(caDevise);
    document.getElementById('kpi-ca-devise-accepte').textContent = formatAmount(caDeviseAccepte);
    document.getElementById('kpi-ca-facture').textContent        = formatAmount(caFacture);
    document.getElementById('kpi-ca-paye').textContent           = formatAmount(caPaye);

    setArcKpi('arc-kpi-paye',           caPaye / base,         KPI_CIRCS.devise);
    setArcKpi('arc-kpi-facture',        caFacture / base,      KPI_CIRCS.deviseAccepte);
    setArcKpi('arc-kpi-devise-accepte', caDeviseAccepte / base, KPI_CIRCS.facture);

    // Part TVA sur devis signés
    const accepted   = quotes.filter(q => q.status === 'accepted');
    const tvaHT      = accepted.reduce((s, q) => s + (q.amount || 0), 0);
    const tvaTTC     = accepted.reduce((s, q) => s + (q.amount_ttc || q.amount || 0), 0);
    const tvaMontant = tvaTTC - tvaHT;
    const ratioTva   = tvaTTC > 0 ? tvaMontant / tvaTTC : 0;

    setArc('arc-kpi-tva', ratioTva);
    document.getElementById('pct-kpi-tva').textContent    = tvaTTC > 0 ? (ratioTva * 100).toFixed(2) + '%' : '—';
    document.getElementById('kpi-tva-ht').textContent      = formatAmount(tvaHT);
    document.getElementById('kpi-tva-montant').textContent = formatAmount(tvaMontant);
    document.getElementById('kpi-tva-ttc').textContent     = formatAmount(tvaTTC);
}

// ===== STAGGERED DUAL TIMELINE =====
const QUOTE_STATUS   = { draft: 'Brouillon', sent: 'Envoyé', accepted: 'Accepté', refused: 'Refusé' };
const INVOICE_STATUS = { pending: 'En attente', paid: 'Payée', late: 'En retard' };
const INV_TYPE       = { deposit: 'Acompte', final: 'Finale', standard: 'Standard' };
const TYPE_META      = {
    call:     { icon: '📞', label: 'Appel'    },
    sms:      { icon: '💬', label: 'SMS'      },
    whatsapp: { icon: '🟢', label: 'WhatsApp' },
    email:    { icon: '📧', label: 'Email'    },
    visit:    { icon: '🏠', label: 'Visite'   },
    note:     { icon: '📝', label: 'Note'     },
    other:    { icon: '•',  label: 'Autre'    },
};

function renderDualTimeline(quotes, invoices, interactions) {
    const container = document.getElementById('tl-container');
    const empty     = document.getElementById('timeline-empty');
    container.innerHTML = '';

    const events = [];

    // Interactions → côté gauche (artisan)
    interactions.forEach(ev => {
        const meta = TYPE_META[ev.type] || TYPE_META.other;
        events.push({
            side: 'left',
            date: ev.date ? new Date(ev.date) : new Date(0),
            dotColor: 'var(--color-primary)',
            cardClass: 'tl-card tl-card--artisan',
            html: `
                <div class="tl-card__title">${meta.icon} ${ev.title || meta.label}</div>
                <div class="tl-card__meta">${meta.label}</div>
                ${ev.notes ? `<div class="tl-card__notes">${ev.notes}</div>` : ''}`,
        });
    });

    // Devis → côté droit (client)
    quotes.forEach(q => {
        _pjQuoteCache[q.id] = q;
        const isAvenant = !!q.parent_quote_id;
        const prefix    = isAvenant ? 'AVN' : 'DEV';
        const ref       = `${prefix}-${q.tenant_id}-${q.id}`;
        let actions = `<button class="btn btn--primary btn--sm" onclick="downloadQuotePDF(${q.id})">PDF</button>`;
        actions    += ` <button class="btn btn--ghost btn--sm" onclick="openQuoteStatusModal(${q.id},'${q.status}')">Statut</button>`;
        if (q.status === 'accepted' && !isAvenant) {
            actions += ` <button class="btn btn--ghost btn--sm" onclick="openDepositModal(${q.id},'${esc(q.title)}',${q.amount})">Acompte</button>`;
            actions += ` <button class="btn btn--ghost btn--sm" onclick="createFinalInvoice(${q.id},'${esc(q.title)}')">Finale</button>`;
            actions += ` <button class="btn btn--ghost btn--sm" onclick="openAvenantModal(${q.id},'${esc(q.title)}')">Avenant</button>`;
        }
        events.push({
            side: 'right',
            date: q.created_at ? new Date(q.created_at) : new Date(0),
            dotColor: '#8b5cf6',
            cardClass: 'tl-card tl-card--quote',
            html: `
                <div class="tl-card__title">📄 ${q.title || ref}</div>
                <div class="tl-card__meta">
                    <span class="badge badge--${q.status}">${QUOTE_STATUS[q.status] || q.status}</span>
                    &nbsp;· ${formatAmount(q.amount)}
                </div>
                <div class="tl-card__actions">${actions}</div>`,
        });
    });

    // Factures → côté droit (client)
    invoices.forEach(inv => {
        const invType = inv.invoice_type || 'standard';
        const prefix  = { deposit: 'ACOMPTE', final: 'FINALE', standard: 'FAC' }[invType] || 'FAC';
        const ref     = `${prefix}-${inv.tenant_id}-${inv.id}`;
        events.push({
            side: 'right',
            date: inv.created_at ? new Date(inv.created_at) : (inv.due_date ? new Date(inv.due_date) : new Date(0)),
            dotColor: 'var(--color-success, #22c55e)',
            cardClass: 'tl-card tl-card--invoice',
            html: `
                <div class="tl-card__title">💰 ${INV_TYPE[invType]} — ${ref}</div>
                <div class="tl-card__meta">
                    <span class="badge badge--${inv.status}">${INVOICE_STATUS[inv.status] || inv.status}</span>
                    &nbsp;· Éch. ${formatDate(inv.due_date)} · ${formatAmount(inv.amount)}
                </div>
                <div class="tl-card__actions">
                    <button class="btn btn--primary btn--sm" onclick="downloadInvoicePDF(${inv.id})">PDF</button>
                    <button class="btn btn--ghost btn--sm" onclick="openInvoiceStatusModal(${inv.id},'${inv.status}')">Statut</button>
                </div>`,
        });
    });

    // Trier : plus récent en haut, plus ancien en bas
    events.sort((a, b) => b.date - a.date);

    if (!events.length) { empty.style.display = ''; return; }
    empty.style.display = 'none';

    events.forEach(ev => {
        const dateStr = ev.date > new Date(1000)
            ? ev.date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
            : '';

        const wrapper = document.createElement('div');
        wrapper.className = `tl-event tl-event--${ev.side}`;

        const cardHtml = `<div class="${ev.cardClass}">${ev.html}</div>`;
        const dotHtml  = `<div class="tl-dot" style="background:${ev.dotColor}"></div>`;
        const dateHtml = `<div class="tl-date">${dateStr}</div>`;

        wrapper.innerHTML = ev.side === 'left'
            ? dateHtml + dotHtml + cardHtml
            : cardHtml + dotHtml + dateHtml;

        container.appendChild(wrapper);
    });
}

// ===== MODAL INTERACTION =====
function openInteractionModal() {
    document.getElementById('interaction-form').reset();
    const now = new Date(); now.setSeconds(0, 0);
    document.getElementById('int-date').value = now.toISOString().slice(0, 16);
    document.getElementById('modal-interaction').classList.remove('hidden');
}

function closeInteractionModal(event) {
    const overlay = document.getElementById('modal-interaction');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function handleInteractionSubmit(e) {
    e.preventDefault();
    if (!jobData?.client_id) { showToast('Aucun client associé à ce projet', 'danger'); return; }
    const dateVal = document.getElementById('int-date').value;
    const body = {
        type:   document.getElementById('int-type').value,
        title:  document.getElementById('int-title').value,
        notes:  document.getElementById('int-notes').value,
        date:   dateVal ? dateVal.replace('T', ' ') + ':00' : null,
        job_id: jobId,
    };
    const res = await apiFetch(`/api/clients/${jobData.client_id}/interactions`, {
        method: 'POST', body: JSON.stringify(body),
    });
    if (res?.ok) {
        closeInteractionModal();
        showToast('Interaction ajoutée', 'success');
        loadSummary();
    } else { showToast('Erreur', 'danger'); }
}

// ===== TÂCHES =====
const TASK_PRIORITY = { high: '🔴 Haute', normal: '🔵 Normale', low: '⚪ Basse' };
const TASK_STATUS   = { todo: 'À faire', in_progress: 'En cours', done: 'Terminée' };

async function loadTasks() {
    const res = await apiFetch(`/api/tasks/?job_id=${jobId}`);
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
        const overdue   = t.due_date && new Date(t.due_date+'T00:00:00') < today && t.status !== 'done';
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
    document.getElementById('task-modal-title').textContent  = task ? 'Modifier la tâche' : 'Nouvelle tâche';
    document.getElementById('task-id').value                 = task?.id || '';
    document.getElementById('task-title').value              = task?.title || '';
    document.getElementById('task-desc').value               = task?.description || '';
    document.getElementById('task-priority').value           = task?.priority || 'normal';
    document.getElementById('task-due').value                = task?.due_date?.slice(0,10) || '';
    document.getElementById('task-status').value             = task?.status || 'todo';
    document.getElementById('task-btn-delete').style.display = task ? '' : 'none';
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
        description: document.getElementById('task-desc').value  || null,
        priority:    document.getElementById('task-priority').value,
        due_date:    document.getElementById('task-due').value    || null,
        status:      document.getElementById('task-status').value,
        job_id:      jobId,
        client_id:   jobData?.client_id || null,
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

// ===== MODAL MODIFIER PROJET =====
function openEditModal() {
    if (!jobData) return;
    document.getElementById('edit-title').value   = jobData.title   || '';
    document.getElementById('edit-status').value  = jobData.status  || 'planned';
    document.getElementById('edit-start').value   = jobData.start_date?.slice(0, 10) || '';
    document.getElementById('edit-end').value     = jobData.end_date?.slice(0, 10)   || '';
    document.getElementById('edit-address').value = jobData.address || '';
    document.getElementById('edit-notes').value   = jobData.notes   || '';
    document.getElementById('modal-edit').classList.remove('hidden');
}

function closeEditModal(event) {
    const overlay = document.getElementById('modal-edit');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function handleEditSubmit(e) {
    e.preventDefault();
    const body = {
        client_id:  jobData.client_id || null,
        title:      document.getElementById('edit-title').value,
        status:     document.getElementById('edit-status').value,
        start_date: document.getElementById('edit-start').value   || null,
        end_date:   document.getElementById('edit-end').value     || null,
        address:    document.getElementById('edit-address').value || null,
        notes:      document.getElementById('edit-notes').value   || null,
    };
    const res = await apiFetch(`/api/jobs/${jobId}`, { method: 'PUT', body: JSON.stringify(body) });
    if (res?.ok) {
        closeEditModal();
        showToast('Projet mis à jour', 'success');
        loadSummary();
    } else { showToast('Erreur', 'danger'); }
}
