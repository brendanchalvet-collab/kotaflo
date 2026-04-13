// ===== QUOTES.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

let currentQuoteId  = null;
let editingQuoteId  = null;   // null = création, number = modification
let currentPage     = 1;
let lineCount       = 0;
let avenantLineCount = 0;
let _quotesCache    = {};     // id → quote complet pour Gmail
let _avenantQuoteId = null;   // devis parent pour modal avenant

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
    return Number(n || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadQuotes();
    loadClientsForSelect();
});

// ===== CHARGEMENT LISTE =====
async function loadQuotes(page = 1) {
    currentPage = page;
    const res = await apiFetch(`/api/quotes/?page=${page}`);
    if (!res) return;
    renderTable(await res.json());
}

async function loadClientsForSelect() {
    const res = await apiFetch('/api/clients/');
    if (!res) return;
    const clients = await res.json();
    const sel = document.getElementById('quote-client');
    sel.innerHTML = '<option value="">Sélectionner un client…</option>';
    clients.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id; opt.textContent = c.name;
        sel.appendChild(opt);
    });
}

// Chargement des projets selon le client sélectionné
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
        opt.value       = j.id;
        opt.textContent = j.title;
        opt.dataset.address = j.address || '';
        jobSel.appendChild(opt);
    });

    // Auto-remplir l'adresse quand on change de projet
    jobSel.onchange = () => {
        const selected = jobSel.options[jobSel.selectedIndex];
        if (addrFld) addrFld.value = selected?.dataset.address || '';
    };
}

// ===== RENDU TABLEAU =====
const STATUS_LABELS = { draft: 'Brouillon', sent: 'Envoyé', accepted: 'Accepté', refused: 'Refusé' };

function renderTable(quotes) {
    const tbody = document.getElementById('quotes-table');
    if (!quotes.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-muted">Aucun devis</td></tr>';
        return;
    }
    // Mise en cache pour l'ouverture Gmail
    quotes.forEach(q => { _quotesCache[q.id] = q; });
    // Séparer devis parents et avenants
    const parents  = quotes.filter(q => !q.parent_quote_id);
    const avenants = quotes.filter(q =>  q.parent_quote_id);
    const avenantsByParent = {};
    avenants.forEach(a => {
        if (!avenantsByParent[a.parent_quote_id]) avenantsByParent[a.parent_quote_id] = [];
        avenantsByParent[a.parent_quote_id].push(a);
    });

    tbody.innerHTML = parents.map(q => {
        let actions = '';
        if (q.status === 'draft') {
            actions = `
                <button class="btn btn--ghost btn--sm" onclick="openEditModal(${q.id})">Modifier</button>
                <button class="btn btn--ghost btn--sm" onclick="openStatusModal(${q.id},'${q.status}')">Statut</button>`;
        } else if (q.status === 'accepted') {
            actions = `
                <button class="btn btn--ghost btn--sm" onclick="openStatusModal(${q.id},'${q.status}')">Statut</button>
                <button class="btn btn--ghost btn--sm" onclick="openAvenantModal(${q.id},'${esc(q.title)}')">Avenant</button>
                <button class="btn btn--ghost btn--sm" onclick="openDepositModal(${q.id},'${esc(q.title)}',${q.amount})" title="Créer une facture d'acompte">Acompte</button>
                <button class="btn btn--ghost btn--sm" onclick="createFinalInvoice(${q.id},'${esc(q.title)}')" title="Créer la facture finale">Finale</button>`;
        } else {
            actions = `<button class="btn btn--ghost btn--sm" onclick="openStatusModal(${q.id},'${q.status}')">Statut</button>`;
        }
        const avRows = (avenantsByParent[q.id] || []).map(a => {
            const aActions = `
                ${a.status === 'draft' ? `<button class="btn btn--ghost btn--sm" onclick="openEditModal(${a.id})">Modifier</button>` : ''}
                <button class="btn btn--ghost btn--sm" onclick="openStatusModal(${a.id},'${a.status}')">Statut</button>
                <button class="btn btn--primary btn--sm" onclick="downloadPDF(${a.id})">PDF</button>`;
            return `
            <tr style="background:var(--color-gray-50)">
                <td style="color:var(--color-primary);font-size:.78rem;padding-left:1.5rem">
                    ↳ AVN-${a.tenant_id}-${a.id} <span style="color:var(--color-gray-400)">n°${a.avenant_number}</span>
                </td>
                <td colspan="2" style="font-size:.82rem;color:var(--color-gray-600)">${a.title || '—'}</td>
                <td></td>
                <td><strong>${formatAmount(a.amount)}</strong></td>
                <td><span class="badge badge--${a.status}">${STATUS_LABELS[a.status] || a.status}</span></td>
                <td style="display:flex;gap:.4rem;flex-wrap:wrap;">${aActions}</td>
            </tr>`;
        }).join('');

        return `
        <tr>
            <td style="color:var(--color-gray-400);font-size:.8rem">DEV-${q.tenant_id}-${q.id}</td>
            <td>${q.client_name || '—'}</td>
            <td>${q.job_title ? `<span style="font-size:.82rem;color:var(--color-primary)">🔨 ${q.job_title}</span>` : '—'}</td>
            <td>${q.title || '—'}</td>
            <td><strong>${formatAmount(q.amount)}</strong></td>
            <td><span class="badge badge--${q.status}">${STATUS_LABELS[q.status] || q.status}</span></td>
            <td style="display:flex;gap:.4rem;flex-wrap:wrap;">
                ${actions}
                <button class="btn btn--primary btn--sm" onclick="downloadPDF(${q.id})">PDF</button>
            </td>
        </tr>${avRows}`;
    }).join('');
}

