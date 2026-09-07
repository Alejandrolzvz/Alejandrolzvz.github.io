# Sistema de Monitoreo de Producción

Una plataforma web modular y robusta diseñada para la digitalización, captura y monitoreo de parámetros de producción industrial. Este proyecto implementa una arquitectura sólida para la gestión de datos operativos, integrando flujos de trabajo ETL (Extracción, Transformación y Carga) desde formatos físicos (PDFs) hacia formatos estructurados (Excel/Base de Datos), facilitando el análisis y la toma de decisiones.

## Características Principales

* **Arquitectura Modular (Blueprints):** La aplicación está dividida en submódulos lógicos por área (Ósmosis, Calidad, Lavado, Pozos, Suavizadores), lo que la hace escalable y fácil de mantener.
* **Autenticación y Autorización (RBAC):** Sistema seguro basado en roles (Administrador, Operador, etc.) implementado con `Flask-Login`.
* **Procesamiento de Archivos PDF:** Scripts automatizados para extraer métricas clave desde reportes en formato PDF y convertirlos a DataFrames estructurados.
* **Contenedores Docker:** El entorno de la aplicación está completamente "dockerizado", garantizando que se pueda desplegar rápidamente de forma consistente en cualquier entorno.
* **Interfaz Dinámica e Intuitiva:** Renderizado rápido utilizando plantillas Jinja2, diseñadas para ser amigables con el usuario final que registra los datos diariamente.
* **Impacto en el Análisis de Datos:** Reemplaza los registros manuales desorganizados por un sistema de captura de datos validado y estructurado, permitiendo asegurar la Calidad de los Datos (Data Quality) desde el origen.

## Tecnologías Utilizadas

* **Backend:** Python, Flask, Werkzeug
* **Base de Datos:** SQLite, SQLAlchemy (a través de utilidades integradas)
* **Ingeniería de Datos / ETL:** Pandas, OpenPyXL, PDFPlumber
* **Frontend:** HTML5, CSS3, Jinja2 Templates
* **Despliegue:** Docker, Docker Compose, Waitress (WSGI Server)

## Configuración y Uso

### Opción 1: Despliegue Rápido con Docker (Recomendado)

Se requiere tener instalado [Docker](https://www.docker.com/) y `docker-compose`.

1. Clonar el repositorio:
   ```bash
   git clone <repositorio>
   cd monitoreo-de-produccion
   ```
2. Levantar el contenedor mediante Docker Compose:
   ```bash
   cd FORMATOS
   docker-compose up -d --build
   ```
3. La aplicación estará disponible en `http://localhost:5000`.

### Opción 2: Instalación Local con Python

Se requiere Python 3.8 o superior.

1. Clonar el repositorio y navegar al directorio del proyecto:
   ```bash
   git clone <repositorio>
   cd monitoreo-de-produccion/FORMATOS/webapp
   ```
2. Crear y activar un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows: venv\Scripts\activate
   # En Linux/Mac: source venv/bin/activate
   ```
3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configurar las variables de entorno (utilizando `.env.example` como referencia).
5. Inicializar la base de datos e iniciar la aplicación:
   ```bash
   python app.py
   ```
6. Acceder a `http://localhost:5000` mediante un navegador web.

## Estructura del Proyecto

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
