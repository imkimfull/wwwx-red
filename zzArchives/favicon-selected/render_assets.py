from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
import resvg_py


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "favicon-hybrids" / "01-junction.svg"
FILES = [
    (SOURCE, "BEFORE", "Original junction"),
    (ROOT / "wwwx-red-favicon-dark.svg", "REFINED / DARK", "Primary favicon"),
    (ROOT / "wwwx-red-favicon-light.svg", "REFINED / LIGHT", "Light UI counterpart"),
]


def render_svg(path: Path, size: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(path.read_text(encoding="utf-8"), width=size, height=size)
    return Image.open(BytesIO(png)).convert("RGBA")


def font(size: int):
    return ImageFont.load_default(size=size)


for theme in ("dark", "light"):
    svg = ROOT / f"wwwx-red-favicon-{theme}.svg"
    for size in (512, 180, 64, 32, 16):
        render_svg(svg, size).save(ROOT / f"wwwx-red-favicon-{theme}-{size}.png", optimize=True)

dark_512 = Image.open(ROOT / "wwwx-red-favicon-dark-512.png").convert("RGBA")
dark_512.save(
    ROOT / "wwwx-red-favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
)

sheet = Image.new("RGB", (1140, 500), "#ECE9E3")
draw = ImageDraw.Draw(sheet)
draw.text((30, 18), "wwwx.red  /  SELECTED FAVICON REFINEMENT", fill="#191919", font=font(25))

for index, (path, label, note) in enumerate(FILES):
    x = 30 + index * 370
    y = 60
    draw.rounded_rectangle((x, y, x + 340, y + 410), radius=22, fill="#FFFFFF")
    icon = render_svg(path, 250)
    sheet.paste(icon, (x + 45, y + 24), icon)
    draw.text((x + 26, y + 292), label, fill="#191919", font=font(20))
    draw.text((x + 26, y + 322), note, fill="#676767", font=font(15))

    for offset, size in zip((0, 62, 110), (64, 32, 16)):
        sample = render_svg(path, size)
        sheet.paste(sample, (x + 26 + offset, y + 350 + (64 - size)), sample)
    draw.text((x + 160, y + 386), "64 / 32 / 16px", fill="#8A8A8A", font=font(13))

sheet.save(ROOT / "wwwx-red-favicon-refinement-preview.png", optimize=True)
