// ===== INVOICES.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

let currentInvoiceId = null;
let currentPage      = 1;

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function formatDate(str) {
    if (!str) return '—';
    return new Date(str).toLocaleDateString('fr-FR');
}

function formatAmount(n) {
    return Number(n || 0).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' });
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadInvoices();
    loadClientsForSelect();
});

// ===== CHARGEMENT =====
async function loadInvoices(page = 1) {
    currentPage = page;
    const res   = await apiFetch(`/api/invoices/?page=${page}`);
    if (!res) return;
    renderTable(await res.json());
}

async function loadClientsForSelect() {
    const res = await apiFetch('/api/clients/');
    if (!res) return;
    const clients = await res.json();
    const sel     = document.getElementById('invoice-client');
    sel.innerHTML = '<option value="">Sélectionner un client…</option>';
    clients.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id; opt.textContent = c.name;
        sel.appendChild(opt);
    });
}

// Chargement projets selon client (partagé avec quotes.js via fonction globale)
async function onClientChange(prefix) {
    const clientId = document.getElementById(`${prefix}-client`).value;
    const jobSel   = document.getElementById(`${prefix}-job`);
    const addrFld  = document.getElementById(`${prefix}-address`);

    jobSel.innerHTML = '<option value="">— Sélectionner un projet —</option>';
    if (addrFld) addrFld.value = '';

    if (!clientId) {
        jobSel.innerHTML = '<option value="">— Sélectionner un client d\'abord —</option>';
        return;
    }

    const res = await apiFetch(`/api/jobs/?client_id=${clientId}`);
    if (!res) return;
    const jobs = await res.json();

    jobs.forEach(j => {
        const opt = document.createElement('option');
        opt.value           = j.id;
        opt.textContent     = j.title;
        opt.dataset.address = j.address || '';
        jobSel.appendChild(opt);
    });

    jobSel.onchange = () => {
        const selected = jobSel.options[jobSel.selectedIndex];
        if (addrFld) addrFld.value = selected?.dataset.address || '';
    };
}

// ===== RENDU TABLEAU =====
const STATUS_LABELS = { pending: 'En attente', paid: 'Payée', late: 'En retard' };
const TYPE_LABELS   = { deposit: 'Acompte', final: 'Finale', standard: 'Standard' };
const TYPE_COLORS   = { deposit: 'var(--color-warning,#f59e0b)', final: 'var(--color-primary)', standard: 'var(--color-gray-400)' };

function renderTable(invoices) {
    const tbody = document.getElementById('invoices-table');
    if (!invoices.length) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-muted">Aucune facture</td></tr>';
        return;
    }
    tbody.innerHTML = invoices.map(inv => {
        const invType  = inv.invoice_type || 'standard';
        const typeLabel = TYPE_LABELS[invType] || invType;
        const typeColor = TYPE_COLORS[invType] || '';

        const prefix = { deposit: 'ACOMPTE', final: 'FINALE', standard: 'FAC' }[invType] || 'FAC';
        const num = `${prefix}-${inv.tenant_id}-${inv.id}`;

        const quoteRef = inv.quote_id
            ? `<span style="font-size:.8rem;color:var(--color-gray-400)">DEV-${inv.tenant_id}-${inv.quote_id}</span>`
            : '—';

        return `
        <tr>
            <td style="color:var(--color-gray-400);font-size:.8rem">${num}</td>
            <td><span style="font-size:.78rem;font-weight:600;color:${typeColor}">${typeLabel}</span></td>
            <td>${inv.client_name || '—'}</td>
            <td>${inv.job_title ? `<span style="font-size:.82rem;color:var(--color-primary)">🔨 ${inv.job_title}</span>` : '—'}</td>
            <td>${quoteRef}</td>
            <td><strong>${formatAmount(inv.amount)}</strong></td>
            <td><span class="badge badge--${inv.status}">${STATUS_LABELS[inv.status] || inv.status}</span></td>
            <td>${formatDate(inv.due_date)}</td>
            <td style="display:flex;gap:.4rem;flex-wrap:wrap;">
                <button class="btn btn--ghost btn--sm" onclick="openStatusModal(${inv.id}, '${inv.status}')">Modifier</button>
                <button class="btn btn--primary btn--sm" onclick="downloadPDF(${inv.id})">PDF</button>
            </td>
        </tr>`;
    }).join('');
}

// ===== TÉLÉCHARGEMENT PDF =====
async function downloadPDF(invoiceId) {
    showToast('Génération du PDF…');
    const res = await apiFetch(`/api/invoices/${invoiceId}/pdf`);
    if (!res || !res.ok) { showToast('Erreur génération PDF', 'danger'); return; }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = Object.assign(document.createElement('a'), { href: url, download: `facture-${invoiceId}.pdf` });
    a.click();
    URL.revokeObjectURL(url);
}

// ===== MODAL CRÉATION =====
function openModal() {
    document.getElementById('invoice-form').reset();
    document.getElementById('invoice-job').innerHTML = '<option value="">— Sélectionner un client d\'abord —</option>';
    document.getElementById('invoice-address').value = '';
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

async function handleSubmit(e) {
    e.preventDefault();
    const jobId = document.getElementById('invoice-job').value;
    if (!jobId) { showToast('Sélectionnez un projet', 'danger'); return; }

    const body = {
        client_id: Number(document.getElementById('invoice-client').value),
        job_id:    Number(jobId),
        amount:    parseFloat(document.getElementById('invoice-amount').value),
        due_date:  document.getElementById('invoice-due').value || null,
        status:    'pending',
    };

    const res = await apiFetch('/api/invoices/', { method: 'POST', body: JSON.stringify(body) });
    if (res?.ok) {
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast('Facture créée', 'success');
        loadInvoices(currentPage);
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== MODAL STATUT =====
function openStatusModal(id, status) {
    currentInvoiceId = id;
    document.getElementById('status-select').value = status;
    document.getElementById('modal-status-overlay').classList.remove('hidden');
}

function closeStatusModal(event) {
    if (event && event.target !== document.getElementById('modal-status-overlay')) return;
    document.getElementById('modal-status-overlay').classList.add('hidden');
}

async function saveStatus() {
    const status = document.getElementById('status-select').value;
    const res = await apiFetch(`/api/invoices/${currentInvoiceId}/status`, {
        method: 'PATCH', body: JSON.stringify({ status }),
    });
    if (res?.ok) { closeStatusModal(); showToast('Facture mise à jour', 'success'); loadInvoices(currentPage); }
}

async function deleteInvoice() {
    if (!confirm('Supprimer cette facture ?')) return;
    const res = await apiFetch(`/api/invoices/${currentInvoiceId}`, { method: 'DELETE' });
    if (res?.ok) { closeStatusModal(); showToast('Facture supprimée'); loadInvoices(currentPage); }
}
