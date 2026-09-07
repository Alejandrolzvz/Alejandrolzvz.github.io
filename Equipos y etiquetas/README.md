# Sistema de Gestión y Etiquetado de Equipos

Una aplicación orientada a la estandarización y captura de datos de inventario. Está diseñada para garantizar que la información técnica de los equipos mantenga coherencia y calidad desde su registro. Este paso es fundamental para proyectos analíticos de mayor escala, como el mantenimiento predictivo o el seguimiento del ciclo de vida de los equipos.

## Características Principales

*   **Estandarización de Datos:** Asegura la consistencia de la información técnica del inventario desde el momento del registro.
*   **Generador Dinámico de Etiquetas:** Incluye un módulo para diseñar y generar etiquetas (con códigos QR) que facilitan el seguimiento en campo.
*   **Autenticación Segura:** Sistema de autenticación de usuarios implementado con JSON Web Tokens (JWT).
*   **Interfaz Ligera y Rápida:** Frontend desarrollado sin frameworks pesados, optimizando la velocidad y la experiencia de usuario.

## Tecnologías Utilizadas

*   **Backend:** Python, FastAPI
*   **Autenticación:** JWT (JSON Web Tokens)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript
*   **Generación de Etiquetas:** qrious (para códigos QR), manipulación del DOM nativa.

## Configuración y Uso

1. Clonar el repositorio y acceder al directorio del proyecto:
   ```bash
   git clone <repositorio>
   cd "Equipos y etiquetas"
   ```

2. Instalar las dependencias del backend:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

3. Iniciar el servidor de desarrollo:
   En sistemas Windows, puede ejecutar el script proporcionado:
   ```bash
   iniciar_servidor.bat
   ```
   Alternativamente, ejecute directamente con uvicorn:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 9000
   ```

4. Acceder a la aplicación a través de `http://localhost:9000`.

## Demo en Vivo

Puede probar la interfaz de generación de etiquetas en línea de forma estática en el siguiente enlace:

[Ver Demo en Vivo](https://alejandrolzvz.github.io/Portafolio_AlejandroLV/Equipos%20y%20etiquetas/demo-etiquetas/index.html)
