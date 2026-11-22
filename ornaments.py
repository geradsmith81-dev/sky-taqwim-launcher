"""Decorative SVG ornaments after early Islamic art (Umayyad and Abbasid, 7th-9th centuries).

* khatam - the eight-pointed star made of two squares, one turned 45 degrees. The plan of the Dome of the
  Rock (691-692) is set out from two such squares inside a circle; eight-fold stars and octagons run through
  Umayyad floor mosaics and the marble window grilles of the Great Mosque of Damascus (706-715).
* rosette - an eight-lobed rosette, as in the rosettes and 'jewel' motifs of the Dome of the Rock mosaics.
* frieze - a two-strand interlace (guilloche) with small eight-pointed stars in its loops over a band of
  coloured tesserae: the interlace of the Damascus grilles and Umayyad floor mosaics, and the gold-ground
  mosaic borders of the Dome of the Rock. (Girih strapwork proper is later, from about 1000 CE.)
* mihrab - a horseshoe arch with alternating voussoirs on two columns: the horseshoe arch of Umayyad Syria
  (Damascus) and of the Great Mosque of Cordoba (begun 785, voussoirs in two colours).
* vine scroll - a running vine with leaves and grape clusters, as in the Damascus 'karma' frieze, the Dome
  of the Rock mosaics and the carved facade of Mshatta (only the vegetal parts are drawn).
* Samarra bevel - a mirrored pair of 'trumpet' forms ending in spirals, with a lancet between, in the
  bevelled ('slant-cut') stucco of Abbasid Samarra (Herzfeld's Style C, mid-9th c.), as also at the Mosque of
  Ibn Tulun in Cairo (876-879).
* qibla compass and the Moon. The Moon is drawn only as the astronomical Moon (lit part and earthshine), never
  as the star-and-crescent, which became an emblem in the Ottoman period.
All are drawn here from simple geometry (no copied images); no figurative imagery.
"""
from __future__ import annotations

import base64
import math

GOLD = "#ebc25f"        # gold tesserae
GOLD_DEEP = "#a8792a"   # the shadowed side of a bevel / gold in shade
GREEN = "#2e7d5b"       # mosaic green
GREEN_LIGHT = "#5fae7e"
LAPIS = "#2a4d9b"       # ultramarine glass
TURQUOISE = "#3fb8af"
CARNELIAN = "#b5412c"
NACRE = "#efe9f4"       # mother-of-pearl
IVORY = "#f6efdc"
NIGHT = "#0b1430"
CARD = "#14214a"
EARTHSHINE = "#24315a"


def _svg(w, h, body, vw=None, vh=None, extra="") -> str:
    vw = w if vw is None else vw
    vh = h if vh is None else vh
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {vw:g} {vh:g}' width='{w:g}' height='{h:g}'"
            f"{extra}>{body}</svg>")


def _pts(points, nd=2) -> str:
    return " ".join(f"{x:.{nd}f},{y:.{nd}f}" for x, y in points)


def star_points(cx, cy, R, n=8, rot=0.0, inner=None):
    """Vertices of an n-pointed star polygon. For n=8 and inner=None the star is exactly two overlapping
    squares (the khatam): inner radius R*cos(45)/cos(22.5)."""
    if inner is None:
        inner = R * math.cos(math.pi / 4) / math.cos(math.pi / 8) if n == 8 else R * 0.5
    out = []
    for k in range(2 * n):
        r = R if k % 2 == 0 else inner
        a = math.radians(rot - 90) + k * math.pi / n
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def khatam(cx, cy, R, color=GOLD, line=NIGHT, center=CARNELIAN, rot=0.0) -> str:
    """Eight-pointed star (two squares), with an inner star line and a jewel at the centre."""
    sw = max(R * 0.09, 0.6)
    s = (f"<polygon points='{_pts(star_points(cx, cy, R, rot=rot + 22.5))}' fill='{color}'/>"
         f"<polygon points='{_pts(star_points(cx, cy, R * 0.62, rot=rot + 22.5))}' fill='none' stroke='{line}' "
         f"stroke-width='{sw:.2f}' stroke-linejoin='round'/>")
    if center:
        s += f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{R * 0.2:.2f}' fill='{center}'/>"
    return s


def khatam_svg(size=28, color=GOLD, center=CARNELIAN, line=NIGHT) -> str:
    return _svg(size, size, khatam(50, 50, 48, color, line, center), 100, 100)


