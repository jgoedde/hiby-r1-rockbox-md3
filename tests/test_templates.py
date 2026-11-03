import pytest
from md3.build import Release, placeholders
from md3.colors import palette
from md3.templates import SKIN_FILES, render, render_skin_file
from md3.variants import VARIANTS


def test_render_fills_placeholders():
    assert render("%Vf({{onSurface}}) # {{name}}", {"onSurface": "f7e1d4", "name": "MD3-X"}) == "%Vf(f7e1d4) # MD3-X"


def test_render_rejects_unknown_placeholder():
    with pytest.raises(KeyError, match="onSurfase"):
        render("%Vf({{onSurfase}})", {"onSurface": "f7e1d4"})


def test_render_leaves_rockbox_syntax_alone():
    text = "%?mp<%xd(play,1)|%xd(play,3)>\n%V(0,0,-,-,-)"
    assert render(text, {}) == text


@pytest.mark.parametrize("ext", SKIN_FILES)
@pytest.mark.parametrize("variant", VARIANTS, ids=lambda v: v.name)
def test_every_skin_file_renders_for_every_variant(variant, ext):
    values = placeholders(variant, palette(variant), Release("3.0", "2026-11-03"))
    text = render_skin_file(ext, values)
    assert "{{" not in text
    assert f"# Rockbox Theme Name: {variant.name}\n" in text
    assert "# Version: 3.0\n" in text


def test_cfg_points_at_the_variant_skins():
    variant = VARIANTS[0]
    text = render_skin_file("cfg", placeholders(variant, palette(variant), Release("3.0", "2026-11-03")))
    assert f"wps: /.rockbox/wps/{variant.name}.wps\n" in text
    assert f"sbs: /.rockbox/wps/{variant.name}.sbs\n" in text
