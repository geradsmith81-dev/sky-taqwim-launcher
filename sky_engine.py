"""
Astronomy from NASA JPL's DE440s planetary ephemeris (via Skyfield).

* new moons (true geocentric conjunction in ecliptic longitude of date)
* equinoxes and solstices
* sunrise and sunset for any place (prayer times are in prayer_times.py)
* the young crescent at the "best time" for any place
  (Yallop 1997, NAO Technical Note 69; Odeh 2004, Experimental Astronomy 18:39-64)

Taken over from Sky Luach (sky_engine.py), whose engine was checked against JPL Horizons
(docs/VALIDATION.md there). Changes: the reference place is Mecca, crescent_table() works for
any place dict {name, lat, lon, tz, elev?}, and the Jewish zmanim were removed.

DE440s covers 1849-12-26 .. 2150-01-22. If the larger de440.bsp (1550-2650) is placed in
ephem/, it is used instead.
"""
from __future__ import annotations

import math
import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import numpy as np
from skyfield import almanac
from skyfield.api import Loader, wgs84

HERE = os.path.dirname(os.path.abspath(__file__))
EPHEM_DIR = os.path.join(HERE, "ephem")

# The Kaaba, al-Masjid al-Haram. Umm al-Qura computations use these coordinates.
MECCA = {"name": "Mecca (al-Masjid al-Haram)", "name_ar": "مكة المكرمة", "lat": 21.4225, "lon": 39.8262,
         "elev": 277.0, "tz": "Asia/Riyadh"}
MOON_RADIUS_KM = 1737.4


class EphemerisMissing(RuntimeError):
    pass


@lru_cache(maxsize=1)
def load():
    """Return (timescale, ephemeris, filename). Prefers de440.bsp if present, else de440s.bsp,
    downloading de440s.bsp from JPL if neither file is there."""
    os.makedirs(EPHEM_DIR, exist_ok=True)
    loader = Loader(EPHEM_DIR, verbose=False)
    ts = loader.timescale(builtin=True)
    for name in ("de440.bsp", "de440s.bsp"):
        if os.path.exists(os.path.join(EPHEM_DIR, name)):
            return ts, loader(name), name
    try:
        url = "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de440s.bsp"
        loader.download(url, filename="de440s.bsp")
        return ts, loader("de440s.bsp"), "de440s.bsp"
    except Exception as exc:  # pragma: no cover - network failure
        raise EphemerisMissing(
            "The JPL ephemeris file de440s.bsp is missing and could not be downloaded "
            f"({exc}). Put de440s.bsp into the 'ephem' folder.") from exc


def ephemeris_range() -> tuple[date, date]:
    ts, eph, name = load()
    seg = eph.segments[0].spk_segment
    t0 = ts.tdb_jd(seg.start_jd)
    t1 = ts.tdb_jd(seg.end_jd)
    return t0.utc_datetime().date() + timedelta(days=1), t1.utc_datetime().date() - timedelta(days=1)


def bodies():
    ts, eph, _ = load()
    return ts, eph, eph["earth"], eph["sun"], eph["moon"]


# ----------------------------------------------------------------------------------------------
# events
# ----------------------------------------------------------------------------------------------
def _clamp_dates(start: date, end: date) -> tuple[date, date]:
    lo, hi = ephemeris_range()
    return max(start, lo), min(end, hi)


def new_moons(start: date, end: date) -> list[datetime]:
    """UTC datetimes of true new moons (conjunctions) between start and end."""
    ts, eph, *_ = bodies()
    start, end = _clamp_dates(start, end)
    t0 = ts.utc(start.year, start.month, start.day)
    t1 = ts.utc(end.year, end.month, end.day)
    t, y = almanac.find_discrete(t0, t1, almanac.moon_phases(eph))
    return [ti.utc_datetime() for ti, yi in zip(t, y) if yi == 0]


def moon_phase_events(start: date, end: date) -> list[tuple[datetime, int]]:
    """(UTC datetime, phase) with phase 0 new, 1 first quarter, 2 full, 3 last quarter."""
    ts, eph, *_ = bodies()
    start, end = _clamp_dates(start, end)
    t, y = almanac.find_discrete(ts.utc(start.year, start.month, start.day),
                                 ts.utc(end.year, end.month, end.day), almanac.moon_phases(eph))
    return [(ti.utc_datetime(), int(yi)) for ti, yi in zip(t, y)]


