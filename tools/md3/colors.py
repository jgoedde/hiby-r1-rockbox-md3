import re
from dataclasses import dataclass, fields

from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot

from md3.variants import Variant

RGB = tuple[int, int, int]

SPEC_VERSION = "2025"
# WCAG contrast the accent needs against surface and surfaceContainerHighest (non-text UI elements).
MIN_ACCENT_CONTRAST = 3.0


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
    """WCAG 2 contrast ratio, 1 to 21."""
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a: RGB, b: RGB, t: float) -> RGB:
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b, strict=True))


def hct_of(rgb: int) -> Hct:
    return Hct.from_int(0xFF000000 | rgb)


def accent_for(seed: int, backgrounds: list[RGB], dark: bool) -> RGB:
    """The seed itself, moved in HCT tone (lighter on dark, darker on light) until it reaches
    MIN_ACCENT_CONTRAST against every background. Hue and chroma are kept."""
    hct = hct_of(seed)
    tone, color = hct.tone, argb_to_rgb(seed)
    while min(contrast(color, bg) for bg in backgrounds) < MIN_ACCENT_CONTRAST and 0 < tone < 100:
        tone = min(100.0, tone + 1) if dark else max(0.0, tone - 1)
        color = argb_to_rgb(Hct.from_hct(hct.hue, hct.chroma, tone).to_int())
    return color


def camel(name: str) -> str:
    """surface_container_high -> surfaceContainerHigh (MD3 token / template placeholder name)."""
    return re.sub(r"_(\w)", lambda m: m.group(1).upper(), name)


@dataclass(frozen=True)
class Palette:
    # MD3 TonalSpot tokens
    surface: RGB
    surface_container_high: RGB
    surface_container_highest: RGB
    on_surface: RGB
    on_surface_variant: RGB
    primary_container: RGB
    on_primary_container: RGB
    secondary_container: RGB
    outline: RGB
    outline_variant: RGB
    error: RGB
    # seed-derived
    accent: RGB
    on_accent: RGB

    def placeholders(self) -> dict[str, str]:
        """Template values: `{{surfaceContainerHigh}}` -> `281e16`."""
        return {camel(f.name): hex_of(getattr(self, f.name)) for f in fields(self)}


SEED_FIELDS = {"accent", "on_accent"}
TOKEN_FIELDS = [f.name for f in fields(Palette) if f.name not in SEED_FIELDS]


def palette(variant: Variant) -> Palette:
    """MD3 tokens, `accent` (seed, contrast-adjusted) and `onAccent` (dark or white, whichever contrasts more)."""
    scheme = SchemeTonalSpot(hct_of(variant.seed), variant.dark, 0.0, spec_version=SPEC_VERSION)
    tokens = {name: argb_to_rgb(getattr(MaterialDynamicColors, camel(name)).get_argb(scheme)) for name in TOKEN_FIELDS}
    accent = accent_for(variant.seed, [tokens["surface"], tokens["surface_container_highest"]], variant.dark)
    on_candidates = [argb_to_rgb(scheme.neutral_palette.tone(10)), (255, 255, 255)]
    on_accent = max(on_candidates, key=lambda c: contrast(c, accent))
    return Palette(**tokens, accent=accent, on_accent=on_accent)
