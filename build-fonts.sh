#!/bin/sh
# Regenerates the Rockbox .fnt files from source-fonts/ using convttf.
# Pixel sizes are chosen so cap heights match the previous Ubuntu fonts
# (Ubuntu 36/45/50/240 -> DM Sans 35/42/48/230).
set -e
cd "$(dirname "$0")"

OUT=.rockbox/fonts
SRC=source-fonts
mkdir -p "$OUT"

./convttf -p 35 -o "$OUT/35-DMSans-Medium.fnt" "$SRC/DMSans-Medium.ttf"
./convttf -p 42 -o "$OUT/42-DMSans-SemiBold.fnt" "$SRC/DMSans-SemiBold.ttf"
./convttf -p 48 -o "$OUT/48-DMSans-SemiBold.fnt" "$SRC/DMSans-SemiBold.ttf"
# Big volume display: only '+' through '9' are needed
./convttf -p 230 -s 43 -l 57 -o "$OUT/230-DMSans-SemiBold.fnt" "$SRC/DMSans-SemiBold.ttf"
