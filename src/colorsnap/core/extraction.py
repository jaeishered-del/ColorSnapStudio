from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps
from .models import ColorEntry

SUPPORTED={".png",".jpg",".jpeg",".webp",".bmp"}
class ImageValidationError(ValueError): pass

def validate_image_path(path:str|Path) -> Path:
    p=Path(path)
    if not p.is_file(): raise ImageValidationError(f"File not found: {p}")
    if p.suffix.lower() not in SUPPORTED: raise ImageValidationError(f"Unsupported format '{p.suffix}'. Use PNG, JPG, JPEG, WEBP or BMP.")
    return p

def load_image(path:str|Path) -> Image.Image:
    p=validate_image_path(path)
    try:
        with Image.open(p) as im:
            im.load(); img=im.copy()
    except Exception as e: raise ImageValidationError(f"Could not open image (it may be corrupt): {e}") from e
    return ImageOps.exif_transpose(img)

def extract_dominant_colors(path_or_image, count:int=6) -> list[ColorEntry]:
    """Median-cut quantization via Pillow. Returns most frequent representative colors."""
    if not 3<=count<=16: raise ValueError("Color count must be between 3 and 16")
    img=load_image(path_or_image) if isinstance(path_or_image,(str,Path)) else path_or_image
    img=img.convert("RGBA")
    # Composite transparency onto checker-neutral dark bg, then RGB
    bg=Image.new("RGBA", img.size, (32,32,32,255)); img=Image.alpha_composite(bg,img).convert("RGB")
    img.thumbnail((320,320), Image.Resampling.LANCZOS)
    # Quantize; Pillow gives palette + pixel counts
    q=img.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette=q.getpalette() or []
    counts=sorted(q.getcolors() or [], reverse=True)  # (count, palette_index)
    out=[]
    for freq, idx in counts[:count]:
        r,g,b=palette[idx*3:idx*3+3]
        out.append(ColorEntry(hex=f"#{r:02X}{g:02X}{b:02X}"))
    if not out: raise ImageValidationError("No colors could be extracted from this image.")
    return out
