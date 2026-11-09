@echo off
rem Guarda una copia de la base de datos en Documentos\CauceRespaldos, con fecha y hora.
cd /d "%~dp0"
venv\Scripts\python.exe -c "import sqlite3, os, datetime; d = os.path.join(os.path.expanduser('~'), 'Documents', 'CauceRespaldos'); os.makedirs(d, exist_ok=True); f = os.path.join(d, 'cauce-' + datetime.datetime.now().strftime('%%Y-%%m-%%d-%%H%%M') + '.db'); o = sqlite3.connect('cauce.db'); c = sqlite3.connect(f); o.backup(c); c.close(); o.close(); print('Copia guardada en', f)"
pause
