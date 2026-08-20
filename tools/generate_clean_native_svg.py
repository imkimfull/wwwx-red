from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = Path(r"C:\Windows\Fonts\bahnschrift.ttf")
WIDTH = 1360
HEIGHT = 360


def glyph_path(char, x, baseline, font_size, weight=650, width_axis=75):
    variable = TTFont(str(FONT_PATH))
    font = instantiateVariableFont(variable, {"wght": weight, "wdth": width_axis}, inplace=False)
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    glyph_name = cmap[ord(char)]
    glyph = glyph_set[glyph_name]
    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    scale = font_size / font["head"].unitsPerEm
    path = (
        f'<path d="{pen.getCommands()}" '
        f'transform="translate({x:.3f} {baseline:.3f}) scale({scale:.8f} {-scale:.8f})"/>'
    )
    advance = glyph.width * scale
    return path, advance


def build(red, background, foreground, filename):
    # One native stroked path creates the WWW signal with mathematically smooth round joins.
    signal = (
        'M100 126 H132 '
        'C148 126 153 135 160 151 '
        'L184 211 '
        'C191 228 209 228 216 211 '
        'L247 148 '
        'C255 131 273 131 281 148 '
        'L309 211 '
        'C317 228 335 228 343 211 '
        'L382 135 '
        'C390 119 408 119 416 135 '
        'L452 211 '
        'C460 228 478 228 486 211 '
        'L516 148 '
        'C524 131 542 131 550 148 '
        'L579 211 '
        'C587 228 605 228 613 211 '
        'L651 135 '
        'C659 119 677 119 685 135 '
        'L721 211 '
        'C729 228 747 228 755 211 '
        'L784 148 '
        'C792 131 810 131 818 148 '
        'L846 211 '
        'C854 228 872 228 880 211 '
        'L923 139 '
        'C932 124 947 122 960 132 '
        'L1021 181'
    )

    text_x = 1144
    text_baseline = 232
    font_size = 142
    letters = []
    for char in "RED":
        path, advance = glyph_path(char, text_x, text_baseline, font_size)
        letters.append(path)
        text_x += advance + 11

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" shape-rendering="geometricPrecision">
  <title>wwwx.red final native vector logo</title>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{background}"/>
  <g id="wwwx-red-logo">
    <path d="{signal}" fill="none" stroke="{foreground}" stroke-width="31" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M1021 181 L1064 137 M1021 181 L1064 225" fill="none" stroke="{red}" stroke-width="31" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="1110" cy="181" r="20" fill="{red}"/>
    <g fill="{red}">{''.join(letters)}</g>
  </g>
</svg>
'''
    (ROOT / filename).write_text(svg, encoding="utf-8")


build("#FC1016", "#191919", "#F7F5F2", "wwwx-red-final-clean-dark.svg")
build("#BB0916", "#F5F2EC", "#202124", "wwwx-red-final-clean-light.svg")

print(ROOT / "wwwx-red-final-clean-dark.svg")
print(ROOT / "wwwx-red-final-clean-light.svg")
