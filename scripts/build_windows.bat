@echo off
setlocal
cd /d %~dp0\..
python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -e .
python -m pytest -q
if errorlevel 1 exit /b 1
pyinstaller --noconfirm ColorSnapStudio.spec
echo.
echo Build finished: dist\ColorSnapStudio.exe
dir dist\ColorSnapStudio.exe
endlocal
