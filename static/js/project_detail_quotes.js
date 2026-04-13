// ===== PROJECT_DETAIL_QUOTES.JS — Devis & Factures depuis le projet =====

let _pjLineCount    = 0;
let _pjQuoteId      = null;   // pour modal statut devis
let _depositQuoteId = null;
let _pjInvoiceId    = null;   // pour modal statut facture
let _avenantQuoteId = null;
let _avenantLineCount = 0;

function formatAmountPj(n) {
    return Number(n || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
}

// ===== LIGNES DU DEVIS =====
function pjAddLine(data = {}) {
    const tbody = document.getElementById('pj-lines-body');
    const id    = _pjLineCount++;
    const tr    = document.createElement('tr');
    tr.id = `pj-line-${id}`;
    tr.innerHTML = `
        <td class="col-desig">
            <input type="text" placeholder="Dépose chaudière" oninput="pjRecalc()" data-field="designation"
                   value="${data.designation || ''}">
        </td>
        <td class="col-desc">
            <input type="text" placeholder="Description optionnelle" data-field="description"
                   value="${data.description || ''}">
        </td>
        <td class="col-tva">
            <select onchange="pjRecalc()" data-field="tva_rate">
                ${[20, 10, 5.5, 2.1, 0].map(r =>
                    `<option value="${r}" ${parseFloat(data.tva_rate || 10) === r ? 'selected' : ''}>${r}%</option>`
                ).join('')}
            </select>
        </td>
        <td class="col-qty">
            <input type="number" value="${data.quantity || 1}" min="1" step="1" oninput="pjRecalc()" data-field="quantity">
        </td>
        <td class="col-pu">
            <input type="number" value="${data.unit_price || ''}" placeholder="0.00" min="0" step="0.01"
                   oninput="pjRecalc()" data-field="unit_price">
        </td>
        <td class="col-total" id="pj-total-${id}">0,00 €</td>
        <td class="col-del">
            <button type="button" onclick="document.getElementById('pj-line-${id}').remove(); pjRecalc();"
                    style="background:none;border:none;cursor:pointer;color:var(--color-danger);font-size:1rem">✕</button>
        </td>`;
    tbody.appendChild(tr);
    pjRecalc();
}

function pjRecalc() {
    const rows = document.querySelectorAll('#pj-lines-body tr');
    let ht = 0, tva = 0;
    rows.forEach(tr => {
        const qty   = parseFloat(tr.querySelector('[data-field="quantity"]')?.value || 0);
        const pu    = parseFloat(tr.querySelector('[data-field="unit_price"]')?.value || 0);
        const rate  = parseFloat(tr.querySelector('[data-field="tva_rate"]')?.value || 10);
        const total = qty * pu;
        ht  += total;
        tva += total * rate / 100;
        const id   = tr.id.replace('pj-line-', '');
        const cell = document.getElementById(`pj-total-${id}`);
        if (cell) cell.textContent = formatAmountPj(total);
    });
    const summary = document.getElementById('pj-total-summary');
    summary.style.display = ht > 0 ? '' : 'none';
    document.getElementById('pj-sum-ht').textContent  = formatAmountPj(ht);
    document.getElementById('pj-sum-tva').textContent = formatAmountPj(tva);
    document.getElementById('pj-sum-ttc').textContent = formatAmountPj(ht + tva);
}

function pjGetLines() {
    return [...document.querySelectorAll('#pj-lines-body tr')].map(tr => ({
        designation: tr.querySelector('[data-field="designation"]').value,
        description: tr.querySelector('[data-field="description"]').value,
        tva_rate:    parseFloat(tr.querySelector('[data-field="tva_rate"]').value),
        quantity:    parseInt(tr.querySelector('[data-field="quantity"]').value) || 1,
        unit_price:  parseFloat(tr.querySelector('[data-field="unit_price"]').value) || 0,
    }));
}

// ===== MODAL NOUVEAU DEVIS =====
function openQuoteModal() {
    document.getElementById('quote-form').reset();
    document.getElementById('pj-lines-body').innerHTML = '';
    document.getElementById('pj-total-summary').style.display = 'none';
    _pjLineCount = 0;
    pjAddLine();
    document.getElementById('modal-quote').classList.remove('hidden');
}

function closeQuoteModal(event) {
    const overlay = document.getElementById('modal-quote');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function handleQuoteSubmit(e) {
    e.preventDefault();
    const lines = pjGetLines();
    if (!lines.length || !lines[0].designation) {
        showToast('Ajoutez au moins une ligne', 'danger'); return;
    }
    const body = {
        client_id:     jobData.client_id,
        job_id:        jobId,
        title:         document.getElementById('pj-quote-title').value,
        payment_terms: document.getElementById('pj-quote-payment').value,
        expiry_date:   document.getElementById('pj-quote-expiry').value || null,
        status:        document.getElementById('pj-quote-status').value,
        notes:         document.getElementById('pj-quote-notes').value,
        lines,
    };
    const res = await apiFetch('/api/quotes/', { method: 'POST', body: JSON.stringify(body) });
    if (!res) return;
    if (res.ok) {
        const quote = await res.json();
        closeQuoteModal();
        showToast('Devis créé', 'success');
        loadSummary();
        setTimeout(() => downloadQuotePDF(quote.id), 600);
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== PDF DEVIS =====
async function downloadQuotePDF(quoteId) {
    showToast('Génération du PDF…');
    const res = await apiFetch(`/api/quotes/${quoteId}/pdf`);
    if (!res?.ok) { showToast('Erreur génération PDF', 'danger'); return; }
    const q      = _pjQuoteCache[quoteId] || {};
    const prefix = q.parent_quote_id ? 'AVN' : 'DEV';
    const name   = `${prefix}-${q.tenant_id || ''}-${quoteId}.pdf`;
    const blob   = await res.blob();
    const url    = URL.createObjectURL(blob);
    Object.assign(document.createElement('a'), { href: url, download: name }).click();
    URL.revokeObjectURL(url);
}

// ===== STATUT DEVIS =====
function openQuoteStatusModal(id, status) {
    _pjQuoteId = id;
    document.getElementById('pj-status-select').value = status;
    document.getElementById('modal-quote-status').classList.remove('hidden');
}

function closeQuoteStatusModal(event) {
    const overlay = document.getElementById('modal-quote-status');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function saveQuoteStatus() {
    const status = document.getElementById('pj-status-select').value;
    const res = await apiFetch(`/api/quotes/${_pjQuoteId}/status`, {
        method: 'PATCH', body: JSON.stringify({ status }),
    });
    if (res?.ok) {
        closeQuoteStatusModal();
        showToast('Statut mis à jour', 'success');
        loadSummary();
    } else {
        showToast('Erreur', 'danger');
    }
}

async function deleteQuote() {
    if (!confirm('Supprimer ce devis ?')) return;
    const res = await apiFetch(`/api/quotes/${_pjQuoteId}`, { method: 'DELETE' });
    if (res?.ok) { closeQuoteStatusModal(); showToast('Devis supprimé'); loadSummary(); }
}

// ===== FACTURE D'ACOMPTE =====
function openDepositModal(quoteId, title, amount) {
    _depositQuoteId = quoteId;
    document.getElementById('deposit-quote-ref').textContent =
        `DEV-…-${quoteId}${title ? ' — ' + title : ''}`;
    document.getElementById('deposit-quote-ht').textContent =
        `(Total HT du devis : ${formatAmountPj(amount)})`;
    document.getElementById('deposit-type').value  = 'percent';
    document.getElementById('deposit-value').value = '30';
    document.getElementById('deposit-due').value   = '';
    document.getElementById('deposit-notes').value = '';
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
        loadSummary();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== FACTURE FINALE =====
async function createFinalInvoice(quoteId, title) {
    const due = prompt(`Facture finale — DEV-…-${quoteId}${title ? ' (' + title + ')' : ''}\nDate d'échéance (YYYY-MM-DD, optionnel) :`, '');
    if (due === null) return;
    const body = { quote_id: quoteId, due_date: due || null };
    const res  = await apiFetch('/api/invoices/final', { method: 'POST', body: JSON.stringify(body) });
    if (res?.ok) {
        showToast('Facture finale créée', 'success');
        loadSummary();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur', 'danger');
    }
}

// ===== STATUT FACTURE =====
function openInvoiceStatusModal(id, status) {
    _pjInvoiceId = id;
    document.getElementById('pj-invoice-status-select').value = status;
    document.getElementById('modal-invoice-status').classList.remove('hidden');
}

function closeInvoiceStatusModal(event) {
    const overlay = document.getElementById('modal-invoice-status');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

async function saveInvoiceStatus() {
    const status = document.getElementById('pj-invoice-status-select').value;
    const res = await apiFetch(`/api/invoices/${_pjInvoiceId}/status`, {
        method: 'PATCH', body: JSON.stringify({ status }),
    });
    if (res?.ok) {
        closeInvoiceStatusModal();
        showToast('Facture mise à jour', 'success');
        loadSummary();
    } else {
        showToast('Erreur', 'danger');
    }
}

// ===== AVENANT =====
function openAvenantModal(quoteId, title) {
    _avenantQuoteId = quoteId;
    const q = _pjQuoteCache[quoteId] || {};
    document.getElementById('avenant-quote-ref').textContent =
        `Avenant au devis DEV-${q.tenant_id || ''}-${quoteId}${title ? ' — ' + title : ''}`;
    document.getElementById('avenant-title').value  = '';
    document.getElementById('avenant-expiry').value = '';
    document.getElementById('avenant-notes').value  = '';
    document.getElementById('avenant-lines-body').innerHTML = '';
    document.getElementById('avenant-total-summary').style.display = 'none';
    _avenantLineCount = 0;
    avenantAddLine();
    document.getElementById('modal-avenant').classList.remove('hidden');
}

function closeAvenantModal(event) {
    const overlay = document.getElementById('modal-avenant');
    if (event && event.target !== overlay) return;
    overlay.classList.add('hidden');
}

function avenantAddLine(data = {}) {
    const tbody = document.getElementById('avenant-lines-body');
    const id    = _avenantLineCount++;
    const tr    = document.createElement('tr');
    tr.id = `av-line-${id}`;
    tr.innerHTML = `
        <td class="col-desig">
            <input type="text" placeholder="Désignation" oninput="avenantRecalc()" data-field="designation"
                   value="${data.designation || ''}">
        </td>
        <td class="col-desc">
            <input type="text" placeholder="Description" data-field="description"
                   value="${data.description || ''}">
        </td>
        <td class="col-tva">
            <select onchange="avenantRecalc()" data-field="tva_rate">
                ${[20, 10, 5.5, 2.1, 0].map(r =>
                    `<option value="${r}" ${parseFloat(data.tva_rate || 10) === r ? 'selected' : ''}>${r}%</option>`
                ).join('')}
            </select>
        </td>
        <td class="col-qty">
            <input type="number" value="${data.quantity || 1}" min="1" step="1" oninput="avenantRecalc()" data-field="quantity">
        </td>
        <td class="col-pu">
            <input type="number" value="${data.unit_price || ''}" placeholder="0.00" step="0.01" min="0"
                   oninput="avenantRecalc()" data-field="unit_price">
        </td>
        <td class="col-total" id="av-total-${id}">0,00 €</td>
        <td class="col-del">
            <button type="button" onclick="document.getElementById('av-line-${id}').remove(); avenantRecalc();"
                    style="background:none;border:none;cursor:pointer;color:var(--color-danger);font-size:1rem">✕</button>
        </td>`;
    tbody.appendChild(tr);
    avenantRecalc();
}

function avenantRecalc() {
    const rows = document.querySelectorAll('#avenant-lines-body tr');
    let ht = 0, tva = 0;
    rows.forEach(tr => {
        const qty  = parseFloat(tr.querySelector('[data-field="quantity"]')?.value || 0);
        const pu   = parseFloat(tr.querySelector('[data-field="unit_price"]')?.value || 0);
        const rate = parseFloat(tr.querySelector('[data-field="tva_rate"]')?.value || 10);
        const total = qty * pu;
        ht  += total;
        tva += total * rate / 100;
        const id   = tr.id.replace('av-line-', '');
        const cell = document.getElementById(`av-total-${id}`);
        if (cell) cell.textContent = formatAmountPj(total);
    });
    const summary = document.getElementById('avenant-total-summary');
    summary.style.display = ht > 0 ? '' : 'none';
    document.getElementById('av-sum-ht').textContent  = formatAmountPj(ht);
    document.getElementById('av-sum-tva').textContent = formatAmountPj(tva);
    document.getElementById('av-sum-ttc').textContent = formatAmountPj(ht + tva);
}

function avenantGetLines() {
    return [...document.querySelectorAll('#avenant-lines-body tr')].map(tr => ({
        designation: tr.querySelector('[data-field="designation"]').value,
        description: tr.querySelector('[data-field="description"]').value,
        tva_rate:    parseFloat(tr.querySelector('[data-field="tva_rate"]').value),
        quantity:    parseFloat(tr.querySelector('[data-field="quantity"]').value) || 1,
        unit_price:  parseFloat(tr.querySelector('[data-field="unit_price"]').value) || 0,
    }));
}

async function handleAvenantSubmit(e) {
    e.preventDefault();
    const lines = avenantGetLines();
    if (!lines.some(l => l.designation && l.unit_price > 0)) {
        showToast('Ajoutez au moins une ligne avec désignation et prix', 'danger');
        return;
    }
    const body = {
        title:       document.getElementById('avenant-title').value   || null,
        expiry_date: document.getElementById('avenant-expiry').value  || null,
        notes:       document.getElementById('avenant-notes').value   || null,
        lines,
    };
    const res = await apiFetch(`/api/quotes/${_avenantQuoteId}/avenant`, {
        method: 'POST', body: JSON.stringify(body),
    });
    if (res?.ok) {
        closeAvenantModal();
        showToast('Avenant créé', 'success');
        loadSummary();
    } else {
        const err = await res.json().catch(() => ({}));
        showToast(err.error || 'Erreur lors de la création', 'danger');
    }
}

// ===== PDF FACTURE =====
async function downloadInvoicePDF(invoiceId) {
    showToast('Génération du PDF…');
    const res = await apiFetch(`/api/invoices/${invoiceId}/pdf`);
    if (!res?.ok) { showToast('Erreur génération PDF', 'danger'); return; }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    Object.assign(document.createElement('a'), { href: url, download: `facture-${invoiceId}.pdf` }).click();
    URL.revokeObjectURL(url);
}
