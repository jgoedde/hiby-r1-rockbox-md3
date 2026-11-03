"""Generate the MD3 Rockbox theme colour variants.

Every variant is a Material Design 3 TonalSpot scheme (materialyoucolor, spec 2025) computed from a seed
colour. The skin files are filled in from templates/, and all colour bitmaps are drawn from geometry here.

    python tools/generate.py                          # all variants into dist/
    python tools/generate.py --only Light-Blue        # one variant into dist/
    python tools/generate.py --only Dark-Pink --install /path/to/simdisk/.rockbox
"""

from __future__ import annotations

import argparse
import datetime
import math
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TEMPLATES = ROOT / "templates"

SEEDS = {"Orange": 0xFF9130, "Blue": 0x3D7BFF, "Green": 0x3FA35B, "Pink": 0xE0457B}
MODES = {"Dark": True, "Light": False}
SPEC_VERSION = "2025"
TOKENS = [
    "surface",
    "surfaceContainerHigh",
    "surfaceContainerHighest",
    "onSurface",
    "onSurfaceVariant",
    "primaryContainer",
    "onPrimaryContainer",
    "secondaryContainer",
    "outline",
    "outlineVariant",
    "error",
]
# WCAG contrast the accent needs against surface and surfaceContainerHighest (non-text UI elements).
MIN_ACCENT_CONTRAST = 3.0
# 1-bit bitmaps take their colour from the viewport foreground and are copied unchanged.
MONO_WPS_BITMAPS = ["speaker.bmp", "shuffle.bmp", "repeat.bmp", "MD3_32.bmp"]

WIDTH, HEIGHT = 480, 800
SUPERSAMPLE = 8
MAGENTA = (255, 0, 255)  # transparent in Rockbox bitmaps

RGB = tuple[int, int, int]


# --- colours -------------------------------------------------------------------------------------------------


def argb_to_rgb(argb: int) -> RGB:
    return (argb >> 16) & 0xFF, (argb >> 8) & 0xFF, argb & 0xFF


def hex_of(color: RGB) -> str:
    return "".join(f"{c:02x}" for c in color)


def luminance(color: RGB) -> float:
    def channel(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = map(channel, color)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: RGB, b: RGB) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b, strict=True))


def accent_for(seed: int, backgrounds: list[RGB], dark: bool) -> RGB:
    """The seed itself, moved in HCT tone (lighter on dark, darker on light) until it reaches
    MIN_ACCENT_CONTRAST against every background. Hue and chroma are kept."""
    hct = Hct.from_int(0xFF000000 | seed)
    tone, color = hct.tone, argb_to_rgb(seed)
    while min(contrast(color, bg) for bg in backgrounds) < MIN_ACCENT_CONTRAST and 0 < tone < 100:
        tone = min(100.0, tone + 1) if dark else max(0.0, tone - 1)
        color = argb_to_rgb(Hct.from_hct(hct.hue, hct.chroma, tone).to_int())
    return color


@dataclass(frozen=True)
class Variant:
    mode: str
    colour: str

    @property
    def name(self) -> str:
        return f"MD3-{self.mode}-{self.colour}"

    @property
    def seed(self) -> int:
        return SEEDS[self.colour]

    @property
    def dark(self) -> bool:
        return MODES[self.mode]


VARIANTS = [Variant(mode, colour) for mode in MODES for colour in SEEDS]


def palette(variant: Variant) -> dict[str, RGB]:
    """MD3 tokens plus `accent` (seed, contrast-adjusted) and `onAccent` (dark or light, whichever contrasts more)."""
    scheme = SchemeTonalSpot(Hct.from_int(0xFF000000 | variant.seed), variant.dark, 0.0, spec_version=SPEC_VERSION)
    colors = {token: argb_to_rgb(getattr(MaterialDynamicColors, token).get_argb(scheme)) for token in TOKENS}
    accent = accent_for(variant.seed, [colors["surface"], colors["surfaceContainerHighest"]], variant.dark)
    on_candidates = [argb_to_rgb(scheme.neutral_palette.tone(10)), (255, 255, 255)]
    colors["accent"] = accent
    colors["onAccent"] = max(on_candidates, key=lambda c: contrast(c, accent))
    return colors


# --- drawing -------------------------------------------------------------------------------------------------

Box = tuple[int, int, int, int]  # x0, y0, x1, y1 (exclusive)
Point = Callable[[float, float], tuple[float, float]]


