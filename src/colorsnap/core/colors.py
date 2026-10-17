from __future__ import annotations
import colorsys, math, re
from dataclasses import dataclass

_HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")
_HEX3_RE = re.compile(r"^#?[0-9a-fA-F]{3}$")

def normalize_hex(value: str) -> str:
    v=value.strip()
    if _HEX3_RE.match(v):
        v=v.lstrip("#"); v="".join(c*2 for c in v)
    if not _HEX_RE.match(v): raise ValueError(f"Invalid HEX color: {value!r} (expected #RRGGBB)")
    return "#"+v.lstrip("#").upper()

def hex_to_rgb(value: str) -> tuple[int,int,int]:
    v=normalize_hex(value)[1:]; return int(v[0:2],16), int(v[2:4],16), int(v[4:6],16)

def rgb_to_hex(r:int,g:int,b:int) -> str:
    for c in (r,g,b):
        if not 0<=c<=255: raise ValueError("RGB components must be 0-255")
    return f"#{r:02X}{g:02X}{b:02X}"

def rgb_to_hsl(r:int,g:int,b:int) -> tuple[int,int,int]:
    h,l,s=colorsys.rgb_to_hls(r/255,g/255,b/255); return round(h*360)%360, round(s*100), round(l*100)

def hsl_to_rgb(h:float,s:float,l:float) -> tuple[int,int,int]:
    if not 0<=s<=100 or not 0<=l<=100: raise ValueError("S/L must be 0-100")
    r,g,b=colorsys.hls_to_rgb((h%360)/360,l/100,s/100); return round(r*255),round(g*255),round(b*255)

def hex_to_hsl(value:str): return rgb_to_hsl(*hex_to_rgb(value))
def hsl_to_hex(h,s,l): return rgb_to_hex(*hsl_to_rgb(h,s,l))

def format_rgb(v:str) -> str: r,g,b=hex_to_rgb(v); return f"rgb({r}, {g}, {b})"
def format_hsl(v:str) -> str: h,s,l=hex_to_hsl(v); return f"hsl({h}, {s}%, {l}%)"

def relative_luminance(value:str) -> float:
    def f(c):
        c=c/255; return c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b=hex_to_rgb(value); return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)

def contrast_ratio(a:str,b:str) -> float:
    la,lb=relative_luminance(a),relative_luminance(b); hi,lo=max(la,lb),min(la,lb); return (hi+0.05)/(lo+0.05)

@dataclass(frozen=True)
class ContrastResult:
    ratio: float; aa_normal: bool; aa_large: bool; aaa_normal: bool; aaa_large: bool
    def summary(self) -> str:
        return f"{self.ratio:.2f}:1 — AA normal: {'PASS' if self.aa_normal else 'FAIL'}, AA large: {'PASS' if self.aa_large else 'FAIL'}, AAA normal: {'PASS' if self.aaa_normal else 'FAIL'}, AAA large: {'PASS' if self.aaa_large else 'FAIL'}"

def check_contrast(fg:str,bg:str) -> ContrastResult:
    r=contrast_ratio(fg,bg); return ContrastResult(r, r>=4.5, r>=3.0, r>=7.0, r>=4.5)

def _shift(v:str,deg:float) -> str:
    h,s,l=hex_to_hsl(v); return hsl_to_hex(h+deg,s,l)

def harmonies(value:str) -> dict[str,list[str]]:
    h,s,l=hex_to_hsl(value); base=normalize_hex(value)
    return {
      "Complementary":[base,_shift(base,180)],
      "Analogous":[_shift(base,-30),base,_shift(base,30)],
      "Triadic":[base,_shift(base,120),_shift(base,240)],
      "Split-Complementary":[base,_shift(base,150),_shift(base,210)],
    }

def best_text_on(bg:str) -> str:
    return "#000000" if contrast_ratio("#000000",bg)>=contrast_ratio("#FFFFFF",bg) else "#FFFFFF"

def suggest_name(v:str) -> str:
    h,s,l=hex_to_hsl(v)
    if s<10: return "Charcoal" if l<25 else "Silver" if l<70 else "Snow"
    names=["Red","Orange","Amber","Yellow","Lime","Green","Teal","Cyan","Blue","Violet","Magenta","Rose"]
    return names[int(((h+15)%360)//30)]
