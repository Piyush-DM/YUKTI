@echo off
rem Start YUKTI on Windows. Double-click this file, or run it from any shell.
rem
rem Finds a Python for you: the repository's own virtual environment if one has
rem been created, then the launcher, then whatever `python` resolves to.
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" yukti.py %*
    goto :done
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 yukti.py %*
    goto :done
)

python yukti.py %*

:done
rem Keep the window open if this was double-clicked and something went wrong.
if %errorlevel% neq 0 pause
endlocal