def paint(img: Image.Image, origin: tuple[int, int], mask: Image.Image, color: RGB) -> None:
    """Composite `color` through a supersampled coverage mask."""
    size = (mask.width // SUPERSAMPLE, mask.height // SUPERSAMPLE)
    img.paste(Image.new("RGB", size, color), origin, mask.resize(size, Image.LANCZOS))


def rounded(img: Image.Image, box: Box, radius: float, color: RGB) -> None:
    x0, y0, x1, y1 = box
    k = SUPERSAMPLE
    mask = Image.new("L", ((x1 - x0) * k, (y1 - y0) * k))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, mask.width - 1, mask.height - 1), radius * k, fill=255)
    paint(img, (x0, y0), mask, color)


def pill(img: Image.Image, box: Box, color: RGB) -> None:
    rounded(img, box, (box[3] - box[1]) / 2, color)


def centre(box: Box) -> tuple[float, float]:
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def icon(
    img: Image.Image,
    center: tuple[float, float],
    scale: float,
    viewbox: tuple[float, float, float, float],
    color: RGB,
    draw: Callable[[ImageDraw.ImageDraw, Point], None],
) -> None:
    """Draw a vector icon given in viewbox units, with the viewbox centred on `center`."""
    vx0, vy0, vx1, vy1 = viewbox
    w, h = (vx1 - vx0) * scale, (vy1 - vy0) * scale
    left, top = math.floor(center[0] - w / 2) - 1, math.floor(center[1] - h / 2) - 1
    dx, dy = center[0] - w / 2 - left, center[1] - h / 2 - top
    k = SUPERSAMPLE
    mask = Image.new("L", ((math.ceil(w) + 3) * k, (math.ceil(h) + 3) * k))

    def point(x: float, y: float) -> tuple[float, float]:
        return (dx + (x - vx0) * scale) * k, (dy + (y - vy0) * scale) * k

    draw(ImageDraw.Draw(mask), point)
    paint(img, (left, top), mask, color)


def polygons(*shapes: list[tuple[float, float]]) -> Callable[[ImageDraw.ImageDraw, Point], None]:
    def draw(d: ImageDraw.ImageDraw, p: Point) -> None:
        for shape in shapes:
            d.polygon([p(x, y) for x, y in shape], fill=255)

    return draw


def music_note(d: ImageDraw.ImageDraw, p: Point) -> None:
    d.ellipse((*p(6, 13), *p(14, 21)), fill=255)
    d.rectangle((*p(12, 3), *p(14, 17)), fill=255)
    d.rectangle((*p(12, 3), *p(18, 7)), fill=255)


# Material icon paths (24-unit viewbox), as polygons
FAST_REWIND = polygons([(11, 18), (11, 6), (2.5, 12)], [(20, 18), (20, 6), (11.5, 12)])
FAST_FORWARD = polygons([(4, 18), (12.5, 12), (4, 6)], [(13, 6), (13, 18), (21.5, 12)])
ARROW_BACK = polygons(
    [(20, 11), (7.83, 11), (13.42, 5.41), (12, 4), (4, 12), (12, 20), (13.41, 18.59), (7.83, 13), (20, 13)]
)


def rounded_play(d: ImageDraw.ImageDraw, p: Point) -> None:
    """Play triangle with 3px round corners in a 26x29 px viewbox (size of the v2.2 Resume glyph):
    inner triangle grown by the corner radius (polygon + edge strokes + vertex discs)."""
    r = 3
    inner = [p(r, r + 0.5), p(r, 29 - r - 0.5), p(26 - r, 14.5)]
    width = round(abs(p(2 * r, 0)[0] - p(0, 0)[0]))
    d.polygon(inner, fill=255)
    d.line([*inner, inner[0]], fill=255, width=width)
    for x, y in inner:
        d.ellipse((x - width / 2, y - width / 2, x + width / 2, y + width / 2), fill=255)


# Geometry, measured from the original Ulmiz bitmap
ALBUM_PILL, YEAR_PILL = (36, 441, 321, 482), (339, 441, 441, 482)
ARTIST_PILL, TITLE_PILL = (16, 488, 465, 543), (16, 546, 465, 601)
SHUFFLE_BTN, REWIND_BTN, PLAY_BTN = (10, 700, 70, 760), (90, 700, 170, 760), (185, 700, 295, 760)
FORWARD_BTN, REPEAT_BTN = (310, 700, 390, 760), (410, 700, 470, 760)
NO_COVER = (150, 152, 328, 330)  # 178x178, centred on %Vl(albumart,41,58,396,366)
SBS_BACK, SBS_RESUME = (50, 715, 130, 775), (350, 715, 430, 775)  # = the %V touch areas in MD3.sbs.tpl
SEEK_ICON_SCALE = 29 / 17.5  # fast_rewind/fast_forward 29px wide
# Progress bar: %pb(22,13,436,26,...) inside %V(0,610,...)
PB_Y, PB_W, PB_H = 610 + 13, 436, 26
PB_STROKE, PB_AMP, PB_WAVELENGTH, PB_GAP, PB_HANDLE_W = 6, 4, 48, 5, 4


