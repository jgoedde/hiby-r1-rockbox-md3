"""The skin files and the bitmaps drawn for them must agree."""

import re

import pytest
from md3.bitmaps import MAGENTA, PB_H, PB_X, PB_Y, all_bitmaps
from md3.build import Release, placeholders
from md3.colors import hex_of, palette
from md3.templates import render_skin_file
from md3.variants import VARIANTS

VIEWPORT = re.compile(r"%V\((\d+),(\d+),(\d+),(\d+),([^)]*)\).*%Vb\(([0-9a-f]{6})\)")


@pytest.fixture(scope="module", params=VARIANTS, ids=lambda v: v.name)
def skin(request):
    variant = request.param
    colors = palette(variant)
    wps = render_skin_file("wps", placeholders(variant, colors, Release("1.0", "2026-01-01")))
    return wps, colors, all_bitmaps(colors)


def text_viewports(wps: str) -> list[tuple[int, int, int, int, str]]:
    """(x, y, w, h, %Vb) of every viewport that draws text with an explicit background colour."""
    found = []
    for line in wps.splitlines():
        if m := VIEWPORT.search(line):
            x, y, w, h, font, bg = m.groups()
            if font.strip() != "-":
                found.append((int(x), int(y), int(w), int(h), bg))
    return found


def test_wps_has_the_pill_viewports(skin):
    wps, _, _ = skin
    assert len(text_viewports(wps)) == 4  # album, year, artist, title


def test_text_viewport_background_matches_the_pill_underneath(skin):
    # font anti-aliasing blends against %Vb, so it must be the colour drawn under the text
    wps, _, bitmaps = skin
    for x, y, w, h, bg in text_viewports(wps):
        assert hex_of(bitmaps["wps_bg.bmp"].getpixel((x + w // 2, y + h // 2))) == bg, (x, y)


def test_bitmap_sizes(skin):
    _, _, bitmaps = skin
    sizes = {name: img.size for name, img in bitmaps.items()}
    assert sizes == {
        "wps_bg.bmp": (480, 800),
        "sbs_bg.bmp": (480, 800),
        "pb_fill.bmp": (436, 26),
        "pb_track.bmp": (436, 26),
        "pb_handle.bmp": (14, 26),
        "play.bmp": (28, 84),
    }


def test_background_behind_progress_bar_is_horizontally_uniform(skin):
    # the handle bitmap is drawn at any x, with the background baked in
    _, _, bitmaps = skin
    bg = bitmaps["wps_bg.bmp"]
    for y in range(PB_Y, PB_Y + PB_H):
        assert len({bg.getpixel((x, y)) for x in range(PB_X, PB_X + 436)}) == 1, y


def test_progress_bitmaps_bake_in_the_background(skin):
    # top and bottom rows are outside the wave, track and handle
    _, _, bitmaps = skin
    bg = bitmaps["wps_bg.bmp"]
    for name in ("pb_fill.bmp", "pb_track.bmp"):
        img = bitmaps[name]
        for y in (0, PB_H - 1):
            assert img.getpixel((10, y)) == bg.getpixel((PB_X + 10, PB_Y + y)), (name, y)
    assert bitmaps["pb_handle.bmp"].getpixel((0, 0)) == bg.getpixel((PB_X, PB_Y))


def test_play_strip_is_on_accent_on_transparent(skin):
    _, colors, bitmaps = skin
    assert {c for _, c in bitmaps["play.bmp"].getcolors()} == {MAGENTA, colors.on_accent}


def test_accent_buttons_use_the_accent(skin):
    _, colors, bitmaps = skin
    assert bitmaps["wps_bg.bmp"].getpixel((200, 710)) == colors.accent  # Play, clear of the icon
    assert bitmaps["sbs_bg.bmp"].getpixel((360, 725)) == colors.accent  # Resume
