from colorsnap.core.colors import *
import pytest
def test_hex_roundtrip():
    assert hex_to_rgb("#FF8000")==(255,128,0); assert rgb_to_hex(255,128,0)=="#FF8000"; assert normalize_hex("ff8000")=="#FF8000"; assert normalize_hex("#f80")=="#FF8800"
def test_hsl_roundtrip():
    assert hex_to_hsl("#FF0000")==(0,100,50); assert hsl_to_hex(240,100,50)=="#0000FF"
def test_invalid():
    with pytest.raises(ValueError): normalize_hex("not-a-color")
def test_contrast_black_white():
    assert abs(contrast_ratio("#000000","#FFFFFF")-21.0)<0.01; r=check_contrast("#000000","#FFFFFF"); assert r.aa_normal and r.aaa_normal
def test_harmonies():
    h=harmonies("#FF0000"); assert h["Complementary"][1]=="#00FFFF"; assert len(h["Triadic"])==3
