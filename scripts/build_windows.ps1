$ErrorActionPreference="Stop"; Set-Location (Join-Path $PSScriptRoot "..")
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip; pip install -r requirements-dev.txt; pip install -e .
python -m pytest -q; pyinstaller --noconfirm ColorSnapStudio.spec
Get-Item dist\ColorSnapStudio.exe
