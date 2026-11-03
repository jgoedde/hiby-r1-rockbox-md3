import math

from PIL import Image, ImageChops, ImageDraw

from md3 import icons
from md3.colors import Palette, mix
from md3.drawing import SUPERSAMPLE, centre, icon, paint, pill, rounded
from md3.paths import ASSETS

WIDTH, HEIGHT = 480, 800
MAGENTA = (255, 0, 255)  # transparent in Rockbox bitmaps
BUTTON_RADIUS = 16  # Play, Resume, "no cover" card

ALBUM_PILL, YEAR_PILL = (36, 441, 321, 482), (339, 441, 441, 482)
ARTIST_PILL, TITLE_PILL = (16, 488, 465, 543), (16, 546, 465, 601)
SHUFFLE_BTN, REWIND_BTN, PLAY_BTN = (10, 700, 70, 760), (90, 700, 170, 760), (185, 700, 295, 760)
FORWARD_BTN, REPEAT_BTN = (310, 700, 390, 760), (410, 700, 470, 760)
NO_COVER = (150, 152, 328, 330)  # 178x178, centred on %Vl(albumart,41,58,396,366)
SBS_BACK, SBS_RESUME = (50, 715, 130, 775), (350, 715, 430, 775)  # = the %V touch areas in MD3.sbs.tpl
SEEK_ICON_SCALE = 29 / 17.5  # fast_rewind/fast_forward 29px wide

# Progress bar: %pb(22,13,436,26,...) inside %V(0,610,...)
PB_X, PB_Y, PB_W, PB_H = 22, 610 + 13, 436, 26
PB_STROKE, PB_AMP, PB_WAVELENGTH, PB_GAP, PB_HANDLE_W = 6, 4, 48, 5, 4


def wps_background(c: Palette) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        d.line([(0, y), (WIDTH - 1, y)], fill=mix(c.surface_container_high, c.surface, y / (HEIGHT - 1)))

    rounded(img, NO_COVER, BUTTON_RADIUS, c.outline_variant)
    icon(img, centre(NO_COVER), 78 / 24, (0, 0, 24, 24), c.outline, icons.music_note)

    pill(img, ALBUM_PILL, c.surface_container_highest)
    pill(img, YEAR_PILL, c.accent)
    pill(img, ARTIST_PILL, c.surface_container_high)
    pill(img, TITLE_PILL, c.primary_container)

    for box in (SHUFFLE_BTN, REWIND_BTN, FORWARD_BTN, REPEAT_BTN):
        pill(img, box, c.surface_container_highest)
    icon(img, centre(REWIND_BTN), SEEK_ICON_SCALE, (2.5, 6, 20, 18), c.on_surface, icons.FAST_REWIND)
    icon(img, centre(FORWARD_BTN), SEEK_ICON_SCALE, (4, 6, 21.5, 18), c.on_surface, icons.FAST_FORWARD)
    rounded(img, PLAY_BTN, BUTTON_RADIUS, c.accent)
    return img


def _bar_background(wps_bg: Image.Image, width: int) -> Image.Image:
    """The background behind the bar, which only varies vertically."""
    return wps_bg.crop((0, PB_Y, 1, PB_Y + PB_H)).resize((width, PB_H))


def _wave_fill(wps_bg: Image.Image, c: Palette) -> Image.Image:
    """Wave over the full width with a round cap on the left; Rockbox crops it at the progress."""
    k = SUPERSAMPLE
    cy, stroke = PB_H * k / 2, PB_STROKE * k
    img = _bar_background(wps_bg, PB_W)
    mask = Image.new("L", (PB_W * k, PB_H * k))
    d = ImageDraw.Draw(mask)
    x = stroke / 2
    while x <= PB_W * k + stroke:
        y = cy + PB_AMP * k * math.sin(2 * math.pi * (x - stroke / 2) / (PB_WAVELENGTH * k))
        d.ellipse((x - stroke / 2, y - stroke / 2, x + stroke / 2, y + stroke / 2), fill=255)
        x += k / 2
    paint(img, (0, 0), mask, c.accent)
    return img


def _track(wps_bg: Image.Image, c: Palette) -> Image.Image:
    """Straight rounded line plus a stop dot at the right end."""
    k = SUPERSAMPLE
    cy, stroke = PB_H * k / 2, PB_STROKE * k
    img = _bar_background(wps_bg, PB_W)
    line, dot = Image.new("L", (PB_W * k, PB_H * k)), Image.new("L", (PB_W * k, PB_H * k))
    ImageDraw.Draw(line).rounded_rectangle((0, cy - stroke / 2, PB_W * k - 1, cy + stroke / 2), stroke / 2, fill=255)
    ImageDraw.Draw(dot).ellipse((PB_W * k - stroke, cy - stroke / 2, PB_W * k - 1, cy + stroke / 2), fill=255)
    paint(img, (0, 0), line, c.secondary_container)
    paint(img, (0, 0), dot, c.accent)
    return img


def _handle(wps_bg: Image.Image, c: Palette) -> Image.Image:
    """Background gap | accent pill | background gap."""
    k = SUPERSAMPLE
    width = PB_HANDLE_W + 2 * PB_GAP
    img = _bar_background(wps_bg, width)
    mask = Image.new("L", (width * k, PB_H * k))
    ImageDraw.Draw(mask).rounded_rectangle(
        (PB_GAP * k, 0, (PB_GAP + PB_HANDLE_W) * k - 1, PB_H * k - 1), PB_HANDLE_W * k / 2, fill=255
    )
    paint(img, (0, 0), mask, c.accent)
    return img


def progress_bitmaps(wps_bg: Image.Image, c: Palette) -> dict[str, Image.Image]:
    """MD3 Expressive static wavy bar for %pb. Opaque, with the WPS background baked in."""
    return {
        "pb_fill.bmp": _wave_fill(wps_bg, c),
        "pb_track.bmp": _track(wps_bg, c),
        "pb_handle.bmp": _handle(wps_bg, c),
    }


def sbs_background(c: Palette) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), c.surface)
    pill(img, SBS_BACK, c.surface_container_highest)
    icon(img, centre(SBS_BACK), 40 / 24, (0, 0, 24, 24), c.on_surface, icons.ARROW_BACK)
    rounded(img, SBS_RESUME, BUTTON_RADIUS, c.accent)
    icon(img, (390, 744.5), 1, (0, 0, 26, 29), c.on_accent, icons.rounded_play)
    return img


def play_strip(c: Palette) -> Image.Image:
    """assets/wps/play.bmp (stop/play/pause frames) with every non-transparent pixel set to onAccent."""
    img = Image.open(ASSETS / "wps" / "play.bmp").convert("RGB")
    transparent = Image.new("RGB", img.size, MAGENTA)
    opaque = ImageChops.difference(img, transparent).convert("L").point(lambda v: 255 if v else 0)
    return Image.composite(Image.new("RGB", img.size, c.on_accent), transparent, opaque)


def all_bitmaps(c: Palette) -> dict[str, Image.Image]:
    """Every colour bitmap of a skin directory, by file name."""
    wps_bg = wps_background(c)
    return {
        "wps_bg.bmp": wps_bg,
        **progress_bitmaps(wps_bg, c),
        "sbs_bg.bmp": sbs_background(c),
        "play.bmp": play_strip(c),
    }
