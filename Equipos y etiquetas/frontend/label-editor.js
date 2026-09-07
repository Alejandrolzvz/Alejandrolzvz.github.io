(() => {
    'use strict';

    const fields = ['serie', 'marca', 'cliente', 'direccion', 'serie_fabrica', 'num_factura', 'fecha_compra', 'descripcion', 'estatus', 'observacion', 'serie_ant', 'qr', 'cod_cliente', 'cliente2'];
    const presets = { '51x25': [51, 25], '50x30': [50, 30], '70x40': [70, 40], '100x50': [100, 50] };
    const defaultTemplateKey = 'equipos-qr-default-template';
    let state = null;
    let drag = null;
    let imageTarget = null;
    let bannerTimer;
    let templateFileHandle = null;

    const $ = id => document.getElementById(id);
    const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
    const clamp = (value, min, max) => Math.max(min, Math.min(max, Number(value) || min));
    const selectedRows = () => state.rows.filter(row => row.__selected);
    const currentRow = () => state.rows[state.preview] || selectedRows()[0] || null;
    const selectedElement = () => state.elements.find(element => element.id === state.selected) || null;

    function notify(message, error = false) {
        const banner = $('banner');
        banner.textContent = message;
        banner.className = `show${error ? ' error' : ''}`;
        clearTimeout(bannerTimer);
        bannerTimer = setTimeout(() => banner.className = '', 4000);
    }

    function initLabelEditor(equipos = []) {
        if (!$('labelCanvas')) return;
        if (!state) {
            state = { rows: [], elements: [], labelW: 51, labelH: 25, selected: null, preview: 0, nextId: 1, filter: '', zoom: 1 };
            bindControls();
            restoreDefaultTemplate();
        }
        state.rows = (equipos || []).map(row => ({ ...row, __selected: false }));
        renderRows();
        renderFields();
        renderCanvas();
        renderProperties();
        renderLayers();
    }
    window.initLabelEditor = initLabelEditor;
    window.printLabelForEquipment = equipo => {
        initLabelEditor([equipo]);
        state.rows[0].__selected = true;
        printLabels();
    };

    function bindControls() {
        $('rowSearch').addEventListener('input', event => { state.filter = event.target.value.toLowerCase(); renderRows(); });
        $('selectAll').addEventListener('click', () => { state.rows.forEach(row => { if (matches(row)) row.__selected = true; }); renderRows(); });
        $('selectNone').addEventListener('click', () => { state.rows.forEach(row => { if (matches(row)) row.__selected = false; }); renderRows(); });
        $('btnAddText').addEventListener('click', () => addText());
        $('btnAddQR').addEventListener('click', () => addQr());
        $('btnAddImage').addEventListener('click', () => { imageTarget = null; $('imageInput').click(); });
        $('imageInput').addEventListener('change', loadImage);
        $('btnSaveTemplate').addEventListener('click', saveTemplate);
        $('btnExportTemplate').addEventListener('click', exportTemplate);
        $('btnImportTemplate').addEventListener('click', importTemplateFromPicker);
        $('importTemplateInput').addEventListener('change', importTemplate);
        $('btnPrint').addEventListener('click', printLabels);
        $('zoomIn').addEventListener('click', () => setZoom(state.zoom + .15));
        $('zoomOut').addEventListener('click', () => setZoom(state.zoom - .15));
        $('zoomReset').addEventListener('click', () => setZoom(1));
        document.addEventListener('wheel', event => {
            if ((!event.ctrlKey && !event.metaKey) || !event.target.closest('.canvas-area')) return;
            event.preventDefault();
            event.stopPropagation();
            setZoom(state.zoom + (event.deltaY < 0 ? .15 : -.15));
        }, { passive: false, capture: true });
        $('presetSize').addEventListener('change', event => { if (presets[event.target.value]) setSize(...presets[event.target.value]); });
        ['labelW', 'labelH'].forEach(id => $(id).addEventListener('input', () => setSize(Number($('labelW').value), Number($('labelH').value))));
        $('labelCanvas').addEventListener('dragover', event => event.preventDefault());
        $('labelCanvas').addEventListener('drop', event => { event.preventDefault(); const field = event.dataTransfer.getData('text/plain'); if (field) addText(field, event); });
        $('labelCanvas').addEventListener('mousedown', event => { if (event.target === $('labelCanvas')) selectElement(null); });
        $('layersList').addEventListener('click', event => {
            const layer = event.target.closest('[data-layer]');
            if (layer) selectElement(layer.dataset.layer);
        });
        document.addEventListener('mousemove', moveElement);
        document.addEventListener('mouseup', () => { drag = null; renderLayers(); });
        window.addEventListener('resize', renderCanvas);
    }

    function matches(row) { return !state.filter || fields.some(field => String(row[field] ?? '').toLowerCase().includes(state.filter)); }
    function renderFields() {
        $('columnsList').innerHTML = fields.map(field => `<button class="field-chip" draggable="true" data-field="${field}">${field}</button>`).join('');
        $('columnsList').querySelectorAll('[draggable]').forEach(chip => { chip.addEventListener('dragstart', event => event.dataTransfer.setData('text/plain', chip.dataset.field)); chip.addEventListener('click', () => addText(chip.dataset.field)); });
    }
    function renderRows() {
        const visible = state.rows.map((row, index) => ({ row, index })).filter(item => matches(item.row));
        $('rowsTable').innerHTML = visible.length ? visible.map(({ row, index }) => `<label class="row-item"><input type="checkbox" data-index="${index}" ${row.__selected ? 'checked' : ''}><span><b>#${index + 1}</b> ${escapeHtml(row.serie || row.marca || `Equipo ${index + 1}`)}</span></label>`).join('') : '<p class="hint">No hay equipos que coincidan.</p>';
        $('rowsTable').querySelectorAll('input').forEach(input => input.addEventListener('change', () => { state.rows[input.dataset.index].__selected = input.checked; updateCount(); }));
        $('rowsTable').querySelectorAll('.row-item span').forEach((label, position) => label.addEventListener('click', () => { state.preview = visible[position].index; renderCanvas(); }));
        updateCount();
    }
    function updateCount() { $('selectedCount').textContent = `${selectedRows().length} de ${state.rows.length}`; }

    function setSize(width, height) {
        state.labelW = clamp(width, 10, 300); state.labelH = clamp(height, 10, 300);
        $('labelW').value = state.labelW; $('labelH').value = state.labelH;
        const preset = Object.keys(presets).find(key => presets[key][0] === state.labelW && presets[key][1] === state.labelH);
        $('presetSize').value = preset || 'custom';
        state.elements.forEach(limitElement); renderCanvas();
    }
    function setZoom(value) { state.zoom = clamp(value, .4, 4); renderCanvas(); }
    function limitElement(element) { element.w = clamp(element.w, 4, state.labelW); element.h = clamp(element.h, 4, state.labelH); element.x = clamp(element.x, 0, state.labelW - element.w); element.y = clamp(element.y, 0, state.labelH - element.h); }
    function newId() { return `el${state.nextId++}`; }
    function addText(bound = null, event = null) {
        const w = Math.min(40, state.labelW - 8), h = Math.min(8, state.labelH - 8);
        const element = { id: newId(), type: 'text', x: event ? 10 : 4, y: event ? 5 : 4 + (state.elements.length % 3) * 7, w, h, fontSize: 12, bold: false, align: 'left', color: '#111827', bound, staticText: bound ? '' : 'Texto' };
        limitElement(element); state.elements.push(element); selectElement(element.id);
    }
    function addQr() { const size = Math.min(20, state.labelW - 8, state.labelH - 8); state.elements.push({ id: newId(), type: 'qr', x: state.labelW - size - 4, y: 4, w: size, h: size, qrColumns: ['serie'], separator: ' | ' }); selectElement(state.elements.at(-1).id); }
    function addImage(src) { const element = { id: newId(), type: 'image', x: 4, y: state.labelH - 16, w: Math.min(16, state.labelW - 8), h: Math.min(12, state.labelH - 8), src }; limitElement(element); state.elements.push(element); selectElement(element.id); }
    function loadImage(event) { const file = event.target.files[0]; if (!file) return; const reader = new FileReader(); reader.onload = () => { if (imageTarget) { imageTarget.src = reader.result; imageTarget = null; renderCanvas(); } else addImage(reader.result); }; reader.readAsDataURL(file); event.target.value = ''; }

    function renderCanvas() {
        const canvas = $('labelCanvas'), row = currentRow();
        canvas.style.width = `${state.labelW}mm`; canvas.style.height = `${state.labelH}mm`; canvas.style.transform = `scale(${state.zoom})`; canvas.style.transformOrigin = 'top left';
        $('canvasWrapper').style.width = `${state.labelW * 3.7795 * state.zoom}px`; $('canvasWrapper').style.height = `${state.labelH * 3.7795 * state.zoom}px`; $('canvasSizeTag').textContent = `${state.labelW} x ${state.labelH} mm`; $('zoomLabel').textContent = `${Math.round(state.zoom * 100)}%`;
        canvas.innerHTML = '';
        state.elements.forEach((element, index) => { const node = document.createElement('div'); node.className = `label-element el-${element.type}${element.id === state.selected ? ' selected' : ''}`; Object.assign(node.style, { left: `${element.x}mm`, top: `${element.y}mm`, width: `${element.w}mm`, height: `${element.h}mm`, zIndex: index + 1 }); node.dataset.id = element.id;
            if (element.type === 'text') { Object.assign(node.style, { fontSize: `${element.fontSize}px`, fontWeight: element.bold ? '700' : '400', color: element.color, textAlign: element.align, justifyContent: element.align === 'right' ? 'flex-end' : element.align === 'center' ? 'center' : 'flex-start' }); node.textContent = element.bound ? String(row?.[element.bound] ?? `{{${element.bound}}}`) : element.staticText; }
            if (element.type === 'qr') { const qrCanvas = document.createElement('canvas'); const value = (element.qrColumns || []).map(field => row?.[field] ?? '').join(element.separator || ' | ') || ' '; new QRious({ element: qrCanvas, value, size: 256, level: 'M' }); node.appendChild(qrCanvas); }
            if (element.type === 'image') { if (element.src) { const image = document.createElement('img'); image.src = element.src; node.appendChild(image); } else node.textContent = 'Imagen'; }
            const handle = document.createElement('i'); handle.className = 'resize-handle'; node.appendChild(handle); node.addEventListener('mousedown', event => startDrag(event, element, false)); handle.addEventListener('mousedown', event => startDrag(event, element, true)); canvas.appendChild(node);
        });
    }
    function startDrag(event, element, resize) { event.preventDefault(); event.stopPropagation(); selectElement(element.id); const scale = $('labelCanvas').getBoundingClientRect().width / state.labelW; drag = { element, resize, x: event.clientX, y: event.clientY, ox: element.x, oy: element.y, ow: element.w, oh: element.h, scale }; }
    function moveElement(event) { if (!drag) return; const dx = (event.clientX - drag.x) / drag.scale, dy = (event.clientY - drag.y) / drag.scale; if (drag.resize) { drag.element.w = clamp(drag.ow + dx, 4, state.labelW - drag.element.x); drag.element.h = clamp(drag.oh + dy, 4, state.labelH - drag.element.y); } else { drag.element.x = clamp(drag.ox + dx, 0, state.labelW - drag.element.w); drag.element.y = clamp(drag.oy + dy, 0, state.labelH - drag.element.h); } renderCanvas(); }
    function selectElement(id) { state.selected = id; renderCanvas(); renderProperties(); renderLayers(); }

    function renderProperties() {
        const element = selectedElement(); if (!element) { $('propsContent').innerHTML = '<p class="hint">Selecciona un elemento del lienzo.</p>'; return; }
        const size = `<div class="prop-inline"><label>Ancho <input data-prop="w" type="number" value="${element.w}"></label><label>Alto <input data-prop="h" type="number" value="${element.h}"></label></div>`;
        if (element.type === 'text') $('propsContent').innerHTML = `<label>Campo<select data-prop="bound"><option value="">Texto fijo</option>${fields.map(field => `<option ${element.bound === field ? 'selected' : ''}>${field}</option>`).join('')}</select></label>${element.bound ? '' : `<label>Contenido<textarea data-prop="staticText">${escapeHtml(element.staticText)}</textarea></label>`}<div class="prop-inline"><label>Tamaño<input data-prop="fontSize" type="number" value="${element.fontSize}"></label><label>Alineación<select data-prop="align"><option>left</option><option ${element.align === 'center' ? 'selected' : ''}>center</option><option ${element.align === 'right' ? 'selected' : ''}>right</option></select></label></div><label><input data-prop="bold" type="checkbox" ${element.bold ? 'checked' : ''}> Negrita</label><label>Color<input data-prop="color" type="color" value="${element.color}"></label>${size}<button class="btn danger full-width" data-delete="${element.id}">Eliminar</button>`;
        if (element.type === 'qr') $('propsContent').innerHTML = `<label>Campos del QR</label><div class="checklist" style="display: flex !important; flex-direction: column !important; gap: 8px !important;">${fields.map(field => `<div style="display: flex !important; flex-direction: row !important; align-items: center !important; gap: 8px !important; text-align: left !important;"><input type="checkbox" data-field="${field}" ${element.qrColumns.includes(field) ? 'checked' : ''} style="display: inline-block !important; width: auto !important; margin: 0 !important;"><label style="display: inline-block !important; margin: 0 !important; cursor: pointer !important;">${field}</label></div>`).join('')}</div><label>Separador<input data-prop="separator" value="${escapeHtml(element.separator)}"></label>${size}<button class="btn danger full-width" data-delete="${element.id}">Eliminar</button>`;
        $('propsContent').querySelectorAll('[data-field]').forEach(input => input.addEventListener('change', () => { element.qrColumns = [...$('propsContent').querySelectorAll('[data-field]:checked')].map(item => item.dataset.field); renderCanvas(); }));
        $('propsContent').querySelector('[data-delete]')?.addEventListener('click', () => { state.elements = state.elements.filter(item => item.id !== element.id); selectElement(null); });
        $('propsContent').querySelector('[data-replace]')?.addEventListener('click', () => { imageTarget = element; $('imageInput').click(); });
    }
    function renderLayers() {
        $('layersList').innerHTML = state.elements.map(element => `<div class="layer-item${element.id === state.selected ? ' selected' : ''}" data-layer="${element.id}"><span>${element.type.toUpperCase()}</span><b>${escapeHtml(element.bound || element.staticText || (element.type === 'qr' ? 'Código QR' : 'Imagen'))}</b></div>`).join('') || '<p class="hint">Sin elementos aún.</p>';
    }

    function templateData() { return JSON.stringify({ name: 'plantilla-etiqueta', labelW: state.labelW, labelH: state.labelH, elements: state.elements }, null, 2); }
    function persistDefaultTemplate() { try { localStorage.setItem(defaultTemplateKey, templateData()); } catch (error) { notify('No se pudo guardar el diseño predeterminado.', true); } }
    function restoreDefaultTemplate() { try { const saved = localStorage.getItem(defaultTemplateKey); if (saved) applyTemplate(JSON.parse(saved), false); } catch (error) { localStorage.removeItem(defaultTemplateKey); } }
    function applyTemplate(data, persist = true) { if (!Array.isArray(data.elements) || typeof data.labelW !== 'number' || typeof data.labelH !== 'number') throw Error(); state.labelW = data.labelW; state.labelH = data.labelH; state.elements = data.elements; state.nextId = state.elements.reduce((highest, element) => Math.max(highest, Number(String(element.id).replace('el', '')) || 0), 0) + 1; setSize(state.labelW, state.labelH); selectElement(null); if (persist) persistDefaultTemplate(); }
    function exportTemplate() { if (!state.elements.length) return notify('Agrega elementos antes de exportar.', true); persistDefaultTemplate(); const blob = new Blob([templateData()], { type: 'application/json' }); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'plantilla-etiqueta.json'; link.click(); URL.revokeObjectURL(link.href); notify('Plantilla exportada y guardada como predeterminada.'); }
    async function saveTemplate() {
        if (!state.elements.length) return notify('Agrega elementos antes de guardar.', true);
        try {
            if (templateFileHandle) {
                const writable = await templateFileHandle.createWritable();
                await writable.write(templateData());
                await writable.close();
                persistDefaultTemplate();
                notify('Plantilla guardada y sobrescrita.');
                return;
            }
            if (window.showSaveFilePicker) {
                templateFileHandle = await window.showSaveFilePicker({ suggestedName: 'plantilla-etiqueta.json', types: [{ description: 'Plantilla JSON', accept: { 'application/json': ['.json'] } }] });
                const writable = await templateFileHandle.createWritable();
                await writable.write(templateData());
                await writable.close();
                persistDefaultTemplate();
                notify('Plantilla guardada.');
                return;
            }
            exportTemplate();
            notify('Tu navegador no permite sobrescribir archivos; se descargó una copia nueva.');
        } catch (error) {
            if (error.name !== 'AbortError') notify('No se pudo guardar la plantilla.', true);
        }
    }
    async function importTemplateFromPicker() {
        if (window.showOpenFilePicker) {
            try {
                const [handle] = await window.showOpenFilePicker({ types: [{ description: 'Plantilla JSON', accept: { 'application/json': ['.json'] } }], multiple: false });
                templateFileHandle = handle;
                const file = await handle.getFile();
                applyTemplate(JSON.parse(await file.text()));
                notify('Plantilla importada. Guardar sobrescribirá este archivo.');
            } catch (error) {
                if (error.name !== 'AbortError') notify('La plantilla no tiene un formato válido.', true);
            }
            return;
        }
        $('importTemplateInput').click();
    }
    function importTemplate(event) { const file = event.target.files[0]; if (!file) return; const reader = new FileReader(); reader.onload = () => { try { applyTemplate(JSON.parse(reader.result)); templateFileHandle = null; notify('Plantilla importada. Guardar descargará una copia nueva.'); } catch { notify('La plantilla no tiene un formato válido.', true); } }; reader.readAsText(file); event.target.value = ''; }
    function printLabels() { const rows = selectedRows(); if (!rows.length || !state.elements.length) return notify(!rows.length ? 'Selecciona al menos un equipo.' : 'Agrega elementos a la etiqueta.', true); const pages = rows.map(row => { const html = state.elements.map(element => { const base = `position:absolute;left:${element.x}mm;top:${element.y}mm;width:${element.w}mm;height:${element.h}mm;overflow:hidden;display:flex;align-items:center;`; if (element.type === 'text') return `<div style="${base}font-size:${element.fontSize}px;font-weight:${element.bold ? 700 : 400};color:${element.color};justify-content:${element.align === 'right' ? 'flex-end' : element.align === 'center' ? 'center' : 'flex-start'};text-align:${element.align};white-space:pre-wrap;word-break:break-word;line-height:1.15">${escapeHtml(element.bound ? row[element.bound] : element.staticText)}</div>`; if (element.type === 'image') return `<div style="${base}"><img src="${element.src}" style="width:100%;height:100%;object-fit:contain"></div>`; const canvas = document.createElement('canvas'); const value = element.qrColumns.map(field => row[field] ?? '').join(element.separator || ' | ') || ' '; new QRious({ element: canvas, value, size: 256 }); return `<div style="${base}"><img src="${canvas.toDataURL()}" style="width:100%;height:100%"></div>`; }).join(''); return `<div class="page">${html}</div>`; }).join(''); const win = window.open('', '_blank'); if (!win) return notify('Permite ventanas emergentes para imprimir.', true); win.document.write(`<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,100..1000&display=swap" rel="stylesheet"><style>@page{size:${state.labelW}mm ${state.labelH}mm;margin:0}*{box-sizing:border-box}body{margin:0;font-family:'Google Sans Flex','Inter',system-ui,sans-serif}.page{position:relative;width:${state.labelW}mm;height:${state.labelH}mm;page-break-after:always;overflow:hidden}</style>${pages}<script>window.onload=()=>{(document.fonts ? document.fonts.ready : Promise.resolve()).then(() => window.print())}<\/script>`); win.document.close(); }
})();
