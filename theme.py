"""Colours, fonts and ornament for a theme drawn from early Islamic art (Umayyad and Abbasid, 7th-9th c.).

Palette: the glass mosaics of the Dome of the Rock (691-692) and the Great Mosque of Damascus (706-715): gold
tesserae, mosaic greens, blue glass and mother-of-pearl; carnelian red for the 'jewels'; turquoise as in the
turquoise-glazed jars of the 8th-9th centuries; gold on deep blue as in the Blue Qur'an. The night-sky ground
is a deep lapis. Ornaments (khatam star, interlace frieze, mihrab arch, vine scroll, Samarra bevel): see
ornaments.py. Geometric and vegetal only; no figurative imagery and no star-and-crescent emblem.
The Sunni and Shia badges are styled alike on purpose: the app does not rank one tradition above the other.

Every text colour has at least 7:1 contrast (WCAG AAA) on its background:
  text colour              BG        CARD     SIDEBAR   FRIDAY_BG  RAMADAN_BG
  TEXT   #f6efdc      15.8:1      13.6:1      15.0:1      12.0:1      13.1:1
  MUTED  #d9d2bd      12.0:1      10.3:1      11.4:1       9.1:1       9.9:1
  GOLD   #ebc25f      10.7:1       9.2:1      10.2:1       8.1:1       8.9:1
  LINK   #9fdcec      12.0:1      10.3:1      11.4:1       9.1:1      10.0:1
  OBS    #bfe3a6      12.8:1      11.0:1      12.1:1       9.7:1      10.6:1
  chips (INK #0b1430 on pastel): eid 11.8, sacred 11.6, fast 12.7, night 11.6, mourning 11.0, birth 12.8, month 12.4, hajj 11.7, civil 13.8
  INK on GOLD (30-year cycle, leap year): 10.7:1
  white on LAPIS (buttons): 8.0:1
  white on #244489 (button hover): 9.3:1
  white on CARNELIAN_DEEP: 8.2:1
  lowest of all: 8.0:1 (all >= 7:1).
"""
import base64
import html
import os

import streamlit as st

import ornaments as orn

HERE = os.path.dirname(os.path.abspath(__file__))

BG = "#0b1430"          # night lapis
CARD = "#14214a"        # deep blue glass panel
SIDEBAR = "#0f1938"
FRIDAY_BG = "#0e3329"   # mosaic green (Friday, al-Jumu'ah)
RAMADAN_BG = "#1f2152"  # indigo night (days of Ramadan)
TEXT = "#f6efdc"        # ivory / mother-of-pearl
MUTED = "#d9d2bd"
GOLD = "#ebc25f"        # gold tesserae
LINK = "#9fdcec"        # pale turquoise-blue
OBS = "#bfe3a6"         # pale mosaic green: what is seen (sightings)
INK = "#0b1430"         # dark ink for chips
GREEN = "#2e7d5b"       # mosaic green (borders, ornament)
LAPIS = "#2a4d9b"       # ultramarine glass (buttons: white text)
TURQUOISE = "#3fb8af"   # borders, ornament
CARNELIAN = "#b5412c"   # accent (ornament, voussoirs)
CARNELIAN_DEEP = "#8e2f1f"  # carnelian that carries white text
NACRE = "#efe9f4"       # mother-of-pearl (the lit Moon)
GOLD_DEEP = "#a8792a"   # gold in shade (rules, bevel)

# Holiday kinds shared with holidays.py: dark ink on pastel chips.
CHIP = {
    "eid": "#efcd6e", "sacred": "#bccff5", "fast": "#e4d7b2", "night": "#d0caf0", "mourning": "#c5c9d3",
    "birth": "#bfe3b4", "month": "#a9e0d8", "hajj": "#f2c6b0", "civil": "#e9e0c9",
}
KIND_LABEL = {
    "eid": "Eid (festival)", "sacred": "Holy day", "fast": "Fast", "night": "Holy night",
    "mourning": "Day of mourning", "birth": "Birth (mawlid)", "month": "New month", "hajj": "Days of the Hajj",
    "civil": "Solar Hijri day",
}
KIND_AR = {
    "eid": "عيد", "sacred": "مناسبة دينية", "fast": "صيام", "night": "ليلة مباركة", "mourning": "عزاء",
    "birth": "مولد", "month": "غرة الشهر", "hajj": "أيام الحج", "civil": "التقويم الشمسي",
}
BRANCH_LABEL = {"sunni": ("Sunni", "سنّي"), "shia": ("Shia", "شيعي")}