SEASON_NAMES = ["March equinox", "June solstice", "September equinox", "December solstice"]


def seasons(start: date, end: date) -> list[tuple[datetime, int]]:
    """(UTC datetime, k) with k 0=March equinox, 1=June solstice, 2=Sept equinox, 3=Dec solstice."""
    ts, eph, *_ = bodies()
    start, end = _clamp_dates(start, end)
    t, y = almanac.find_discrete(ts.utc(start.year, start.month, start.day),
                                 ts.utc(end.year, end.month, end.day), almanac.seasons(eph))
    return [(ti.utc_datetime(), int(yi)) for ti, yi in zip(t, y)]


def moon_illumination(when_utc: list[datetime]) -> np.ndarray:
    """Illuminated fraction of the Moon (geocentric) at the given UTC datetimes."""
    ts, eph, earth, sun, moon = bodies()
    t = ts.from_datetimes(when_utc)
    return almanac.fraction_illuminated(eph, "moon", t)


def moon_elongation(when_utc: list[datetime]) -> np.ndarray:
    """Moon minus Sun apparent ecliptic longitude, 0..360 deg (0 new, 180 full)."""
    ts, eph, earth, sun, moon = bodies()
    t = ts.from_datetimes(when_utc)
    e = earth.at(t)
    _, ls, _ = e.observe(sun).apparent().frame_latlon(_ecliptic_of_date())
    _, lm, _ = e.observe(moon).apparent().frame_latlon(_ecliptic_of_date())
    return (lm.degrees - ls.degrees) % 360.0


def _ecliptic_of_date():
    from skyfield.framelib import ecliptic_frame
    return ecliptic_frame


# ----------------------------------------------------------------------------------------------
# sunrise / sunset for a place
# ----------------------------------------------------------------------------------------------
def _observer(lat, lon, elev=0.0):
    return wgs84.latlon(lat, lon, elevation_m=elev)


def sun_events(lat: float, lon: float, start_utc: datetime, end_utc: datetime,
               horizon: float = -0.8333, elev: float = 0.0) -> tuple[list[datetime], list[datetime]]:
    """Sunrises and sunsets (UTC) with the Sun's centre at `horizon` degrees
    (-0.8333 = upper limb on a sea-level horizon with standard refraction)."""
    ts, eph, earth, sun, moon = bodies()
    obs = earth + _observer(lat, lon, elev)
    t0, t1 = ts.from_datetime(start_utc), ts.from_datetime(end_utc)
    tr, yr = almanac.find_risings(obs, sun, t0, t1, horizon_degrees=horizon)
    tsun, ys = almanac.find_settings(obs, sun, t0, t1, horizon_degrees=horizon)
    rises = [t.utc_datetime() for t, ok in zip(tr, yr) if ok]
    sets = [t.utc_datetime() for t, ok in zip(tsun, ys) if ok]
    return rises, sets


def sunset_on(place: dict, d: date) -> datetime | None:
    """Local sunset (tz-aware) on the civil date d at `place` (None in polar day or night)."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(place["tz"])
    start = datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(timezone.utc)
    _, sets = sun_events(place["lat"], place["lon"], start, start + timedelta(days=1))
    sets = [s.astimezone(tz) for s in sets if s.astimezone(tz).date() == d]
    return sets[-1] if sets else None


# ----------------------------------------------------------------------------------------------
# the young crescent seen from any place
# ----------------------------------------------------------------------------------------------
def _geo_altaz(ra_h, dec_deg, gast_h, lat, lon):
    """Airless altitude/azimuth seen from the Earth's centre, in the local horizon frame."""
    ha = np.radians((gast_h - ra_h) * 15.0 + lon)
    dec = np.radians(dec_deg)
    phi = np.radians(lat)
    sin_alt = np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.cos(ha)
    alt = np.arcsin(np.clip(sin_alt, -1, 1))
    az = np.arctan2(-np.cos(dec) * np.sin(ha),
                    np.sin(dec) * np.cos(phi) - np.cos(dec) * np.sin(phi) * np.cos(ha))
    return np.degrees(alt), np.degrees(az) % 360.0


