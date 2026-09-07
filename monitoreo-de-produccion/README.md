# Sistema de Monitoreo de Producción

Plataforma web para digitalizar registros de producción industrial y convertir formatos físicos en datos estructurados, consultables y listos para análisis de calidad.

## Qué demuestra

- Extracción de tablas y métricas desde PDF hacia DataFrames y Excel.
- Captura validada de parámetros operativos desde módulos separados por área.
- Control de acceso por roles con Flask-Login.
- Organización modular con Blueprints y despliegue reproducible mediante Docker.

## Flujo de datos

`PDF / registro operativo -> extracción y validación -> SQLite -> aplicación Flask -> consulta y seguimiento`

## Stack

**Backend:** Python, Flask, Werkzeug, Jinja2
**Datos:** SQLite, Pandas, OpenPyXL, PDFPlumber
**Despliegue:** Docker, Docker Compose y Waitress

## Configuración y uso

### Opción 1: Despliegue Rápido con Docker (Recomendado)

Se requiere tener instalado [Docker](https://www.docker.com/) y `docker-compose`.

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
   cd monitoreo-de-produccion
   ```
2. Levanta el contenedor mediante Docker Compose:
   ```bash
   cd FORMATOS
   docker-compose up -d --build
   ```
3. Abre `http://localhost:5000`.

### Opción 2: instalación local con Python

Se requiere Python 3.8 o superior.

1. Clona el repositorio y navega al directorio de la aplicación:
   ```bash
   git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
   cd monitoreo-de-produccion/FORMATOS/webapp
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows: venv\Scripts\activate
   # En Linux/Mac: source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las variables de entorno según `.env.example`.
5. Inicializa la base de datos e inicia la aplicación:
   ```bash
   python app.py
   ```
6. Abre `http://localhost:5000` en el navegador.

## Estructura del proyecto

```text
├── FORMATOS/
│   ├── webapp/                 # Código fuente principal de la aplicación web (Flask)
│   │   ├── app.py              # Punto de entrada de la aplicación
│   │   ├── routes/             # Blueprints de las diferentes áreas operativas
│   │   ├── templates/          # Plantillas HTML (Jinja2)
│   │   ├── utils/              # Conexiones DB y modelos
│   │   └── data/               # Archivos de la base de datos (SQLite)
│   ├── convert_pdf_to_excel.py # Script ETL para extracción de tablas
│   ├── docker-compose.yml      # Orquestación de contenedores
│   └── ...
└── README.md
```

Los scripts de conversión y la aplicación web se mantienen separados para distinguir la preparación de datos de la captura y consulta operativa.