FONT_KUFI = "NotoKufiArabic-Bold-sub.woff2"
FONT_NASKH = "NotoNaskhArabic-Regular-sub.woff2"
ARABIC_RANGE = "U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F"


def _font_face() -> str:
    """Embed the two subset Arabic fonts (assets/fonts, about 24 kB together) as data URIs. If a file is
    missing the stacks below fall back to the system's Arabic fonts."""
    out = []
    for family, fname, weight in (("TaqwimKufi", FONT_KUFI, 700), ("TaqwimNaskh", FONT_NASKH, 400)):
        path = os.path.join(HERE, "assets", "fonts", fname)
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
        except OSError:
            continue
        out.append(f"@font-face {{ font-family: '{family}'; src: url(data:font/woff2;base64,{b64}) format('woff2'); "
                   f"font-weight: {weight}; font-style: normal; font-display: swap; unicode-range: {ARABIC_RANGE}; }}")
    return "\n".join(out)


FRIEZE = orn.data_uri(orn.frieze_tile_svg())
STAR = orn.data_uri(orn.khatam_svg(40))
STAR_INK = orn.data_uri(orn.khatam_svg(40, color=INK, center=CARNELIAN, line=GOLD))

SERIF = "'Palatino Linotype', Palatino, 'Book Antiqua', Georgia, 'Times New Roman', serif"
ARAB = "'TaqwimNaskh', 'Noto Naskh Arabic', 'Amiri', 'Traditional Arabic', 'Segoe UI', 'Tahoma', sans-serif"
KUFI = "'TaqwimKufi', 'Noto Kufi Arabic', " + ARAB

