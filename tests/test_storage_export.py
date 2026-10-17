import json
from colorsnap.core.models import Palette, ColorEntry
from colorsnap.services.storage import save_library, load_library
from colorsnap.services.exporters import export_palette
def make(): return Palette(name="Sunset", colors=[ColorEntry("#FF8000","Orange"), ColorEntry("#003366","Deep Blue")], source_image="a.jpg")
def test_library_roundtrip(tmp_path):
    p=tmp_path/"lib.json"; save_library([make()],p); loaded=load_library(p); assert loaded[0].name=="Sunset" and loaded[0].colors[1].hex=="#003366"
def test_missing_library(tmp_path): assert load_library(tmp_path/"nope.json")==[]
def test_exports(tmp_path):
    pal=make()
    for fmt,needle in [("json",'"#FF8000"'),("css","--orange: #FF8000"),("scss","$orange: #FF8000"),("txt","RGB(255, 128, 0)")]:
        out=export_palette(pal,fmt,tmp_path/f"o.{fmt}"); assert needle in out.read_text()


def test_user_data_dir_respects_xdg_data_home(monkeypatch, tmp_path):
    from colorsnap.services.storage import user_data_dir
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg-data"))
    result = user_data_dir("ColorSnapTest")
    assert result == tmp_path / "xdg-data" / "ColorSnapTest"
    assert result.is_dir()