def rosette_svg(size=28, petals=8, color=GOLD, center=CARNELIAN) -> str:
    """Eight-lobed rosette in a ring, with a small khatam at the centre."""
    c = 50
    out = []
    for k in range(petals):
        a = 360 * k / petals + 180 / petals
        out.append(f"<path d='M{c},{c} C{c - 15},{c - 18} {c - 11},{c - 40} {c},{c - 42} "
                   f"C{c + 11},{c - 40} {c + 15},{c - 18} {c},{c} Z' transform='rotate({a:.1f} {c} {c})' fill='{color}'/>")
    out.append(f"<circle cx='{c}' cy='{c}' r='47' fill='none' stroke='{color}' stroke-width='3'/>")
    out.append(khatam(c, c, 15, NIGHT, color, center))
    return _svg(size, size, "".join(out), 100, 100)


# --------------------------------------------------------------------------------------------- frieze
def _wave(x0, x1, yc, amp, period, sign, step=1.0):
    pts = []
    x = x0
    while x <= x1 + 1e-9:
        pts.append((x, yc + sign * amp * math.sin(2 * math.pi * x / period)))
        x += step
    return pts


def frieze_tile_svg(h=34) -> str:
    """One repeat (80 x 34) of the frieze: two-strand interlace with stars in its loops, over a tesserae band.
    The strands pass over and under in turn at each crossing; the tile joins seamlessly with repeat-x."""
    w, period, yc, amp = 80, 40, 14.5, 8.0
    half = period / 2
    out = [f"<line x1='0' y1='1.2' x2='{w}' y2='1.2' stroke='{GOLD}' stroke-width='1.2'/>"]
    # stars in the loops (centres midway between crossings)
    for i, x in enumerate((10, 30, 50, 70)):
        out.append(khatam(x, yc, 5.0, TURQUOISE if i % 2 == 0 else CARNELIAN, NIGHT, IVORY))
    # crossings at x = 0, 20, 40, 60, 80; segments of +-10 around each; the over strand alternates
    for j in range(0, 5):
        xc = j * half
        segs = [_wave(xc - 10, xc + 10, yc, amp, period, s, 1.0) for s in (1, -1)]
        order = segs if j % 2 == 0 else segs[::-1]
        for seg in order:
            p = _pts(seg, 1)
            out.append(f"<polyline points='{p}' fill='none' stroke='{NIGHT}' stroke-width='4.6' stroke-linecap='butt'/>")
            out.append(f"<polyline points='{p}' fill='none' stroke='{GOLD}' stroke-width='2.4' stroke-linecap='butt'/>")
    # tesserae band: small squares set on edge, gold / green / gold / lapis ...
    out.append(f"<line x1='0' y1='26.2' x2='{w}' y2='26.2' stroke='{GOLD}' stroke-width='1'/>")
    cols = [GOLD, GREEN_LIGHT, GOLD, TURQUOISE, GOLD, GREEN_LIGHT, GOLD, CARNELIAN]
    for k, col in enumerate(cols):
        x = 5 + 10 * k
        out.append(f"<rect x='{x - 2.4:.1f}' y='{29.6 - 2.4:.1f}' width='4.8' height='4.8' fill='{col}' "
                   f"transform='rotate(45 {x} 29.6)'/>")
    out.append(f"<line x1='0' y1='33.2' x2='{w}' y2='33.2' stroke='{GOLD}' stroke-width='1'/>")
    return _svg(w * h / 34, h, "".join(out), w, 34)


# --------------------------------------------------------------------------------------------- mihrab arch
def horseshoe_arch(cx, cy, r_out, r_in, drop_deg, n_vous=11, colors=(GOLD, CARNELIAN)) -> str:
    """A horseshoe arch band: the circle continues drop_deg below the line of its centre on both sides.
    The band is cut into alternating voussoirs (as at Cordoba)."""
    total = math.pi + 2 * math.radians(drop_deg)
    out = []
    for k in range(n_vous):
        t0 = math.pi + math.radians(drop_deg) - total * k / n_vous      # left springing, over the top, to the right
        t1 = math.pi + math.radians(drop_deg) - total * (k + 1) / n_vous
        p = []
        for t in (t0, t1):
            p.append((cx + r_out * math.cos(t), cy - r_out * math.sin(t)))
        for t in (t1, t0):
            p.append((cx + r_in * math.cos(t), cy - r_in * math.sin(t)))
        out.append(f"<path d='M{p[0][0]:.2f},{p[0][1]:.2f} A{r_out},{r_out} 0 0 1 {p[1][0]:.2f},{p[1][1]:.2f} "
                   f"L{p[2][0]:.2f},{p[2][1]:.2f} A{r_in},{r_in} 0 0 0 {p[3][0]:.2f},{p[3][1]:.2f} Z' "
                   f"fill='{colors[k % len(colors)]}'/>")
    return "".join(out)


