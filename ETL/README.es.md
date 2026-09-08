# Pipeline ETL de Ventas y Clientes

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>

Pipeline reproducible para extraer reportes comerciales, validarlos y cargarlos en PostgreSQL. Demuestra prácticas de ingeniería de datos aplicadas a ventas, clientes, direcciones y rutas operativas.

## Qué demuestra

- Cargas automatizadas desde archivos CSV.
- Transformaciones eficientes con Polars y validaciones contra duplicados.
- Estrategias de `upsert` para mantener catálogos actualizados.
- Credenciales fuera del código mediante `PIPELINE_DB_PASSWORD`.

## Flujo

`CSV de origen -> Polars -> validaciones y reglas de negocio -> SQLAlchemy -> PostgreSQL`

## Configuración y uso

```bash
git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
cd Alejandrolzvz.github.io/ETL
pip install polars sqlalchemy psycopg2-binary
```

Configura `PIPELINE_DB_PASSWORD`, coloca los CSV en `data/` y ejecuta el pipeline requerido:

```bash
python pipeline.py
python pipeline_clientes.py
```

## Archivos principales

- `pipeline.py`: procesa ventas y evita fechas de liquidación duplicadas.
- `pipeline_clientes.py`: actualiza el catálogo con `ON CONFLICT`.
- `pipeline_direcciones.py`: carga direcciones y valida GUIDs.
- `db_utils.py`: centraliza la conexión PostgreSQL.
- `ult_fecha_vta.py`: consulta las últimas fechas por unidad de negocio.
- `data/`: CSV sintéticos o anonimizados.
- `sql/`: consultas de extracción.

Las credenciales y los datos productivos no forman parte del repositorio.

<p align="center">
  <a href="https://alejandrolzvz.github.io/"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/English-d97706?style=for-the-badge&logo=readme&logoColor=white" alt="Read in English"></a>
  <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>
