# Sky Taqwim engine — API reference

Pure Python, no Streamlit. Every module finds its files relative to its own folder
(`ephem/de440s.bsp`, `data/…`), so the working directory does not matter. Put the engine modules
next to `app.py` (flat layout, as in Sky Luach). Speeds below were measured on the development
machine (8 cores, Windows); first calls include loading the ephemeris (about 0.3 s).

Files: `sky_engine.py`, `hijri_core.py`, `tabular_calendar.py`, `ummalqura_calendar.py`,
`sighting_calendar.py`, `crescent_data.py` (shared crescent-table loader; added),
`solar_hijri_calendar.py`, `prayer_times.py`, `qibla.py`, `data/crescents_mecca.csv.gz` (1.3 MB),
`data/seasons.csv`, `tools/build_tables.py`, `tools/smoke_test.py`, `tools/validate.py`,
`docs/VALIDATION.md`, `docs/validation_results.json`, `requirements.txt`.
`ephem/de440s.bsp` is not included: copy it in (or it is downloaded from JPL on first use).

## Day convention
A civil (Gregorian) date `d` stands for the Islamic day whose **daytime** is `d`; that day began
at the sunset of `d − 1`. The solar Hijri calendar uses civil days (midnight to midnight).

## hijri_core
```python
MONTHS            # [(translit, arabic)] for months 1..12 ("Muharram", "محرم") ...
SOLAR_MONTHS      # [("Farvardin", "فروردین"), ...]
MUHARRAM … DHU_AL_HIJJAH = 1 … 12;  RAMADAN = 9
arabic_digits(n), persian_digits(n), month_name(m, calendar="lunar"), month_ar(m, calendar)

@dataclass(frozen=True) HDate(year, month, day, calendar="lunar")    # calendar "lunar" | "solar"
    .month_name  .month_ar  .era ("AH"/"SH")
    str(h) -> "14 Ramadan 1447 AH";  h.arabic() -> "١٤ رمضان ١٤٤٧ هـ"  (solar: "۲۳ آبان ۱۴۰۵ ه‍.ش.")
@dataclass HMonth(year, month, start: date, length: int, note="", extra={}, calendar="lunar")
    .end  .name  .name_ar  .title ("Ramadan 1447")
class LunarCalendar:       # every calendar below implements this
    kind, label, label_ar, calendar
    first_day, last_day, covers(d), from_gregorian(d) -> HDate|None,
    to_gregorian(y, m, d) -> date|None, month_of(d) -> HMonth|None, get_month(y, m) -> HMonth|None,
    year_months(y) -> [HMonth], years() -> [int] (complete years only), year_length(y) -> int|None,
    months (list of all HMonth, ordered)
```
`HMonth.note` is a plain-English sentence on how the month began, ready to show.

## Calendars
| Class | kind | Covers | Build time |
|---|---|---|---|
| `UmmAlQuraCalendar(source="auto")` — `"auto"`, `"official"`, `"computed"` | `ummalqura` | auto/computed: 14 Jan 1850 – 30 Dec 2149 (1267–1574 AH); official: 1 Aug 1924 – 16 Nov 2077 (1343–1500 AH) | 0.4 s first time (reads the Mecca table), then cached |
| `TabularCalendar(variant="kuwaiti")` — `"kuwaiti"`, `"fatimid"` | `tabular_kuwaiti`, `tabular_fatimid` | 1850–2149 | 0.03 s |
| `SightingCalendar(place=None, criterion="yallop_B", span=None)` | `sighting` | Mecca (place None or Mecca): 1850–2149; other places: `span` (default 3 years before to 3 years after today) | Mecca 0.3 s; other places 0.15 s per year of span (about 0.9 s for the default 7 years), cached per (place, criterion, span) |
| `SolarHijriCalendar(rule="true_noon_52.5")` | `solar_hijri` | 21 Mar 1850 – 20 Mar 2149 (1229–1527 SH) | 0.3 s first time |

