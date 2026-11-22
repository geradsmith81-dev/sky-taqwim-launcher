# Sky Taqwim · design notes

Design track: `theme.py`, `ornaments.py`, fonts, icons, the phone launcher and the Streamlit theme files.
The theme is drawn from **early Islamic art, Umayyad and Abbasid (7th-9th centuries)**: art made before the later
dynastic and sectarian styles, and shared by Sunni and Shia Muslims alike. Ornament is **geometric and vegetal
only**. Nothing is copied from photographs: every motif is drawn from simple geometry in `ornaments.py`.

Previews (rendered from the SVG with resvg, using the embedded fonts):
`previews/ornament_sheet.png`, `previews/mock_month_cell_and_card.png`, `previews/icons_512_and_maskable.png`,
`previews/icons_small.png`.

## 1. Motifs and their sources

| Motif (function) | Where it comes from | Sources |
|---|---|---|
| Eight-pointed star, *khatam* (`khatam_svg`, `khatam`, `star_points`) | Two squares, one turned 45 degrees. The plan of the **Dome of the Rock** (Jerusalem, 691-692) is set out from two such squares inside a circle, which give its octagon. Eight-fold stars and octagons recur in Umayyad floor mosaics and in the marble window grilles of the **Great Mosque of Damascus** (706-715). Used as the card-heading mark, the badge mark and the tip of the qibla needle. | Creswell, *Early Muslim Architecture* I (2nd ed., 1969), on the Dome of the Rock plan; Grabar, *The Shape of the Holy* (1996); Bonner, *Islamic Geometric Patterns* (2017). |
| Interlace frieze (`frieze_tile_svg`) | A two-strand interlace (guilloche) passing over and under in turn, with small stars in its loops, over a band of coloured tesserae. The Damascus window grilles are the earliest surviving geometric interlace in Islamic architecture; guilloche and jewelled bands frame the Dome of the Rock mosaics. **Note:** girih strapwork proper (the Persian "knot" patterns) is later, from about 1000 CE, so the frieze is called interlace, not girih. | Flood, *The Great Mosque of Damascus* (2001); Ettinghausen, Grabar and Jenkins-Madina, *Islamic Art and Architecture 650-1250* (2001). |
| Mihrab arch (`mihrab_svg`, `mihrab`) | A horseshoe arch (the circle continues below its centre line) on two columns, with voussoirs in two colours. Horseshoe arches appear in Umayyad Syria (Damascus) and become the hallmark of the **Great Mosque of Cordoba** (begun 785), whose voussoirs alternate red brick and pale stone. The concave mihrab niche itself goes back to al-Walid I's rebuilding of the Prophet's Mosque at Medina (c. 707-709). Used in the header and the icon. | Creswell (1969); Ettinghausen et al. (2001); Dodds (ed.), *Al-Andalus* (1992). |
| Vine scroll (`vine_scroll_svg`) | A running vine with three-lobed leaves, tendrils and grapes: the vine and acanthus scrolls of the Dome of the Rock mosaics, the vine frieze (*karma*) of the Damascus prayer hall, and the carved facade of **Mshatta** (c. 743-744, now in Berlin). Only the vegetal parts are drawn; the animals that appear among the vines on part of the Mshatta facade are left out. | Grabar (1996); Ettinghausen et al. (2001). |
| Samarra bevel (`samarra_bevel_svg`, `samarra_band_svg`) | Mirrored "trumpet" forms ending in spirals, with a lancet between: the **bevelled** ("slant-cut", mould-made) stucco of Abbasid **Samarra** (c. 836-892), Herzfeld's Style C. Motif and ground are not separated; the bevel is shown by a darker copy set slightly below each face. The style spread to the Mosque of Ibn Tulun in Cairo (876-879). | Herzfeld, *Der Wandschmuck der Bauten von Samarra und seine Ornamentik* (1923); Northedge, *The Historical Topography of Samarra* (2005); Ettinghausen et al. (2001). |
| Eight-lobed rosette (`rosette_svg`) | Rosettes and jewelled motifs among the Dome of the Rock mosaics. | Grabar (1996). |
| Kufic title (Noto Kufi Arabic) | The title تقويم السماء is set in a Kufi typeface, recalling the angular script of the earliest dated Islamic monumental inscription: the 240 m mosaic band inside the Dome of the Rock (dated 72 AH / 691-692), gold on blue-green. **Noto Kufi Arabic is a modern typeface in the Kufi manner, not a reconstruction** of 7th-century letter forms. | Blair, *Islamic Inscriptions* (1998) and *Islamic Calligraphy* (2006); Milwright, *The Dome of the Rock and its Umayyad Mosaic Inscriptions* (2016). |
| Qibla compass (`qibla_compass_svg`) | A compass card with an eight-pointed rose (two squares again), N/E/S/W, and a gold needle toward the qibla ending in a small khatam. No picture of the Kaaba. | - |
| The Moon (`moon_phase_svg`, `moon_body`) | Drawn **only as the astronomical Moon**: lit part plus the dark part in earthshine, with an optional tilt so the lit limb can face the Sun. In the icon it is the young waxing crescent (*hilal*) of the first evening of a month, lit side down toward the set Sun. | - |

