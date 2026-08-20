from pathlib import Path
from PIL import Image, ImageFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = Path(r"C:\Windows\Fonts\NotoSansTC-VF.ttf")
COMPANY_NAME = "紅品牌策略有限公司"
WIDTH = 1360
HEIGHT = 360
LOGO_X = 70
LOGO_Y = 50
LOGO_W = 1220
TEXT_TOP = 235
TEXT_SIZE = 44
LETTER_SPACING = 9


def trace_runs(values):
    runs = []
    start = None
    for index, active in enumerate(values):
        if active and start is None:
            start = index
        elif not active and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(values)))
    return runs


def binary_mask(image, kind):
    rgba = image.convert("RGBA")
    width, height = rgba.size
    mask = [[False] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            r, g, b, a = rgba.getpixel((x, y))
            if a == 0:
                continue
            if kind == "dark-white":
                active = r > 185 and g > 185 and b > 185
            elif kind == "dark-red":
                active = r > g * 1.5 and r > b * 1.45 and r > 115
            elif kind == "light-charcoal":
                active = r < 90 and g < 90 and b < 90 and abs(r - g) < 24 and abs(g - b) < 24
            elif kind == "light-red":
                active = r > g * 1.5 and r > b * 1.35 and r > 95
            else:
                active = False
            mask[y][x] = active
    return mask


def mask_to_path(mask):
    height = len(mask)
    width = len(mask[0])
    edges = []
    for y in range(height):
        for x0, x1 in trace_runs(mask[y]):
            for x in range(x0, x1):
                if y == 0 or not mask[y - 1][x]:
                    edges.append(((x, y), (x + 1, y)))
                if y == height - 1 or not mask[y + 1][x]:
                    edges.append(((x + 1, y + 1), (x, y + 1)))
                if x == 0 or not mask[y][x - 1]:
                    edges.append(((x, y + 1), (x, y)))
                if x == width - 1 or not mask[y][x + 1]:
                    edges.append(((x + 1, y), (x + 1, y + 1)))

    by_start = {}
    for start, end in edges:
        by_start.setdefault(start, []).append(end)

    paths = []
    while by_start:
        start = next(iter(by_start))
        point = start
        contour = [point]
        while True:
            candidates = by_start.get(point)
            if not candidates:
                break
            nxt = candidates.pop()
            if not candidates:
                del by_start[point]
            point = nxt
            if point == start:
                break
            contour.append(point)
        if len(contour) >= 4 and point == start:
            simplified = []
            for p in contour:
                simplified.append(p)
                while len(simplified) >= 3:
                    a, b, c = simplified[-3:]
                    if (a[0] == b[0] == c[0]) or (a[1] == b[1] == c[1]):
                        simplified.pop(-2)
                    else:
                        break
            data = [f"M{simplified[0][0]} {simplified[0][1]}"]
            data.extend(f"L{x} {y}" for x, y in simplified[1:])
            data.append("Z")
            paths.append(" ".join(data))
    return " ".join(paths)


def text_path_data(text):
    variable_font = TTFont(str(FONT_PATH))
    font = instantiateVariableFont(variable_font, {"wght": 560}, inplace=False)
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    units_per_em = font["head"].unitsPerEm
    scale = TEXT_SIZE / units_per_em
    x_cursor = 0.0
    paths = []
    for char in text:
        glyph_name = cmap.get(ord(char), ".notdef")
        glyph = glyph_set[glyph_name]
        pen = SVGPathPen(glyph_set)
        glyph.draw(pen)
        data = pen.getCommands()
        paths.append((data, x_cursor))
        x_cursor += glyph.width * scale + LETTER_SPACING
    total_width = x_cursor - LETTER_SPACING
    return paths, total_width, scale


def content_bounds(image, kinds):
    combined = None
    for kind in kinds:
        mask = binary_mask(image, kind)
        if combined is None:
            combined = mask
        else:
            for y in range(len(mask)):
                for x in range(len(mask[0])):
                    combined[y][x] = combined[y][x] or mask[y][x]
    xs = []
    ys = []
    for y, row in enumerate(combined):
        for x, active in enumerate(row):
            if active:
                xs.append(x)
                ys.append(y)
    return min(xs), min(ys), max(xs) + 1, max(ys) + 1


def make_svg(image_name, color_specs, background, company_fill, output_name):
    image = Image.open(ROOT / image_name)
    left, top, right, bottom = content_bounds(image, [kind for kind, _ in color_specs])
    content_w = right - left
    content_h = bottom - top
    logo_scale = min(LOGO_W / content_w, 225 / content_h)
    logo_draw_w = content_w * logo_scale
    logo_draw_h = content_h * logo_scale
    logo_tx = (WIDTH - logo_draw_w) / 2 - left * logo_scale
    logo_ty = LOGO_Y - top * logo_scale
    logo_paths = []
    for kind, fill in color_specs:
        data = mask_to_path(binary_mask(image, kind))
        logo_paths.append(f'<path d="{data}" fill="{fill}"/>')

    company_paths, company_w, text_scale = text_path_data(COMPANY_NAME)
    company_x = (WIDTH - company_w) / 2
    baseline_y = TEXT_TOP + TEXT_SIZE
    company_svg = []
    for data, glyph_x in company_paths:
        company_svg.append(
            f'<path d="{data}" transform="translate({company_x + glyph_x:.3f} {baseline_y:.3f}) '
            f'scale({text_scale:.8f} {-text_scale:.8f})"/>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <title>wwwx.red — {COMPANY_NAME}</title>
  <desc>Final logo lockup with company name converted to vector paths.</desc>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{background}"/>
  <g id="logo" transform="translate({logo_tx:.4f} {logo_ty:.4f}) scale({logo_scale:.8f})">
    {''.join(logo_paths)}
  </g>
  <g id="company-name" fill="{company_fill}" fill-rule="nonzero">
    {''.join(company_svg)}
  </g>
</svg>
'''
    (ROOT / output_name).write_text(svg, encoding="utf-8")


def make_preview(image_name, kinds, background, company_fill, output_name):
    from PIL import ImageDraw

    source = Image.open(ROOT / image_name).convert("RGB")
    left, top, right, bottom = content_bounds(source, kinds)
    content_w = right - left
    content_h = bottom - top
    logo_scale = min(LOGO_W / content_w, 225 / content_h)
    logo_w = round(content_w * logo_scale)
    logo_h = round(content_h * logo_scale)
    logo = source.crop((left, top, right, bottom)).resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    preview = Image.new("RGB", (WIDTH, HEIGHT), background)
    preview.paste(logo, ((WIDTH - logo_w) // 2, LOGO_Y))

    font = ImageFont.truetype(str(FONT_PATH), TEXT_SIZE)
    if hasattr(font, "set_variation_by_axes"):
        font.set_variation_by_axes([560])
    draw = ImageDraw.Draw(preview)
    widths = [draw.textlength(char, font=font) for char in COMPANY_NAME]
    text_w = sum(widths) + LETTER_SPACING * (len(COMPANY_NAME) - 1)
    x = (WIDTH - text_w) / 2
    for char, width in zip(COMPANY_NAME, widths):
        draw.text((x, TEXT_TOP), char, font=font, fill=company_fill)
        x += width + LETTER_SPACING
    preview.save(ROOT / output_name)


make_svg(
    "signal-ribbon-dark-fc1016.png",
    [("dark-white", "#F7F5F2"), ("dark-red", "#FC1016")],
    "#191919",
    "#F7F5F2",
    "wwwx-red-final-company-dark.svg",
)
make_preview(
    "signal-ribbon-dark-fc1016.png",
    ["dark-white", "dark-red"],
    "#191919",
    "#F7F5F2",
    "wwwx-red-final-company-dark-preview.png",
)

make_svg(
    "signal-ribbon-light-bb0916.png",
    [("light-charcoal", "#202124"), ("light-red", "#BB0916")],
    "#F5F2EC",
    "#202124",
    "wwwx-red-final-company-light.svg",
)
make_preview(
    "signal-ribbon-light-bb0916.png",
    ["light-charcoal", "light-red"],
    "#F5F2EC",
    "#202124",
    "wwwx-red-final-company-light-preview.png",
)

print(ROOT / "wwwx-red-final-company-dark.svg")
print(ROOT / "wwwx-red-final-company-light.svg")
