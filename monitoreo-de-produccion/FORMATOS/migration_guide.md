# Guía de Migración a un Nuevo Dispositivo

Sigue estos pasos para mover la aplicación a otra computadora manteniendo todos los datos y configuraciones.

## 1. Preparación en el equipo actual
Copia la carpeta completa del proyecto. Asegúrate de incluir:
- La carpeta `webapp/` (contiene el código y la base de datos).
- El archivo [database.db](file:///C:/PROYECTOS/FORMATOS/webapp/database.db) (en `webapp/`).
- El archivo [.env](file:///c:/PROYECTOS/FORMATOS/webapp/.env) (contiene la clave secreta).
- El archivo `requirements.txt`.

## 2. Configuración en el nuevo equipo (Windows)

### A. Instalar Python
1. Descarga e instala **Python 3.10 o superior** desde [python.org](https://www.python.org/).
2. **MUY IMPORTANTE:** Al instalar, marca la casilla que dice **"Add Python to PATH"**.

### B. Instalar Dependencias
1. Abre una terminal (PowerShell o CMD) en la carpeta `webapp/` del nuevo equipo.
2. Ejecuta el comando para instalar todas las librerías necesarias:
   ```bash
   pip install -r requirements.txt
   ```

### C. Ajustar el archivo [.env](file:///c:/PROYECTOS/FORMATOS/webapp/.env)
Si la nueva computadora tendrá una dirección IP distinta, no necesitas cambiar nada en el código, pero asegúrate de que el archivo [.env](file:///c:/PROYECTOS/FORMATOS/webapp/.env) tenga la configuración correcta:
```env
SECRET_KEY=tu_clave_secreta
FLASK_DEBUG=False
```

## 3. Instalación de Servicios Automáticos
Para que la aplicación arranque sola y los respaldos funcionen:
1. Abre **PowerShell como Administrador**.
2. Navega hasta la carpeta `webapp/`.
3. Ejecuta el script de instalación que preparamos:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process
   .\install_tasks.ps1
   ```
4. **Nota:** Si las rutas cambiaron (por ejemplo, si ya no es `C:\PROYECTOS\FORMATOS`), deberás editar `start_server.vbs`, `backup_db.bat` e `install_tasks.ps1` con la nueva ruta antes de ejecutar este paso.

## 4. Verificación
1. Abre el navegador en el nuevo equipo e ingresa a `http://localhost:5000`.
2. Para que otros dispositivos lo vean, busca la nueva IP con `ipconfig` y asegúrate de abrir el puerto 5000 en el Firewall de Windows (como lo hicimos anteriormente).

---
**¿Necesitas que ajuste los scripts para una ruta diferente en el nuevo equipo?** Solo dime la nueva ubicación y lo actualizo.