// ===== TÉLÉCHARGEMENT PDF =====
async function downloadPDF(quoteId) {
    showToast('Génération du PDF…');
    const res = await apiFetch(`/api/quotes/${quoteId}/pdf`);
    if (!res || !res.ok) { showToast('Erreur génération PDF', 'danger'); return; }
    const q      = _quotesCache[quoteId] || {};
    const prefix = q.parent_quote_id ? 'AVN' : 'DEV';
    const name   = `${prefix}-${q.tenant_id || ''}-${quoteId}.pdf`;
    const blob   = await res.blob();
    const url    = URL.createObjectURL(blob);
    Object.assign(document.createElement('a'), { href: url, download: name }).click();
    URL.revokeObjectURL(url);
}

// ===== LIGNES DYNAMIQUES =====
function addLine(data = {}) {
    const tbody = document.getElementById('lines-body');
    const id    = lineCount++;
    const tr    = document.createElement('tr');
    tr.id = `line-${id}`;
    tr.innerHTML = `
        <td class="col-desig">
            <input type="text" placeholder="Dépose chaudière" oninput="recalc()" data-field="designation"
                   value="${data.designation || ''}">
        </td>
        <td class="col-desc">
            <input type="text" placeholder="Description optionnelle" data-field="description"
                   value="${data.description || ''}">
        </td>
        <td class="col-tva">
            <select onchange="recalc()" data-field="tva_rate">
                ${[20, 10, 5.5, 2.1, 0].map(r =>
                    `<option value="${r}" ${parseFloat(data.tva_rate || 10) === r ? 'selected' : ''}>${r}%</option>`
                ).join('')}
            </select>
        </td>
        <td class="col-qty">
            <input type="number" value="${data.quantity || 1}" min="1" step="1" oninput="recalc()" data-field="quantity">
        </td>
        <td class="col-pu">
            <input type="number" value="${data.unit_price || 0}" min="0" step="0.01" oninput="recalc()" data-field="unit_price">
        </td>
        <td class="col-total" id="total-${id}">0,00 €</td>
        <td class="col-del">
            <button type="button" onclick="removeLine(${id})"
                style="background:none;border:none;cursor:pointer;color:var(--color-danger);font-size:1rem">✕</button>
        </td>`;
    tbody.appendChild(tr);
    recalc();
}

function removeLine(id) {
    document.getElementById(`line-${id}`)?.remove();
    recalc();
}

function getLines() {
    return Array.from(document.querySelectorAll('#lines-body tr')).map(tr => ({
        designation: tr.querySelector('[data-field="designation"]').value,
        description: tr.querySelector('[data-field="description"]').value,
        tva_rate:    parseFloat(tr.querySelector('[data-field="tva_rate"]').value),
        quantity:    parseInt(tr.querySelector('[data-field="quantity"]').value) || 1,
        unit_price:  parseFloat(tr.querySelector('[data-field="unit_price"]').value) || 0,
    }));
}

