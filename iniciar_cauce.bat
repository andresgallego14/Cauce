@echo off
rem Inicia Cauce en este computador y abre la pagina en el navegador.
cd /d "%~dp0"
start "Cauce - servidor" cmd /k venv\Scripts\python.exe -m uvicorn main:app
timeout /t 3 /nobreak >nul
start "" http://127.0.0.1:8000/