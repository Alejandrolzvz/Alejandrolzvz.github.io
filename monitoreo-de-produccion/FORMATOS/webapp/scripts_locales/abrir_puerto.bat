@echo off
:: Comprobar si se tienen privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando privilegios de administrador...
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo Agregando regla al Firewall de Windows para habilitar el puerto 5000...
powershell -Command "New-NetFirewallRule -DisplayName 'WebApp Flask (Puerto 5000)' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow"

echo Regla agregada correctamente. Ya deberias poder acceder desde otros equipos en la red local.
pause
