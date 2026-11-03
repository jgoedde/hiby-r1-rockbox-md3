"""Generate the MD3 Rockbox theme colour variants.

Every variant is a Material Design 3 TonalSpot scheme (materialyoucolor, spec 2025) computed from a seed
colour. The skin files are filled in from templates/, and all colour bitmaps are drawn from geometry.

    python tools/generate.py                          # all variants into dist/
    python tools/generate.py --only Light-Blue        # one variant into dist/
    python tools/generate.py --only Dark-Pink --install /path/to/simdisk/.rockbox
"""

import argparse
import shutil
import sys
from pathlib import Path

from md3.build import Release, build
from md3.colors import argb_to_rgb, hex_of
from md3.gitinfo import commit_date, detect_version
from md3.paths import ROOT
from md3.variants import select


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", action="append", metavar="VARIANT", help="e.g. Light-Blue (repeatable; default: all)")
    parser.add_argument("--install", type=Path, metavar="PATH/.rockbox", help="merge one variant into this directory")
    parser.add_argument("--out", type=Path, default=ROOT / "dist", help="output directory (default: dist/)")
    parser.add_argument("--version", help="version for the file headers (default: from git)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        variants = select(args.only)
    except ValueError as e:
        sys.exit(str(e))
    if args.install and (args.install.name != ".rockbox" or not args.install.is_dir()):
        sys.exit(f"--install needs an existing .rockbox directory, got {args.install}")
    if args.install and len(variants) != 1:
        sys.exit("--install merges one variant: pass exactly one --only")
    release = Release(args.version or detect_version(), commit_date())

    # dist/MD3-all/.rockbox: every variant merged, only when all of them are built
    merged = None if args.install or args.only else args.out / "MD3-all" / ".rockbox"
    if merged:
        shutil.rmtree(merged.parent, ignore_errors=True)

    for variant in variants:
        rockbox = args.install or args.out / variant.name / ".rockbox"
        if not args.install:
            shutil.rmtree(rockbox.parent, ignore_errors=True)
        colors = build(variant, rockbox, release)
        if merged:
            shutil.copytree(rockbox, merged, dirs_exist_ok=True)
        seed = argb_to_rgb(variant.seed)
        note = "" if colors.accent == seed else f" (seed {hex_of(seed)} adjusted for contrast)"
        print(f"{variant.name} {release.version}: accent {hex_of(colors.accent)}{note} -> {rockbox}")


if __name__ == "__main__":
    main()
