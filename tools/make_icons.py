"""Make the app icons from ornaments.icon_svg / icon_small_svg (run once; needs resvg-py, Pillow and numpy).

    python tools/make_icons.py

Writes assets/taqwim_icon.png (512), assets/taqwim_icon.ico (16-256; 16-48 px use the simpler drawing),
and apple-touch-icon.png (180), favicon-32.png, icon-192.png, icon-512.png, icon-maskable-512.png into both
assets/ and launcher/icons/. Then checks that the maskable icon has no art outside the central circle of
radius 40% (every pixel outside it must be exactly the background colour).
"""
import io
import os
import sys

import numpy as np
import resvg_py
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import ornaments as orn  # noqa: E402


def render(svg: str, n: int) -> Image.Image:
    png = resvg_py.svg_to_bytes(svg_string=svg, width=n, height=n)
    return Image.open(io.BytesIO(bytes(png))).convert("RGB")


def main():
    assets = os.path.join(HERE, "assets")
    icons = os.path.join(HERE, "launcher", "icons")
    os.makedirs(assets, exist_ok=True)
    os.makedirs(icons, exist_ok=True)
    full, small = orn.icon_svg(512), orn.icon_small_svg(512)
    mask = render(orn.icon_svg(512, maskable=True), 512)
    render(full, 512).save(os.path.join(assets, "taqwim_icon.png"), optimize=True)
    outs = {"apple-touch-icon.png": render(full, 180), "favicon-32.png": render(small, 32),
            "icon-192.png": render(full, 192), "icon-512.png": render(full, 512), "icon-maskable-512.png": mask}
    for name, im in outs.items():
        im.save(os.path.join(assets, name), optimize=True)
        im.save(os.path.join(icons, name), optimize=True)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    ims = {n: render(small if n <= 48 else full, n) for n in sizes}
    ims[256].save(os.path.join(assets, "taqwim_icon.ico"), format="ICO", sizes=[(n, n) for n in sizes],
                  append_images=[ims[n] for n in sizes if n != 256])
    # maskable safe zone
    m = np.asarray(mask).astype(int)
    yy, xx = np.mgrid[0:512, 0:512]
    outside = (xx + 0.5 - 256) ** 2 + (yy + 0.5 - 256) ** 2 > (0.4 * 512) ** 2
    bg = np.array([int(orn.NIGHT[i:i + 2], 16) for i in (1, 3, 5)])
    bad = int((np.abs(m - bg).max(axis=2)[outside] > 0).sum())
    print(f"maskable icon: {bad} art pixels outside the 40% safe circle (must be 0)")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
