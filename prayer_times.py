"""
Prayer times from NASA JPL DE440s (via Skyfield), for any place and calculation method.

Each time is the moment the Sun's centre reaches a given altitude (airless, topocentric):
* Fajr   the Sun `fajr` degrees below the horizon in the morning (true dawn)
* Sunrise / Sunset  centre at -0.8333 deg (upper limb on the horizon, standard refraction),
         lowered by the dip of the horizon 0.0347 x sqrt(elevation in m) if elev > 0
* Dhuhr  the Sun's transit (true noon). Many timetables add a minute or more of caution.
* Asr    the shadow of a stick equals its noon shadow plus 1x (standard: Maliki, Shafi'i,
         Hanbali, and Ja'fari) or 2x its length (Hanafi). The noon shadow uses the
         declination at transit.
* Maghrib  sunset (Sunni methods), or the Sun `maghrib` degrees below the horizon (Ja'fari
         methods: after the redness in the eastern sky has passed overhead)
* Isha   the Sun `isha` degrees below the horizon, or a fixed number of minutes after Maghrib
* Midnight  "standard": half-way from sunset to sunrise; "jafari": half-way from sunset to Fajr
* Imsak  a precaution before Fajr in Ramadan (default 10 minutes)

The angles of each method follow the published tables of PrayTimes.org ("Calculation
Methods", H. Hosseini) and the AlAdhan / adhan libraries (B. Ali Khan, adhan-js), which
document the bodies' own rules; see the `source` field of each method.

High latitudes: when the Sun never gets as low as the angle (e.g. summer in northern Europe)
or the twilight would last unusually long, Fajr and Isha are limited to a portion of the night
(PrayTimes.org rule): "angle_based" (angle/60 of the night), "one_seventh", "middle_of_night"
(half), or "none".

Speed: one month for one place takes about 0.1-0.2 s.
"""
from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

import sky_engine as se