def wps_background(c: dict[str, RGB]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    d = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        d.line([(0, y), (WIDTH - 1, y)], fill=mix(c["surfaceContainerHigh"], c["surface"], y / (HEIGHT - 1)))

    rounded(img, NO_COVER, 16, c["outlineVariant"])
    icon(img, centre(NO_COVER), 78 / 24, (0, 0, 24, 24), c["outline"], music_note)

    pill(img, ALBUM_PILL, c["surfaceContainerHighest"])
    pill(img, YEAR_PILL, c["accent"])
    pill(img, ARTIST_PILL, c["surfaceContainerHigh"])
    pill(img, TITLE_PILL, c["primaryContainer"])

    for box in (SHUFFLE_BTN, REWIND_BTN, FORWARD_BTN, REPEAT_BTN):
        pill(img, box, c["surfaceContainerHighest"])
    icon(img, centre(REWIND_BTN), SEEK_ICON_SCALE, (2.5, 6, 20, 18), c["onSurface"], FAST_REWIND)
    icon(img, centre(FORWARD_BTN), SEEK_ICON_SCALE, (4, 6, 21.5, 18), c["onSurface"], FAST_FORWARD)
    rounded(img, PLAY_BTN, 16, c["accent"])
    return img


def progress_bitmaps(background: Image.Image, c: dict[str, RGB]) -> dict[str, Image.Image]:
    """MD3 Expressive static wavy bar. Opaque, with the (vertical-only) background baked in."""
    k = SUPERSAMPLE
    cy, stroke = PB_H * k / 2, PB_STROKE * k

    def base(width: int) -> Image.Image:
        return background.crop((0, PB_Y, 1, PB_Y + PB_H)).resize((width, PB_H))

    # fill: wave over the full width, round cap on the left
    fill = base(PB_W)
    mask = Image.new("L", (PB_W * k, PB_H * k))
    d = ImageDraw.Draw(mask)
    x = stroke / 2
    while x <= PB_W * k + stroke:
        y = cy + PB_AMP * k * math.sin(2 * math.pi * (x - stroke / 2) / (PB_WAVELENGTH * k))
        d.ellipse((x - stroke / 2, y - stroke / 2, x + stroke / 2, y + stroke / 2), fill=255)
        x += k / 2
    paint(fill, (0, 0), mask, c["accent"])

    # track (backdrop): straight rounded line plus stop dot at the right end
    track = base(PB_W)
    line, dot = Image.new("L", mask.size), Image.new("L", mask.size)
    ImageDraw.Draw(line).rounded_rectangle((0, cy - stroke / 2, PB_W * k - 1, cy + stroke / 2), stroke / 2, fill=255)
    ImageDraw.Draw(dot).ellipse((PB_W * k - stroke, cy - stroke / 2, PB_W * k - 1, cy + stroke / 2), fill=255)
    paint(track, (0, 0), line, c["secondaryContainer"])
    paint(track, (0, 0), dot, c["accent"])

    # handle (slider): background gap | accent pill | background gap
    handle_w = PB_HANDLE_W + 2 * PB_GAP
    handle = base(handle_w)
    mask = Image.new("L", (handle_w * k, PB_H * k))
    ImageDraw.Draw(mask).rounded_rectangle(
        (PB_GAP * k, 0, (PB_GAP + PB_HANDLE_W) * k - 1, PB_H * k - 1), PB_HANDLE_W * k / 2, fill=255
    )
    paint(handle, (0, 0), mask, c["accent"])
    return {"pb_fill.bmp": fill, "pb_track.bmp": track, "pb_handle.bmp": handle}


def sbs_background(c: dict[str, RGB]) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), c["surface"])
    pill(img, SBS_BACK, c["surfaceContainerHighest"])
    icon(img, centre(SBS_BACK), 40 / 24, (0, 0, 24, 24), c["onSurface"], ARROW_BACK)
    rounded(img, SBS_RESUME, 16, c["accent"])
    icon(img, (390, 744.5), 1, (0, 0, 26, 29), c["onAccent"], rounded_play)
    return img


def play_strip(c: dict[str, RGB]) -> Image.Image:
    """assets/wps/play.bmp (stop/play/pause frames) with every non-transparent pixel set to onAccent."""
    img = Image.open(ASSETS / "wps" / "play.bmp").convert("RGB")
    transparent = Image.new("RGB", img.size, MAGENTA)
    opaque = ImageChops.difference(img, transparent).convert("L").point(lambda v: 255 if v else 0)
    return Image.composite(Image.new("RGB", img.size, c["onAccent"]), transparent, opaque)


