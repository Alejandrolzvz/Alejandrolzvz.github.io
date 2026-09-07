# ETL portfolio package

The publishable artifacts are:

- `sql/`: SQL extracted from the FastReport `.FRSql` objects.
- `data/`: UTF-8 CSV files with stable synthetic identifiers, names, addresses,
  contact data, coordinates and shifted dates.
- `pipeline*.py`, `respaldo.py` and `ult_fecha_vta.py`: ETL code with database
  credentials read from `PIPELINE_DB_PASSWORD`.

Raw CSV exports, the workbook, binary export and `.FRSql` report objects are
excluded by `.gitignore`. Never publish those source files.