**ummalqura_calendar**: `SOURCES` (key → label), `official_table_month(y, m) -> HMonth|None`,
`computed_month(y, m)`, `rule_on(day29) -> (bool, info)`, `UmmAlQuraCalendar.is_official(y, m)`.
`HMonth.extra`: `source` ("official"/"computed"); for computed months also `day29`, `conj_utc`,
`sunset_utc`, `moonset_utc`, `lag_min`, `conj_before_sunset`, `moon_sets_after_sun`, `rule_met`
(these describe the 29th day of the month *before*, which decided this month's start).

**tabular_calendar**: `VARIANTS` (label, label_ar, leaps, epoch), `is_leap(y, variant)`,
`month_length(y, m, variant)`, `to_ordinal(y, m, d, variant)` (no range limit),
`TabularCalendar.is_leap(y)`. `extra = {"leap_year": bool}`.

**sighting_calendar**: `CRITERIA` (key → English label: `yallop_A`, `yallop_B` default, `yallop_C`,
`odeh_A`, `odeh_B`, `odeh_C`), `CRITERIA_SHORT`, `DEFAULT_CRITERION`,
`PRESET_PLACES` (list of {name, name_ar, lat, lon, tz, elev}: Mecca, Medina, Najaf, Karbala,
Baghdad, Qom, Tehran, Mashhad, Jerusalem, Cairo, Rabat, Istanbul, Kabul, Karachi, Dhaka,
Kuala Lumpur, Jakarta, London, New York), `PRESETS_BY_NAME`, `visible(row, criterion)`,
`evening_info(evening, place=None) -> dict|None` (crescent-table row: conj_utc, evening,
sunset_utc, moonset_utc, lag_min, best_utc, age_h, moon_alt_sunset, arcl, arcv, daz, w, q,
arcl_topo, arcv_topo, w_topo, v, yallop, odeh; None if no new moon from 1 day before to 3 days
after), `default_span()`, `MECCA_FILE`, `build_mecca_table()`.
`SightingCalendar.stats` = {"start_minus_ummalqura": {days: count}, "beyond_3_days": n};
`.evening_info(evening)`. `HMonth.extra`: `seen`, `sighting_evening` (date or None), `evening29`,
`q`, `v`, `yallop`, `odeh`, `conj_utc`, `criterion`, `ummalqura_start`, `diff_vs_ummalqura`
(the q/v/zones are for the 29th evening of the month before, which decided this start).
A place is any dict with `lat`, `lon`, `tz` (and optional `name`, `elev`).

**solar_hijri_calendar**: `RULES`, `DEFAULT_RULE`, `AFGHAN_MONTHS` (Hamal … Hut, Dari),
`IRST`, `nowruz_dates(rule) -> {sh_year: date}`, `equinox_utc(sh_year)`, `season_table()`
(every equinox and solstice 1850–2150, UTC), `build_seasons()`,
`SolarHijriCalendar.nowruz(y)`, `.is_leap(y)`. HDate/HMonth have `calendar="solar"`.

## sky_engine
`load()`, `ephemeris_range()`, `bodies()`, `MECCA`, `new_moons(start, end) -> [UTC datetime]`,
`moon_phase_events(start, end) -> [(UTC, 0..3)]`, `seasons(start, end) -> [(UTC, 0..3)]`,
`SEASON_NAMES`, `moon_illumination([UTC])`, `moon_elongation([UTC])`,
`sun_events(lat, lon, start_utc, end_utc, horizon=-0.8333, elev=0)`, `sunset_on(place, d)`,
`yallop_zone(q)`, `odeh_zone(v)`, `YALLOP_TEXT`, `ODEH_TEXT`,
`crescent_table(start, end, place=None, days_before=1, days_after=3) -> DataFrame`
(any place; about 0.15–0.3 s per year).

## prayer_times
```python
METHODS   # key -> {label, label_ar, branch "sunni"|"shia", fajr, isha | isha_min (+ isha_min_ramadan),
          #         maghrib (0 = sunset, else degrees), midnight "standard"|"jafari", offsets?, source}
          # keys: mwl, isna, egypt, umm_al_qura, karachi, diyanet, gulf, kuwait, qatar, dubai,
          #       singapore (also JAKIM/KEMENAG), jafari (Leva, Qum), tehran (Inst. of Geophysics)
DEFAULT_METHOD = {"sunni": "mwl", "shia": "jafari"};  methods_for(branch) -> METHODS reordered
ASR_FACTOR = {"standard": 1, "hanafi": 2};  HIGH_LAT (key -> label);  KEYS
times_for_days(lat, lon, tz, days, method="mwl", asr="standard", high_lat="angle_based",
               imsak_minutes=10, elev=0.0, ramadan_dates=None, apply_offsets=True) -> [dict]
    # dict keys: date, imsak, fajr, sunrise, dhuhr, asr, sunset, maghrib, isha, midnight
    # (tz-aware datetimes, None if undefined). Umm al-Qura's Ramadan Isha (120 min) is applied
    # automatically from the Umm al-Qura calendar unless ramadan_dates is given.
month_table(lat, lon, tz, year, month, **kw)
```
Speed: one day 0.02–0.06 s; one month 0.04 s; one year 0.3 s.

## qibla
`KAABA = (21.42252, 39.82621)`, `qibla(lat, lon) -> (bearing_deg, distance_km)`,
`compass_point(b) -> "ESE"`, `describe(lat, lon) -> "118.99° (ESE), 4,794 km"`,
`describe_bearing(b) -> "119° (ESE)"`.

## Tools
`python tools/build_tables.py` rebuilds `data/crescents_mecca.csv.gz` and `data/seasons.csv` (about 1.5 min).
`python tools/smoke_test.py` runs every calendar for today and 1 Ramadan 1447 (about 5 s).
`python tools/validate.py` writes `docs/validation_results.json` (about 40 s; needs the extras in requirements.txt).

## Notes for the integrator
- Cache the calendar objects in Streamlit (`st.cache_resource`), keyed by their arguments. The modules cache internally too, but `SightingCalendar` for a new place takes about 1 s.
- Branch defaults suggested: Sunni → `UmmAlQuraCalendar("auto")`, sighting criterion `yallop_B`, prayer method `mwl`, Asr standard (Hanafi as an option). Shia → `SightingCalendar(Najaf or the user's place, "odeh_B")`, since most Twelver authorities (marja') require an actual sighting, some accepting optical aid; prayer method `jafari` (or `tehran` for Iran); solar Hijri shown alongside for Iran and Afghanistan. Practice varies, so make these defaults, not rules.
- The Fatimid tabular calendar is the Dawoodi Bohra reckoning (an Isma'ili Shia community), not the Twelver Shia calendar; label it so.
- `HDate` is frozen and orderable, so it can be used as a dict key.
