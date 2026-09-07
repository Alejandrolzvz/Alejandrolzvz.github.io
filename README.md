# Portafolio de Análisis de Datos - Alejandro

Bienvenido a mi portafolio profesional. En este repositorio documento los proyectos que he desarrollado para demostrar mis habilidades en el análisis y procesamiento de datos, así como en la estructuración de la información. Mi enfoque abarca el ciclo completo de los datos: desde la captura estructurada, limpieza y procesamiento, hasta la visualización y construcción de dashboards para facilitar la toma de decisiones.

## Contenido del Repositorio

*   **[Dashboard de Ventas y Rutas](./sales-pipeline-dashboard/README.md):**
    Este es un proyecto integral desarrollado desde cero. El backend está construido en Python utilizando FastAPI, el procesamiento de datos se realiza con Pandas, y la persistencia se gestiona mediante SQLAlchemy conectándose a una base de datos PostgreSQL. En cuanto a la visualización, el frontend fue diseñado con HTML, Tailwind CSS para una interfaz moderna, y Chart.js para las representaciones gráficas. El objetivo de la herramienta es monitorizar el rendimiento de ventas, analizar la eficiencia de las rutas de campo y medir las tasas de conversión.
    Adicionalmente, se incluye una versión estática (`DEMO_Dashboard_Ventas.html`) en la carpeta del proyecto para visualizar el diseño e interfaz sin necesidad de ejecutar el servidor local.

*   **[Sistema de Gestión y Etiquetado de Equipos](./Equipos%20y%20etiquetas/README.md):**
    Una aplicación orientada a la estandarización y captura de datos de inventario. Está diseñada para garantizar que la información técnica de los equipos mantenga coherencia y calidad desde su registro. Este paso es fundamental para proyectos analíticos de mayor escala, como el mantenimiento predictivo o el seguimiento del ciclo de vida de los equipos. El proyecto implementa una arquitectura basada en FastAPI para el backend, autenticación mediante JWT, y un frontend sin frameworks pesados (Vanilla JS) que incluye un generador dinámico de etiquetas.

*   **[ETL de Ventas y Clientes](./ETL/README.md):**
    Un pipeline ETL (Extract, Transform, Load) diseñado para procesar y cargar datos comerciales desde archivos CSV hacia una base de datos PostgreSQL. Utiliza Polars para la extracción y transformación, y SQLAlchemy para la carga en base de datos.

*   **[Sistema de Monitoreo de Producción](./monitoreo-de-produccion/README.md):**
    Una plataforma web diseñada para la digitalización, captura y monitoreo de parámetros de producción industrial. Implementa procesos ETL desde formatos físicos hacia formatos estructurados, facilitando el análisis de calidad de los datos desde el origen.

Cualquier consulta técnica o feedback sobre el código es bienvenido.
