@echo off
setlocal
python -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if errorlevel 1 goto launcher
python "%~dp0debug_terminal.py" %*
exit /b %errorlevel%
:launcher
py -3 "%~dp0debug_terminal.py" %*
exit /b %errorlevel%
