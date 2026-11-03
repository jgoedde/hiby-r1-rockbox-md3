<h1>hiby-r1-rockbox-md3</h1>

A Material Design 3 Port of Simon Rothens "Ulmiz" Theme for the HiBy R1 Rockbox

<img width="388" height="512" alt="image" src="https://github.com/user-attachments/assets/4c3aab56-d466-48ad-9aac-e892e87567cf" />

<h2>Contents</h2>

<!-- TOC -->

* [Installation](#installation)
* [Variants](#variants)
* [Development](#development)
* [Fonts](#fonts)
* [Credits](#credits)

<!-- TOC -->

## Installation

1. Download a ZIP from the [latest release](../../releases/latest): one variant (e.g. `MD3-Dark-Orange-v3.0.zip`)
   or `MD3-all-v3.0.zip` with every variant. Unzip it.
2. Connect the HiBy R1 to your computer over USB.
3. Copy the `.rockbox` folder from the ZIP onto the root of the player, so that it merges with the `.rockbox`
   folder already there. Only new files are added, all named `MD3-…`, so your settings and other themes stay
   untouched. `.rockbox` is a hidden folder on macOS and Linux: press <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>.</kbd> in
   Finder or <kbd>Ctrl</kbd>+<kbd>H</kbd> in most Linux file managers to show it.
4. Eject the player safely, then on the device open **Settings → Theme Settings → Browse Theme Files** and select
   the variant, e.g. **MD3-Dark-Orange**.

The repository itself does not contain a ready-to-copy `.rockbox` folder; the themes are generated (see
[Development](#development)).

## Variants

| Variant            | Seed      |
|--------------------|-----------|
| `MD3-Dark-Orange`  | `#FF9130` |
| `MD3-Dark-Blue`    | `#3D7BFF` |
| `MD3-Dark-Green`   | `#3FA35B` |
| `MD3-Dark-Pink`    | `#E0457B` |
| `MD3-Light-Orange` | `#FF9130` |
| `MD3-Light-Blue`   | `#3D7BFF` |
| `MD3-Light-Green`  | `#3FA35B` |
| `MD3-Light-Pink`   | `#E0457B` |

Colours are Material Design 3 TonalSpot schemes (spec 2025) computed from the seed with
[materialyoucolor](https://pypi.org/project/materialyoucolor/). Accent fills (year pill, play button, progress bar,
active shuffle/repeat, menu title icon, battery while charging) use the seed itself. If the seed has less than 3:1
contrast against the background, its tone is adjusted until it does (the generator prints this).

## Development

`tools/generate.py` is the command line; the work happens in the `tools/md3/` package:

| Module        | Does                                                              |
|---------------|-------------------------------------------------------------------|
| `variants.py` | The 8 variants and `--only` name lookup                           |
| `colors.py`   | MD3 tokens per variant, accent contrast, WCAG contrast            |
| `templates.py`| Fills `templates/MD3.{wps,sbs,cfg}.tpl`, CRLF/LF line endings     |
| `drawing.py`  | Anti-aliased shapes and icons (supersampled masks)                |
| `icons.py`    | Icon shapes (Material paths)                                      |
| `bitmaps.py`  | Geometry and every colour bitmap of a skin                        |
| `build.py`    | Writes one variant into a `.rockbox` folder                       |
| `gitinfo.py`  | Version and date for the file headers                             |

Static files (fonts, 1-bit icons, `play.bmp`) live in `assets/`. It needs Python 3.15 (see `.python-version`):

```sh
python3.15 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

```sh
python tools/generate.py                      # all variants into dist/<variant>/.rockbox and dist/MD3-all/.rockbox
python tools/generate.py --only Light-Blue    # one variant (repeatable)
python tools/generate.py --only Dark-Pink --install /path/to/simdisk/.rockbox   # merge into a .rockbox folder
```

`--install` works with the Rockbox simulator (`tools/configure --target=hibyr1 --type=s`, then `make`; its
`simdisk/.rockbox`) or with the player's `.rockbox` folder. The version in the file headers comes from
`git describe`.

Test and lint before committing (CI runs the same):

```sh
pytest
ruff check . && ruff format --check .
```

Releases: pushing a tag `v*` builds all variants and publishes a GitHub release with one ZIP per variant plus
`MD3-all`. Tags containing `-rc` become pre-releases.

## Fonts

The theme uses [DM Sans](https://fonts.google.com/specimen/DM+Sans). The source TTFs are in `source-fonts/`, and the
Rockbox `.fnt` files in `assets/fonts/` are generated from them with `convttf` (a Linux x86-64 build is included,
linked against `libfreetype.so.6`).

To regenerate the fonts:

```sh
./build-fonts.sh
```

| Font file                 | Used for                                               |
|---------------------------|--------------------------------------------------------|
| `35-DMSans-Medium.fnt`    | Status bar, album, year, times (font slot 8)           |
| `42-DMSans-SemiBold.fnt`  | UI font and artist (font slot 3)                       |
| `48-DMSans-SemiBold.fnt`  | Track title and menu title (font slot 4)               |
| `230-DMSans-SemiBold.fnt` | Big volume display (font slot 6), only `+` through `9` |

The pixel sizes are chosen so cap heights match the Ubuntu fonts the theme used before (36/45/50/240). DM Sans has
taller line boxes, so text sits 1–2px lower in its viewport than it did with Ubuntu.

The fonts cover Latin only (403 glyphs). Greek and Cyrillic tags fall back to the default character.

## Credits

- Based on the "Ulmiz" theme by Simon Rothen (rothen@gmx.net), licensed under
  [CC-BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). This port is released under the same license.
- Icon set taken from the advaitapod theme vector files.
- Repeat & Shuffle icons derived from the Gnome-Shell High Contrast icons.
- [DM Sans](https://fonts.google.com/specimen/DM+Sans) by Colophon Foundry, licensed under the SIL Open Font License
  1.1.
- `convttf` from the [Rockbox](https://www.rockbox.org/) project, licensed under the GPL.
- MD3 port by Julian Gödde.
