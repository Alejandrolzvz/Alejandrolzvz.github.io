import os

content = """const API_URL = '/api';
let token = localStorage.getItem('token') || null;
let currentUser = null;
let equipos = [];
let tipos = [];
let marcas = [];
let settings = {};

// DOM Elements
const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const currentUsername = document.getElementById('current-username');

// Sections
const sectionEquipos = document.getElementById('section-equipos');
const sectionGenerator = document.getElementById('section-generator');
const sectionUsers = document.getElementById('section-users');
const sectionCatalogos = document.getElementById('section-catalogos');

// Nav Buttons
const btnShowEquipos = document.getElementById('btn-show-equipos');
const btnShowGenerator = document.getElementById('btn-show-generator');
const adminUsersBtn = document.getElementById('admin-users-btn');
const adminCatalogosBtn = document.getElementById('admin-catalogos-btn');
const btnLogout = document.getElementById('btn-logout');

const allSections = [sectionEquipos, sectionGenerator, sectionUsers, sectionCatalogos];
const allNavBtns = [btnShowEquipos, btnShowGenerator, adminUsersBtn, adminCatalogosBtn];

if (token) {
    fetchCurrentUser();
}

// ==================== AUTH ====================
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('username').value;
    const p = document.getElementById('password').value;
    
    const formData = new URLSearchParams();
    formData.append('username', u);
    formData.append('password', p);

    try {
        const res = await fetch(`${API_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });
        if (!res.ok) throw new Error('Credenciales incorrectas');
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        loginError.classList.add('hidden');
        await fetchCurrentUser();
    } catch (err) {
        loginError.textContent = err.message;
        loginError.classList.remove('hidden');
    }
});

btnLogout.addEventListener('click', () => {
    token = null;
    localStorage.removeItem('token');
    currentUser = null;
    showView(loginView);
});

async function fetchCurrentUser() {
    try {
        const res = await fetch(`${API_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Token inválido');
        currentUser = await res.json();
        currentUsername.textContent = currentUser.username;
        
        if (currentUser.is_superadmin) {
            adminUsersBtn.classList.remove('hidden');
        } else {
            adminUsersBtn.classList.add('hidden');
        }
        
        if (currentUser.is_superadmin || currentUser.is_admin) {
            adminCatalogosBtn.classList.remove('hidden');
        } else {
            adminCatalogosBtn.classList.add('hidden');
        }
        
        showView(dashboardView);
        await loadSettings();
        loadEquipos();
        loadTipos();
        loadMarcas();
    } catch (err) {
        token = null;
        localStorage.removeItem('token');
        showView(loginView);
    }
}

// ==================== SETTINGS ====================
async function loadSettings() {
    try {
        const res = await fetch(`${API_URL}/settings`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando config');
        const data = await res.json();
        data.forEach(s => settings[s.key] = s.value);
        applySettings();
    } catch(err) {
        console.error(err);
    }
}

function applySettings() {
    const showSerieAnt = settings['show_serie_ant'] === 'true';
    document.querySelectorAll('.col-serie-ant').forEach(el => {
        if (showSerieAnt) el.classList.remove('hidden');
        else el.classList.add('hidden');
    });
    
    const cb = document.getElementById('config-show-serie-ant');
    if (cb) cb.checked = showSerieAnt;
}

document.getElementById('btn-save-config')?.addEventListener('click', async () => {
    if (!currentUser?.is_superadmin) return;
    const val = document.getElementById('config-show-serie-ant').checked ? 'true' : 'false';
    try {
        await fetch(`${API_URL}/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ key: 'show_serie_ant', value: val })
        });
        document.getElementById('config-msg').textContent = 'Configuración guardada';
        document.getElementById('config-msg').classList.remove('hidden');
        settings['show_serie_ant'] = val;
        applySettings();
        setTimeout(() => document.getElementById('config-msg').classList.add('hidden'), 3000);
    } catch(err) {
        alert('Error al guardar configuración');
    }
});


// ==================== CREATE USER ====================
document.getElementById('create-user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentUser?.is_superadmin) return;
    
    const u = document.getElementById('new-username').value;
    const p = document.getElementById('new-password').value;
    const isSuperadmin = document.getElementById('new-is-superadmin').checked;
    const isAdmin = document.getElementById('new-is-admin').checked;
    const msg = document.getElementById('user-msg');

    try {
        const res = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ username: u, password: p, is_superadmin: isSuperadmin, is_admin: isAdmin })
        });
        if (!res.ok) throw new Error('Error al crear usuario');
        msg.textContent = 'Usuario creado exitosamente';
        msg.style.color = '#4ade80';
        msg.classList.remove('hidden');
        e.target.reset();
    } catch (err) {
        msg.textContent = err.message;
        msg.classList.remove('hidden');
        msg.style.color = 'var(--danger)';
    }
});

// ==================== NAVIGATION ====================
function showView(view) {
    loginView.classList.add('hidden');
    dashboardView.classList.add('hidden');
    view.classList.remove('hidden');
}

function switchSection(section, btn) {
    allSections.forEach(s => {
        s.classList.add('hidden');
        s.classList.remove('active-section');
    });
    allNavBtns.forEach(b => b.classList.remove('active'));
    section.classList.remove('hidden');
    section.classList.add('active-section');
    btn.classList.add('active');
}

btnShowEquipos.addEventListener('click', () => switchSection(sectionEquipos, btnShowEquipos));
btnShowGenerator.addEventListener('click', () => { switchSection(sectionGenerator, btnShowGenerator); renderGeneratorList(); });
adminUsersBtn.addEventListener('click', () => switchSection(sectionUsers, adminUsersBtn));
adminCatalogosBtn.addEventListener('click', () => { switchSection(sectionCatalogos, adminCatalogosBtn); loadTipos(); loadMarcas(); });

// ==================== EQUIPOS CRUD ====================
async function loadEquipos() {
    try {
        const res = await fetch(`${API_URL}/equipos`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando equipos');
        equipos = await res.json();
        renderTable();
    } catch (err) {
        console.error(err);
    }
}

function renderTable() {
    const tbody = document.querySelector('#equipos-table tbody');
    tbody.innerHTML = '';
    const showSerieAnt = settings['show_serie_ant'] === 'true';
    
    equipos.forEach(eq => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${eq.serie || '-'}</td>
            <td>${eq.marca || '-'}</td>
            <td class="col-serie-ant ${showSerieAnt ? '' : 'hidden'}">${eq.serie_ant || '-'}</td>
            <td>${eq.cliente || '-'}</td>
            <td>${eq.fecha_compra || '-'}</td>
            <td>${eq.fisicamente || '-'}</td>
            <td class="action-links">
                <button onclick="editEquipo(${eq.id})">Editar</button>
                ${currentUser?.is_superadmin ? `<button class="del" onclick="deleteEquipo(${eq.id})">Eliminar</button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Modal handling
const modal = document.getElementById('equipo-modal');
const equipoForm = document.getElementById('equipo-form');
const eqTipoSelect = document.getElementById('eq-tipo');
const eqSerieInput = document.getElementById('eq-serie');
const eqMarcaSelect = document.getElementById('eq-marca');

// Tabs in Modal
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.remove('hidden');
    });
});

document.getElementById('btn-add-equipo').addEventListener('click', () => {
    equipoForm.reset();
    document.getElementById('eq-id').value = '';
    document.getElementById('modal-title').textContent = 'Nuevo Equipo';
    eqSerieInput.value = '';
    eqSerieInput.readOnly = true;
    eqSerieInput.style.opacity = '0.7';
    eqSerieInput.style.cursor = 'not-allowed';
    
    document.getElementById('eq-desc-prefix').value = '';
    
    // Select first tab
    document.querySelector('.tab-btn[data-tab="tab-datos"]').click();
    
    populateTipoDropdown();
    populateMarcaDropdown();
    modal.classList.remove('hidden');
});

document.getElementById('btn-cancel-modal').addEventListener('click', () => modal.classList.add('hidden'));

function populateTipoDropdown() {
    eqTipoSelect.innerHTML = '<option value="">— Seleccionar tipo —</option>';
    tipos.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.prefix;
        opt.textContent = `${t.prefix} - ${t.description || ''}`;
        opt.dataset.desc = t.description || '';
        eqTipoSelect.appendChild(opt);
    });
}

function populateMarcaDropdown() {
    eqMarcaSelect.innerHTML = '<option value="">— Sin Marca —</option>';
    marcas.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m.name;
        opt.textContent = m.name;
        eqMarcaSelect.appendChild(opt);
    });
}

// Auto-fill serial and description when tipo changes (only for new equipos)
eqTipoSelect.addEventListener('change', async () => {
    const prefix = eqTipoSelect.value;
    const isEditing = !!document.getElementById('eq-id').value;
    
    // Update prefix description
    const selectedOpt = eqTipoSelect.options[eqTipoSelect.selectedIndex];
    document.getElementById('eq-desc-prefix').value = selectedOpt ? selectedOpt.dataset.desc || '' : '';

    if (!prefix || isEditing) {
        if (!isEditing) eqSerieInput.value = '';
        return;
    }
    
    try {
        const res = await fetch(`${API_URL}/equipos/next-serial/${prefix}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Error obteniendo serie');
        const data = await res.json();
        eqSerieInput.value = data.serial;
    } catch (err) {
        console.error(err);
        eqSerieInput.value = '';
    }
});

equipoForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('eq-id').value;
    
    // Combine desc
    const pref = document.getElementById('eq-desc-prefix').value.trim();
    const ext = document.getElementById('eq-desc-extra').value.trim();
    const finalDesc = pref ? (ext ? `${pref} ${ext}` : pref) : ext;

    const payload = {
        serie: document.getElementById('eq-serie').value,
        marca: document.getElementById('eq-marca').value,
        serie_fabrica: document.getElementById('eq-serie-fabrica').value,
        num_factura: document.getElementById('eq-num-factura').value,
        fecha_compra: document.getElementById('eq-fecha').value,
        descripcion: finalDesc,
        serie_ant: document.getElementById('eq-serie-ant').value,
        
        cliente: document.getElementById('eq-cliente').value,
        fisicamente: document.getElementById('eq-fisica').value,
        observacion: document.getElementById('eq-obs').value,
    };
    
    const method = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/equipos/${id}` : `${API_URL}/equipos`;

    try {
        const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error('Error al guardar');
        modal.classList.add('hidden');
        loadEquipos();
    } catch (err) {
        alert(err.message);
    }
});

window.editEquipo = (id) => {
    const eq = equipos.find(e => e.id === id);
    if(!eq) return;
    document.getElementById('eq-id').value = eq.id;
    document.getElementById('eq-serie').value = eq.serie || '';
    
    populateTipoDropdown();
    populateMarcaDropdown();
    
    document.getElementById('eq-marca').value = eq.marca || '';
    document.getElementById('eq-serie-fabrica').value = eq.serie_fabrica || '';
    document.getElementById('eq-num-factura').value = eq.num_factura || '';
    document.getElementById('eq-fecha').value = eq.fecha_compra || '';
    document.getElementById('eq-serie-ant').value = eq.serie_ant || '';
    document.getElementById('eq-cliente').value = eq.cliente || '';
    document.getElementById('eq-fisica').value = eq.fisicamente || '';
    document.getElementById('eq-obs').value = eq.observacion || '';
    
    // For description, we need to extract prefix if possible, or just dump it all to extra
    let prefix = '';
    if (eq.serie) {
        const parts = eq.serie.split('-');
        if (parts.length >= 1) {
            eqTipoSelect.value = parts[0];
            const selectedOpt = eqTipoSelect.options[eqTipoSelect.selectedIndex];
            prefix = selectedOpt ? selectedOpt.dataset.desc || '' : '';
        }
    }
    document.getElementById('eq-desc-prefix').value = prefix;
    
    let extra = eq.descripcion || '';
    if (prefix && extra.startsWith(prefix)) {
        extra = extra.substring(prefix.length).trim();
    }
    document.getElementById('eq-desc-extra').value = extra;
    
    eqSerieInput.readOnly = false;
    eqSerieInput.style.opacity = '1';
    eqSerieInput.style.cursor = 'text';
    
    document.querySelector('.tab-btn[data-tab="tab-datos"]').click();
    document.getElementById('modal-title').textContent = 'Editar Equipo';
    modal.classList.remove('hidden');
}

window.deleteEquipo = async (id) => {
    if(!currentUser?.is_superadmin) return alert('No tienes permisos');
    if(!confirm('¿Estás seguro de eliminar este equipo?')) return;
    try {
        const res = await fetch(`${API_URL}/equipos/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Error al eliminar');
        loadEquipos();
    } catch (err) {
        alert(err.message);
    }
}

// ==================== CATALOGOS ====================
async function loadTipos() {
    try {
        const res = await fetch(`${API_URL}/tipos`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando tipos');
        tipos = await res.json();
        renderTiposTable();
    } catch (err) {
        console.error(err);
    }
}

function renderTiposTable() {
    const tbody = document.querySelector('#tipos-table tbody');
    tbody.innerHTML = '';
    tipos.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${t.prefix}</strong></td>
            <td>${t.description || '-'}</td>
            <td class="action-links">
                ${currentUser?.is_superadmin ? `<button class="del" onclick="deleteTipo(${t.id})">Eliminar</button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

document.getElementById('btn-add-tipo').addEventListener('click', () => {
    document.getElementById('tipo-form-container').classList.remove('hidden');
});
document.getElementById('btn-cancel-tipo').addEventListener('click', () => {
    document.getElementById('tipo-form-container').classList.add('hidden');
    document.getElementById('tipo-form').reset();
});

document.getElementById('tipo-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prefix = document.getElementById('tipo-prefix').value.trim().toUpperCase();
    const desc = document.getElementById('tipo-desc').value.trim();
    
    try {
        const res = await fetch(`${API_URL}/tipos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ prefix, description: desc })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Error al crear tipo');
        }
        document.getElementById('tipo-form').reset();
        document.getElementById('tipo-form-container').classList.add('hidden');
        loadTipos();
    } catch (err) {
        alert(err.message);
    }
});

window.deleteTipo = async (id) => {
    if(!currentUser?.is_superadmin) return alert('No tienes permisos');
    if(!confirm('¿Estás seguro de eliminar este tipo?')) return;
    try {
        const res = await fetch(`${API_URL}/tipos/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Error al eliminar');
        loadTipos();
    } catch (err) {
        alert(err.message);
    }
}

// Marcas
async function loadMarcas() {
    try {
        const res = await fetch(`${API_URL}/marcas`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando marcas');
        marcas = await res.json();
        renderMarcasTable();
    } catch (err) {
        console.error(err);
    }
}

function renderMarcasTable() {
    const tbody = document.querySelector('#marcas-table tbody');
    tbody.innerHTML = '';
    marcas.forEach(m => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${m.name}</td>
            <td class="action-links">
                ${currentUser?.is_superadmin ? `<button class="del" onclick="deleteMarca(${m.id})">Eliminar</button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

document.getElementById('btn-add-marca').addEventListener('click', () => {
    document.getElementById('marca-form-container').classList.remove('hidden');
});
document.getElementById('btn-cancel-marca').addEventListener('click', () => {
    document.getElementById('marca-form-container').classList.add('hidden');
    document.getElementById('marca-form').reset();
});

document.getElementById('marca-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('marca-name').value.trim();
    
    try {
        const res = await fetch(`${API_URL}/marcas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name })
        });
        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Error al crear marca');
        }
        document.getElementById('marca-form').reset();
        document.getElementById('marca-form-container').classList.add('hidden');
        loadMarcas();
    } catch (err) {
        alert(err.message);
    }
});

window.deleteMarca = async (id) => {
    if(!currentUser?.is_superadmin) return alert('No tienes permisos');
    if(!confirm('¿Estás seguro de eliminar esta marca?')) return;
    try {
        const res = await fetch(`${API_URL}/marcas/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Error al eliminar');
        loadMarcas();
    } catch (err) {
        alert(err.message);
    }
}


// Tipos Excel upload
document.getElementById('tipos-excel-upload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if(!currentUser?.is_superadmin) return alert('No tienes permisos');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(`${API_URL}/tipos/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (!res.ok) throw new Error('Error al procesar el Excel');
        const data = await res.json();
        alert(`Se han importado ${data.count} tipos de equipo exitosamente.`);
        loadTipos();
    } catch (err) {
        alert(err.message);
    }
    
    e.target.value = '';
});

// ==================== GENERATOR QR ====================
let currentQR = new QRious({ size: 300, padding: 0 });

function renderGeneratorList() {
    const list = document.getElementById('gen-equipos-list');
    list.innerHTML = '';
    equipos.forEach(eq => {
        const div = document.createElement('div');
        div.className = 'list-item';
        div.textContent = `${eq.serie || 'Sin Serie'} - ${eq.marca || 'Sin Marca'}`;
        div.onclick = () => {
            document.querySelectorAll('.list-item').forEach(el => el.classList.remove('selected'));
            div.classList.add('selected');
            generateQRFor(eq);
        };
        list.appendChild(div);
    });
}

function generateQRFor(eq) {
    const qrVal = eq.qr || eq.serie || eq.id.toString();
    currentQR.value = qrVal;
    
    const qrPlaceholder = document.getElementById('qr-placeholder');
    const qrImg = document.getElementById('qr-img');
    
    qrPlaceholder.classList.add('hidden');
    qrImg.src = currentQR.toDataURL();
    qrImg.classList.remove('hidden');
}

document.getElementById('btnPrint').addEventListener('click', () => {
    const canvas = document.getElementById('labelCanvas');
    const win = window.open('', '_blank');
    win.document.write(`
        <html>
        <head>
            <style>
                body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
                .label { width: 51mm; height: 25mm; position: relative; border: 1px dashed #ccc; }
                .label img { width: 100%; height: 100%; object-fit: contain; }
                @media print {
                    .label { border: none; }
                }
            </style>
        </head>
        <body>
            <div class="label">
                ${canvas.innerHTML}
            </div>
            <script>
                window.onload = () => { window.print(); window.close(); }
            </script>
        </body>
        </html>
    `);
    win.document.close();
});

// ==================== EXCEL UPLOAD (EQUIPOS) ====================
document.getElementById('excel-upload-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if(!currentUser?.is_superadmin) return alert('No tienes permisos');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(`${API_URL}/equipos/upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (!res.ok) throw new Error('Error al procesar el Excel');
        const data = await res.json();
        alert(`Se han importado ${data.count} equipos exitosamente.`);
        loadEquipos();
    } catch (err) {
        alert(err.message);
    }
    
    e.target.value = '';
});
"""

with open(r'c:\PROYECTOS\Equipos y etiquetas\frontend\app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.js")
