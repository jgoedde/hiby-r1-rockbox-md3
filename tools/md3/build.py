import shutil
from dataclasses import dataclass
from pathlib import Path

from md3.bitmaps import all_bitmaps
from md3.colors import Palette, palette
from md3.paths import ASSETS
from md3.templates import SKIN_FILES, render_skin_file, write_skin_file
from md3.variants import Variant

# 1-bit bitmaps take their colour from the viewport foreground; Rockbox only loads skin images from wps/<name>/.
MONO_WPS_BITMAPS = ["speaker.bmp", "shuffle.bmp", "repeat.bmp", "MD3_32.bmp"]


@dataclass(frozen=True)
class Release:
    """What the skin file headers say about the build."""

    version: str
    date: str


def placeholders(variant: Variant, colors: Palette, release: Release) -> dict[str, str]:
    return colors.placeholders() | {
        "name": variant.name,
        "version": release.version,
        "date": release.date,
        "scheme": variant.mode.lower(),
        "seed": f"#{variant.seed:06X}",
    }


def build(variant: Variant, rockbox: Path, release: Release) -> Palette:
    """Write one variant into `rockbox`, merging with what is already there."""
    colors = palette(variant)
    _write_skin_files(variant, rockbox, placeholders(variant, colors, release))
    _write_bitmaps(rockbox / "wps" / variant.name, colors)
    _copy_shared_assets(rockbox)
    return colors


def _write_skin_files(variant: Variant, rockbox: Path, values: dict[str, str]) -> None:
    for ext in SKIN_FILES:
        directory = rockbox / ("themes" if ext == "cfg" else "wps")
        directory.mkdir(parents=True, exist_ok=True)
        write_skin_file(directory / f"{variant.name}.{ext}", ext, render_skin_file(ext, values))


def _write_bitmaps(skin: Path, colors: Palette) -> None:
    skin.mkdir(parents=True, exist_ok=True)
    for name, img in all_bitmaps(colors).items():
        img.save(skin / name)
    for name in MONO_WPS_BITMAPS:
        shutil.copyfile(ASSETS / "wps" / name, skin / name)


def _copy_shared_assets(rockbox: Path) -> None:
    for sub in ("fonts", "icons"):
        shutil.copytree(ASSETS / sub, rockbox / sub, dirs_exist_ok=True)
