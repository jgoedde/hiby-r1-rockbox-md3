"""Anti-aliased drawing primitives: shapes are drawn into a supersampled mask, then composited."""

import math
from collections.abc import Callable

from PIL import Image, ImageDraw

from md3.colors import RGB

SUPERSAMPLE = 8

Box = tuple[int, int, int, int]  # x0, y0, x1, y1 (exclusive)
Point = Callable[[float, float], tuple[float, float]]  # viewbox units -> supersampled mask pixels
IconShape = Callable[[ImageDraw.ImageDraw, Point], None]


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
    """Fully rounded rectangle (radius = half the height)."""
    rounded(img, box, (box[3] - box[1]) / 2, color)


def centre(box: Box) -> tuple[float, float]:
    return (box[0] + box[2]) / 2, (box[1] + box[3]) / 2


def icon(
    img: Image.Image,
    center: tuple[float, float],
    scale: float,
    viewbox: tuple[float, float, float, float],
    color: RGB,
    shape: IconShape,
) -> None:
    """Draw a vector icon given in viewbox units, scaled by `scale`, with the viewbox centred on `center`."""
    vx0, vy0, vx1, vy1 = viewbox
    w, h = (vx1 - vx0) * scale, (vy1 - vy0) * scale
    left, top = math.floor(center[0] - w / 2) - 1, math.floor(center[1] - h / 2) - 1
    dx, dy = center[0] - w / 2 - left, center[1] - h / 2 - top
    k = SUPERSAMPLE
    mask = Image.new("L", ((math.ceil(w) + 3) * k, (math.ceil(h) + 3) * k))

    def point(x: float, y: float) -> tuple[float, float]:
        return (dx + (x - vx0) * scale) * k, (dy + (y - vy0) * scale) * k

    shape(ImageDraw.Draw(mask), point)
    paint(img, (left, top), mask, color)
