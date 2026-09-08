# Equipment Management and Labeling System

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/equipos-y-etiquetas"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>

Application for recording technical inventory with consistent data and generating QR labels to support field equipment traceability.

**[Open the interactive demo on GitHub Pages](https://alejandrolzvz.github.io/equipos-y-etiquetas/demo-etiquetas/index.html)**

## What it demonstrates

- Structured capture of serial number, brand, status, customer, and address.
- Inventory search and filtering for fast equipment lookup.
- Visual label editor with dynamic fields, layers, QR codes, and preview.
- FastAPI API with JWT-based authentication for the complete workflow.

## Stack

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy, JWT
**Frontend:** HTML, CSS, and framework-free JavaScript
**Demo:** Static HTML and QRious with fictional data

## Local setup

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/equipos-y-etiquetas
pip install fastapi uvicorn pydantic sqlalchemy python-jose passlib[bcrypt]
uvicorn backend.main:app --host 0.0.0.0 --port 9000
```

On Windows, you can also run `iniciar_servidor.bat`. Then open `http://localhost:9000`.

The public demo runs without a backend and uses fictional data. The local server enables the API and the persistence configured in the project.

## Main files

- `backend/`: API, authentication, models, schemas, and data access.
- `frontend/`: inventory interface and label editor.
- `demo-etiquetas/`: static version published on GitHub Pages.
- `plantilla-etiqueta (7).json`: reference design template.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/equipos-y-etiquetas"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>
