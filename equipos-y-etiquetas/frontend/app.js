const API_URL = '/api';
let token = localStorage.getItem('token') || null;
let currentUser = null;
let equipos = [];
let tipos = [];
let marcas = [];
let allUsers = [];
let settings = {};
let selectedClientCode = '';

// DOM Elements
const loginView = document.getElementById('login-view');
const dashboardView = document.getElementById('dashboard-view');
const forcePasswordView = document.getElementById('force-password-view');
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
        
        if (currentUser.must_change_password) {
            showView(forcePasswordView);
            return;
        }
        
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
        if (currentUser.is_superadmin) {
            loadUsers();
        }
    } catch (err) {
        token = null;
        localStorage.removeItem('token');
        showView(loginView);
    }
}

// Force password change
document.getElementById('force-password-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldP = document.getElementById('force-old-password').value;
    const newP = document.getElementById('force-new-password').value;
    const confirmP = document.getElementById('force-confirm-password').value;
    const err = document.getElementById('force-password-error');
    if (newP !== confirmP) {
        err.textContent = "Las contraseñas no coinciden";
        err.classList.remove('hidden');
        return;
    }
    try {
        const res = await fetch(`${API_URL}/users/me/change-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ old_password: oldP, new_password: newP })
        });
        if (!res.ok) throw new Error('Contraseña actual incorrecta');
        err.classList.add('hidden');
        document.getElementById('force-password-form').reset();
        await fetchCurrentUser();
    } catch (error) {
        err.textContent = error.message;
        err.classList.remove('hidden');
    }
});

document.getElementById('btn-cancel-force-password').addEventListener('click', () => {
    btnLogout.click();
});

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

// ==================== USERS ====================
async function loadUsers() {
    if (!currentUser?.is_superadmin) return;
    try {
        const res = await fetch(`${API_URL}/users`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando usuarios');
        allUsers = await res.json();
        renderUsersTable(allUsers);
    } catch(err) {
        console.error(err);
    }
}

function renderUsersTable(usersData) {
    const tbody = document.querySelector('#users-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    usersData.forEach(u => {
        let role = 'Usuario';
        if (u.is_superadmin) role = 'Superadmin';
        else if (u.is_admin) role = 'Admin';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${u.id}</td>
            <td>${u.username}</td>
            <td>${role}</td>
            <td>
                <button class="btn small ghost" onclick="resetUserPassword(${u.id})">Restablecer Contraseña</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

document.getElementById('search-users')?.addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    const filtered = allUsers.filter(u => u.username.toLowerCase().includes(term) || u.id.toString().includes(term));
    renderUsersTable(filtered);
});

window.resetUserPassword = async (id) => {
    const tempPass = prompt("Ingresa la contraseña temporal para este usuario:");
    if (!tempPass) return;
    try {
        const res = await fetch(`${API_URL}/users/${id}/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ new_password: tempPass })
        });
        if (!res.ok) throw new Error('Error al restablecer');
        alert('Contraseña restablecida correctamente.');
        loadUsers();
    } catch (err) {
        alert(err.message);
    }
}

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
        loadUsers();
        setTimeout(() => msg.classList.add('hidden'), 3000);
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
    forcePasswordView.classList.add('hidden');
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
btnShowGenerator.addEventListener('click', () => { switchSection(sectionGenerator, btnShowGenerator); initLabelEditor(equipos); });
adminUsersBtn.addEventListener('click', () => switchSection(sectionUsers, adminUsersBtn));
adminCatalogosBtn.addEventListener('click', () => { switchSection(sectionCatalogos, adminCatalogosBtn); loadTipos(); loadMarcas(); });

