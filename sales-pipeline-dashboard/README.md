# Sales Performance and Route Efficiency Dashboard

<p align="center">
	<a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
	<a href="README.es.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/sales-pipeline-dashboard"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>

An analytical dashboard for exploring field-route performance and comparing sales, visits, and conversions by period, time slot, segment, and business unit.

**[Open the static demo on GitHub Pages](https://alejandrolzvz.github.io/sales-pipeline-dashboard/DEMO_Dashboard_Ventas.html)**

## What it solves

- Converts route records into sales, scheduled visits, completed visits, and purchase KPIs.
- Enables analysis by route, category, business unit, day, month, and time slot.
- Supports route ranking and segment comparisons to identify operational opportunities.
- Includes CSV export and an HTML snapshot that can be shared without a backend.

## Data flow

`PostgreSQL -> FastAPI -> Pandas -> API JSON -> HTML / Chart.js`

The backend normalizes dates and routes, calculates time-based aggregations, and returns a structure ready for frontend filtering and visualization.

## Stack

**Backend:** Python, FastAPI, Uvicorn, Pandas, SQLAlchemy, PostgreSQL
**Frontend:** HTML, Tailwind CSS, JavaScript, Chart.js
**Publishing:** Static HTML compatible with GitHub Pages

## Local setup

Requires Python and PostgreSQL.

```bash
cd sales-pipeline-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql://usuario:password@localhost:5432/tu_base_de_datos
python app.py
```

On Linux or macOS, use `source venv/bin/activate` and configure `DATABASE_URL` with `export`.

Open `http://localhost:8000/`. The public demo does not need PostgreSQL: it uses a snapshot with sample data and is not a live connection.

## Main files

- `app.py`: FastAPI API, PostgreSQL query, and business aggregations.
- `index.html`: API-connected interface.
- `DEMO_Dashboard_Ventas.html`: self-contained GitHub Pages version.
- `requirements.txt`: runtime dependencies.

<p align="center">
	<a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
	<a href="README.es.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
	<a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/sales-pipeline-dashboard"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>