**Why there is no star-and-crescent.** A star and a crescent appear as separate marks in the margins of Sasanian
coins, and the Arab-Sasanian silver of the first Islamic decades kept them; Abd al-Malik's reform (gold 77 AH / 696-697, silver 79 AH / 698-699) replaced images with text. Their use as
an emblem of Islam is modern: an Ottoman decree of 1793 gave the navy a red flag with a white star and crescent, and
that design became the Ottoman national flag in 1844. Ottoman prestige then made it read as a sign of Islam in general,
which some Muslims accept and others reject. It belongs to neither branch in the period this theme draws on, so it is
not used.

**Sunni and Shia.** The badge (`branch_badge`) is styled the same for both: the same gold border, the same star mark.
Green and black, which carry meaning in some communities (green for the Prophet's family, black for mourning in
Muharram), are not used to tell the branches apart. The `mourning` chip is a soft ash grey, which suggests mourning
without a black chip that would be hard to read.

## 2. Palette

| Name | Hex | Source |
|---|---|---|
| BG (night lapis) | `#0b1430` | Night sky; the blue grounds of the mosaics |
| CARD | `#14214a` | Deep blue glass; gold-on-blue of the Blue Qur'an (North Africa, probably 9th-10th c.; date debated) |
| SIDEBAR | `#0f1938` | - |
| FRIDAY_BG | `#0e3329` | Dark mosaic green (Damascus) |
| RAMADAN_BG | `#1f2152` | Indigo night, for the nights of Ramadan (optional `tq-ram`) |
| TEXT (ivory, mother-of-pearl) | `#f6efdc` | Mother-of-pearl inlays of the Dome of the Rock mosaics |
| MUTED | `#d9d2bd` | - |
| GOLD | `#ebc25f` | Gold-glass tesserae |
| LINK (pale turquoise-blue) | `#9fdcec` | - |
| OBS (pale mosaic green) | `#bfe3a6` | What is observed (crescent sightings) |
| INK | `#0b1430` | Dark ink for chips |
| GREEN | `#2e7d5b` | Mosaic green (ornament, borders) |
| LAPIS | `#2a4d9b` | Ultramarine glass (buttons, primary colour) |
| TURQUOISE | `#3fb8af` | Turquoise alkaline glazes on Iraqi storage jars of the 8th-9th centuries |
| CARNELIAN | `#b5412c` | Red "jewels" in the mosaics; Cordoba red voussoirs (ornament only) |
| CARNELIAN_DEEP | `#8e2f1f` | Carnelian dark enough to carry white text |
| NACRE | `#efe9f4` | The lit Moon |
| GOLD_DEEP | `#a8792a` | Gold in shade: rules, borders, bevels |

## 3. Contrast (WCAG 2.x; AAA needs 7:1 for normal text)

Computed from the constants in `theme.py` with the WCAG relative-luminance formula.

| Text colour | on BG | on CARD | on SIDEBAR | on FRIDAY_BG | on RAMADAN_BG |
|---|---|---|---|---|---|
| TEXT `#f6efdc` | 15.8:1 | 13.6:1 | 15.0:1 | 12.0:1 | 13.1:1 |
| MUTED `#d9d2bd` | 12.0:1 | 10.3:1 | 11.4:1 | 9.1:1 | 9.9:1 |
| GOLD `#ebc25f` | 10.7:1 | 9.2:1 | 10.2:1 | 8.1:1 | 8.9:1 |
| LINK `#9fdcec` | 12.0:1 | 10.3:1 | 11.4:1 | 9.1:1 | 10.0:1 |
| OBS `#bfe3a6` | 12.8:1 | 11.0:1 | 12.1:1 | 9.7:1 | 10.6:1 |

Holiday chips (INK `#0b1430` on pastel):

