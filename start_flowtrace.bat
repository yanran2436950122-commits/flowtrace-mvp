@echo off
setlocal

cd /d "%~dp0"
set "FLOWTRACE_ROOT=%~dp0"
set "FLOWTRACE_URL=http://127.0.0.1:8765/"

start "FlowTrace Service" cmd /k "cd /d ""%FLOWTRACE_ROOT%"" && set PYTHONPATH=%FLOWTRACE_ROOT%src && if exist ""%FLOWTRACE_ROOT%.venv\Scripts\python.exe"" (""%FLOWTRACE_ROOT%.venv\Scripts\python.exe"" -m flowtrace.server) else (python -m flowtrace.server)"

timeout /t 2 /nobreak >nul
start "" "%FLOWTRACE_URL%"

endlocal
