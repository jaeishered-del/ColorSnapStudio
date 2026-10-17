from __future__ import annotations
import json, os
from pathlib import Path
from ..core.models import Palette

FORMAT_VERSION=1
def user_data_dir(app="ColorSnapStudio") -> Path:
    if os.name=="nt":
        base=Path(os.environ.get("APPDATA", Path.home()/"AppData/Roaming"))
    else:
        # Respect XDG on Linux and other POSIX systems, including containers
        # where /home may not exist or the user's home directory is customized.
        base=Path(os.environ.get("XDG_DATA_HOME", Path.home()/".local/share"))
    d=base/app; d.mkdir(parents=True, exist_ok=True); return d

def default_library_path() -> Path: return user_data_dir()/"palettes.json"

class LibraryError(ValueError): pass

def save_library(palettes:list[Palette], path:Path|None=None) -> Path:
    p=path or default_library_path(); p.parent.mkdir(parents=True, exist_ok=True)
    data={"format":"ColorSnapStudio palettes","version":FORMAT_VERSION,"palettes":[x.to_dict() for x in palettes]}
    tmp=p.with_suffix(".tmp"); tmp.write_text(json.dumps(data,indent=2),encoding="utf-8"); tmp.replace(p); return p

def load_library(path:Path|None=None) -> list[Palette]:
    p=path or default_library_path()
    if not p.exists(): return []
    try: data=json.loads(p.read_text(encoding="utf-8"))
    except Exception as e: raise LibraryError(f"Palette library is corrupted: {e}") from e
    if not isinstance(data,dict) or data.get("version")!=FORMAT_VERSION or not isinstance(data.get("palettes"),list):
        raise LibraryError("Unsupported or invalid palette library format/version.")
    try: return [Palette.from_dict(x) for x in data["palettes"]]
    except Exception as e: raise LibraryError(f"Invalid palette data: {e}") from e

def settings_path() -> Path: return user_data_dir()/"settings.json"
def save_settings(s:dict) -> Path:
    p=settings_path(); p.write_text(json.dumps(s,indent=2),encoding="utf-8"); return p
def load_settings() -> dict:
    p=settings_path()
    if not p.exists(): return {}
    try:
        d=json.loads(p.read_text(encoding="utf-8")); return d if isinstance(d,dict) else {}
    except Exception: return {}