CSS = f"""
<style>
{_font_face()}
.block-container, [data-testid="stMainBlockContainer"] {{ padding-top: 4.6rem; }}
[data-testid="stAppViewContainer"] {{ background:
   radial-gradient(ellipse at 50% -10%, rgba(42,77,155,.38), rgba(0,0,0,0) 58%), {BG}; }}
[data-testid="stSidebar"] {{ background: {SIDEBAR}; border-right: 1px solid rgba(235,194,95,.30); }}
h1, h2, h3, h4 {{ font-family: {SERIF}; color: {GOLD}; }}
.tq-head {{ display:flex; align-items:center; gap: 14px; margin: .4rem 0 .2rem 0; }}
.tq-head svg {{ flex: 0 0 auto; }}
.tq-title {{ font-family: {SERIF}; font-size: 2.05rem; font-weight: 700; color: {GOLD}; line-height:1.15; }}
.tq-kufi {{ font-family: {KUFI}; font-weight: 700; color: {GOLD}; direction: rtl; unicode-bidi: isolate;
           font-size: 1.75rem; letter-spacing: 0; margin-left: .35rem; }}
.tq-sub {{ color: {MUTED}; margin-bottom: 0.4rem; font-size: .95rem; }}
.tq-frieze {{ height: 34px; background-image: url("{FRIEZE}"); background-repeat: repeat-x;
             background-size: auto 34px; margin: .25rem 0 .7rem 0; opacity: .95; }}
.tq-ar, .tq-ar-big {{ font-family: {ARAB}; direction: rtl; unicode-bidi: isolate; line-height: 1.5; }}
.tq-ar {{ color: {GOLD}; font-size: 1.08em; }}
.tq-ar-big {{ font-size: 1.5rem; color: {GOLD}; }}
.tq-card {{ background: {CARD}; border: 1px solid {GOLD_DEEP}; outline: 1px solid rgba(235,194,95,.35);
           outline-offset: -5px; border-radius: 4px; padding: .95rem 1.15rem; margin-bottom: .8rem; color: {TEXT}; }}
.tq-card h3 {{ font-family: {SERIF}; color: {GOLD}; margin: 0 0 .4rem 0; font-size: 1.08rem; font-weight: 700;
              padding-left: 27px; background: url("{STAR}") no-repeat left center; background-size: 19px 19px; }}
.tq-card h3 .tq-ar {{ font-size: 1.1rem; }}
.tq-big {{ font-family: {SERIF}; font-size: 1.55rem; font-weight: 700; color: {TEXT}; line-height: 1.25; }}
.tq-big .tq-ar {{ font-size: 1.35rem; }}
.tq-muted {{ color: {MUTED}; font-size: .92rem; }}
.tq-obs {{ color: {OBS}; }}
.tq-grid {{ width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }}
.tq-grid th {{ font-family: {SERIF}; color: {GOLD}; font-weight: 700; font-size: .9rem; padding: 2px 4px; text-align: left;
              border-bottom: 2px solid {GOLD_DEEP}; }}
.tq-grid th .tq-ar {{ font-size: .95rem; }}
.tq-grid td {{ background: {CARD}; border-radius: 3px; vertical-align: top; padding: 5px 6px;
              height: 108px; color: {TEXT}; border: 1px solid rgba(168,121,42,.55); }}
.tq-grid td.tq-empty {{ background: transparent; border: none; }}
.tq-grid td.tq-fri {{ background: {FRIDAY_BG}; border-color: rgba(95,174,126,.85); }}
.tq-grid td.tq-ram {{ background: {RAMADAN_BG}; box-shadow: inset 0 3px 0 rgba(235,194,95,.75); }}
.tq-grid td.tq-fri.tq-ram {{ background: {FRIDAY_BG}; }}
.tq-grid td.tq-today {{ border: 2px solid {GOLD}; }}
.tq-civ {{ font-weight: 700; font-size: 1.05rem; color: {TEXT}; }}
.tq-civm {{ font-size: .78rem; color: {MUTED}; margin-left: 3px; }}
.tq-hd {{ float: right; text-align: right; font-family: {ARAB}; font-size: 1.08rem; color: {GOLD}; line-height: 1.2; }}
.tq-hd small {{ color: {MUTED}; font-size: .74rem; font-family: {SERIF}; display: block; }}
.tq-other {{ font-size: .74rem; color: {OBS}; display: block; margin-top: 1px; }}
.tq-chip {{ display: inline-block; color: {INK}; border-radius: 3px; padding: 1px 6px; margin: 2px 2px 0 0;
           font-size: .76rem; font-weight: 600; line-height: 1.45; border: 1px solid rgba(11,20,48,.35); }}
.tq-chip .tq-ar {{ color: {INK}; font-weight: 600; font-size: .95rem; line-height: 1.2; }}
.tq-line {{ font-size: .76rem; color: {MUTED}; display: block; margin-top: 2px; }}
.tq-line b {{ color: {TEXT}; }}
.tq-line .tq-ar {{ font-size: .88rem; }}
.tq-list {{ width: 100%; border-collapse: collapse; }}
.tq-list td {{ border-bottom: 1px solid rgba(168,121,42,.45); padding: 7px 4px; vertical-align: top; color: {TEXT}; }}
.tq-list td.tq-fri {{ background: {FRIDAY_BG}; }}
.tq-list td.tq-ram {{ background: {RAMADAN_BG}; }}
.tq-list td.tq-today {{ outline: 2px solid {GOLD}; }}
.tq-legend span {{ margin-right: 6px; }}
.tq-table {{ width: 100%; border-collapse: collapse; font-size: .93rem; }}
.tq-table th {{ font-family: {SERIF}; color: {GOLD}; text-align: left; border-bottom: 2px solid {GOLD_DEEP}; padding: 5px 6px; }}
.tq-table td {{ color: {TEXT}; border-bottom: 1px solid rgba(168,121,42,.40); padding: 5px 6px; vertical-align: top; }}
.tq-table td.tq-diff {{ color: {GOLD}; font-weight: 700; }}
.tq-cycle {{ display: inline-block; width: 2.1rem; height: 2.1rem; line-height: 2.1rem; text-align: center;
            border-radius: 50%; margin: 2px; font-weight: 700; font-size: .9rem; }}
.tq-cycle.leap {{ background: {GOLD}; color: {INK}; }}
.tq-cycle.common {{ background: {CARD}; color: {TEXT}; border: 1px solid {GOLD_DEEP}; }}
.tq-cycle.now {{ outline: 3px solid {LINK}; outline-offset: 2px; }}
.tq-pop {{ display: inline-block; position: relative; vertical-align: top; }}
.tq-pop > summary {{ list-style: none; cursor: pointer; display: inline; }}
.tq-pop > summary::-webkit-details-marker {{ display: none; }}
.tq-pop > summary .tq-chip {{ text-decoration: underline dotted rgba(11,20,48,.6); text-underline-offset: 2px; }}
.tq-pop[open] > summary .tq-chip {{ outline: 2px solid {GOLD}; }}
.tq-popbody {{ position: absolute; z-index: 1000; left: 0; top: calc(100% + 4px); width: 340px; max-width: 80vw;
              background: {CARD}; color: {TEXT}; border: 1px solid {GOLD}; border-radius: 6px; padding: .7rem .85rem;
              box-shadow: 0 8px 24px rgba(0,0,0,.65); font-size: .86rem; line-height: 1.45; text-align: left;
              white-space: normal; font-weight: 400; }}
.tq-pop-r .tq-popbody {{ left: auto; right: 0; }}
.tq-pop-title {{ font-family: {SERIF}; color: {GOLD}; font-weight: 700; font-size: 1rem; margin-bottom: .3rem; }}
.tq-pop-text {{ color: {TEXT}; }}
.tq-pop-src {{ color: {MUTED}; font-size: .78rem; margin-top: .45rem; font-style: italic; }}
.tq-branch {{ display: inline-flex; align-items: center; gap: .4rem; background: {CARD}; color: {TEXT};
             border: 1px solid {GOLD}; border-radius: 999px; padding: .12rem .7rem .12rem .45rem;
             font-family: {SERIF}; font-size: .9rem; font-weight: 700; vertical-align: middle; }}
.tq-branch::before {{ content: ""; width: 15px; height: 15px; background: url("{STAR}") no-repeat center;
                     background-size: 15px 15px; }}
.tq-branch .tq-ar {{ font-weight: 400; }}
.tq-qibla {{ display: flex; flex-wrap: wrap; align-items: center; gap: .6rem 1.1rem; background: {CARD};
            border: 1px solid {GOLD_DEEP}; border-radius: 6px; padding: .7rem .9rem; color: {TEXT}; }}
.tq-qibla svg {{ flex: 0 0 auto; max-width: 100%; height: auto; }}
.tq-qibla-deg {{ font-family: {SERIF}; font-size: 1.7rem; font-weight: 700; color: {GOLD}; line-height: 1.1; }}
.tq-qibla-text {{ color: {MUTED}; font-size: .9rem; }}
.tq-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; max-height: 70vh; overflow-y: auto;
              border: 1px solid {GOLD_DEEP}; border-radius: 6px; background: {CARD}; }}
.tq-times {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.tq-times th {{ position: sticky; top: 0; background: {SIDEBAR}; color: {GOLD}; z-index: 1; }}
.tq-times th, .tq-times td {{ padding: .3rem .55rem; text-align: left; border-bottom: 1px solid rgba(235,194,95,.18); color: {TEXT}; }}
.tq-times tr.tq-today-row td {{ background: #24356c; color: #ffffff; font-weight: 700; }}
.tq-moon {{ display: inline-block; vertical-align: middle; line-height: 0; }}
a {{ color: {LINK}; }}
@media (pointer: coarse) {{
  .tq-grid td {{ height: auto; min-height: 80px; }}
  div[data-testid="stRadio"] label {{ padding: 6px 4px; }}
  button {{ min-height: 44px; }}
}}
@media (max-width: 640px) {{
  .tq-popbody {{ position: static; width: auto; max-width: none; margin-top: 4px; }}
  .tq-title {{ font-size: 1.5rem; }} .tq-kufi {{ font-size: 1.3rem; }}
  .tq-big {{ font-size: 1.28rem; }}
  .tq-head svg {{ width: 48px; height: 58px; }}
  .tq-grid td {{ padding: 3px 3px; }}
  .tq-hd {{ font-size: .95rem; }}
}}
</style>
"""

