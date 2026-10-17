#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then echo "Run ./scripts/build_linux.sh first."; exit 1; fi
source .venv/bin/activate
PYTHONPATH=src python entry.py
