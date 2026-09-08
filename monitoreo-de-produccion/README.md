# Production Monitoring System

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/README.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/monitoreo-de-produccion"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>

Web platform for digitizing industrial production records and converting physical forms into structured, searchable data ready for quality analysis.

## What it demonstrates

- Extraction of tables and metrics from PDF files into DataFrames and Excel.
- Validated capture of operational parameters through area-specific modules.
- Role-based access control with Flask-Login.
- Modular Blueprints architecture and reproducible Docker deployment.

## Data flow

`PDF / operational record -> extraction and validation -> SQLite -> Flask application -> monitoring and analysis`

## Stack

**Backend:** Python, Flask, Werkzeug, Jinja2
**Data:** SQLite, Pandas, OpenPyXL, PDFPlumber
**Deployment:** Docker, Docker Compose, and Waitress

## Setup and usage

### Option 1: Docker deployment

Requires [Docker](https://www.docker.com/) and Docker Compose.

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/monitoreo-de-produccion/FORMATOS
docker-compose up -d --build
```

Open `http://localhost:5000`.

### Option 2: Local Python setup

Requires Python 3.8 or newer.

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/monitoreo-de-produccion/FORMATOS/webapp
python -m venv venv
pip install -r requirements.txt
python app.py
```

Configure environment variables according to `.env.example`, then open `http://localhost:5000`.

## Project structure

- `FORMATOS/webapp/`: Flask application, routes, templates, utilities, and data.
- `FORMATOS/convert_pdf_to_excel.py`: PDF table extraction script.
- `FORMATOS/docker-compose.yml`: container orchestration.

The conversion scripts and web application remain separate to distinguish data preparation from operational capture and querying.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/README.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/monitoreo-de-produccion"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>
