"""Build the two embedded Arabic fonts from the Google Fonts originals (run once; needs fontTools and brotli).

    python tools/build_fonts.py  <folder with NotoKufiArabic[wght].ttf and NotoNaskhArabic[wght].ttf>

Sources: github.com/google/fonts, ofl/notokufiarabic and ofl/notonaskharabic (SIL Open Font License 1.1).
Each variable font is fixed at one weight (Kufi 700 for the title, Naskh 400 for running text) and cut down to
the Arabic letters, short vowels, Arabic and Persian digits and Arabic punctuation, with all OpenType layout
features kept so that letters still join. Output: assets/fonts/*.woff2 (a few tens of kB each).
"""
import os
import sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "assets", "fonts")

# U+0621-0652 letters and short vowels; 0670 dagger alif; 0660-066D Arabic digits and signs; Persian letters
# pe, che, zhe, keheh, gaf, Farsi yeh and Persian digits (Shia and Iranian names); FD3E/FD3F ornate parentheses.
ARABIC = (list(range(0x0621, 0x0653)) + [0x0670] + list(range(0x0660, 0x066E)) + [0x060C, 0x061B, 0x061F, 0x0640]
          + [0x067E, 0x0686, 0x0698, 0x06A9, 0x06AF, 0x06CC] + list(range(0x06F0, 0x06FA))
          + [0x0020, 0x00A0, 0x200C, 0x200D, 0x200E, 0x200F, 0xFD3E, 0xFD3F])

JOBS = [("NotoKufiArabic[wght].ttf", 700, "NotoKufiArabic-Bold-sub.woff2"),
        ("NotoNaskhArabic[wght].ttf", 400, "NotoNaskhArabic-Regular-sub.woff2")]


def build(src_dir: str):
    os.makedirs(OUT, exist_ok=True)
    for src, wght, out in JOBS:
        f = instancer.instantiateVariableFont(TTFont(os.path.join(src_dir, src)), {"wght": wght})
        o = subset.Options()
        o.layout_features = ["*"]
        o.name_IDs = ["*"]
        o.name_legacy = True
        o.notdef_outline = True
        o.hinting = False
        o.flavor = "woff2"
        s = subset.Subsetter(o)
        s.populate(unicodes=ARABIC)
        s.subset(f)
        f.flavor = "woff2"
        f.save(os.path.join(OUT, out))
        print(out, os.path.getsize(os.path.join(OUT, out)), "bytes")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
