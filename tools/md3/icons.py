"""Icon shapes for `drawing.icon`. Material icons use their 24-unit viewbox."""

from PIL import ImageDraw

from md3.drawing import IconShape, Point


def polygons(*shapes: list[tuple[float, float]]) -> IconShape:
    def draw(d: ImageDraw.ImageDraw, p: Point) -> None:
        for shape in shapes:
            d.polygon([p(x, y) for x, y in shape], fill=255)

    return draw


FAST_REWIND = polygons([(11, 18), (11, 6), (2.5, 12)], [(20, 18), (20, 6), (11.5, 12)])
FAST_FORWARD = polygons([(4, 18), (12.5, 12), (4, 6)], [(13, 6), (13, 18), (21.5, 12)])
ARROW_BACK = polygons(
    [(20, 11), (7.83, 11), (13.42, 5.41), (12, 4), (4, 12), (12, 20), (13.41, 18.59), (7.83, 13), (20, 13)]
)


def music_note(d: ImageDraw.ImageDraw, p: Point) -> None:
    d.ellipse((*p(6, 13), *p(14, 21)), fill=255)
    d.rectangle((*p(12, 3), *p(14, 17)), fill=255)
    d.rectangle((*p(12, 3), *p(18, 7)), fill=255)


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
