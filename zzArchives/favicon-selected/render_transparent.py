from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import resvg_py


ROOT = Path(__file__).resolve().parent
ITEMS = [
    ("wwwx-red-mark-for-dark.svg", "DARK SURFACES", "#F7F5F2 + #FC1016", "#191919"),
    ("wwwx-red-mark-for-light.svg", "LIGHT SURFACES", "#202124 + #BB0916", "#F5F2EC"),
]


def render_svg(path: Path, size: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(path.read_text(encoding="utf-8"), width=size, height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def font(size: int):
    return ImageFont.load_default(size=size)


def checkerboard(size: int, cell: int = 20) -> Image.Image:
    board = Image.new("RGB", (size, size), "#E8E8E8")
    board_draw = ImageDraw.Draw(board)
    for row in range(0, size, cell):
        for col in range(0, size, cell):
            if (row // cell + col // cell) % 2:
                board_draw.rectangle((col, row, col + cell - 1, row + cell - 1), fill="#CFCFCF")
    return board


for filename, _, _, _ in ITEMS:
    svg = ROOT / filename
    stem = svg.stem
    for size in (512, 180, 64, 32, 16):
        render_svg(svg, size).save(ROOT / f"{stem}-{size}.png", optimize=True)

sheet = Image.new("RGB", (1000, 570), "#ECE9E3")
draw = ImageDraw.Draw(sheet)
draw.text((30, 18), "wwwx.red  /  TRANSPARENT MARKS", fill="#191919", font=font(25))

for index, (filename, label, colors, sample_bg) in enumerate(ITEMS):
    x = 30 + index * 480
    y = 60
    draw.rounded_rectangle((x, y, x + 450, y + 480), radius=22, fill="#FFFFFF")

    board = checkerboard(270)
    icon = render_svg(ROOT / filename, 240)
    board.paste(icon, (15, 15), icon)
    sheet.paste(board, (x + 24, y + 24))
    draw.text((x + 310, y + 34), label, fill="#191919", font=font(14))
    draw.text((x + 316, y + 64), "Transparent SVG", fill="#676767", font=font(14))
    draw.text((x + 316, y + 88), colors, fill="#676767", font=font(13))

    draw.rounded_rectangle((x + 24, y + 320, x + 426, y + 438), radius=16, fill=sample_bg)
    for offset, size in zip((24, 122, 190), (64, 32, 16)):
        sample = render_svg(ROOT / filename, size)
        top = y + 347 + (64 - size) // 2
        sheet.paste(sample, (x + offset, top), sample)
    label_color = "#F7F5F2" if sample_bg == "#191919" else "#555555"
    draw.text((x + 256, y + 374), "64 / 32 / 16px", fill=label_color, font=font(13))
    draw.text((x + 24, y + 450), "Checkerboard and sample surface are preview only.", fill="#8A8A8A", font=font(12))

sheet.save(ROOT / "wwwx-red-transparent-marks-preview.png", optimize=True)
