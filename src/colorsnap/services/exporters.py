from __future__ import annotations
import json, re
from pathlib import Path
from ..core.models import Palette
from ..core.colors import hex_to_rgb, hex_to_hsl

def _slug(name:str,i:int) -> str:
    s=re.sub(r"[^a-z0-9]+","-",name.lower()).strip("-"); return s or f"color-{i+1}"

def export_palette(p:Palette, fmt:str, path:str|Path) -> Path:
    fmt=fmt.lower(); out=Path(path)
    if fmt=="json":
        text=json.dumps({"format":"ColorSnapStudio palette","version":1, **p.to_dict()},indent=2)
    elif fmt=="css":
        lines=[":root {"]
        for i,c in enumerate(p.colors):
            r,g,b=hex_to_rgb(c.hex); h,s,l=hex_to_hsl(c.hex)
            lines.append(f"  --{_slug(c.name,i)}: {c.hex}; /* rgb({r}, {g}, {b}) hsl({h}, {s}%, {l}%) */")
        lines.append("}"); text="\n".join(lines)+"\n"
    elif fmt=="scss":
        text="".join(f"${_slug(c.name,i)}: {c.hex};\n" for i,c in enumerate(p.colors))
    elif fmt=="txt":
        lines=[f"{p.name} — ColorSnap Studio"]
        for c in p.colors:
            r,g,b=hex_to_rgb(c.hex); h,s,l=hex_to_hsl(c.hex)
            lines.append(f"{c.name}: {c.hex}  RGB({r}, {g}, {b})  HSL({h}, {s}%, {l}%)")
        text="\n".join(lines)+"\n"
    else: raise ValueError(f"Unsupported export format: {fmt}")
    out.write_text(text,encoding="utf-8"); return out