def _sep_deg(ra1_h, dec1, ra2_h, dec2):
    a1, a2 = np.radians(ra1_h * 15), np.radians(ra2_h * 15)
    d1, d2 = np.radians(dec1), np.radians(dec2)
    c = np.sin(d1) * np.sin(d2) + np.cos(d1) * np.cos(d2) * np.cos(a1 - a2)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def yallop_zone(q: float) -> str:
    if q > 0.216:
        return "A"
    if q > -0.014:
        return "B"
    if q > -0.160:
        return "C"
    if q > -0.232:
        return "D"
    if q > -0.293:
        return "E"
    return "F"


YALLOP_TEXT = {
    "A": "easily visible to the naked eye",
    "B": "visible to the naked eye under perfect conditions",
    "C": "may need binoculars to find, then naked eye",
    "D": "binoculars or telescope only",
    "E": "not visible even with a telescope",
    "F": "not visible (below the Danjon limit)",
}


def odeh_zone(v: float) -> str:
    if v >= 5.65:
        return "A"
    if v >= 2.0:
        return "B"
    if v >= -0.96:
        return "C"
    return "D"


ODEH_TEXT = {"A": "visible to the naked eye", "B": "visible with optical aid; may be seen by naked eye",
             "C": "visible with optical aid only", "D": "not visible even with optical aid"}


