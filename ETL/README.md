# Pipeline ETL de Ventas y Clientes

<p align="center">
   <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
   <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>

Pipeline reproducible para extraer reportes comerciales, validarlos y cargarlos en PostgreSQL. El proyecto muestra prácticas de ingeniería de datos aplicadas a ventas, clientes, direcciones y rutas operativas.

## Qué demuestra

- Automatización de cargas de ventas, clientes y direcciones desde CSV.
- Transformaciones eficientes con Polars y validaciones para evitar duplicados.
- Estrategias de `upsert` para mantener catálogos actualizados.
- Credenciales fuera del código mediante `PIPELINE_DB_PASSWORD`.

## Flujo

`CSV de origen -> Polars -> validaciones y reglas de negocio -> SQLAlchemy -> PostgreSQL`

## Tecnologías

Python 3, Polars, SQLAlchemy y PostgreSQL.

## Configuración y uso

Para ejecutar los pipelines en un entorno local, es necesario configurar las credenciales de la base de datos a través de variables de entorno para mantener los estándares de seguridad.

1. Clona el repositorio y entra al proyecto:
   ```bash
   git clone https://github.com/Alejandrolzvz/Alejandrolzvz.github.io.git
   cd Alejandrolzvz.github.io/ETL
   ```

2. Instala las dependencias en un entorno virtual:
   ```bash
   pip install polars sqlalchemy psycopg2-binary
   ```

3. Configura la contraseña de PostgreSQL:
   ```bash
   # En Linux / macOS
   export PIPELINE_DB_PASSWORD="tu_password_aqui"

   # En Windows (CMD)
   set PIPELINE_DB_PASSWORD=tu_password_aqui
   ```

4. Coloca los CSV de entrada en `data/` y ejecuta el pipeline requerido:
   ```bash
   python pipeline.py
   python pipeline_clientes.py
   ```

## Archivos principales

- `pipeline.py`: procesa ventas y evita duplicar fechas de liquidación.
- `pipeline_clientes.py`: actualiza el catálogo de clientes con `ON CONFLICT`.
- `pipeline_direcciones.py`: carga direcciones y valida duplicados mediante GUIDs.
- `db_utils.py`: centraliza la conexión a PostgreSQL.
- `ult_fecha_vta.py`: consulta las últimas fechas de venta por UDN.
- `data/`: archivos CSV sintéticos o anonimizados para el portafolio.
- `sql/`: consultas usadas para extraer la información de los sistemas origen.

Las credenciales y los datos productivos no forman parte del repositorio.

<p align="center">
   <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io"><img src="https://img.shields.io/badge/Volver%20al%20portafolio-1f2937?style=for-the-badge&logo=github&logoColor=white" alt="Volver al portafolio"></a>
   <a href="https://github.com/Alejandrolzvz/Alejandrolzvz.github.io/tree/main/ETL"><img src="https://img.shields.io/badge/Ver%20proyecto%20en%20GitHub-2563eb?style=for-the-badge&logo=github&logoColor=white" alt="Ver proyecto en GitHub"></a>
</p>
