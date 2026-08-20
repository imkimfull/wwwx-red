from pathlib import Path

from PIL import Image

from generate_final_logo_svg import binary_mask, content_bounds, mask_to_path


ROOT = Path(__file__).resolve().parents[1]
CANVAS_W = 1360
CANVAS_H = 360
PADDING_X = 70
PADDING_Y = 55


def make_logo_svg(image_name, color_specs, background, output_name):
    image = Image.open(ROOT / image_name)
    kinds = [kind for kind, _ in color_specs]
    left, top, right, bottom = content_bounds(image, kinds)
    content_w = right - left
    content_h = bottom - top

    scale = min(
        (CANVAS_W - PADDING_X * 2) / content_w,
        (CANVAS_H - PADDING_Y * 2) / content_h,
    )
    draw_w = content_w * scale
    draw_h = content_h * scale
    tx = (CANVAS_W - draw_w) / 2 - left * scale
    ty = (CANVAS_H - draw_h) / 2 - top * scale

    paths = []
    for kind, fill in color_specs:
        data = mask_to_path(binary_mask(image, kind))
        paths.append(f'<path d="{data}" fill="{fill}"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}">
  <title>wwwx.red final logo</title>
  <rect width="{CANVAS_W}" height="{CANVAS_H}" fill="{background}"/>
  <g id="wwwx-red-logo" transform="translate({tx:.4f} {ty:.4f}) scale({scale:.8f})">
    {''.join(paths)}
  </g>
</svg>
'''
    (ROOT / output_name).write_text(svg, encoding="utf-8")


make_logo_svg(
    "signal-ribbon-dark-fc1016.png",
    [("dark-white", "#F7F5F2"), ("dark-red", "#FC1016")],
    "#191919",
    "wwwx-red-final-dark.svg",
)

make_logo_svg(
    "signal-ribbon-light-bb0916.png",
    [("light-charcoal", "#202124"), ("light-red", "#BB0916")],
    "#F5F2EC",
    "wwwx-red-final-light.svg",
)

print(ROOT / "wwwx-red-final-dark.svg")
print(ROOT / "wwwx-red-final-light.svg")
