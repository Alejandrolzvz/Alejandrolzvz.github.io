@echo off
:: Formato AAAA-MM-DD_HHMM
set "stamp=%date:~6,4%-%date:~3,2%-%date:~0,2%_%time:~0,2%%time:~3,2%"
set "stamp=%stamp: =0%"
set "backup_dir=C:\PROYECTOS\FORMATOS\webapp\backups"

echo Respaldando base de datos...
copy "C:\PROYECTOS\FORMATOS\webapp\database.db" "%backup_dir%\database_%stamp%.db"

echo Limpiando respaldos antiguos (más de 30 días)...
forfiles /P "%backup_dir%" /S /M *.db /D -30 /C "cmd /c del @path"

echo Proceso finalizado.