# fajr / isha: degrees below the horizon; isha_min: minutes after Maghrib instead of an angle;
# maghrib: 0 = sunset, else degrees below the horizon; offsets: minutes added after computing
METHODS = {
    "mwl": {"label": "Muslim World League", "label_ar": "رابطة العالم الإسلامي", "branch": "sunni",
            "fajr": 18.0, "isha": 17.0, "maghrib": 0.0, "midnight": "standard",
            "source": "PrayTimes.org; AlAdhan method 3"},
    "isna": {"label": "Islamic Society of North America", "label_ar": "الجمعية الإسلامية لأمريكا الشمالية",
             "branch": "sunni", "fajr": 15.0, "isha": 15.0, "maghrib": 0.0, "midnight": "standard",
             "source": "PrayTimes.org; AlAdhan method 2"},
    "egypt": {"label": "Egyptian General Authority of Survey", "label_ar": "الهيئة المصرية العامة للمساحة",
              "branch": "sunni", "fajr": 19.5, "isha": 17.5, "maghrib": 0.0, "midnight": "standard",
              "source": "PrayTimes.org; AlAdhan method 5"},
    "umm_al_qura": {"label": "Umm al-Qura University, Makkah", "label_ar": "جامعة أم القرى، مكة المكرمة",
                    "branch": "sunni", "fajr": 18.5, "isha_min": 90, "isha_min_ramadan": 120, "maghrib": 0.0,
                    "midnight": "standard",
                    "source": "PrayTimes.org (Fajr 19 deg before 1430 AH); AlAdhan method 4; "
                              "Isha 90 min after Maghrib, 120 min in Ramadan"},
    "karachi": {"label": "University of Islamic Sciences, Karachi", "label_ar": "جامعة العلوم الإسلامية، كراتشي",
                "branch": "sunni", "fajr": 18.0, "isha": 18.0, "maghrib": 0.0, "midnight": "standard",
                "source": "PrayTimes.org; AlAdhan method 1"},
    "diyanet": {"label": "Diyanet, Turkey (approximation)", "label_ar": "رئاسة الشؤون الدينية التركية", "branch": "sunni",
                "fajr": 18.0, "isha": 17.0, "maghrib": 0.0, "midnight": "standard",
                "offsets": {"sunrise": -7, "dhuhr": 5, "asr": 4, "maghrib": 7},
                "source": "AlAdhan method 13; adhan-js 'Turkey()', which calls itself an approximation of "
                          "the Diyanet method: 18/17 with offsets sunrise -7, Dhuhr +5, Asr +4, Maghrib +7 min"},
    "gulf": {"label": "Gulf Region", "label_ar": "منطقة الخليج", "branch": "sunni",
             "fajr": 19.5, "isha_min": 90, "maghrib": 0.0, "midnight": "standard",
             "source": "AlAdhan method 8"},
    "kuwait": {"label": "Kuwait", "label_ar": "الكويت", "branch": "sunni",
               "fajr": 18.0, "isha": 17.5, "maghrib": 0.0, "midnight": "standard",
               "source": "AlAdhan method 9; adhan-js 'Kuwait'"},
    "qatar": {"label": "Qatar", "label_ar": "قطر", "branch": "sunni",
              "fajr": 18.0, "isha_min": 90, "maghrib": 0.0, "midnight": "standard",
              "source": "AlAdhan method 10; adhan-js 'Qatar'"},
    "dubai": {"label": "Dubai (UAE)", "label_ar": "دبي", "branch": "sunni",
              "fajr": 18.2, "isha": 18.2, "maghrib": 0.0, "midnight": "standard",
              "source": "AlAdhan method 16; adhan-js 'Dubai' (without its minute offsets)"},
    "singapore": {"label": "Singapore, Malaysia (JAKIM), Indonesia", "label_ar": "سنغافورة وماليزيا وإندونيسيا",
                  "branch": "sunni", "fajr": 20.0, "isha": 18.0, "maghrib": 0.0, "midnight": "standard",
                  "source": "AlAdhan methods 11 (MUIS), 17 (JAKIM), 20 (KEMENAG); adhan-js 'Singapore'"},
    "jafari": {"label": "Shia Ithna-Ashari, Leva Institute, Qum", "label_ar": "مؤسسة ليوا، قم (الجعفري)",
               "branch": "shia", "fajr": 16.0, "isha": 14.0, "maghrib": 4.0, "midnight": "jafari",
               "source": "PrayTimes.org 'Jafari'; AlAdhan method 0"},
    "tehran": {"label": "Institute of Geophysics, University of Tehran", "label_ar": "مؤسسه ژئوفیزیک دانشگاه تهران",
               "branch": "shia", "fajr": 17.7, "isha": 14.0, "maghrib": 4.5, "midnight": "jafari",
               "source": "PrayTimes.org 'Tehran'; AlAdhan method 7"},
}
DEFAULT_METHOD = {"sunni": "mwl", "shia": "jafari"}
ASR_FACTOR = {"standard": 1, "hanafi": 2}
HIGH_LAT = {"angle_based": "Angle-based (angle/60 of the night)", "middle_of_night": "Middle of the night",
            "one_seventh": "One seventh of the night", "none": "No adjustment"}
KEYS = ["imsak", "fajr", "sunrise", "dhuhr", "asr", "sunset", "maghrib", "isha", "midnight"]


def methods_for(branch: str) -> dict:
    """Methods to offer in Sunni or Shia mode (the other branch's methods follow)."""
    first = {k: v for k, v in METHODS.items() if v["branch"] in (branch, "both")}
    rest = {k: v for k, v in METHODS.items() if k not in first}
    return {**first, **rest}


def _hadec(lat, lon, elev, tt):
    ts, eph, earth, sun, moon = se.bodies()
    obs = earth + se._observer(lat, lon, elev)
    t = ts.tt_jd(tt)
    ha, dec, _ = obs.at(t).observe(sun).apparent().hadec()
    h = ha.radians
    h = (h + math.pi) % (2 * math.pi) - math.pi
    return h, dec.radians