def _arch_outline(cx, cy, r, drop_deg, base_y) -> str:
    d = math.radians(drop_deg)
    xl, xr = cx - r * math.cos(d), cx + r * math.cos(d)
    ys = cy + r * math.sin(d)
    return (f"M{xl:.2f},{base_y:.2f} L{xl:.2f},{ys:.2f} A{r},{r} 0 1 1 {xr:.2f},{ys:.2f} L{xr:.2f},{base_y:.2f}")


def mihrab(x0, y0, s=1.0, star=True, voussoirs=True) -> str:
    """Horseshoe-arched niche in a 66 x 80 box at (x0, y0), scaled by s."""
    def X(v):
        return x0 + v * s

    def Y(v):
        return y0 + v * s
    cx, cy, ro, ri, drop = 33, 31, 27, 19.5, 24
    out = []
    # the niche (a slightly lighter field) and its outline
    out.append(f"<path d='{_arch_outline(X(cx), Y(cy), ri * s, drop, Y(74))} Z' fill='{CARD}'/>")
    if voussoirs:
        out.append(horseshoe_arch(X(cx), Y(cy), ro * s, ri * s, drop))
    else:
        out.append(f"<path d='{_arch_outline(X(cx), Y(cy), (ro + ri) / 2 * s, drop, Y(74))}' fill='none' "
                   f"stroke='{GOLD}' stroke-width='{(ro - ri) * s:.2f}'/>")
    out.append(f"<path d='{_arch_outline(X(cx), Y(cy), ro * s, drop, Y(74))}' fill='none' stroke='{GOLD}' "
               f"stroke-width='{1.4 * s:.2f}'/>")
    # columns with capitals and bases
    d = math.radians(drop)
    for side in (-1, 1):
        xc = cx + side * (ri + ro) / 2 * math.cos(d)
        ys = cy + (ri + ro) / 2 * math.sin(d) + 3
        out.append(f"<rect x='{X(xc - 3.6):.2f}' y='{Y(ys):.2f}' width='{7.2 * s:.2f}' height='{3.2 * s:.2f}' fill='{GOLD}'/>")
        out.append(f"<rect x='{X(xc - 2.2):.2f}' y='{Y(ys + 3.2):.2f}' width='{4.4 * s:.2f}' height='{(70.5 - ys - 3.2) * s:.2f}' fill='{GOLD}'/>")
        out.append(f"<rect x='{X(xc - 3.6):.2f}' y='{Y(70.5):.2f}' width='{7.2 * s:.2f}' height='{3.5 * s:.2f}' fill='{GOLD}'/>")
    out.append(f"<rect x='{X(2):.2f}' y='{Y(74):.2f}' width='{62 * s:.2f}' height='{2.2 * s:.2f}' fill='{GOLD}'/>")
    if star:
        out.append(khatam(X(cx), Y(cy + 9), 11 * s))
        # a small vine sprig rising under the star
        out.append(f"<path d='M{X(cx):.2f},{Y(70):.2f} L{X(cx):.2f},{Y(cy + 21):.2f}' stroke='{GREEN_LIGHT}' stroke-width='{1.4 * s:.2f}'/>")
        for side in (-1, 1):
            out.append(f"<path d='M{X(cx):.2f},{Y(62):.2f} q{side * 6 * s:.2f},{-2 * s:.2f} {side * 8 * s:.2f},{-9 * s:.2f} "
                       f"q{-side * 6 * s:.2f},{1 * s:.2f} {-side * 8 * s:.2f},{9 * s:.2f} Z' fill='{GREEN_LIGHT}'/>")
    return "".join(out)


def mihrab_svg(w=66, h=80) -> str:
    return _svg(w, h, mihrab(0, 0, 1.0), 66, 80)