// ==================== EQUIPOS CRUD ====================
async function loadEquipos() {
    try {
        const res = await fetch(`${API_URL}/equipos`, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error cargando equipos');
        equipos = await res.json();
        populateEquipmentFilters();
        renderTable();
    } catch (err) {
        console.error(err);
    }
}

const equipmentFields = ['id', 'serie', 'marca', 'fecha_compra', 'serie_fabrica', 'num_factura', 'descripcion', 'serie_ant', 'cliente', 'direccion', 'estatus', 'observacion'];

function getFilteredEquipos() {
    const search = (document.getElementById('search-equipos')?.value || '').trim().toLowerCase();
    const marca = document.getElementById('filter-marca')?.value || '';
    const estatus = document.getElementById('filter-estatus')?.value || '';
    return equipos.filter(eq => {
        const matchesSearch = !search || equipmentFields.some(field => String(eq[field] ?? '').toLowerCase().includes(search));
        return matchesSearch && (!marca || eq.marca === marca) && (!estatus || eq.estatus === estatus);
    });
}

function populateEquipmentFilters() {
    const marcaFilter = document.getElementById('filter-marca');
    const statusFilter = document.getElementById('filter-estatus');
    if (!marcaFilter || !statusFilter) return;
    const selectedMarca = marcaFilter.value;
    const selectedStatus = statusFilter.value;
    const uniqueValues = field => [...new Set(equipos.map(eq => eq[field]).filter(Boolean))].sort();
    marcaFilter.innerHTML = '<option value="">Todas las marcas</option>' + uniqueValues('marca').map(value => `<option value="${escapeTableText(value)}">${escapeTableText(value)}</option>`).join('');
    statusFilter.innerHTML = '<option value="">Todos los estatus</option>' + ['Disponible', 'Asignado', 'Baja'].map(value => `<option value="${value}">${value}</option>`).join('');
    marcaFilter.value = selectedMarca;
    statusFilter.value = selectedStatus;
}

function escapeTableText(value) {
    return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function renderTable() {
    const tbody = document.querySelector('#equipos-table tbody');
    tbody.innerHTML = '';
    const showSerieAnt = settings['show_serie_ant'] === 'true';
    const filteredEquipos = getFilteredEquipos();
    const count = document.getElementById('equipment-count');
    if (count) count.textContent = `${filteredEquipos.length} de ${equipos.length} equipos`;
    
    filteredEquipos.forEach(eq => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${escapeTableText(eq.id)}</td>
            <td>${escapeTableText(eq.serie ? eq.serie.split('-')[0] : '-')}</td>
            <td>${escapeTableText(eq.serie || '-')}</td>
            <td>${escapeTableText(eq.marca || '-')}</td>
            <td>${escapeTableText(eq.fecha_compra || '-')}</td>
            <td>${escapeTableText(eq.serie_fabrica || '-')}</td>
            <td>${escapeTableText(eq.num_factura || '-')}</td>
            <td>${escapeTableText(eq.descripcion || '-')}</td>
            <td class="col-serie-ant ${showSerieAnt ? '' : 'hidden'}">${escapeTableText(eq.serie_ant || '-')}</td>
            <td>${escapeTableText(eq.cliente || '-')}</td>
            <td>${escapeTableText(eq.direccion || '-')}</td>
            <td>${escapeTableText(eq.estatus || 'Disponible')}</td>
            <td>${escapeTableText(eq.observacion || '-')}</td>
            <td class="action-links">
                <button onclick="editEquipo(${eq.id})">Editar</button>
                <button onclick="printEquipoEtiqueta(${eq.id})">Imprimir etiqueta</button>
                ${currentUser?.is_superadmin ? `<button class="del" onclick="deleteEquipo(${eq.id})">Eliminar</button>` : ''}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

window.printEquipoEtiqueta = (id) => {
    const equipo = equipos.find(eq => eq.id === id);
    if (!equipo) return;
    switchSection(sectionGenerator, btnShowGenerator);
    window.printLabelForEquipment(equipo);
};

['search-equipos', 'filter-marca', 'filter-estatus'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', renderTable);
    document.getElementById(id)?.addEventListener('change', renderTable);
});
document.getElementById('clear-equipment-filters')?.addEventListener('click', () => {
    document.getElementById('search-equipos').value = '';
    document.getElementById('filter-marca').value = '';
    document.getElementById('filter-estatus').value = '';
    renderTable();
});

// Modal handling
const modal = document.getElementById('equipo-modal');
const equipoForm = document.getElementById('equipo-form');
const eqTipoSelect = document.getElementById('eq-tipo');
const eqSerieInput = document.getElementById('eq-serie');
const eqMarcaSelect = document.getElementById('eq-marca');

const clientCodeInput = document.getElementById('eq-cod-cliente');
const clientInput = document.getElementById('eq-cliente');
const clientsList = document.getElementById('clientes-list');
clientCodeInput.addEventListener('input', async () => {
    selectedClientCode = '';
    clientInput.value = '';
    const query = clientCodeInput.value.trim();
    clientsList.innerHTML = '';
    if (query.length < 2 || clientInput.disabled) return;
    try {
        const res = await fetch(`${API_URL}/clientes?q=${encodeURIComponent(query)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) return;
        const clients = await res.json();
        clients.forEach(client => {
            const option = document.createElement('option');
            option.value = client.codigo;
            option.label = client.nombre_comercial;
            option.dataset.codigo = client.codigo;
            option.dataset.nombre = client.nombre_comercial;
            clientsList.appendChild(option);
        });
        const selected = clients.find(client => client.codigo === clientCodeInput.value);
        if (selected) {
            selectedClientCode = selected.codigo;
            clientInput.value = selected.nombre_comercial;
            await loadClientAddresses(selected.codigo);
        }
    } catch (err) {
        console.error('Error buscando clientes', err);
    }
});

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
    selectedClientCode = '';
    document.getElementById('eq-direccion').innerHTML = '<option value="">Selecciona una dirección...</option>';
    document.getElementById('eq-id').value = '';
    document.getElementById('modal-title').textContent = 'Nuevo Equipo';
    eqSerieInput.value = '';
    eqSerieInput.readOnly = true;
    eqSerieInput.style.opacity = '0.7';
    eqSerieInput.style.cursor = 'not-allowed';
    
    document.getElementById('eq-desc-prefix').value = '';
    document.getElementById('eq-estatus').value = 'Disponible';
    updateClientAvailability();
    
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

eqTipoSelect.addEventListener('change', async () => {
    const prefix = eqTipoSelect.value;
    const isEditing = !!document.getElementById('eq-id').value;
    
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
        cod_cliente: selectedClientCode || null,
        direccion: document.getElementById('eq-direccion').value || null,
        estatus: document.getElementById('eq-estatus').value,
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

function updateClientAvailability() {
    const status = document.getElementById('eq-estatus').value;
    const client = document.getElementById('eq-cliente');
    const clientCode = document.getElementById('eq-cod-cliente');
    const address = document.getElementById('eq-direccion');
    client.disabled = status !== 'Asignado';
    clientCode.disabled = status !== 'Asignado';
    address.disabled = status !== 'Asignado';
    if (client.disabled) {
        client.value = '';
        clientCode.value = '';
        selectedClientCode = '';
        address.innerHTML = '<option value="">Selecciona una dirección...</option>';
    }
}

document.getElementById('eq-estatus').addEventListener('change', updateClientAvailability);

async function loadClientAddresses(code, selectedAddress = '') {
    const address = document.getElementById('eq-direccion');
    address.innerHTML = '<option value="">Cargando direcciones...</option>';
    if (!code) {
        address.innerHTML = '<option value="">Selecciona primero un cliente...</option>';
        return;
    }
    try {
        const res = await fetch(`${API_URL}/direcciones?cod_cliente=${encodeURIComponent(code)}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('No se pudieron cargar las direcciones');
        const addresses = await res.json();
        address.innerHTML = addresses.length
            ? '<option value="">Selecciona una dirección...</option>' + addresses.map(item => `<option value="${escapeTableText(item.direccion)}">${escapeTableText(item.direccion)}</option>`).join('')
            : '<option value="">Este cliente no tiene direcciones</option>';
        if (selectedAddress) address.value = selectedAddress;
    } catch (err) {
        address.innerHTML = '<option value="">Error cargando direcciones</option>';
        console.error('Error buscando direcciones', err);
    }
}

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
    document.getElementById('eq-cod-cliente').value = eq.cod_cliente || '';
    selectedClientCode = eq.cod_cliente || '';
    const equipmentStatus = eq.estatus || (eq.fisicamente === 'Asignado' ? 'Asignado' : eq.fisicamente === 'Baja' ? 'Baja' : 'Disponible');
    document.getElementById('eq-estatus').value = equipmentStatus;
    updateClientAvailability();
    if (equipmentStatus === 'Asignado' && eq.cod_cliente) loadClientAddresses(eq.cod_cliente, eq.direccion || '');
    document.getElementById('eq-obs').value = eq.observacion || '';
    
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
