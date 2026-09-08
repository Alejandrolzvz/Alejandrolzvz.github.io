# Sistema de Monitoreo de Producción

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="../README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/monitoreo-de-produccion/ESP"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>

Plataforma web para digitalizar registros de producción industrial y convertir formatos físicos en datos estructurados, consultables y listos para análisis de calidad.

## Qué demuestra

- Extracción de tablas y métricas desde PDF hacia DataFrames y Excel.
- Captura validada de parámetros operativos por área.
- Control de acceso por roles con Flask-Login.
- Arquitectura modular con Blueprints y despliegue reproducible con Docker.

## Flujo de datos

`PDF / registro operativo -> extracción y validación -> SQLite -> aplicación Flask -> monitoreo y análisis`

## Configuración y uso

### Docker

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/monitoreo-de-produccion/FORMATOS
docker-compose up -d --build
```

Abre `http://localhost:5000`.

### Python local

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/monitoreo-de-produccion/FORMATOS/webapp
python -m venv venv
pip install -r requirements.txt
python app.py
```

Configura las variables según `.env.example` y abre `http://localhost:5000`.

## Estructura

- `FORMATOS/webapp/`: aplicación Flask, rutas, plantillas, utilidades y datos.
- `FORMATOS/convert_pdf_to_excel.py`: extracción de tablas desde PDF.
- `FORMATOS/docker-compose.yml`: orquestación de contenedores.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="../README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/monitoreo-de-produccion/ESP"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>
