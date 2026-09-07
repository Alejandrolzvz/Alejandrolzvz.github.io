# Dashboard de Ventas y Eficiencia de Rutas

Dashboard analítico para explorar el desempeño comercial de rutas de campo y comparar ventas, visitas y conversiones por periodo, horario, segmento y unidad de negocio.

**[Abrir demo estática en GitHub Pages](https://alejandrolzvz.github.io/sales-pipeline-dashboard/DEMO_Dashboard_Ventas.html)**

## Qué resuelve

- Convierte registros de recorridos en KPIs de ventas, visitas programadas, visitas realizadas y compras.
- Permite analizar el desempeño por ruta, categoría, UDN, día, mes y franja horaria.
- Facilita el ranking de rutas y la comparación entre segmentos para detectar oportunidades operativas.
- Incluye exportación de datos a CSV y un snapshot HTML para compartir el análisis sin backend.

## Flujo de datos

`PostgreSQL -> FastAPI -> Pandas -> API JSON -> HTML / Chart.js`

El backend normaliza fechas y rutas, calcula agrupaciones temporales y devuelve una estructura lista para que el frontend filtre y visualice los indicadores.

## Stack

**Backend:** Python, FastAPI, Uvicorn, Pandas, SQLAlchemy, PostgreSQL
**Frontend:** HTML, Tailwind CSS, JavaScript, Chart.js
**Publicación:** HTML estático compatible con GitHub Pages

## Ejecución local

Requiere Python y PostgreSQL.

```bash
cd sales-pipeline-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql://usuario:password@localhost:5432/tu_base_de_datos
python app.py
```

En Linux o macOS, sustituye la activación por `source venv/bin/activate` y configura `DATABASE_URL` con `export`.

Abre `http://localhost:8000/`. La demo pública no necesita PostgreSQL: usa un snapshot con datos de ejemplo y no representa una conexión en vivo.

## Archivos principales

- `app.py`: API FastAPI, consulta a PostgreSQL y agregaciones de negocio.
- `index.html`: interfaz conectada a la API.
- `DEMO_Dashboard_Ventas.html`: versión autocontenida para GitHub Pages.
- `requirements.txt`: dependencias de ejecución.
