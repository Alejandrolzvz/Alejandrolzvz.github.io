@echo off
echo Iniciando el Servidor de Etiquetas QR...
echo La aplicacion estara disponible en tu red local.
echo.
echo Para acceder desde esta computadora: http://localhost:9000
echo.
uvicorn backend.main:app --host 0.0.0.0 --port 9000
pause
