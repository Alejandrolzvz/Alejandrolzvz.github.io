# Dashboard de Ventas y Eficiencia de Rutas

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/sales-pipeline-dashboard"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>

Dashboard analítico para explorar el desempeño comercial de rutas de campo y comparar ventas, visitas y conversiones por periodo, horario, segmento y unidad de negocio.

**[Abrir demo estática en GitHub Pages](https://alejandrolzvz.github.io/sales-pipeline-dashboard/DEMO_Dashboard_Ventas.html)**

## Qué resuelve

- Convierte registros de recorridos en KPIs de ventas, visitas programadas, visitas realizadas y compras.
- Permite analizar el desempeño por ruta, categoría, unidad de negocio, día, mes y franja horaria.
- Facilita el ranking de rutas y la comparación entre segmentos.
- Incluye exportación a CSV y un snapshot HTML sin backend.

## Flujo de datos

`PostgreSQL -> FastAPI -> Pandas -> API JSON -> HTML / Chart.js`

## Stack

**Backend:** Python, FastAPI, Uvicorn, Pandas, SQLAlchemy, PostgreSQL  
**Frontend:** HTML, Tailwind CSS, JavaScript, Chart.js  
**Publicación:** HTML estático compatible con GitHub Pages

## Ejecución local

```bash
cd sales-pipeline-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql://usuario:password@localhost:5432/tu_base_de_datos
python app.py
```

Abre `http://localhost:8000/`. La demo pública usa datos de ejemplo y no representa una conexión en vivo.

## Archivos principales

- `app.py`: API FastAPI, consulta a PostgreSQL y agregaciones.
- `index.html`: interfaz conectada a la API.
- `DEMO_Dashboard_Ventas.html`: versión autocontenida para GitHub Pages.
- `requirements.txt`: dependencias.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/sales-pipeline-dashboard"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>
