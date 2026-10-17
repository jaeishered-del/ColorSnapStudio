# PyInstaller spec — windowed, one-file Windows build. Also used on Linux for smoke builds.
import pathlib
root=pathlib.Path(SPECPATH)
a=Analysis([str(root/"entry.py")], pathex=[str(root/"src")], binaries=[], datas=[(str(root/"assets/icon.png"),"colorsnap/resources"),(str(root/"src/colorsnap/resources/icon.png"),"colorsnap/resources")], hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=[], noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name="ColorSnapStudio",debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(root/"assets/icon.ico"))