# --------------------------------------------------------------------------------------------- vine scroll
def _leaf(x, y, size, angle, color) -> str:
    """A three-lobed vine leaf (a fan of three pointed lobes)."""
    s = size
    out = []
    for da, L in ((-38, 0.8), (0, 1.0), (38, 0.8)):
        out.append(f"<path d='M0,0 C{-0.32 * s * L:.2f},{-0.35 * s * L:.2f} {-0.18 * s * L:.2f},{-0.85 * s * L:.2f} 0,{-s * L:.2f} "
                   f"C{0.18 * s * L:.2f},{-0.85 * s * L:.2f} {0.32 * s * L:.2f},{-0.35 * s * L:.2f} 0,0 Z' "
                   f"transform='translate({x:.2f} {y:.2f}) rotate({angle + da:.1f})' fill='{color}'/>")
    return "".join(out)


def _grapes(x, y, r, color, angle=0.0) -> str:
    """A hanging bunch of grapes: rows of 3, 2, 2, 1 berries below (x, y)."""
    berries = [(-1, 0), (0, 0), (1, 0), (-0.5, 0.9), (0.5, 0.9), (-0.5, 1.8), (0.5, 1.8), (0, 2.7)]
    out = [f"<g transform='translate({x:.2f} {y:.2f}) rotate({angle:.1f})'>"]
    for dx, dy in berries:
        out.append(f"<circle cx='{dx * 2 * r:.2f}' cy='{dy * 2 * r:.2f}' r='{r:.2f}' fill='{color}'/>")
    out.append("</g>")
    return "".join(out)


def vine_scroll_svg(w=120, h=34, color=GOLD, leaf=GREEN_LIGHT, fruit=NACRE) -> str:
    """One repeat (120 x 34) of a running vine scroll: a wavy stem, tendril spirals, leaves and grapes."""
    period, yc, amp = 120, 15, 6
    stem = _pts(_wave(-2, w + 2, yc, amp, period, 1, 2.0), 1)
    out = [f"<polyline points='{stem}' fill='none' stroke='{color}' stroke-width='2.2'/>"]
    for xk, sign in ((30, 1), (90, -1)):
        y = yc + amp * math.sin(2 * math.pi * xk / period)
        # tendril spiral
        sp = []
        for i in range(48):
            t = i / 47
            r = 6.5 * (1 - 0.8 * t)
            a = -math.pi / 2 * sign + sign * 2 * math.pi * 1.2 * t
            sp.append((xk + 9 + r * math.cos(a), y - sign * 7 + r * math.sin(a) * sign))
        out.append(f"<polyline points='{_pts(sp)}' fill='none' stroke='{color}' stroke-width='1.2'/>")
        out.append(_leaf(xk - 7, y, 11, -25 * sign if sign > 0 else 180 + 25, leaf))
        xg = xk + (15 if sign > 0 else 24)
        yg = yc + amp * math.sin(2 * math.pi * xg / period)
        out.append(_grapes(xg, yg + 3, 1.4, fruit))
    return _svg(w * h / 34, h, "".join(out), w, 34)


# --------------------------------------------------------------------------------------------- Samarra bevel
def _trumpet(sign: int) -> str:
    """One trumpet form for the right (sign=1) or left (sign=-1) half of a 100 x 100 Samarra motif."""
    def P(x, y):
        return f"{50 + sign * x:.2f},{y:.2f}"
    return (f"M{P(2, 94)} C{P(10, 74)} {P(40, 74)} {P(44, 52)} C{P(47, 36)} {P(36, 24)} {P(26, 28)} "
            f"C{P(17, 32)} {P(20, 45)} {P(30, 43)} C{P(25, 52)} {P(14, 50)} {P(13, 40)} "
            f"C{P(12, 22)} {P(40, 14)} {P(48, 34)} C{P(55, 54)} {P(34, 80)} {P(8, 96)} Z")