| Kind | Label | Chip | Contrast |
|---|---|---|---|
| `eid` | Eid (festival) · عيد | `#efcd6e` | 11.8:1 |
| `sacred` | Holy day · مناسبة دينية | `#bccff5` | 11.6:1 |
| `fast` | Fast · صيام | `#e4d7b2` | 12.7:1 |
| `night` | Holy night · ليلة مباركة | `#d0caf0` | 11.6:1 |
| `mourning` | Day of mourning · عزاء | `#c5c9d3` | 11.0:1 |
| `birth` | Birth (mawlid) · مولد | `#bfe3b4` | 12.8:1 |
| `month` | New month · غرة الشهر | `#a9e0d8` | 12.4:1 |
| `hajj` | Days of the Hajj · أيام الحج | `#f2c6b0` | 11.7:1 |
| `civil` | Solar Hijri day · التقويم الشمسي | `#e9e0c9` | 13.8:1 |

| Other pairs | Contrast |
|---|---|
| INK on GOLD (30-year cycle, leap year) | 10.7:1 |
| white on LAPIS (buttons) | 8.0:1 |
| white on #244489 (button hover) | 9.3:1 |
| white on CARNELIAN_DEEP | 8.2:1 |

Launcher page:

| Pair | Contrast |
|---|---|
| ivory on page (#f6efdc / #0b1430) | 15.8:1 |
| gold title (#ebc25f / #0b1430) | 10.7:1 |
| muted text (#d9d2bd / #0b1430) | 12.0:1 |
| status text (#f6efdc / #14214a) | 13.6:1 |
| white on lapis button (#ffffff / #2a4d9b) | 8.0:1 |
| "not set yet" button (#d9d2bd / #14214a) | 10.3:1 |
| gold summary (#ebc25f / #14214a) | 9.2:1 |
| link (#9fdcec / #0b1430) | 12.0:1 |

Lowest text contrast anywhere in the theme: **8.0:1** (white on the lapis button). Decorative colours (GREEN,
TURQUOISE, CARNELIAN, LAPIS ornament) never carry text.

## 4. Fonts

* **Noto Kufi Arabic** (title, class `tq-kufi`) and **Noto Naskh Arabic** (all other Arabic, `tq-ar`, `tq-hd`), from
  github.com/google/fonts (`ofl/notokufiarabic`, `ofl/notonaskharabic`), SIL Open Font License 1.1. The licence
  texts are in `assets/fonts/NotoKufiArabic_OFL.txt` and `assets/fonts/NotoNaskhArabic_OFL.txt`.
* `tools/build_fonts.py` fixes each variable font at one weight (Kufi 700, Naskh 400) and keeps only the Arabic
  letters, short vowels, Arabic and Persian digits, the Persian letters (پ چ ژ ک گ ی) and Arabic punctuation, with
  every OpenType layout feature (letters still join). Result: `NotoKufiArabic-Bold-sub.woff2` 9,448 bytes,
  `NotoNaskhArabic-Regular-sub.woff2` 14,204 bytes. Both are embedded in the CSS as data URIs with an Arabic
  `unicode-range`, so Latin text keeps the serif. If a file is missing, the stack falls back to
  'Noto Naskh Arabic', 'Amiri', 'Traditional Arabic', 'Segoe UI', 'Tahoma', sans-serif.
* Latin text uses the same serif stack as Sky Luach (Palatino Linotype, Palatino, Book Antiqua, Georgia).
* The whole CSS string, fonts included, is about 54 kB.

## 5. Icons

* `assets/taqwim_icon.png` (512) and `assets/taqwim_icon.ico` (16, 24, 32, 48, 64, 128, 256). The 16-48 px sizes
  use a simpler drawing (`icon_small_svg`: plain gold arch, large star, small crescent) so they stay legible.
* `apple-touch-icon.png` (180), `favicon-32.png`, `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` in
  `assets/` and `launcher/icons/`.
* Motif: the young crescent Moon in an evening sky above a horseshoe-arched mihrab with an eight-pointed star and a
  vine sprig, on a row of tesserae. It is a sibling of Sky Luach's icon (a gold capital under a crescent on a dark-blue
  sky).
* Maskable check (`tools/make_icons.py`): pixels outside the central circle of radius 40% (204.8 px) that differ from
  the background = **0**. The art reaches 188 px from the centre.
* All icons are rendered from the SVG in `ornaments.py` with resvg (`tools/make_icons.py`, needs `resvg-py`; build
  time only, not needed by the app).

## 6. Notes for the integrator (contract)

`theme.py` imports only `streamlit` and `ornaments` (no Arabic-names module), so it works on its own.

* `theme.apply()`; `theme.header(subtitle="", branch=None)`. With `branch="sunni"` or `"shia"` the header shows the
  badge after the subtitle. The default subtitle is "the Islamic calendar, Sunni and Shia, from NASA JPL astronomy".
* `theme.chip(kind, text, ar="")`, `theme.legend(kinds=None)`; `CHIP`, `KIND_LABEL`, and `KIND_AR` (Arabic kind
  names) cover all nine shared kinds.
* Added: `branch_badge(branch)`, `moon(illum, waxing, size=22, tilt=0)`,
  `qibla_box(bearing_deg, place="", distance_km=None, size=150)`, `BRANCH_LABEL`, `SUBTITLE`, `TITLE_AR`,
  `RAMADAN_BG`, `CARNELIAN_DEEP`, `NACRE`, `GOLD_DEEP`, `FRIEZE`, `STAR`.
* CSS classes: tq-head, tq-title, tq-kufi, tq-sub, tq-frieze, tq-ar, tq-ar-big, tq-card (h3 with the khatam), tq-big,
  tq-muted, tq-obs, tq-grid (th; td; td.tq-empty, td.tq-fri, td.tq-today, td.tq-ram), tq-civ, tq-civm, tq-hd (with an
  optional `<small>` month name under the day number), tq-other, tq-chip, tq-line, tq-list (td.tq-fri, .tq-ram,
  .tq-today), tq-legend, tq-table (td.tq-diff), tq-cycle (.leap .common .now: for the 30-year cycle, `leap` = the 11
  leap years), tq-pop, tq-pop-r, tq-popbody, tq-pop-title, tq-pop-text, tq-pop-src, tq-branch (and tq-branch-sunni,
  tq-branch-shia, styled the same), tq-qibla (tq-qibla-deg, tq-qibla-text), tq-moon.
* **Location button:** pass `theme.LOCATOR_CSS` as the component CSS in `locator.py`. It styles both `tq-loc-*` and
  Sky Luach's `sl-loc-*` class names. It draws a small gold star on the button, so **remove the emoji** from the button
  label in the JavaScript (`'\u{1F4CD} Use my location'` becomes `'Use my location'`). Also rename
  `skyluach-auto-located`, `__skyluachLoc`, `skyluach_locator` and "Open Sky Luach full-screen".
* Page set-up: `st.set_page_config(page_title="Sky Taqwim · تقويم السماء", page_icon=os.path.join(HERE, "assets",
  "taqwim_icon.png"), ...)`; the desktop shortcut uses `assets/taqwim_icon.ico`.
* Streamlit theme: `.streamlit/config.toml` and `config.toml for GitHub (paste).txt` (identical). These use the same
  always-dark trick as Sky Luach: the light slot repeats the dark colours. Primary colour is lapis `#2a4d9b`.
* Ornaments: `data_uri`, `khatam_svg`, `rosette_svg`, `frieze_tile_svg`, `mihrab_svg`, `vine_scroll_svg`,
  `samarra_bevel_svg`, `samarra_band_svg`, `qibla_compass_svg(bearing_deg, size=160, caption="")`,
  `moon_phase_svg(illum, waxing=True, size=40, tilt=0.0, ...)`, `icon_svg`, `icon_small_svg`.
  `moon_phase_svg`: `waxing=True` puts the lit limb on the right (northern-hemisphere view, Moon upright); `tilt`
  turns it clockwise.

## 7. How this was checked

* Contrast: computed from the module constants (table above).
* Rendering: every ornament, both icons and a mock month row and card were rasterised with resvg (`resvg-py`), which
  shapes Arabic with HarfBuzz, so joining and right-to-left order could be checked. Headless browsers were not used.
  The mock is drawn from the theme colours; it is not a browser screenshot of the Streamlit page.
* Streamlit: `apply()`, `header(branch="shia")`, `chip`, `legend`, `branch_badge`, `qibla_box` and `moon` ran in
  Streamlit's AppTest with no exceptions.
* Launcher: the page script was run in QuickJS against stub page objects. With the placeholder address it never
  redirects and the button reads "The app address is not set yet". With a real `https://` address it redirects only
  when opened from the home screen (the template's behaviour).
* Fonts: both subsets cover every character of the title, keep the init/medi/fina/rlig joining features, and are
  static (no variation tables).
* Qibla needles in the preview use computed great-circle bearings (London 119.0°, Delhi 266.6°,
  Jakarta 295.2°).
