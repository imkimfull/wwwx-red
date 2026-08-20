from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
VIEW_W = 1360
VIEW_H = 360
PAD_X = 65
PAD_Y = 55


def select_mask(rgb, kind):
    r = rgb[:, :, 0].astype(np.int16)
    g = rgb[:, :, 1].astype(np.int16)
    b = rgb[:, :, 2].astype(np.int16)
    if kind == "dark-white":
        active = (r > 185) & (g > 185) & (b > 185)
    elif kind == "dark-red":
        active = (r > 115) & (r > g * 1.5) & (r > b * 1.45)
    elif kind == "light-charcoal":
        active = (r < 90) & (g < 90) & (b < 90) & (np.abs(r - g) < 24) & (np.abs(g - b) < 24)
    elif kind == "light-red":
        active = (r > 95) & (r > g * 1.5) & (r > b * 1.35)
    else:
        raise ValueError(kind)
    return active.astype(np.uint8) * 255


def catmull_rom_to_bezier(points, closed=True):
    pts = [np.asarray(point, dtype=float) for point in points]
    if len(pts) < 3:
        return ""
    commands = [f"M{pts[0][0]:.3f},{pts[0][1]:.3f}"]
    count = len(pts)
    segment_count = count if closed else count - 1
    for index in range(segment_count):
        p0 = pts[(index - 1) % count] if closed else pts[max(index - 1, 0)]
        p1 = pts[index % count]
        p2 = pts[(index + 1) % count]
        p3 = pts[(index + 2) % count] if closed else pts[min(index + 2, count - 1)]
        c1 = p1 + (p2 - p0) / 6.0
        c2 = p2 - (p3 - p1) / 6.0
        commands.append(
            f"C{c1[0]:.3f},{c1[1]:.3f} {c2[0]:.3f},{c2[1]:.3f} {p2[0]:.3f},{p2[1]:.3f}"
        )
    if closed:
        commands.append("Z")
    return " ".join(commands)


def contours_to_paths(mask, epsilon=1.5):
    # A light close removes one-pixel stair-step gaps without altering proportions.
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    paths = []
    for contour in contours:
        if cv2.contourArea(contour) < 50:
            continue
        approx = cv2.approxPolyDP(contour, epsilon, True)
        points = [item[0] for item in approx]
        if len(points) < 4:
            continue
        paths.append(catmull_rom_to_bezier(points, closed=True))
    return paths


def bounds_of_masks(masks):
    combined = np.maximum.reduce(masks)
    ys, xs = np.nonzero(combined)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def generate(input_name, color_specs, background, output_name):
    rgb = np.asarray(Image.open(ROOT / input_name).convert("RGB"))
    masks = [select_mask(rgb, kind) for kind, _ in color_specs]
    left, top, right, bottom = bounds_of_masks(masks)
    content_w = right - left
    content_h = bottom - top
    scale = min((VIEW_W - PAD_X * 2) / content_w, (VIEW_H - PAD_Y * 2) / content_h)
    tx = (VIEW_W - content_w * scale) / 2 - left * scale
    ty = (VIEW_H - content_h * scale) / 2 - top * scale

    groups = []
    for mask, (_, fill) in zip(masks, color_specs):
        paths = contours_to_paths(mask)
        children = "".join(f'<path d="{path}"/>' for path in paths)
        groups.append(f'<g fill="{fill}">{children}</g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{VIEW_H}" viewBox="0 0 {VIEW_W} {VIEW_H}">
  <title>wwwx.red final smooth vector logo</title>
  <rect width="{VIEW_W}" height="{VIEW_H}" fill="{background}"/>
  <g id="wwwx-red-logo" transform="translate({tx:.5f} {ty:.5f}) scale({scale:.8f})">
    {''.join(groups)}
  </g>
</svg>
'''
    (ROOT / output_name).write_text(svg, encoding="utf-8")


generate(
    "signal-ribbon-dark-fc1016.png",
    [("dark-white", "#F7F5F2"), ("dark-red", "#FC1016")],
    "#191919",
    "wwwx-red-final-smooth-dark.svg",
)

generate(
    "signal-ribbon-light-bb0916.png",
    [("light-charcoal", "#202124"), ("light-red", "#BB0916")],
    "#F5F2EC",
    "wwwx-red-final-smooth-light.svg",
)

print(ROOT / "wwwx-red-final-smooth-dark.svg")
print(ROOT / "wwwx-red-final-smooth-light.svg")
