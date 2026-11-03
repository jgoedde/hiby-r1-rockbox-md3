import pytest
from md3.colors import Palette, contrast, palette
from md3.variants import VARIANTS, Variant

DARK_ORANGE = Variant(dark=True, seed_name="Orange")


def test_contrast_matches_wcag_extremes():
    assert contrast((0, 0, 0), (255, 255, 255)) == pytest.approx(21)
    assert contrast((18, 52, 86), (18, 52, 86)) == pytest.approx(1)


def test_dark_orange_reproduces_shipped_v2_2_colours():
    # literal values from the hand-made v2.2 theme files
    expected = {
        "surface": "130d09",
        "surfaceContainerHigh": "281e16",
        "surfaceContainerHighest": "2f231b",
        "onSurface": "f7e1d4",
        "onSurfaceVariant": "bba79b",
        "primaryContainer": "724929",
        "onPrimaryContainer": "ffddc6",
        "secondaryContainer": "4e3624",
        "outline": "837267",
        "accent": "ff9130",
    }
    assert palette(DARK_ORANGE).placeholders().items() >= expected.items()


def test_accent_is_the_seed_when_it_already_contrasts():
    assert palette(DARK_ORANGE).accent == (0xFF, 0x91, 0x30)


def test_light_orange_accent_is_darkened_to_reach_contrast():
    # #FF9130 is about 2:1 on a light surface
    accent = palette(Variant(dark=False, seed_name="Orange")).accent
    assert accent != (0xFF, 0x91, 0x30)
    assert accent[0] > accent[1] > accent[2]  # still orange


@pytest.mark.parametrize("variant", VARIANTS, ids=lambda v: v.name)
def test_accent_contrasts_with_backgrounds(variant):
    c = palette(variant)
    assert contrast(c.accent, c.surface) >= 3
    assert contrast(c.accent, c.surface_container_highest) >= 3


@pytest.mark.parametrize("variant", VARIANTS, ids=lambda v: v.name)
def test_text_on_accent_is_readable(variant):
    c = palette(variant)
    assert contrast(c.on_accent, c.accent) >= 3


def test_placeholders_use_md3_token_names():
    names = set(palette(DARK_ORANGE).placeholders())
    assert {"surfaceContainerHighest", "onPrimaryContainer", "outlineVariant", "onAccent"} <= names
    assert len(names) == len(Palette.__dataclass_fields__)