# The location button (locator.py: use as its component CSS). Both class prefixes are styled, so the button
# looks right whether the component's JavaScript names its elements tq-loc-* or keeps Sky Luach's sl-loc-*.
_PIN = orn.data_uri(orn.khatam_svg(32, color=GOLD, center="#ffffff", line=LAPIS))
LOCATOR_CSS = f"""
.tq-loc, .sl-loc {{ display:flex; flex-wrap:wrap; align-items:center; gap:.5rem .8rem; margin:.1rem 0 .5rem 0;
          font-family: {SERIF}; }}
.tq-loc-btn, .sl-loc-btn {{ background:{LAPIS}; color:#ffffff; border:1px solid {GOLD}; border-radius:6px;
              padding:.35rem .8rem .35rem 2rem; font-weight:700; font-size:.92rem; cursor:pointer; min-height:36px;
              background-image:url("{_PIN}"); background-repeat:no-repeat; background-position:.55rem center;
              background-size:16px 16px; }}
.tq-loc-btn:hover, .sl-loc-btn:hover {{ background-color:#244489; }}
.tq-loc-btn:focus-visible, .sl-loc-btn:focus-visible {{ outline:2px solid {GOLD}; outline-offset:2px; }}
.tq-loc-place, .sl-loc-place {{ color:{TEXT}; font-size:.95rem; }}
.tq-loc-status, .sl-loc-status {{ color:{MUTED}; font-size:.88rem; }}
.tq-loc-status a, .sl-loc-status a {{ color:{LINK}; }}
@media (pointer: coarse) {{ .tq-loc-btn, .sl-loc-btn {{ min-height:44px; }} }}
"""


