from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import resvg_py


ROOT = Path(__file__).resolve().parent
ITEMS = [
    ("01-junction.svg", "01  JUNCTION", "Direct handoff"),
    ("02-interlock.svg", "02  INTERLOCK", "White signal crosses red"),
    ("03-rising-signal.svg", "03  RISING SIGNAL", "W launches into arrow"),
]


def render_svg(path: Path, size: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(path.read_text(encoding="utf-8"), width=size, height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def font(size: int):
    return ImageFont.load_default(size=size)


sheet = Image.new("RGB", (1140, 470), "#ECE9E3")
draw = ImageDraw.Draw(sheet)
draw.text((30, 18), "wwwx.red  /  W + ARROW HYBRIDS", fill="#191919", font=font(25))

for index, (filename, label, note) in enumerate(ITEMS):
    x = 30 + index * 370
    y = 60
    draw.rounded_rectangle((x, y, x + 340, y + 380), radius=22, fill="#FFFFFF")

    icon = render_svg(ROOT / filename, 236)
    sheet.paste(icon, (x + 52, y + 28), icon)
    draw.text((x + 26, y + 280), label, fill="#191919", font=font(20))
    draw.text((x + 26, y + 310), note, fill="#676767", font=font(15))

    icon32 = render_svg(ROOT / filename, 32)
    icon16 = render_svg(ROOT / filename, 16)
    sheet.paste(icon32, (x + 26, y + 338), icon32)
    sheet.paste(icon16, (x + 74, y + 346), icon16)
    draw.text((x + 106, y + 345), "32px  /  16px", fill="#8A8A8A", font=font(13))

sheet.save(ROOT / "favicon-hybrids-preview.png", optimize=True)
