@echo off
title Reiniciando Servidor Web

:: Comprobar si se tienen privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando privilegios de administrador para poder apagar el servidor fantasma...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo =========================================
echo       Reiniciando Servidor Web...
echo =========================================
echo.

echo [1/2] Forzando detencion de todos los procesos Python previos...
taskkill /F /IM python.exe >nul 2>&1

:: Esperar 2 segundos para asegurar de que el puerto 5000 ha sido liberado
timeout /t 2 /nobreak >nul

echo.
echo [2/2] Iniciando el servidor productivo nuevamente...
start "" "C:\PROYECTOS\FORMATOS\webapp\start_server.vbs"

echo.
echo =========================================
echo    Servidor reiniciado exitosamente!
echo =========================================
timeout /t 3 >nul
