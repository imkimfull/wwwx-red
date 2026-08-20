from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import resvg_py


ROOT = Path(__file__).resolve().parent
ITEMS = [
    ("01a-crossing-x-compact.svg", "01A  COMPACT X", "Stable / compact"),
    ("01b-crossing-x-forward.svg", "01B  FORWARD X", "Fast / directional"),
    ("01c-crossing-x-red-field.svg", "01C  RED FIELD X", "Bold / inverted"),
    ("02a-signal-w-balanced.svg", "02A  BALANCED W", "Closest to logo"),
    ("02b-signal-w-endpoint.svg", "02B  ENDPOINT W", "Signal / domain point"),
    ("02c-signal-w-light.svg", "02C  LIGHT W", "Light UI version"),
]

SHEET_W, SHEET_H = 1140, 880
CARD_W, CARD_H = 340, 380
GAP_X, GAP_Y = 30, 30
START_X, START_Y = 30, 60


def render_svg(path: Path, size: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(path.read_text(encoding="utf-8"), width=size, height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def font(size: int, bold: bool = False):
    return ImageFont.load_default(size=size)


canvas = Image.new("RGB", (SHEET_W, SHEET_H), "#ECE9E3")
draw = ImageDraw.Draw(canvas)
draw.text((30, 18), "wwwx.red  /  FAVICON EXTENSIONS", fill="#191919", font=font(25, True))

for index, (filename, label, note) in enumerate(ITEMS):
    col, row = index % 3, index // 3
    x = START_X + col * (CARD_W + GAP_X)
    y = START_Y + row * (CARD_H + GAP_Y)

    draw.rounded_rectangle((x, y, x + CARD_W, y + CARD_H), radius=22, fill="#FFFFFF")
    icon = render_svg(ROOT / filename, 236)
    canvas.paste(icon, (x + 52, y + 28), icon)

    draw.text((x + 26, y + 280), label, fill="#191919", font=font(20, True))
    draw.text((x + 26, y + 310), note, fill="#676767", font=font(15))

    icon32 = render_svg(ROOT / filename, 32)
    icon16 = render_svg(ROOT / filename, 16)
    canvas.paste(icon32, (x + 26, y + 338), icon32)
    canvas.paste(icon16, (x + 74, y + 346), icon16)
    draw.text((x + 106, y + 345), "32px  /  16px", fill="#8A8A8A", font=font(13))

canvas.save(ROOT / "favicon-extensions-preview.png", optimize=True)
