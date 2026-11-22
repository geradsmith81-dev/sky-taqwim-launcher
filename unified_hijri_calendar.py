"""
The Unified Hijri Calendar of the Istanbul congress of 2016 (al-Taqwim al-Hijri al-Muwahhad; Turkish
Uluslararasi Hicri Takvim Birligi Kongresi, 28-30 May 2016), computed from NASA JPL DE440s.

The whole world is one sighting zone (matla') and every month begins on the same civil day everywhere.
Day D is the 1st of a month when, on the evening before it,

  A. somewhere on Earth whose sunset comes before 00:00 UT of D, after the conjunction, the Moon is at
     least 5 degrees above the horizon at sunset and at least 8 degrees from the Sun (elongation); or
  B. the same holds somewhere on the mainland of the Americas (where sunset may come after 00:00 UT),
     provided the conjunction came before dawn in New Zealand (Wellington) on its date D.

It is used by the Presidency of Religious Affairs of Turkey (Diyanet), by the Muhammadiyah's Kalender
Hijriah Global Tunggal (from 1446 AH / 2025), and, with the same 5 + 8 degree parameters, by the European
Council for Fatwa and Research and the Fiqh Council of North America for Ramadan and Shawwal.

Reading of the rule (the published texts leave the frames open): topocentric, unrefracted altitude of
the Moon's centre; geocentric elongation; sunset = the Sun's centre 0.8333 degrees below a sea-level
horizon; dawn in Wellington = the Sun 18 degrees below (Diyanet's own angle). For clause A each latitude
from 60 S to 60 N is tried at the point where the Sun sets exactly at 00:00 UT (the oldest Moon allowed
there); for clause B the westernmost point of the Americas mainland at each latitude from 53 S to 71 N.
This is the reading that reproduces 184 of Diyanet's 186 published month starts in the libmuslim
project's study (Apache-2.0; its coastline table, derived from Natural Earth 1:50m land, public domain,
is used here); this module's own score is in docs/VALIDATION.md.

The month starts are precomputed into data/unified_hijri_starts.csv (tools/build_tables.py).
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import numpy as np
import pandas as pd

from hijri_core import HMonth, LunarCalendar

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
STARTS_FILE = os.path.join(DATA, "unified_hijri_starts.csv")

H0_SUNSET = np.radians(-0.8333)
H0_DAWN = np.radians(-18.0)
EARTH_R_KM = 6378.137
WELLINGTON = (-41.2865, 174.7762)

# westernmost longitude of the Americas mainland at each whole degree of latitude, 53 S .. 71 N, is in
# data/americas_west_coast.json (from Natural Earth 1:50m land, islands excluded; the table published in
# libmuslim hijri.h, Apache-2.0)


def _coast():
    p = os.path.join(DATA, "americas_west_coast.json")
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    lats = np.arange(d["first_lat"], d["first_lat"] + len(d["lon"]))
    return lats.astype(float), np.array(d["lon"], dtype=float)


# ----------------------------------------------------------------------------------------------
# geometry
# ----------------------------------------------------------------------------------------------
def _eq(tt_jd: np.ndarray):
    """Apparent geocentric RA/Dec (radians) of Sun and Moon, Moon distance (km), GAST (radians)."""
    import sky_engine as se
    ts, eph, earth, sun, moon = se.bodies()
    t = ts.tt_jd(tt_jd)
    e = earth.at(t)
    ra_s, de_s, _ = e.observe(sun).apparent().radec(epoch="date")
    ra_m, de_m, d_m = e.observe(moon).apparent().radec(epoch="date")
    return (ra_s.radians, de_s.radians, ra_m.radians, de_m.radians, d_m.km, np.radians(t.gast * 15.0))


def _elong(ras, des, ram, dem):
    c = np.sin(des) * np.sin(dem) + np.cos(des) * np.cos(dem) * np.cos(ras - ram)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def _topo_alt(lat, lon, gast, ram, dem, dist):
    """Topocentric unrefracted altitude (deg) of the Moon's centre, spherical-Earth parallax."""
    phi = np.radians(lat)
    theta = gast + np.radians(lon)                # local sidereal angle
    mx, my, mz = dist * np.cos(dem) * np.cos(ram), dist * np.cos(dem) * np.sin(ram), dist * np.sin(dem)
    ox, oy, oz = EARTH_R_KM * np.cos(phi) * np.cos(theta), EARTH_R_KM * np.cos(phi) * np.sin(theta), EARTH_R_KM * np.sin(phi)
    tx, ty, tz = mx - ox, my - oy, mz - oz
    r = np.sqrt(tx * tx + ty * ty + tz * tz)
    # unit vector of the local zenith
    zx, zy, zz = np.cos(phi) * np.cos(theta), np.cos(phi) * np.sin(theta), np.sin(phi)
    return np.degrees(np.arcsin(np.clip((tx * zx + ty * zy + tz * zz) / r, -1, 1)))


