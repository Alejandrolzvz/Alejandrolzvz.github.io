# Dashboard de Ventas y Eficiencia de Rutas

Este proyecto fue desarrollado con el objetivo de proporcionar una solución analítica para monitorear el desempeño en campo de los equipos de ventas.

La herramienta está diseñada para facilitar la visualización del rendimiento de ventas, evaluar la eficiencia de las rutas operativas (con un enfoque especial en las variaciones de desempeño entre distintos horarios) y medir las tasas de conversión de visitas programadas a ventas concretadas.

## Características Principales

*   **Monitoreo de Rendimiento:** Visualización en tiempo real del progreso de ventas.
*   **Análisis de Rutas:** Evaluación detallada de la eficiencia de las rutas operativas según horarios y ubicaciones.
*   **Tasas de Conversión:** Métricas precisas sobre la conversión de visitas a ventas efectivas.
*   **Interfaz Dinámica:** Dashboard interactivo para explorar diferentes KPIs de negocio.

## Tecnologías Utilizadas

El proyecto utiliza un conjunto de tecnologías modernas y robustas:
- **FastAPI** (y Uvicorn) para el desarrollo de la API del backend.
- **Pandas** para el procesamiento, limpieza y análisis de datos.
- **SQLAlchemy** para la integración con la base de datos **PostgreSQL**.
- **HTML**, **Tailwind CSS** y **Chart.js** para la construcción de una interfaz de usuario visual e interactiva.

## Configuración y Uso

Para ejecutar el proyecto completo, incluyendo el backend, siga los pasos a continuación. Se requiere tener instalados Python y PostgreSQL.

1. **Clonar el repositorio e ingresar al directorio:**
   ```bash
   cd sales-pipeline-dashboard
   ```

2. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En entornos Linux o macOS
   # venv\Scripts\activate   # En entornos Windows
   ```

3. **Instalar las dependencias del proyecto:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la conexión a la base de datos:**
   La aplicación requiere una variable de entorno para la conexión a PostgreSQL. Configure la siguiente variable con sus credenciales correspondientes:
   ```bash
   export DATABASE_URL="postgresql://usuario:password@localhost:5432/tu_base_de_datos"
   ```
   *(Si esta variable no se configura, el servidor iniciará correctamente, pero se presentarán errores al intentar obtener datos desde el frontend).*

5. **Iniciar el servidor:**
   ```bash
   python app.py
   ```
   *(Alternativamente, puede ejecutar: `uvicorn app:app --host 0.0.0.0 --port 8000 --reload`)*

6. **Acceso a la aplicación:**
   Una vez iniciado el servidor, acceda a `http://localhost:8000/` desde su navegador web.

## Demo en Vivo

Puede visualizar el diseño estático y la interfaz del dashboard sin necesidad de configurar el entorno de ejecución backend en el siguiente enlace:

[Ver Demo en Vivo](https://alejandrolzvz.github.io/Portafolio_AlejandroLV/sales-pipeline-dashboard/DEMO_Dashboard_Ventas.html)
