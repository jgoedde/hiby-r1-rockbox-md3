# hiby-r1-rockbox-jgulmiz

A Material Design 3 Port of Simon Rothens "Ulmiz" Theme for the HiBy R1 Rockbox

<img width="507" height="592" alt="image" src="https://github.com/user-attachments/assets/208c77e9-1159-4eb6-8d87-24288def1bf2" />

## Fonts

The theme uses [DM Sans](https://fonts.google.com/specimen/DM+Sans). The source TTFs are in `source-fonts/`, and the
Rockbox `.fnt` files in `.rockbox/fonts/` are generated from them with `convttf` (a Linux x86-64 build is included,
linked against `libfreetype.so.6`).

To regenerate the fonts:

```sh
./build-fonts.sh
```

| Font file               | Used for                                               |
|-------------------------|--------------------------------------------------------|
| `35-DMSans-Regular.fnt` | Status bar, album, year, times (font slot 8)           |
| `42-DMSans-Medium.fnt`  | UI font and artist (font slot 3)                       |
| `48-DMSans-Medium.fnt`  | Track title and menu title (font slot 4)               |
| `230-DMSans-Medium.fnt` | Big volume display (font slot 6), only `+` through `9` |

The pixel sizes are chosen so cap heights match the Ubuntu fonts the theme used before (36/45/50/240). DM Sans has
taller line boxes, so text sits 1–2px lower in its viewport than it did with Ubuntu.

The fonts cover Latin only (403 glyphs). Greek and Cyrillic tags fall back to the default character.
