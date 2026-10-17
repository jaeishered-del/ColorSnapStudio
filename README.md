# ColorSnap Studio 🎨

Premium, fully-offline desktop app for extracting dominant color palettes from images, editing them, checking WCAG contrast, and exporting design tokens. Targets **Windows 10/11** (source is cross-platform so a Fedora/Linux build is straightforward).

![Icon](assets/icon.png)

## Features
- Drag & drop / open **PNG, JPG, JPEG, WEBP, BMP** with validation and graceful corrupt-file errors
- Genuine dominant-color extraction (Pillow median-cut quantization, most-frequent-first), 3–16 colors, in a background thread
- Swatch cards with HEX/RGB/HSL, one-click copy per format, copy-all, rename, reorder (←/→), remove, manual picker + HEX input
- Harmonies: complementary, analogous, triadic, split-complementary
- WCAG 2.x contrast checker (ratios + AA/AAA for normal & large text, with disclaimer)
- Local palette library: versioned JSON (`"version": 1`) in the OS user-data dir (`%APPDATA%\ColorSnapStudio` on Windows), rename/delete with confirmation
- Export **JSON / CSS custom properties / SCSS / TXT**
- Settings (theme dark/light, default color count) persisted locally; first-run empty state, status-bar toasts, shortcuts `Ctrl+O` / `Ctrl+S` / `Ctrl+E`

## Privacy
All processing is 100% local. Images are never uploaded; there is no network access, account, telemetry, or API key.

## Quick start (Windows)
```bat
git clone <your-repo-url> ColorSnapStudio
cd ColorSnapStudio
scripts\build_windows.bat
dist\ColorSnapStudio.exe
```
Or develop:
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
set PYTHONPATH=src
python -m colorsnap.main
```

## Linux / Fedora development
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .
PYTHONPATH=src python -m colorsnap.main
# headless test: QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m colorsnap.main &
```

## Tests
```bash
python -m pytest -q
```

## Windows packaging
`scripts/build_windows.bat` creates `.venv`, installs deps, runs tests, then runs PyInstaller via `ColorSnapStudio.spec` → a windowed (no console) `dist\ColorSnapStudio.exe` with the custom icon. Optional installer: open `scripts/installer.iss` in Inno Setup 6 and Compile.

> Note: a Windows `.exe` must be built on Windows (or a Windows CI runner, e.g. GitHub Actions `windows-latest`). A Linux build produces a Linux binary, not a Windows EXE.

## Project structure
```
src/colorsnap/{main.py, core/{colors,models,extraction}.py, services/{storage,exporters}.py, ui/{main_window,theme}.py, resources/icon.png}
tests/  assets/icon.{png,ico}  scripts/{build_windows.bat,build_windows.ps1,installer.iss,run_dev.bat}
```

## Suggested GitHub Actions (Windows EXE on release)
Add `.github/workflows/build-windows.yml` with `runs-on: windows-latest`, setup-python 3.12, then `scripts\build_windows.bat`, and upload `dist/ColorSnapStudio.exe` as an artifact. (Included below in repo.)

## License
MIT — see `LICENSE`. Built with PySide6 (LGPL), Pillow, NumPy.

## Run/build on Linux

From the project root, run `./scripts/build_linux.sh`. This creates a virtual environment, installs dependencies, runs the tests, and attempts to build `dist/ColorSnapStudio`. It requires Python 3, internet access to install packages, and Qt-compatible system libraries. The result is a Linux executable, not a Windows `.exe`.

To run from source after setup, use `./scripts/run_linux.sh`.

## Build the Windows EXE without a Windows PC

The GitHub Actions workflow at `.github/workflows/build-windows.yml` builds on a hosted Windows runner. Push this project to a GitHub repository, then open **Actions → Build Windows EXE → Run workflow**. When it finishes, download the `ColorSnapStudio-Windows` artifact from that workflow run. Pushing a version tag such as `v1.0.1` also attaches the executable to a GitHub Release. The Windows EXE is not included in this ZIP because a Windows build has not yet been run or verified.
