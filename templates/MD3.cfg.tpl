# Rockbox Theme Name: {{name}}
# Platform: Hiby R1 (480x800)
# Original Author: Simon Rothen (rothen@gmx.net)
# MD3 Port: Julian Gödde
# Licencing: CC-BY-SA 3.0
# iconset taken from advaitapod theme vector files
# Repeat & Shuffle Icons derived from Gnome-Shell High Contrast Icons
#
# Version: {{version}}
# Date: {{date}}
#
# Theme File
#
#

wps: /.rockbox/wps/{{name}}.wps
sbs: /.rockbox/wps/{{name}}.sbs
# Colours: MD3 {{scheme}} scheme tokens, seed {{seed}} (see {{name}}.wps).
# onSurface on surface (surface = flat sbs_bg.bmp, so anti-aliased text blends correctly)
foreground color: {{onSurface}}
background color: {{surface}}
font: /.rockbox/fonts/42-DMSans-SemiBold.fnt
iconset: /.rockbox/icons/MD3_icons.bmp
viewers iconset: /.rockbox/icons/MD3_viewer.bmp
backdrop: -
show icons: on
filetype colours: -
scrollbar: right
scrollbar width: 40
selector type: bar (color)
statusbar: top
# selected item: onPrimaryContainer on primaryContainer (same pairing as the WPS title pill)
line selector text color: {{onPrimaryContainer}}
line selector end color: {{primaryContainer}}
line selector start color: {{primaryContainer}}
ui viewport: -
list padding: 38
#touchscreen mode: point
#list separator height: off