# The live qibla compass (qibla_live.py: its component CSS).
QIBLA_LIVE_CSS = f"""
.tq-ql-wrap {{ position: relative; padding-top: 14px; flex: 0 0 auto; }}
.tq-ql-lubber {{ position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 0; height: 0;
                border-left: 9px solid transparent; border-right: 9px solid transparent; border-top: 13px solid {CARNELIAN}; }}
.tq-ql-stage {{ position: relative; border-radius: 50%; transition: box-shadow .25s; }}
.tq-ql-stage.tq-ql-on {{ box-shadow: 0 0 0 4px {OBS}, 0 0 18px 4px rgba(191,227,166,.55); }}
.tq-ql-dial, .tq-ql-arrow {{ position: absolute; inset: 0; will-change: transform; transform-origin: 50% 50%; }}
.tq-ql-dial svg, .tq-ql-arrow svg {{ width: 100% !important; height: 100% !important; max-width: none !important; display: block; }}
.tq-ql-info {{ flex: 1 1 13rem; min-width: 12rem; }}
.tq-ql-btn {{ display: none; margin-top: .55rem; background: {LAPIS}; color: #ffffff; border: 1px solid {GOLD};
             border-radius: 6px; padding: .45rem .9rem; font: 700 .95rem {SERIF}; min-height: 44px; cursor: pointer; }}
.tq-ql-btn:focus-visible {{ outline: 2px solid {GOLD}; outline-offset: 2px; }}
.tq-ql-status {{ margin-top: .45rem; color: {TEXT}; font-size: .95rem; font-weight: 600; min-height: 1.3em; }}
.tq-ql-status.tq-ql-good {{ color: {OBS}; }}
.tq-ql-status.tq-ql-warn {{ color: {GOLD}; }}
.tq-ql-tab {{ display: none; margin-top: .4rem; color: {LINK}; font-size: .92rem; }}
"""

