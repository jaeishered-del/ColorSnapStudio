#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Python 3 is required. Install Python and venv support with your distro package manager."
  exit 1
fi
"$PYTHON" --version
if [ ! -d .venv ]; then "$PYTHON" -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt pyinstaller
PYTHONPATH=src python -m pytest -q
pyinstaller --noconfirm --clean --windowed --name ColorSnapStudio \
  --add-data "assets/icon.png:assets" \
  --add-data "src/colorsnap/resources/icon.png:colorsnap/resources" \
  --paths src entry.py
echo "Linux build output: dist/ColorSnapStudio (Linux executable, not Windows .exe)"
