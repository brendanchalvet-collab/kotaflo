// ===== PROFILE.JS =====

const token = localStorage.getItem('token');
if (!token) window.location.href = '/login';

const FIELDS = [
    'company_name', 'address', 'zip_code', 'city',
    'phone', 'email', 'website',
    'siret', 'tva_number', 'rge_number', 'insurance_info',
    'iban', 'bic'
];

// ===== HELPERS =====
function authHeaders() {
    return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

function showToast(msg, type = '') {
    const t = document.createElement('div');
    t.className = `toast ${type ? 'toast--' + type : ''}`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 3000);
}

function val(id) {
    return document.getElementById(id)?.value?.trim() || '';
}

// ===== INIT =====
document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
    checkGmailStatus();
    FIELDS.forEach(f => {
        document.getElementById(f)?.addEventListener('input', updatePreview);
    });
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const el = document.getElementById('sidebar-name');
        if (el) el.textContent = payload.sub || '';
        const av = document.getElementById('sidebar-avatar');
        if (av && payload.sub) av.textContent = payload.sub[0].toUpperCase();
    } catch (_) {}

    // Toast si retour OAuth Google
    const params = new URLSearchParams(window.location.search);
    if (params.get('gmail') === 'connected') {
        showToast('Gmail connecté avec succès !', 'success');
        history.replaceState({}, '', '/profile');
    } else if (params.get('gmail') === 'error') {
        showToast('Erreur lors de la connexion Gmail', 'danger');
        history.replaceState({}, '', '/profile');
    }
});

// ===== CHARGEMENT =====
async function loadProfile() {
    const res  = await fetch('/api/profile/', { headers: authHeaders() });
    const data = await res.json();

    FIELDS.forEach(f => {
        const el = document.getElementById(f);
        if (el) el.value = data[f] || '';
    });

    updatePreview();
}

// ===== APERÇU EN TEMPS RÉEL =====
function updatePreview() {
    const name    = val('company_name') || '—';
    const address = val('address');
    const city    = [val('zip_code'), val('city')].filter(Boolean).join(' ');
    const contact = [
        val('phone') ? `Tel : ${val('phone')}` : '',
        val('email') ? `Email : ${val('email')}` : '',
    ].filter(Boolean).join('  |  ');
    const siret   = val('siret') ? `SIRET : ${val('siret')}` : '';
    const tva     = val('tva_number') ? `  ·  TVA : ${val('tva_number')}` : '';

    document.getElementById('prev-name').textContent    = name;
    document.getElementById('prev-address').textContent = address;
    document.getElementById('prev-city').textContent    = city;
    document.getElementById('prev-contact').textContent = contact;
    document.getElementById('prev-siret').textContent   = siret + tva;
}

// ===== GMAIL =====
async function checkGmailStatus() {
    const res  = await fetch('/api/profile/', { headers: authHeaders() });
    const data = await res.json();
    const connected = !!data.google_connected;

    document.getElementById('gmail-badge').textContent = connected
        ? '✓ Gmail connecté'
        : 'Non connecté';
    document.getElementById('gmail-badge').style.color = connected
        ? 'var(--color-success)'
        : 'var(--color-gray-400)';
    document.getElementById('gmail-btn').style.display            = connected ? 'none'  : '';
    document.getElementById('gmail-disconnect-btn').style.display = connected ? ''      : 'none';
}

async function connectGmail() {
    const res = await fetch('/api/google/auth', { headers: authHeaders() });
    if (!res.ok) { showToast('Erreur', 'danger'); return; }
    const { auth_url } = await res.json();
    window.location.href = auth_url;
}

async function disconnectGmail() {
    if (!confirm('Déconnecter Gmail ?')) return;
    const res = await fetch('/api/google/disconnect', { method: 'DELETE', headers: authHeaders() });
    if (res.ok) { showToast('Gmail déconnecté'); checkGmailStatus(); }
}

// ===== SAUVEGARDE =====
async function handleSubmit(e) {
    e.preventDefault();
    const btn = document.getElementById('btn-save');
    btn.disabled    = true;
    btn.textContent = 'Enregistrement…';

    const body = {};
    FIELDS.forEach(f => { body[f] = val(f) || null; });

    const res = await fetch('/api/profile/', {
        method:  'PUT',
        headers: authHeaders(),
        body:    JSON.stringify(body),
    });

    if (res.ok) {
        showToast('Profil enregistré', 'success');
    } else {
        showToast('Erreur lors de la sauvegarde', 'danger');
    }

    btn.disabled    = false;
    btn.textContent = 'Enregistrer les modifications';
}
