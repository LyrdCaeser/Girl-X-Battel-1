@echo off
setlocal
set PYTHONUTF8=1
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv .venv
) else (
    python -m venv .venv
)
if errorlevel 1 goto python_missing
:install
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" server.py --open %*
if errorlevel 1 goto failed
exit /b 0
:python_missing
echo Instala Python 3.10 o posterior desde https://www.python.org/downloads/windows/
echo Activa la opcion de agregar Python al PATH y vuelve a abrir este archivo.
pause
exit /b 1
:failed
echo No se pudo iniciar el juego. Revisa el mensaje de arriba.
echo Si los puertos estan ocupados: Iniciar-Windows.cmd --http-port 9242 --tcp-port 9243
pause
exit /b 1