def _hour_angle(lat, dec, h0):
    """Hour angle (rad) at which a body of declination dec is at altitude h0; nan if it never is."""
    phi = np.radians(lat)
    c = (np.sin(h0) - np.sin(phi) * np.sin(dec)) / (np.cos(phi) * np.cos(dec))
    return np.where(np.abs(c) <= 1, np.arccos(np.clip(c, -1, 1)), np.nan)


def _wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def _solve_sun_event(lat, lon, tt_guess, h0, evening=True, iters=4):
    """TT Julian dates of sunset (evening) or dawn (morning) at (lat, lon) near tt_guess; nan where the
    Sun does not reach that altitude (polar day or night)."""
    t = np.array(tt_guess, dtype=float)
    bad = np.zeros(t.shape, dtype=bool)
    for _ in range(iters):
        ras, des, _, _, _, gast = _eq(t)
        H = _hour_angle(lat, des, h0)
        bad |= ~np.isfinite(H)
        target = np.where(np.isfinite(H), H, 0.0) * (1 if evening else -1)
        lha = gast + np.radians(lon) - ras
        t = t + np.where(bad, 0.0, _wrap(target - lha) / (2 * np.pi) * 0.99727)   # sidereal day
    return np.where(bad, np.nan, t)


# ----------------------------------------------------------------------------------------------
# the search
# ----------------------------------------------------------------------------------------------
def _ut_midnight_tt(d: date) -> float:
    import sky_engine as se
    ts = se.bodies()[0]
    return ts.utc(d.year, d.month, d.day).tt


def compute_starts(start: date = date(1850, 1, 1), end: date = date(2150, 1, 1), progress=False) -> pd.DataFrame:
    """Month starts of the unified calendar between start and end (one row per new moon)."""
    import sky_engine as se
    ts = se.bodies()[0]
    clat, clon = _coast()
    lat_a = np.arange(-60.0, 60.01, 1.0)
    rows = []
    conj = se.new_moons(start - timedelta(days=3), end + timedelta(days=3))
    conj_tt = np.array([ts.from_datetime(c).tt for c in conj])
    # candidate days D: conj date + 1, + 2, + 3 (D = conj date fails: the conjunction must precede 00:00 UT of D)
    cand = []
    for i, c in enumerate(conj):
        d0 = c.date()
        for k in (1, 2, 3, 4):
            cand.append((i, d0 + timedelta(days=k)))
    D_tt = np.array([_ut_midnight_tt(d) for _, d in cand])
    ci = np.array([i for i, _ in cand])
    ctt = conj_tt[ci]

    # --- clause A: at T0 = 00:00 UT of D, along the sunset line
    ras, des, ram, dem, dm, gast = _eq(D_tt)
    elong_A = _elong(ras, des, ram, dem)
    H = _hour_angle(lat_a[None, :], des[:, None], H0_SUNSET)                 # (n, lat)
    lon_set = np.degrees(_wrap(H + ras[:, None] - gast[:, None]))             # sunset longitude at T0
    altA = _topo_alt(lat_a[None, :], lon_set, gast[:, None], ram[:, None], dem[:, None], dm[:, None])
    altA = np.where(np.isfinite(altA), altA, -90.0)
    best_i = np.argmax(altA, axis=1)
    altA_max = altA[np.arange(len(cand)), best_i]
    passA = (ctt < D_tt) & (elong_A >= 8.0) & (altA_max >= 5.0)

    # --- Wellington dawn on its local date D (local mean time = UT + 11.65 h; dawn about 5 h local)
    wl_lat, wl_lon = WELLINGTON
    dawn = _solve_sun_event(np.full(len(cand), wl_lat), np.full(len(cand), wl_lon),
                            D_tt - wl_lon / 360.0 + 5.0 / 24.0, H0_DAWN, evening=False)

    # --- clause B: sunset of local date D-1 at the westernmost mainland point of each latitude
    n, m = len(cand), len(clat)
    LAT = np.broadcast_to(clat, (n, m)).ravel()
    LON = np.broadcast_to(clon, (n, m)).ravel()
    guess = (np.repeat(D_tt, m) - 1.0) + (18.0 / 24.0) - LON / 360.0     # 18:00 local mean time on D-1
    tB = np.empty_like(guess)
    altB = np.empty_like(guess)
    elB = np.empty_like(guess)
    CH = 200_000
    for a in range(0, len(guess), CH):
        sl = slice(a, a + CH)
        tt = _solve_sun_event(LAT[sl], LON[sl], guess[sl], H0_SUNSET, evening=True)
        r_s, d_s, r_m, d_m, dist, g = _eq(np.where(np.isfinite(tt), tt, guess[sl]))
        tB[sl] = tt
        elB[sl] = _elong(r_s, d_s, r_m, d_m)
        altB[sl] = _topo_alt(LAT[sl], LON[sl], g, r_m, d_m, dist)
        if progress:
            print("clause B", a, "/", len(guess))
    tB, altB, elB = tB.reshape(n, m), altB.reshape(n, m), elB.reshape(n, m)
    okB = np.isfinite(tB) & (ctt[:, None] < tB) & (altB >= 5.0) & (elB >= 8.0)
    passB = okB.any(axis=1) & (ctt < dawn)

    # first passing D per new moon
    passed = passA | passB
    out = {}
    for k, (i, d) in enumerate(cand):
        if i in out or not passed[k]:
            continue
        if passA[k]:
            how = (f"A: Moon {altA_max[k]:.1f} deg high and {elong_A[k]:.1f} deg from the Sun at sunset, "
                   f"latitude {lat_a[best_i[k]]:+.0f}, longitude {lon_set[k, best_i[k]]:+.0f}, before 00:00 UT")
            clause = "A"
        else:
            j = int(np.argmax(np.where(okB[k], altB[k], -99)))
            how = (f"B: Moon {altB[k, j]:.1f} deg high and {elB[k, j]:.1f} deg from the Sun at sunset on the "
                   f"Americas mainland, latitude {clat[j]:+.0f}, longitude {clon[j]:+.1f}")
            clause = "B"
        out[i] = (d, clause, how)
    for i, c in enumerate(conj):
        if i not in out:      # should not happen within 4 days; fall back to the 4th day
            out[i] = (c.date() + timedelta(days=5), "-", "no evening within four days met the rule")
        d, clause, how = out[i]
        if start <= d <= end:
            rows.append({"start": d.isoformat(), "conj_utc": c.isoformat(), "clause": clause, "how": how})
    return pd.DataFrame(rows)