def _solve(lat, lon, elev, tt_noon_guess, targets):
    """targets: list of (key, altitude_deg array or float, side -1 morning / +1 afternoon / 0 transit).
    Returns {key: tt array (nan where the Sun never reaches the altitude)} and transit declination."""
    phi = math.radians(lat)
    n = len(tt_noon_guess)
    # transit
    tt = tt_noon_guess.copy()
    for _ in range(3):
        h, dec = _hadec(lat, lon, elev, tt)
        tt = tt - h / (2 * math.pi)          # the Sun's hour angle turns 2 pi in about a day
    h, dec_noon = _hadec(lat, lon, elev, tt)
    transit = tt - h / (2 * math.pi)
    out = {"dhuhr": transit}
    keys = [k for k, _, _ in targets]
    alts = [np.radians(np.broadcast_to(np.asarray(a, dtype=float), (n,))) for _, a, _ in targets]
    sides = [s for _, _, s in targets]
    A = np.concatenate(alts)
    S = np.concatenate([np.full(n, s, dtype=float) for s in sides])
    T0 = np.tile(transit, len(targets))
    D = np.tile(dec_noon, len(targets))

    def req_ha(dec):
        c = (np.sin(A) - math.sin(phi) * np.sin(dec)) / (math.cos(phi) * np.cos(dec))
        return np.where(np.abs(c) <= 1, np.arccos(np.clip(c, -1, 1)), np.nan)

    H = req_ha(D)
    T = T0 + S * H / (2 * math.pi)
    for _ in range(3):
        ok = np.isfinite(T)
        if not ok.any():
            break
        hh = np.full_like(T, np.nan)
        dd = np.full_like(T, np.nan)
        hh[ok], dd[ok] = _hadec(lat, lon, elev, T[ok])
        H = req_ha(dd)
        T = T + (S * H - hh) / (2 * math.pi)
    for i, k in enumerate(keys):
        out[k] = T[i * n:(i + 1) * n]
    return out, dec_noon


def _ramadan_days(days) -> set:
    """Days of Ramadan by the Umm al-Qura calendar (official table; tabular outside it)."""
    import ummalqura_calendar as uq
    import tabular_calendar as tc
    out = set()
    try:
        off = uq._official()
    except Exception:
        off = {}
    tab = None
    for d in days:
        hit = None
        for y in (d.year - 579, d.year - 578, d.year - 580):
            v = off.get((y, 9))
            if v:
                s = date(v[0].year, v[0].month, v[0].day)
                if s <= d < s + timedelta(days=v[1]):
                    hit = True
                    break
        if hit is None and not off.get((d.year - 579, 9)):
            tab = tab or tc.TabularCalendar("kuwaiti")
            h = tab.from_gregorian(d)
            hit = bool(h and h.month == 9)
        if hit:
            out.add(d)
    return out


