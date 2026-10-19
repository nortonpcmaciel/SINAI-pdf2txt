@echo off
cd /d "%~dp0"
set "PYTHON_LOCAL=C:\Users\User\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%PYTHON_LOCAL%" (
  start "" "http://127.0.0.1:8765"
  "%PYTHON_LOCAL%" app.py
) else (
  python -m pip install -r requirements.txt
  if errorlevel 1 goto erro
  start "" "http://127.0.0.1:8765"
  python app.py
)
pause
exit /b
:erro
echo Instale o Python 3 e tente novamente.
pause