# Streamlit's own widgets, text and menus. These rules set the colours directly, so the app reads the same
# (ivory and gold on night lapis) whether the browser, the phone or Streamlit's menu is in light or dark mode,
# and even if .streamlit/config.toml is missing. Every pair here is at least 7:1 (WCAG AAA).
FORCE_CSS = f"""
<style>
:root {{ color-scheme: dark; }}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stBottom"] > div {{ color: {TEXT}; }}
.stApp {{ background-color: {BG}; }}
[data-testid="stHeader"] {{ background: rgba(11,20,48,.92); color: {TEXT}; }}
[data-testid="stHeader"] button, [data-testid="stHeader"] a, [data-testid="stToolbar"] *,
[data-testid="stSidebarCollapseButton"] *, [data-testid="stExpandSidebarButton"] *, [data-testid="stSidebarCollapsedControl"] * {{
  color: {TEXT} !important; fill: currentColor; }}
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {{ background-color: {SIDEBAR} !important; color: {TEXT}; }}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stText"], [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, label, legend,
[data-testid="stRadio"] label, [data-testid="stRadio"] p, [data-testid="stCheckbox"] p, [data-testid="stToggle"] p,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] p {{ color: {TEXT} !important; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stCaption, small,
[data-testid="stWidgetLabel"] [data-testid="stTooltipIcon"] {{ color: {MUTED} !important; }}
[data-testid="stMarkdownContainer"] a, [data-testid="stCaptionContainer"] a {{ color: {LINK} !important; }}
[data-testid="stMarkdownContainer"] code {{ background: {CARD}; color: {GOLD}; }}
h1, h2, h3, h4, h5, h6, [data-testid="stHeading"] * {{ color: {GOLD} !important; }}
/* text boxes, number boxes, select boxes and their menus */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div,
[data-testid="stNumberInputContainer"], [data-testid="stDateInput"] [data-baseweb="input"] {{
  background-color: {CARD} !important; border-color: rgba(235,194,95,.55) !important; color: {TEXT} !important; }}
[data-baseweb="input"] input, [data-baseweb="base-input"] input, textarea, [data-baseweb="select"] input,
[data-baseweb="select"] div, [data-baseweb="select"] span {{ color: {TEXT} !important; -webkit-text-fill-color: {TEXT}; background-color: transparent; }}
input::placeholder, textarea::placeholder {{ color: {MUTED} !important; -webkit-text-fill-color: {MUTED}; opacity: 1; }}
[data-baseweb="select"] svg, [data-testid="stNumberInputContainer"] svg {{ color: {TEXT} !important; fill: currentColor; }}
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] {{ background: {CARD} !important; color: {TEXT} !important; }}
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul, [data-baseweb="menu"], [role="listbox"] {{
  background-color: {CARD} !important; color: {TEXT} !important; border-color: {GOLD_DEEP} !important; }}
[data-baseweb="popover"] li, [role="option"] {{ color: {TEXT} !important; background-color: {CARD}; }}
[data-baseweb="popover"] li:hover, [role="option"]:hover, [role="option"][aria-selected="true"] {{ background-color: #24356c !important; }}
[data-baseweb="tag"] {{ background-color: {LAPIS} !important; color: #ffffff !important; }}
[data-baseweb="tag"] * {{ color: #ffffff !important; }}
[data-baseweb="calendar"], [data-baseweb="calendar"] * {{ background-color: {CARD}; color: {TEXT}; }}
[data-baseweb="tooltip"], [data-baseweb="tooltip"] * {{ background-color: {CARD} !important; color: {TEXT} !important; }}
/* buttons */
[data-testid^="stBaseButton-secondary"], [data-testid="stDownloadButton"] button, .stButton > button {{
  background-color: {CARD} !important; color: {TEXT} !important; border: 1px solid {GOLD} !important; }}
[data-testid^="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button:hover, .stButton > button:hover {{
  background-color: #24356c !important; color: #ffffff !important; }}
[data-testid^="stBaseButton-primary"] {{ background-color: {LAPIS} !important; color: #ffffff !important; border: 1px solid {GOLD} !important; }}
[data-testid^="stBaseButton"] p {{ color: inherit !important; }}
/* radio dots, check boxes and toggles stay visible on the dark ground */
[data-testid="stRadio"] [role="radio"] > div:first-child, [data-baseweb="radio"] > div:first-child {{ border-color: {GOLD} !important; }}
[data-baseweb="checkbox"] [role="checkbox"], [data-baseweb="checkbox"] > div:first-child {{ border-color: {GOLD} !important; }}
/* expanders, tabs, alerts, tables */
[data-testid="stExpander"] details, [data-testid="stExpander"] > details {{ background-color: {CARD} !important;
  border-color: rgba(235,194,95,.45) !important; color: {TEXT} !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: {GOLD} !important; background-color: transparent; }}
[data-testid="stExpander"] summary:hover {{ background-color: #1a2a5a !important; }}
[data-baseweb="tab"], [data-baseweb="tab"] p {{ color: {TEXT} !important; }}
[data-baseweb="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] p {{ color: {GOLD} !important; }}
[data-testid="stAlertContainer"], [data-testid="stAlert"] > div {{ background-color: {CARD} !important; color: {TEXT} !important;
  border: 1px solid {GOLD_DEEP}; }}
[data-testid="stAlertContainer"] *, [data-testid="stAlert"] * {{ color: {TEXT} !important; }}
[data-testid="stTable"] table, [data-testid="stTable"] th, [data-testid="stTable"] td {{ color: {TEXT} !important;
  background-color: {CARD} !important; border-color: rgba(235,194,95,.3) !important; }}
[data-testid="stTable"] th {{ color: {GOLD} !important; }}
[data-testid="stSpinner"], [data-testid="stSpinner"] * {{ color: {TEXT} !important; }}
[data-testid="stToast"] {{ background-color: {CARD} !important; color: {TEXT} !important; }}
hr {{ border-color: rgba(235,194,95,.35) !important; }}
</style>
"""