function recalc() {
    const lines = getLines();
    let ht = 0, tva = 0;
    lines.forEach((l, i) => {
        const total = l.quantity * l.unit_price;
        ht  += total;
        tva += total * (l.tva_rate / 100);
        const cell = document.querySelector(`#lines-body tr:nth-child(${i + 1}) .col-total`);
        if (cell) cell.textContent = total.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
    });
    const summary = document.getElementById('total-summary');
    summary.style.display = lines.length ? '' : 'none';
    document.getElementById('sum-ht').textContent  = ht.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
    document.getElementById('sum-tva').textContent = tva.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
    document.getElementById('sum-ttc').textContent = (ht + tva).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
}

// ===== MODAL CRÉATION =====
function openModal() {
    editingQuoteId = null;
    document.querySelector('#modal-overlay h3').textContent = 'Nouveau devis';
    document.getElementById('quote-form').reset();
    document.getElementById('quote-job').innerHTML = '<option value="">— Sélectionner un client d\'abord —</option>';
    document.getElementById('quote-address').value = '';
    document.getElementById('lines-body').innerHTML = '';
    document.getElementById('total-summary').style.display = 'none';
    lineCount = 0;
    addLine();
    document.getElementById('modal-overlay').classList.remove('hidden');
}

// ===== MODAL MODIFICATION (brouillon) =====
async function openEditModal(quoteId) {
    const res = await apiFetch(`/api/quotes/${quoteId}`);
    if (!res) return;
    const quote = await res.json();

    const resLines = await apiFetch(`/api/quotes/${quoteId}/lines`);
    const lines    = resLines ? await resLines.json() : [];

    editingQuoteId = quoteId;
    document.querySelector('#modal-overlay h3').textContent = 'Modifier le devis';

    // Remplir les champs
    document.getElementById('quote-client').value  = quote.client_id || '';
    document.getElementById('quote-title').value   = quote.title || '';
    document.getElementById('quote-payment').value = quote.payment_terms || 'Comptant';
    document.getElementById('quote-expiry').value  = quote.expiry_date ? quote.expiry_date.slice(0, 10) : '';
    document.getElementById('quote-status').value  = quote.status || 'draft';
    document.getElementById('quote-notes').value   = quote.notes || '';

    // Charger les projets du client puis sélectionner le bon
    if (quote.client_id) {
        await onClientChange('quote');
        document.getElementById('quote-job').value = quote.job_id || '';
        // Déclencher l'auto-remplissage de l'adresse
        document.getElementById('quote-job').dispatchEvent(new Event('change'));
    }

    // Remplir les lignes
    document.getElementById('lines-body').innerHTML = '';
    lineCount = 0;
    if (lines.length) {
        lines.forEach(l => addLine(l));
    } else {
        addLine();
    }

    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal(event) {
    if (event && event.target !== document.getElementById('modal-overlay')) return;
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ===== SOUMISSION =====
async function handleSubmit(e) {
    e.preventDefault();
    const lines = getLines();
    if (!lines.length || !lines[0].designation) {
        showToast('Ajoutez au moins une ligne', 'danger'); return;
    }

    const jobId = document.getElementById('quote-job').value;
    if (!jobId) { showToast('Sélectionnez un projet', 'danger'); return; }

    const body = {
        client_id:     Number(document.getElementById('quote-client').value),
        job_id:        Number(jobId),
        title:         document.getElementById('quote-title').value,
        payment_terms: document.getElementById('quote-payment').value,
        expiry_date:   document.getElementById('quote-expiry').value || null,
        status:        document.getElementById('quote-status').value,
        notes:         document.getElementById('quote-notes').value,
        lines,
    };

    const url    = editingQuoteId ? `/api/quotes/${editingQuoteId}` : '/api/quotes/';
    const method = editingQuoteId ? 'PUT' : 'POST';

    const res = await apiFetch(url, { method, body: JSON.stringify(body) });
    if (!res) return;

    if (res.ok) {
        const quote = await res.json();
        document.getElementById('modal-overlay').classList.add('hidden');
        showToast(editingQuoteId ? 'Devis mis à jour' : 'Devis créé', 'success');
        loadQuotes(currentPage);
        if (!editingQuoteId) setTimeout(() => downloadPDF(quote.id), 500);
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== ACOMPTE =====
let _depositQuoteId = null;

function esc(v) { return (v || '').replace(/'/g, "\\'"); }

// ===== AVENANT =====
function openAvenantModal(quoteId, title) {
    _avenantQuoteId = quoteId;
    const q = _quotesCache[quoteId] || {};
    document.getElementById('avenant-quote-ref').textContent =
        `Avenant au devis DEV-${q.tenant_id || ''}-${quoteId}${title ? ' — ' + title : ''}`;
    document.getElementById('avenant-title').value  = '';
    document.getElementById('avenant-expiry').value = '';
    document.getElementById('avenant-notes').value  = '';
    document.getElementById('avenant-lines-body').innerHTML = '';
    document.getElementById('avenant-total-summary').style.display = 'none';
    avenantLineCount = 0;
    addAvenantLine();
    document.getElementById('modal-avenant').classList.remove('hidden');
}

function closeAvenantModal(event) {
    const overlay = document.getElementById('modal-avenant');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

function addAvenantLine(data = {}) {
    const tbody = document.getElementById('avenant-lines-body');
    const id    = avenantLineCount++;
    const tr    = document.createElement('tr');
    tr.id = `av-line-${id}`;
    tr.innerHTML = `
        <td class="col-desig">
            <input type="text" placeholder="Désignation" oninput="recalcAvenant()" data-field="designation"
                   value="${data.designation || ''}">
        </td>
        <td class="col-desc">
            <input type="text" placeholder="Description" data-field="description"
                   value="${data.description || ''}">
        </td>
        <td class="col-tva">
            <select onchange="recalcAvenant()" data-field="tva_rate">
                ${[20, 10, 5.5, 2.1, 0].map(r =>
                    `<option value="${r}" ${parseFloat(data.tva_rate || 10) === r ? 'selected' : ''}>${r}%</option>`
                ).join('')}
            </select>
        </td>
        <td class="col-qty">
            <input type="number" value="${data.quantity || 1}" min="1" step="1" oninput="recalcAvenant()" data-field="quantity">
        </td>
        <td class="col-pu">
            <input type="number" value="${data.unit_price || ''}" placeholder="0.00" step="0.01" min="0"
                   oninput="recalcAvenant()" data-field="unit_price">
        </td>
        <td class="col-total" id="av-total-${id}">0,00 €</td>
        <td class="col-del">
            <button type="button" onclick="document.getElementById('av-line-${id}').remove(); recalcAvenant();"
                    style="background:none;border:none;cursor:pointer;color:var(--color-gray-400);font-size:1.1rem">✕</button>
        </td>`;
    tbody.appendChild(tr);
    recalcAvenant();
}

function recalcAvenant() {
    const rows = document.querySelectorAll('#avenant-lines-body tr');
    let totalHt = 0, totalTva = 0;
    rows.forEach(tr => {
        const qty   = parseFloat(tr.querySelector('[data-field="quantity"]')?.value || 0);
        const pu    = parseFloat(tr.querySelector('[data-field="unit_price"]')?.value || 0);
        const tva   = parseFloat(tr.querySelector('[data-field="tva_rate"]')?.value || 10);
        const ht    = qty * pu;
        totalHt  += ht;
        totalTva += ht * tva / 100;
        const id = tr.id.replace('av-line-', '');
        const cell = document.getElementById(`av-total-${id}`);
        if (cell) cell.textContent = formatAmount(ht);
    });
    const summary = document.getElementById('avenant-total-summary');
    summary.style.display = totalHt > 0 ? '' : 'none';
    document.getElementById('av-sum-ht').textContent  = formatAmount(totalHt);
    document.getElementById('av-sum-tva').textContent = formatAmount(totalTva);
    document.getElementById('av-sum-ttc').textContent = formatAmount(totalHt + totalTva);
}

function _getAvenantLines() {
    return [...document.querySelectorAll('#avenant-lines-body tr')].map(tr => ({
        designation: tr.querySelector('[data-field="designation"]')?.value || '',
        description: tr.querySelector('[data-field="description"]')?.value || '',
        tva_rate:    parseFloat(tr.querySelector('[data-field="tva_rate"]')?.value || 10),
        quantity:    parseFloat(tr.querySelector('[data-field="quantity"]')?.value || 1),
        unit_price:  parseFloat(tr.querySelector('[data-field="unit_price"]')?.value || 0),
    }));
}

async function submitAvenant(e) {
    e.preventDefault();
    const lines = _getAvenantLines();
    if (!lines.some(l => l.designation && l.unit_price > 0)) {
        showToast('Ajoutez au moins une ligne avec désignation et prix', 'danger');
        return;
    }
    const body = {
        title:       document.getElementById('avenant-title').value || null,
        expiry_date: document.getElementById('avenant-expiry').value || null,
        notes:       document.getElementById('avenant-notes').value || null,
        lines,
    };
    const res = await apiFetch(`/api/quotes/${_avenantQuoteId}/avenant`, {
        method: 'POST', body: JSON.stringify(body),
    });
    if (res?.ok) {
        closeAvenantModal();
        showToast('Avenant créé', 'success');
        loadQuotes(currentPage);
    } else {
        showToast('Erreur lors de la création', 'danger');
    }
}

// ===== FACTURE D'ACOMPTE =====
function openDepositModal(quoteId, title, amount) {
    _depositQuoteId = quoteId;
    document.getElementById('deposit-quote-ref').textContent =
        `DEV-…-${quoteId}${title ? ' — ' + title : ''}`;
    document.getElementById('deposit-quote-ht').textContent  =
        `(Total HT du devis : ${formatAmount(amount)})`;
    document.getElementById('deposit-type').value    = 'percent';
    document.getElementById('deposit-value').value   = '30';
    document.getElementById('deposit-due').value     = '';
    document.getElementById('deposit-notes').value   = '';
    toggleDepositLabel();
    document.getElementById('modal-deposit').classList.remove('hidden');
}

function toggleDepositLabel() {
    const type = document.getElementById('deposit-type').value;
    document.getElementById('deposit-value-label').textContent =
        type === 'percent' ? 'Pourcentage (%)' : 'Montant HT (€)';
}

function closeDepositModal(event) {
    const overlay = document.getElementById('modal-deposit');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function submitDeposit(e) {
    e.preventDefault();
    const body = {
        quote_id:      _depositQuoteId,
        deposit_type:  document.getElementById('deposit-type').value,
        deposit_value: parseFloat(document.getElementById('deposit-value').value),
        due_date:      document.getElementById('deposit-due').value || null,
        notes:         document.getElementById('deposit-notes').value || null,
    };
    const res = await apiFetch('/api/invoices/deposit', { method: 'POST', body: JSON.stringify(body) });
    if (res?.ok) {
        document.getElementById('modal-deposit').classList.add('hidden');
        showToast('Facture d\'acompte créée', 'success');
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

async function createFinalInvoice(quoteId, title) {
    const due = prompt(`Facture finale — DEV-…-${quoteId}${title ? ' (' + title + ')' : ''}\nDate d'échéance (YYYY-MM-DD, optionnel) :`, '');
    if (due === null) return; // annulé
    const body = { quote_id: quoteId, due_date: due || null };
    const res  = await apiFetch('/api/invoices/final', { method: 'POST', body: JSON.stringify(body) });
    if (res?.ok) {
        showToast('Facture finale créée', 'success');
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== MODAL STATUT =====
function openStatusModal(id, status) {
    currentQuoteId = id;
    document.getElementById('status-select').value = status;
    document.getElementById('modal-status-overlay').classList.remove('hidden');
}

function closeStatusModal(event) {
    if (event && event.target !== document.getElementById('modal-status-overlay')) return;
    document.getElementById('modal-status-overlay').classList.add('hidden');
}

async function saveStatus() {
    const status = document.getElementById('status-select').value;
    const res = await apiFetch(`/api/quotes/${currentQuoteId}/status`, {
        method: 'PATCH', body: JSON.stringify({ status }),
    });
    if (res?.ok) {
        const data = await res.json();
        if (_quotesCache[currentQuoteId]) {
            Object.assign(_quotesCache[currentQuoteId], data);
        }
        closeStatusModal();

        if (status === 'sent') {
            if (data.email_warning) {
                showToast(`Statut mis à jour — email non envoyé : ${data.email_warning}`, 'error');
            } else {
                showToast('Devis envoyé par email au client ✓', 'success');
            }
        } else {
            showToast('Statut mis à jour', 'success');
        }

        loadQuotes(currentPage);
    }
}

async function deleteQuote() {
    if (!confirm('Supprimer ce devis ?')) return;
    const res = await apiFetch(`/api/quotes/${currentQuoteId}`, { method: 'DELETE' });
    if (res?.ok) { closeStatusModal(); showToast('Devis supprimé'); loadQuotes(currentPage); }
}
