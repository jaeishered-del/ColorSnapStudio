from PIL import Image
from colorsnap.core.extraction import extract_dominant_colors, load_image
def test_extract_solid(tmp_path):
    p=tmp_path/"red.png"; Image.new("RGB",(40,40),(255,0,0)).save(p)
    cols=extract_dominant_colors(p,3); assert cols and cols[0].hex=="#FF0000"
def test_extract_two_colors(tmp_path):
    p=tmp_path/"two.png"; im=Image.new("RGB",(40,40),(0,0,255)); 
    for x in range(20):
        for y in range(40): im.putpixel((x,y),(255,0,0))
    im.save(p); hexes={c.hex for c in extract_dominant_colors(p,4)}; assert "#FF0000" in hexes and "#0000FF" in hexes
def test_count_validation(tmp_path):
    p=tmp_path/"x.png"; Image.new("RGB",(10,10)).save(p)
    import pytest
    with pytest.raises(ValueError): extract_dominant_colors(p,2)


def test_extract_gradient_returns_multiple_colors(tmp_path):
    p = tmp_path / "gradient.png"
    im = Image.new("RGB", (120, 20))
    for x in range(120):
        color = (round(x * 255 / 119), 0, round((119 - x) * 255 / 119))
        for y in range(20):
            im.putpixel((x, y), color)
    im.save(p)
    colors = extract_dominant_colors(p, 6)
    assert 3 <= len(colors) <= 6
    assert len({c.hex for c in colors}) == len(colors)