# --- output --------------------------------------------------------------------------------------------------


def render(template: str, values: dict[str, str]) -> str:
    def substitute(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"unknown placeholder {{{{{key}}}}}")
        return values[key]

    return re.sub(r"\{\{(\w+)\}\}", substitute, template)


def write_text(path: Path, text: str, crlf: bool) -> None:
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\r\n" if crlf else "\n")


def build(variant: Variant, rockbox: Path, version: str, date: str) -> dict[str, RGB]:
    """Write one variant into a `.rockbox` directory, merging with what is already there."""
    colors = palette(variant)
    values = {key: hex_of(color) for key, color in colors.items()}
    values |= {
        "name": variant.name,
        "version": version,
        "date": date,
        "scheme": variant.mode.lower(),
        "seed": f"#{variant.seed:06X}",
    }
    skin = rockbox / "wps" / variant.name
    for directory in (rockbox / "themes", skin, rockbox / "fonts", rockbox / "icons"):
        directory.mkdir(parents=True, exist_ok=True)

    for ext, target, crlf in (
        ("wps", rockbox / "wps", True),
        ("sbs", rockbox / "wps", True),
        ("cfg", rockbox / "themes", False),
    ):
        text = render((TEMPLATES / f"MD3.{ext}.tpl").read_text(encoding="utf-8"), values)
        write_text(target / f"{variant.name}.{ext}", text, crlf)

    background = wps_background(colors)
    background.save(skin / "wps_bg.bmp")
    for name, img in progress_bitmaps(background, colors).items():
        img.save(skin / name)
    sbs_background(colors).save(skin / "sbs_bg.bmp")
    play_strip(colors).save(skin / "play.bmp")
    for name in MONO_WPS_BITMAPS:
        shutil.copyfile(ASSETS / "wps" / name, skin / name)
    for sub in ("fonts", "icons"):
        for f in (ASSETS / sub).iterdir():
            shutil.copyfile(f, rockbox / sub / f.name)
    return colors


def git(*args: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return None
    return (out.returncode == 0 and out.stdout.strip()) or None


def detect_version() -> str:
    """Tag name in CI (GitHub Actions tag build), `git describe` locally. Leading `v` is dropped."""
    if os.environ.get("GITHUB_REF_TYPE") == "tag":
        tag = os.environ["GITHUB_REF_NAME"]
    else:
        tag = git("describe", "--tags", "--always", "--dirty") or "dev"
    return tag.removeprefix("v")


def select(only: list[str] | None) -> list[Variant]:
    if not only:
        return VARIANTS
    by_name = {v.name.lower(): v for v in VARIANTS}
    selected = []
    for name in only:
        key = name.lower() if name.lower().startswith("md3-") else f"md3-{name.lower()}"
        if key not in by_name:
            sys.exit(f"unknown variant {name!r}; choose from: {', '.join(v.name for v in VARIANTS)}")
        selected.append(by_name[key])
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", metavar="VARIANT", help="e.g. Light-Blue (repeatable; default: all)")
    parser.add_argument("--install", type=Path, metavar="PATH/.rockbox", help="merge into this .rockbox directory")
    parser.add_argument("--out", type=Path, default=ROOT / "dist", help="output directory (default: dist/)")
    parser.add_argument("--version", help="version for the file headers (default: from git)")
    args = parser.parse_args()

    variants = select(args.only)
    version = args.version or detect_version()
    date = git("log", "-1", "--format=%cs") or datetime.date.today().isoformat()

    # dist/MD3-all/.rockbox: every variant merged, only when all of them are built
    everything = None if args.install or args.only else args.out / "MD3-all" / ".rockbox"
    if args.install and (args.install.name != ".rockbox" or not args.install.is_dir()):
        sys.exit(f"--install needs an existing .rockbox directory, got {args.install}")
    if args.install and len(variants) != 1:
        sys.exit("--install merges one variant: pass exactly one --only")
    if everything:
        shutil.rmtree(everything.parent, ignore_errors=True)

    for variant in variants:
        rockbox = args.install or args.out / variant.name / ".rockbox"
        if not args.install:
            shutil.rmtree(rockbox.parent, ignore_errors=True)
        colors = build(variant, rockbox, version, date)
        if everything:
            shutil.copytree(rockbox, everything, dirs_exist_ok=True)
        seed = argb_to_rgb(variant.seed)
        note = "" if colors["accent"] == seed else f" (seed {hex_of(seed)} adjusted for contrast)"
        print(f"{variant.name} {version}: accent {hex_of(colors['accent'])}{note} -> {rockbox}")


if __name__ == "__main__":
    main()
