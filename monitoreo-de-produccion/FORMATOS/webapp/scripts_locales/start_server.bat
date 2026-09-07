@echo off
set PYTHONUTF8=1
cd /d C:\PROYECTOS\FORMATOS\webapp
:: Respaldar base de datos al iniciar
call backup_db.bat
call C:\Users\pc\anaconda3\Scripts\activate.bat base
C:\Users\pc\anaconda3\python.exe run_waitress.py
