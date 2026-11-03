<h1>hiby-r1-rockbox-md3</h1>

A Material Design 3 Port of Simon Rothens "Ulmiz" Theme for the HiBy R1 Rockbox

<img width="388" height="512" alt="image" src="https://github.com/user-attachments/assets/4c3aab56-d466-48ad-9aac-e892e87567cf" />

<h2>Contents</h2>

<!-- TOC -->

* [Installation](#installation)
* [Fonts](#fonts)
* [Credits](#credits)

<!-- TOC -->

## Installation

1. Download this repository: a [tagged release](../../releases) or **Code → Download ZIP**, then unzip it.
2. Connect the HiBy R1 to your computer over USB.
3. Copy the `.rockbox` folder from the download onto the root of the player, so that it merges with the `.rockbox`
   folder already there. Only new files are added, all named `MD3`, so your settings and other themes stay untouched.
   `.rockbox` is a hidden folder on macOS and Linux: press <kbd>Cmd</kbd>+<kbd>Shift</kbd>+<kbd>.</kbd> in Finder or
   <kbd>Ctrl</kbd>+<kbd>H</kbd> in most Linux file managers to show it.
4. Eject the player safely, then on the device open **Settings → Theme Settings → Browse Theme Files** and select
   **MD3**.

The other files in this repository (`source-fonts/`, `convttf`, `build-fonts.sh`) are only needed to rebuild the
fonts and do not belong on the player.

## Fonts

The theme uses [DM Sans](https://fonts.google.com/specimen/DM+Sans). The source TTFs are in `source-fonts/`, and the
Rockbox `.fnt` files in `.rockbox/fonts/` are generated from them with `convttf` (a Linux x86-64 build is included,
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
