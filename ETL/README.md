# Sales and Customer ETL Pipeline

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/README.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>

Reproducible pipeline to extract, validate, and load commercial reports into PostgreSQL. It demonstrates data engineering practices applied to sales, customers, addresses, and operational routes.

## What it demonstrates

- Automated loading of sales, customers, and addresses from CSV files.
- Efficient Polars transformations and duplicate-prevention validations.
- `upsert` strategies to keep catalogs up to date.
- Credentials kept outside the code through `PIPELINE_DB_PASSWORD`.

## Flow

`Source CSV -> Polars -> validations and business rules -> SQLAlchemy -> PostgreSQL`

## Technologies

Python 3, Polars, SQLAlchemy, and PostgreSQL.

## Setup and usage

Configure database credentials through environment variables before running the pipelines.

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/ETL
pip install polars sqlalchemy psycopg2-binary
```

```bash
# Linux / macOS
export PIPELINE_DB_PASSWORD="your_password_here"

# Windows CMD
set PIPELINE_DB_PASSWORD=your_password_here
```

Place input CSV files in `data/` and run the required pipeline:

```bash
python pipeline.py
python pipeline_clientes.py
```

## Main files

- `pipeline.py`: processes sales and prevents duplicate settlement dates.
- `pipeline_clientes.py`: updates the customer catalog with `ON CONFLICT`.
- `pipeline_direcciones.py`: loads addresses and validates GUID duplicates.
- `db_utils.py`: centralizes the PostgreSQL connection.
- `ult_fecha_vta.py`: queries the latest sales dates by business unit.
- `data/`: synthetic or anonymized portfolio CSV files.
- `sql/`: queries used to extract source-system data.

Credentials and production data are not included in the repository.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Back%20to%20portfolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Back to portfolio"></a>
  <a href="ESP/README.md"><img src="https://img.shields.io/badge/Español-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Leer en español"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/View%20project%20on%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="View project on GitHub"></a>
</p>