SUBTITLE = "the Islamic calendar, Sunni and Shia, from NASA JPL astronomy"
TITLE_AR = "تقويم السماء"


def apply():
    st.html(CSS)
    st.html(FORCE_CSS)
    # the components' stylesheets, page-wide as well (their own css= was not applied on Streamlit Cloud)
    st.html("<style>" + QIBLA_LIVE_CSS + LOCATOR_CSS + "</style>")


def branch_badge(branch: str) -> str:
    """A small badge showing which tradition the app is following ('sunni' or 'shia')."""
    en, ar = BRANCH_LABEL.get(branch, BRANCH_LABEL["sunni"])
    return (f"<span class='tq-branch tq-branch-{html.escape(branch)}' title='Calendar, sighting rule and holidays "
            f"follow {en} practice'>{en} <span class='tq-ar' lang='ar' dir='rtl'>{ar}</span></span>")


def header(subtitle: str = "", branch: str | None = None):
    arch = orn.mihrab_svg(56, 68)
    sub = html.escape(subtitle or SUBTITLE)
    badge = f" {branch_badge(branch)}" if branch else ""
    st.html(f"<div class='tq-head'>{arch}<div><div class='tq-title'>Sky Taqwim "
            f"<span class='tq-kufi' lang='ar' dir='rtl' title='Taqwim al-Sama: the calendar of the sky'>{TITLE_AR}</span>"
            f"</div><div class='tq-sub'>{sub}{badge}</div></div></div>"
            f"<div class='tq-frieze' role='presentation'></div>")


def chip(kind: str, text: str, ar: str = "") -> str:
    inner = html.escape(text)
    if ar:
        inner += f" <span class='tq-ar' lang='ar' dir='rtl'>{html.escape(ar)}</span>"
    return f"<span class='tq-chip' style='background:{CHIP.get(kind, '#e9e0c9')}'>{inner}</span>"


def legend(kinds=None) -> str:
    """Chips for the given kinds (all kinds if None), in the order of KIND_LABEL."""
    ks = [k for k in KIND_LABEL if kinds is None or k in kinds]
    return "<div class='tq-legend'>" + "".join(chip(k, KIND_LABEL[k], KIND_AR.get(k, "")) for k in ks) + "</div>"


def moon(illum: float, waxing: bool, size: int = 22, tilt: float = 0.0) -> str:
    """The Moon's phase as a small inline picture."""
    return f"<span class='tq-moon'>{orn.moon_phase_svg(illum, waxing, size, tilt)}</span>"


def qibla_box(bearing_deg: float, place: str = "", distance_km: float | None = None, size: int = 150) -> str:
    """The qibla compass with its bearing in words. bearing_deg: degrees clockwise from true north."""
    b = float(bearing_deg) % 360.0
    pts = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
    word = pts[int((b + 22.5) // 45) % 8]
    where = f" from {html.escape(place)}" if place else ""
    dist = f"<div class='tq-qibla-text'>Mecca is {distance_km:,.0f} km away (great-circle).</div>" if distance_km else ""
    return (f"<div class='tq-qibla'>{orn.qibla_compass_svg(b, size)}<div>"
            f"<div class='tq-qibla-deg'>{b:.1f}° <span class='tq-ar' lang='ar' dir='rtl'>القبلة</span></div>"
            f"<div class='tq-qibla-text'>Qibla{where}: {b:.1f}° from true north, toward the {word}.</div>{dist}"
            f"<div class='tq-qibla-text'>A magnetic compass differs from true north by the local declination.</div>"
            f"</div></div>")
