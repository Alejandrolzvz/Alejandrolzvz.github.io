# Pipeline ETL de Ventas y Clientes

Este directorio contiene un pipeline ETL (Extracción, Transformación y Carga) diseñado para procesar y cargar datos comerciales desde archivos en formato CSV hacia una base de datos relacional PostgreSQL.

El proyecto fue desarrollado para automatizar el procesamiento de reportes de ventas, el directorio de clientes y la información de rutas operativas. Con el objetivo de lograr un procesamiento eficiente de grandes volúmenes de datos, se implementó **Polars** para la fase de extracción y transformación, y **SQLAlchemy** para la gestión de las conexiones y la carga de datos.

## Características Principales

*   **Automatización Comercial:** Automatiza la carga y actualización de datos de ventas, clientes y rutas.
*   **Procesamiento Eficiente:** Maneja grandes volúmenes de información en CSV mediante Polars para minimizar el uso de memoria.
*   **Lógica de Negocio (Upsert):** Implementa actualizaciones condicionales en base de datos para no duplicar catálogos existentes.
*   **Gestión Segura:** Conexión centralizada a la base de datos PostgreSQL utilizando SQLAlchemy y variables de entorno para las credenciales.

## Tecnologías Utilizadas

*   **Python 3**
*   **Polars**: Utilizado por su gran velocidad y bajo consumo de memoria al procesar archivos CSV pesados.
*   **SQLAlchemy**: Para manejar las conexiones y operaciones en PostgreSQL de forma segura.
*   **PostgreSQL**: Base de datos destino para almacenar la información procesada (Staging y Data Warehouse).

## Configuración y Uso

Para ejecutar los pipelines en un entorno local, es necesario configurar las credenciales de la base de datos a través de variables de entorno para mantener los estándares de seguridad.

1. Clona el repositorio:
   ```bash
   git clone <tu-repositorio>
   cd <nombre-repo>/ETL
   ```

2. Instala las dependencias (se recomienda usar un entorno virtual):
   ```bash
   pip install polars sqlalchemy psycopg2-binary
   ```

3. Exporta la contraseña de tu base de datos local (Postgres):
   ```bash
   # En Linux / macOS
   export PIPELINE_DB_PASSWORD="tu_password_aqui"

   # En Windows (CMD)
   set PIPELINE_DB_PASSWORD=tu_password_aqui
   ```

4. Ejecuta el pipeline que necesites. Por ejemplo:
   ```bash
   python pipeline.py
   python pipeline_clientes.py
   ```

## Estructura del Proyecto

*   `pipeline.py`: Script principal para procesar los archivos de ventas (`ventas.csv` o `ventas.xlsx`). Incluye validaciones para evitar la duplicidad de fechas de liquidación.
*   `pipeline_clientes.py`: Procesa el catálogo de clientes (`clientes.csv`). Implementa una estrategia de "Upsert" (Update/Insert) utilizando `ON CONFLICT` en PostgreSQL para mantener el catálogo actualizado sin duplicar registros.
*   `pipeline_direcciones.py`: Procesa el directorio de direcciones de clientes (`direcciones.csv`), manejando coordenadas geográficas y múltiples validaciones de duplicados a través de GUIDs.
*   `db_utils.py`: Módulo compartido que centraliza la lógica de conexión a la base de datos de manera segura y reutilizable (principio DRY).
*   `ult_fecha_vta.py`: Utilidad para consultar rápidamente las últimas 5 fechas de liquidación registradas por UDN en la base de datos.
*   `data/`: Directorio donde se colocan los archivos fuente CSV. *(Nota: Por privacidad, los datos incluidos en este repositorio portafolio son sintéticos/anonimizados).*
*   `sql/`: Consultas SQL de extracción utilizadas en los sistemas origen (FastReport) para generar los CSVs.