def samarra_bevel_svg(size=80, face=GOLD, shade=GOLD_DEEP, line=NIGHT) -> str:
    """Mirrored trumpets ending in spirals, with a lancet between: bevelled (slant-cut) stucco, Style C.
    The bevel is shown by a darker copy set slightly down and right of each face."""
    out = []
    lancet = "M50,8 C58,30 58,62 50,92 C42,62 42,30 50,8 Z"
    for d, col in ((f"translate(1.8 2.4)", shade), ("", face)):
        g = f"<g transform='{d}'>" if d else "<g>"
        out.append(g + f"<path d='{_trumpet(1)}' fill='{col}'/><path d='{_trumpet(-1)}' fill='{col}'/>"
                   f"<path d='{lancet}' fill='{col}'/></g>")
    out.append(f"<path d='M50,18 L50,82' stroke='{line}' stroke-width='1.6' stroke-linecap='round'/>")
    for sx in (1, -1):
        out.append(f"<circle cx='{50 + sx * 30:.1f}' cy='35.5' r='2.6' fill='{line}'/>")
        out.append(f"<path d='M{50 + sx * 6:.1f},88 C{50 + sx * 22:.1f},74 {50 + sx * 36:.1f},68 {50 + sx * 39:.1f},52' "
                   f"fill='none' stroke='{line}' stroke-width='1.3' stroke-linecap='round'/>")
    return _svg(size, size, "".join(out), 100, 100)


def samarra_band_svg(h=34) -> str:
    """A repeat-x band of the Samarra motif, alternately upright and inverted."""
    inner = samarra_bevel_svg(34)
    body = (f"<g transform='translate(0 0)'>{inner}</g>"
            f"<g transform='translate(68 34) rotate(180)'>{inner}</g>")
    return _svg(68 * h / 34, h, body, 68, 34)


