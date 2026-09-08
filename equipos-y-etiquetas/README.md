# Sistema de Gestión y Etiquetado de Equipos

<p align="center">
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/equipos-y-etiquetas"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>

Aplicación para registrar inventario técnico con datos consistentes y generar etiquetas con QR para facilitar la trazabilidad de equipos en campo.

**[Abrir demo interactiva en GitHub Pages](https://alejandrolzvz.github.io/equipos-y-etiquetas/demo-etiquetas/index.html)**

## Qué demuestra

- Captura estructurada de serie, marca, estado, cliente y dirección.
- Búsqueda y filtrado de inventario para localizar equipos rápidamente.
- Editor visual de etiquetas con campos dinámicos, capas, QR y vista previa.
- API con FastAPI y autenticación basada en JWT para el flujo completo.

## Stack

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy, JWT
**Frontend:** HTML, CSS y JavaScript sin framework
**Demo:** HTML estático y QRious con datos inventados

## Ejecución local

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/equipos-y-etiquetas
pip install fastapi uvicorn pydantic sqlalchemy python-jose passlib[bcrypt]
uvicorn backend.main:app --host 0.0.0.0 --port 9000
```

En Windows también puedes ejecutar `iniciar_servidor.bat`. Después abre `http://localhost:9000`.

La demo pública funciona sin backend y usa datos inventados. El servidor local habilita la API y la persistencia configurada en el proyecto.

## Archivos principales

- `backend/`: API, autenticación, modelos, esquemas y acceso a datos.
- `frontend/`: interfaz de inventario y editor de etiquetas.
- `demo-etiquetas/`: versión estática publicada en GitHub Pages.
- `plantilla-etiqueta (7).json`: plantilla de referencia para el diseño.

<p align="center">
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/equipos-y-etiquetas"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>