def crescent_table(start: date, end: date, place: dict | None = None, days_before: int = 1,
                   days_after: int = 3) -> "pandas.DataFrame":
    """Crescent parameters on each evening from `days_before` before to `days_after` after every
    new moon between start and end, for `place` (a dict with lat, lon, tz; default Mecca).
    The horizon is the sea-level horizon (elevation 0), as Yallop and Odeh assume.
    Speed: about 0.3 s per year of span.
    Best time Tb = sunset + 4/9 x lag (Yallop). Columns:
    conj_utc, evening (local civil date of the sunset), sunset_utc, moonset_utc, lag_min,
    best_utc, age_h (at best time), moon_alt_sunset, arcl, arcv, daz, w (Yallop, arcmin), q,
    yallop, arcl_topo, arcv_topo, w_topo, v (Odeh), odeh."""
    import pandas as pd
    from zoneinfo import ZoneInfo
    ts, eph, earth, sun, moon = bodies()
    place = place or MECCA
    tz = ZoneInfo(place["tz"])
    topos = _observer(place["lat"], place["lon"], 0.0)
    obs = earth + topos

    conj = new_moons(start - timedelta(days=2), end + timedelta(days=2))
    # sunsets and moonsets covering the whole interval
    lo, hi = _clamp_dates(start - timedelta(days=days_before + 3), end + timedelta(days=days_after + 4))
    t0 = ts.utc(lo.year, lo.month, lo.day)
    t1 = ts.utc(hi.year, hi.month, hi.day)
    tss, yss = almanac.find_settings(obs, sun, t0, t1)
    sunsets = np.array([t.tt for t, ok in zip(tss, yss) if ok])
    tms, yms = almanac.find_settings(obs, moon, t0, t1)
    moonsets = np.array([t.tt for t, ok in zip(tms, yms) if ok])

    rows = []
    for c in conj:
        c_tt = ts.from_datetime(c).tt
        # sunsets from days_before before the conjunction to days_after after it
        sel = sunsets[(sunsets > c_tt - days_before - 0.5) & (sunsets < c_tt + days_after + 0.5)]
        for s in sel:
            i = np.searchsorted(moonsets, s)
            ms_next = moonsets[i] if i < len(moonsets) else np.nan
            ms_prev = moonsets[i - 1] if i > 0 else np.nan
            rows.append((c, c_tt, s, ms_next, ms_prev))
    if not rows:
        return pd.DataFrame()

    c_dt = [r[0] for r in rows]
    c_tt = np.array([r[1] for r in rows])
    s_tt = np.array([r[2] for r in rows])
    ms_next = np.array([r[3] for r in rows])
    ms_prev = np.array([r[4] for r in rows])

    t_set = ts.tt_jd(s_tt)
    alt_set, _, dist_set = obs.at(t_set).observe(moon).apparent().altaz()
    moon_alt_set = alt_set.degrees
    # topocentric elongation at sunset (used by the Neo-MABIMS rule: altitude 3 deg, elongation 6.4 deg)
    elong_set_topo = obs.at(t_set).observe(sun).apparent().separation_from(
        obs.at(t_set).observe(moon).apparent()).degrees
    # Skyfield's moonset: centre at -(34' refraction + apparent radius) on an airless altitude.
    moon_horizon = -(34.0 / 60.0) - np.degrees(np.arcsin(MOON_RADIUS_KM / dist_set.km))
    # Moon sets after the Sun if it is above its setting altitude at sunset and the next moonset
    # is within ~half a day; otherwise the lag is negative (it set before the Sun).
    lag_days = np.where(moon_alt_set > moon_horizon, ms_next - s_tt, ms_prev - s_tt)
    lag_days = np.where(np.abs(lag_days) < 0.6, lag_days, np.nan)
    best_tt = s_tt + np.where(lag_days > 0, 4.0 / 9.0 * lag_days, 0.0)
    t_best = ts.tt_jd(best_tt)

    # geocentric apparent places
    e = earth.at(t_best)
    ra_s, dec_s, _ = e.observe(sun).apparent().radec(epoch="date")
    ra_m, dec_m, dist_m = e.observe(moon).apparent().radec(epoch="date")
    gast = t_best.gast
    alt_s, az_s = _geo_altaz(ra_s.hours, dec_s.degrees, gast, place["lat"], place["lon"])
    alt_m, az_m = _geo_altaz(ra_m.hours, dec_m.degrees, gast, place["lat"], place["lon"])
    arcl = _sep_deg(ra_s.hours, dec_s.degrees, ra_m.hours, dec_m.degrees)
    arcv = alt_m - alt_s
    daz = ((az_s - az_m + 180) % 360) - 180

    # topocentric (airless) places
    o = obs.at(t_best)
    ps = o.observe(sun).apparent()
    pm = o.observe(moon).apparent()
    alt_st, az_st, _ = ps.altaz()
    alt_mt, az_mt, d_mt = pm.altaz()
    arcl_t = ps.separation_from(pm).degrees
    arcv_t = alt_mt.degrees - alt_st.degrees
    sd_topo = np.degrees(np.arcsin(MOON_RADIUS_KM / d_mt.km)) * 60.0  # arcmin

    w = sd_topo * (1 - np.cos(np.radians(arcl)))          # Yallop: geocentric ARCL
    w_t = sd_topo * (1 - np.cos(np.radians(arcl_t)))      # Odeh: topocentric ARCL
    q = (arcv - (11.8371 - 6.3226 * w + 0.7319 * w ** 2 - 0.1018 * w ** 3)) / 10.0
    v = arcv_t - (7.1651 - 6.3226 * w_t + 0.7319 * w_t ** 2 - 0.1018 * w_t ** 3)

    # not visible if the Moon sets before the Sun or the conjunction is after the best time
    invisible = ~(lag_days > 0) | (best_tt < c_tt)
    q = np.where(invisible, np.nan, q)
    v = np.where(invisible, np.nan, v)

    def to_utc(tt):
        return [x.utc_datetime() if np.isfinite(y) else None for x, y in zip(ts.tt_jd(np.nan_to_num(tt)), tt)]

    sunset_utc = [t.utc_datetime() for t in t_set]
    df = pd.DataFrame({
        "conj_utc": c_dt,
        "evening": [s.astimezone(tz).date() for s in sunset_utc],
        "sunset_utc": sunset_utc,
        "moonset_utc": to_utc(np.where(lag_days > 0, s_tt + lag_days, np.nan)),
        "lag_min": np.round(lag_days * 1440, 1),
        "best_utc": [t.utc_datetime() for t in t_best],
        "age_h": np.round((best_tt - c_tt) * 24, 2),
        "moon_alt_sunset": np.round(moon_alt_set, 3), "elong_sunset_topo": np.round(elong_set_topo, 3),
        "arcl": np.round(arcl, 4), "arcv": np.round(arcv, 4), "daz": np.round(daz, 4),
        "w": np.round(w, 4), "q": np.round(q, 4),
        "arcl_topo": np.round(arcl_t, 4), "arcv_topo": np.round(arcv_t, 4), "w_topo": np.round(w_t, 4),
        "v": np.round(v, 4),
    })
    df["yallop"] = [yallop_zone(x) if np.isfinite(x) else "-" for x in df["q"]]
    df["odeh"] = [odeh_zone(x) if np.isfinite(x) else "-" for x in df["v"]]
    df = df.drop_duplicates(subset=["evening"]).sort_values("sunset_utc").reset_index(drop=True)
    return df