def build_table() -> None:
    os.makedirs(DATA, exist_ok=True)
    compute_starts().to_csv(STARTS_FILE, index=False)


@lru_cache(maxsize=1)
def starts_table() -> pd.DataFrame:
    if not os.path.exists(STARTS_FILE):
        build_table()
    df = pd.read_csv(STARTS_FILE)
    df["start"] = pd.to_datetime(df["start"]).dt.date
    return df


# ----------------------------------------------------------------------------------------------
# the calendar
# ----------------------------------------------------------------------------------------------
class UnifiedHijriCalendar(LunarCalendar):
    kind = "unified"
    label = "Unified Hijri Calendar (Istanbul 2016)"
    label_ar = "التقويم الهجري الموحد"

    def __init__(self):
        self._set_months(_months())


@lru_cache(maxsize=1)
def _months() -> list[HMonth]:
    import ummalqura_calendar as uq
    ref = uq.UmmAlQuraCalendar("auto")
    df = starts_table()
    starts = list(df["start"])
    out = []
    prev = None
    for k in range(len(starts) - 1):
        s, e = starts[k], starts[k + 1]
        # Hijri label: the Umm al-Qura month whose start is nearest (within 3 days); else continue the count
        lab = None
        for dd in (0, 1, -1, 2, -2, 3, -3):
            hm = ref.month_of(s + timedelta(days=dd))
            if hm is not None and hm.start == s + timedelta(days=dd):
                lab = (hm.year, hm.month)
                break
        if lab is None and prev is not None:
            y, mth = prev
            lab = (y + (mth == 12), mth % 12 + 1)
        if lab is None:
            continue
        if prev is not None and lab == prev:          # never repeat a label
            y, mth = prev
            lab = (y + (mth == 12), mth % 12 + 1)
        row = df.iloc[k]
        note = ("Unified Hijri Calendar (Istanbul 2016): " + str(row["how"]) +
                f". New moon {pd.Timestamp(row['conj_utc']).strftime('%d %b %H:%M')} UT")
        out.append(HMonth(lab[0], lab[1], s, (e - s).days, note,
                          {"clause": row["clause"], "conj_utc": pd.Timestamp(row["conj_utc"]).to_pydatetime()}))
        prev = lab
    return out