# --------------------------------------------------------------------------------------------- qibla compass
def qibla_compass_svg(bearing_deg: float, size: int = 160, caption: str = "", needle: bool = True) -> str:
    """A compass card with N, E, S and W, an eight-pointed rose, and a gold needle toward the qibla.
    bearing_deg: initial great-circle bearing to the Kaaba, degrees clockwise from true north."""
    c, R = 80, 74
    out = [f"<circle cx='{c}' cy='{c}' r='{R}' fill='{CARD}' stroke='{GOLD}' stroke-width='2.2'/>",
           f"<circle cx='{c}' cy='{c}' r='{R - 5}' fill='none' stroke='{GOLD}' stroke-width='0.8' stroke-opacity='0.6'/>"]
    # faint khatam rose
    out.append(f"<polygon points='{_pts(star_points(c, c, 46, rot=0))}' fill='none' stroke='{TURQUOISE}' "
               f"stroke-width='1' stroke-opacity='0.55'/>")
    out.append(f"<polygon points='{_pts(star_points(c, c, 46, rot=22.5))}' fill='none' stroke='{TURQUOISE}' "
               f"stroke-width='1' stroke-opacity='0.35'/>")
    for deg in range(0, 360, 15):
        L = 9 if deg % 90 == 0 else (6 if deg % 45 == 0 else 3.5)
        a = math.radians(deg - 90)
        x1, y1 = c + (R - 5) * math.cos(a), c + (R - 5) * math.sin(a)
        x2, y2 = c + (R - 5 - L) * math.cos(a), c + (R - 5 - L) * math.sin(a)
        out.append(f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='{GOLD}' stroke-width='{1.6 if L > 5 else 1}'/>")
    for lab, deg in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
        a = math.radians(deg - 90)
        x, y = c + 52 * math.cos(a), c + 52 * math.sin(a) + 5
        col = GOLD if lab == "N" else IVORY
        out.append(f"<text x='{x:.1f}' y='{y:.1f}' text-anchor='middle' font-family='Segoe UI, Helvetica, Arial, sans-serif' "
                   f"font-size='14' font-weight='700' fill='{col}'>{lab}</text>")
    # needle toward the qibla, with a small khatam at the tip; a short muted tail
    b = float(bearing_deg) % 360.0
    if not needle:   # the dial alone (the live compass draws its own arrow on top)
        return _svg(size, size, "".join(out), 160, 160, extra=" role='presentation'")
    out.append(f"<g transform='rotate({b:.2f} {c} {c})'>"
               f"<polygon points='{c},{c + 16} {c - 3.2},{c} {c + 3.2},{c}' fill='{GOLD_DEEP}'/>"
               f"<polygon points='{c},{c - 50} {c - 5.2},{c} {c},{c + 4} {c + 5.2},{c}' fill='{GOLD}' stroke='{NIGHT}' stroke-width='0.8'/>"
               f"{khatam(c, c - 56, 6.2, GOLD, NIGHT, CARNELIAN)}</g>")
    out.append(f"<circle cx='{c}' cy='{c}' r='4.2' fill='{NIGHT}' stroke='{GOLD}' stroke-width='1.6'/>")
    hh = 160
    if caption:
        hh = 184
        out.append(f"<text x='{c}' y='178' text-anchor='middle' font-family='Segoe UI, Helvetica, Arial, sans-serif' "
                   f"font-size='13' fill='{IVORY}'>{caption}</text>")
    return _svg(size, size * hh / 160, "".join(out), 160, hh,
                extra=f" role='img' aria-label='Qibla direction {b:.0f} degrees from north'")


def qibla_arrow_svg(size: int = 160) -> str:
    """A bold gold arrow pointing up (toward the top of the drawing), with a small Kaaba at its tip.
    Drawn in the same 160 x 160 frame as the compass dial, so it can sit on top of it and be turned."""
    c = 80
    kaaba = (f"<rect x='{c - 7}' y='9' width='14' height='13' rx='1.2' fill='{NIGHT}' stroke='{GOLD}' stroke-width='1.4'/>"
             f"<rect x='{c - 7}' y='12.2' width='14' height='2.4' fill='{GOLD}'/>")
    arrow = (f"<polygon points='{c},25 {c - 13},50 {c - 5},48 {c - 5},{c + 30} {c + 5},{c + 30} {c + 5},48 {c + 13},50' "
             f"fill='{GOLD}' stroke='{NIGHT}' stroke-width='1.4' stroke-linejoin='round'/>"
             f"<polygon points='{c},25 {c},{c + 30} {c + 5},{c + 30} {c + 5},48 {c + 13},50' fill='{GOLD_DEEP}' opacity='0.55'/>")
    hub = f"<circle cx='{c}' cy='{c}' r='6' fill='{NIGHT}' stroke='{GOLD}' stroke-width='2'/>"
    return _svg(size, size, kaaba + arrow + hub, 160, 160, extra=" role='presentation'")


# --------------------------------------------------------------------------------------------- the Moon
def moon_body(cx, cy, r, illum, waxing=True, tilt=0.0, lit=NACRE, dark=EARTHSHINE, rim=None,
              dark_opacity=1.0) -> str:
    """The Moon's disc: the dark part (earthshine) and the lit part. illum 0..1 is the lit fraction.
    waxing=True puts the lit limb on the right (as seen from the northern hemisphere, Moon upright);
    tilt turns the lit limb clockwise by that many degrees (e.g. toward the set Sun)."""
    k = min(max(float(illum), 0.0), 1.0)
    out = [f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{r:.2f}' fill='{dark}' fill-opacity='{dark_opacity:g}'/>"]
    if k > 0.003:
        rx = r * abs(1 - 2 * k)
        sweep = 0 if k < 0.5 else 1
        d = (f"M{cx:.2f},{cy - r:.2f} A{r:.2f},{r:.2f} 0 0 1 {cx:.2f},{cy + r:.2f} "
             f"A{rx:.2f},{r:.2f} 0 0 {sweep} {cx:.2f},{cy - r:.2f} Z")
        tf = f"rotate({tilt:.2f} {cx:.2f} {cy:.2f})"
        if not waxing:
            tf += f" translate({2 * cx:.2f} 0) scale(-1 1)"
        out.append(f"<path d='{d}' fill='{lit}' transform='{tf}'/>")
    if rim:
        out.append(f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{r:.2f}' fill='none' stroke='{rim}' stroke-width='{max(r * 0.04, 0.6):.2f}'/>")
    return "".join(out)


def moon_phase_svg(illum: float, waxing: bool = True, size: int = 40, tilt: float = 0.0,
                   lit: str = NACRE, dark: str = EARTHSHINE, rim: str | None = "#5b6a94") -> str:
    """The Moon as it looks: lit fraction illum (0..1), lit limb right when waxing."""
    pct = round(100 * min(max(illum, 0.0), 1.0))
    return _svg(size, size, moon_body(50, 50, 46, illum, waxing, tilt, lit, dark, rim), 100, 100,
                extra=f" role='img' aria-label='Moon {pct}% lit, {'waxing' if waxing else 'waning'}'")


# --------------------------------------------------------------------------------------------- app icon
def icon_svg(size: int = 512, maskable: bool = False, rounded: bool = False) -> str:
    """The app icon: the young (waxing) crescent Moon in an evening sky above a horseshoe-arched mihrab with
    an eight-pointed star, on a band of tesserae. A sibling of Sky Luach's capital-under-the-Moon icon.
    maskable=True shrinks the art into the central circle of radius 40% (the safe zone) on a flat field."""
    S = 512
    out = []
    bg = NIGHT
    if rounded:
        out.append(f"<rect width='{S}' height='{S}' rx='96' fill='{bg}'/>")
    else:
        out.append(f"<rect width='{S}' height='{S}' fill='{bg}'/>")
    defs = ("<defs><radialGradient id='glow' cx='0.5' cy='0.5' r='0.5'>"
            f"<stop offset='0' stop-color='{LAPIS}' stop-opacity='0.95'/>"
            f"<stop offset='0.55' stop-color='{LAPIS}' stop-opacity='0.45'/>"
            f"<stop offset='1' stop-color='{LAPIS}' stop-opacity='0'/></radialGradient></defs>")
    art = []
    glow = "<circle cx='256' cy='150' r='235' fill='url(#glow)'/>"
    if not maskable:
        art.append(glow)
    art.append(moon_body(256, 98, 54, 0.17, True, 38, NACRE, "#3a5294", dark_opacity=0.55))
    # mihrab: horseshoe arch, voussoirs, columns, star
    art.append(mihrab(256 - 33 * 3.75, 172, 3.75))
    # tesserae row
    cols = [GREEN_LIGHT, TURQUOISE, CARNELIAN, GOLD, CARNELIAN, TURQUOISE, GREEN_LIGHT]
    for k, col in enumerate(cols):
        x = 256 + (k - 3) * 34
        art.append(f"<rect x='{x - 8}' y='{482 - 8}' width='16' height='16' fill='{col}' transform='rotate(45 {x} 482)'/>")
    body = "".join(art)
    if maskable:
        sc = 0.70
        body = f"<g transform='translate({256 * (1 - sc):.2f} {256 * (1 - sc) + 8:.2f}) scale({sc})'>{body}</g>"
        # a smaller glow that fades out well inside the safe circle (radius 0.4 * 512 = 204.8)
        body = "<circle cx='256' cy='232' r='160' fill='url(#glow)'/>" + body
    return _svg(size, size, defs + "".join(out) + body, S, S)


def icon_small_svg(size: int = 32) -> str:
    """A simpler drawing of the icon for 16-48 px (favicon, small ICO sizes): a plain gold horseshoe arch,
    a large eight-pointed star in the niche and the young crescent in the corner of the sky."""
    S = 512
    out = [f"<rect width='{S}' height='{S}' fill='{NIGHT}'/>",
           "<defs><radialGradient id='glow2' cx='0.5' cy='0.5' r='0.5'>"
           f"<stop offset='0' stop-color='{LAPIS}' stop-opacity='0.9'/>"
           f"<stop offset='1' stop-color='{LAPIS}' stop-opacity='0'/></radialGradient></defs>",
           "<circle cx='256' cy='170' r='300' fill='url(#glow2)'/>"]
    s = 5.4
    x0, y0 = 256 - 33 * s, 66
    cx, cy, r = 256, y0 + 31 * s, 23.25 * s
    d = math.radians(24)
    xl, xr, ys = cx - r * math.cos(d), cx + r * math.cos(d), cy + r * math.sin(d)
    base = y0 + 74 * s
    out.append(f"<path d='M{xl:.1f},{base:.1f} L{xl:.1f},{ys:.1f} A{r:.1f},{r:.1f} 0 1 1 {xr:.1f},{ys:.1f} "
               f"L{xr:.1f},{base:.1f} Z' fill='{CARD}'/>")
    out.append(f"<path d='M{xl:.1f},{base:.1f} L{xl:.1f},{ys:.1f} A{r:.1f},{r:.1f} 0 1 1 {xr:.1f},{ys:.1f} "
               f"L{xr:.1f},{base:.1f}' fill='none' stroke='{GOLD}' stroke-width='{7.5 * s:.1f}'/>")
    out.append(f"<rect x='{x0 + 2 * s:.1f}' y='{base - 6:.1f}' width='{62 * s:.1f}' height='34' fill='{GOLD}'/>")
    out.append(khatam(cx, cy + 12 * s, 15.5 * s, GOLD, NIGHT, CARNELIAN))
    out.append(moon_body(438, 74, 52, 0.2, True, 38, NACRE, "#3a5294", dark_opacity=0.0))
    return _svg(size, size, "".join(out), S, S)


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