def times_for_days(lat: float, lon: float, tz: str, days: list[date], method: str = "mwl",
                   asr: str = "standard", high_lat: str = "angle_based", imsak_minutes: float = 10,
                   elev: float = 0.0, ramadan_dates=None, apply_offsets: bool = True) -> list[dict]:
    """Prayer times for each local civil day in `days` at (lat, lon) in time zone `tz`.

    Returns one dict per day with keys date, imsak, fajr, sunrise, dhuhr, asr, sunset, maghrib,
    isha, midnight (tz-aware datetimes; None where the Sun does not reach the altitude and no
    high-latitude rule applies). `ramadan_dates` (a set of dates) switches Isha to the Ramadan
    interval for methods that have one; by default Ramadan follows the Umm al-Qura calendar."""
    m = METHODS[method]
    zone = ZoneInfo(tz)
    days = list(days)
    if not days:
        return []
    ts, *_ = se.bodies()
    all_days = days + [days[-1] + timedelta(days=1)]          # next sunrise/fajr for midnight
    # first guess of transit: 12:00 local mean solar time
    guess = []
    for d in all_days:
        t = datetime(d.year, d.month, d.day, 12, tzinfo=timezone.utc) - timedelta(hours=lon / 15.0)
        guess.append(ts.from_datetime(t).tt)
    guess = np.array(guess)
    dip = 0.0347 * math.sqrt(max(elev, 0.0))
    horizon = -0.8333 - dip
    # Asr altitude from the noon declination (first pass with the guess)
    _, dec0 = _hadec(lat, lon, elev, guess)
    sfac = ASR_FACTOR[asr]
    asr_alt = np.degrees(np.arctan(1.0 / (sfac + np.tan(np.abs(math.radians(lat) - dec0)))))
    targets = [("fajr", -m["fajr"], -1), ("sunrise", horizon, -1), ("asr", asr_alt, +1),
               ("sunset", horizon, +1)]
    if m.get("maghrib"):
        targets.append(("maghrib", -m["maghrib"], +1))
    if "isha" in m:
        targets.append(("isha", -m["isha"], +1))
    res, _ = _solve(lat, lon, elev, guess, targets)

    def to_dt(tt):
        if not np.isfinite(tt):
            return None
        return ts.tt_jd(tt).utc_datetime().astimezone(zone)

    if ramadan_dates is None and "isha_min_ramadan" in m:
        ramadan_dates = _ramadan_days(days)
    ramadan_dates = ramadan_dates or set()
    offsets = m.get("offsets", {}) if apply_offsets else {}
    out = []
    for i, d in enumerate(days):
        r = {k: res[k][i] if k in res else np.nan for k in ("fajr", "sunrise", "dhuhr", "asr", "sunset")}
        r["maghrib"] = res["maghrib"][i] if "maghrib" in res else r["sunset"]
        if "isha" in res:
            r["isha"] = res["isha"][i]
        else:
            mins = m["isha_min_ramadan"] if (d in ramadan_dates and "isha_min_ramadan" in m) else m["isha_min"]
            r["isha"] = r["maghrib"] + mins / 1440.0
        next_sunrise, next_fajr = res["sunrise"][i + 1], res["fajr"][i + 1]
        # high-latitude limits (PrayTimes.org)
        if high_lat != "none" and np.isfinite(r["sunrise"]) and np.isfinite(r["sunset"]):
            night = (next_sunrise if np.isfinite(next_sunrise) else r["sunrise"] + 1) - r["sunset"]

            def portion(angle):
                f = {"angle_based": angle / 60.0, "one_seventh": 1 / 7.0, "middle_of_night": 0.5}[high_lat]
                return f * night
            p = portion(m["fajr"])
            if not np.isfinite(r["fajr"]) or r["sunrise"] - r["fajr"] > p:
                r["fajr"] = r["sunrise"] - p
            if "isha" in m:
                p = portion(m["isha"])
                if not np.isfinite(r["isha"]) or r["isha"] - r["sunset"] > p:
                    r["isha"] = r["sunset"] + p
            if m.get("maghrib"):
                p = portion(m["maghrib"])
                if not np.isfinite(r["maghrib"]) or r["maghrib"] - r["sunset"] > p:
                    r["maghrib"] = r["sunset"] + p
            if not np.isfinite(next_fajr):
                next_fajr = next_sunrise - portion(m["fajr"]) if np.isfinite(next_sunrise) else np.nan
        r["imsak"] = r["fajr"] - imsak_minutes / 1440.0
        if m["midnight"] == "jafari":
            r["midnight"] = r["sunset"] + (next_fajr - r["sunset"]) / 2
        else:
            r["midnight"] = r["sunset"] + (next_sunrise - r["sunset"]) / 2
        row = {"date": d}
        for k in KEYS:
            dt = to_dt(r[k])
            if dt is not None and k in offsets:
                dt = dt + timedelta(minutes=offsets[k])
            row[k] = dt
        out.append(row)
    return out


def month_table(lat, lon, tz, year: int, month: int, **kw) -> list[dict]:
    """Prayer times for every day of a Gregorian month."""
    d = date(year, month, 1)
    days = []
    while d.month == month:
        days.append(d)
        d += timedelta(days=1)
    return times_for_days(lat, lon, tz, days, **kw)
