"""Validation of the Sky Taqwim engine against independent sources.

Run from the engine folder:  python tools/validate.py
Writes docs/validation_results.json (the numbers quoted in docs/VALIDATION.md). Needs the extra
packages adhanpy, jdatetime and persiantools (pip install adhanpy jdatetime persiantools).
"""
import json
import math
import os
import sys
import time
import warnings
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
warnings.simplefilter("ignore", DeprecationWarning)

import prayer_times as pt  # noqa: E402
import qibla as qb  # noqa: E402
import sighting_calendar as sc  # noqa: E402
import solar_hijri_calendar as shc  # noqa: E402
import tabular_calendar as tc  # noqa: E402
import ummalqura_calendar as uqc  # noqa: E402

R = {"generated": datetime.now().strftime("%Y-%m-%d %H:%M")}


# ------------------------------------------------------------------ 1. Umm al-Qura
def uaq():
    comp = uqc.UmmAlQuraCalendar("computed")
    out = {}
    for name, (y0, y1) in {"1423-1500": (1423, 1500), "1420-1422": (1420, 1422),
                           "1343-1419": (1343, 1419)}.items():
        n, mism, diffs = 0, [], Counter()
        for y in range(y0, y1 + 1):
            for m in range(1, 13):
                o = uqc.official_table_month(y, m)
                c = comp.get_month(y, m)
                n += 1
                dd = (c.start - o.start).days
                diffs[dd] += 1
                py, pm = (y - 1, 12) if m == 1 else (y, m - 1)
                prev = uqc.official_table_month(py, pm)
                if dd and prev is None:          # first month of the table: no 29th day to show
                    mism.append({"month": f"{m}/{y}", "official": str(o.start), "computed_minus_official": dd})
                elif dd:
                    ok, info = uqc.rule_on(prev.start + timedelta(days=28))
                    mism.append({"month": f"{m}/{y}", "official": str(o.start), "computed_minus_official": dd,
                                 "day29_official": str(prev.start + timedelta(days=28)),
                                 "conj_utc": info["conj_utc"].strftime("%Y-%m-%d %H:%M:%S") if info["conj_utc"] else None,
                                 "sunset_utc": info["sunset_utc"].strftime("%H:%M:%S") if info["sunset_utc"] else None,
                                 "lag_min": info["lag_min"]})
        out[name] = {"months": n, "mismatches": len(mism), "diff_hist": dict(sorted(diffs.items())),
                     "list": mism if len(mism) < 20 else mism[:5]}
    # the 1420-1422 rule (moonset after sunset only), for comparison
    n = bad = 0
    for y in range(1420, 1423):
        for m in range(1, 13):
            o = uqc.official_table_month(y, m)
            py, pm = (y - 1, 12) if m == 1 else (y, m - 1)
            prev = uqc.official_table_month(py, pm)
            ok, info = uqc.rule_on(prev.start + timedelta(days=28))
            lag = info["lag_min"]
            ok_old = (lag is not None and lag > 0) if info["conj_utc"] is not None else ok
            pred = prev.start + timedelta(days=29 if ok_old else 30)
            n += 1
            bad += pred != o.start
    out["1420-1422_with_old_rule_moonset_only"] = {"months": n, "mismatches": bad}
    lengths = Counter(uqc.official_table_month(y, m).length for y in range(1343, 1501) for m in range(1, 13))
    out["official_month_lengths"] = dict(sorted(lengths.items()))
    R["ummalqura"] = out


# ------------------------------------------------------------------ 2. tabular
def tabular():
    from convertdate import islamic
    k = tc.TabularCalendar("kuwaiti")
    d, n, bad, rt = date(1850, 1, 1), 0, 0, 0
    first_bad = []
    while d <= date(2149, 12, 31):
        h = k.from_gregorian(d)
        if h is not None:
            n += 1
            if (h.year, h.month, h.day) != islamic.from_gregorian(d.year, d.month, d.day):
                bad += 1
                if len(first_bad) < 5:
                    first_bad.append(str(d))
            if k.to_gregorian(h.year, h.month, h.day) != d:
                rt += 1
        d += timedelta(days=1)
    # Fatimid: against an independent closed formula (leap if (11y + 11) mod 30 < 11; epoch JD 1948438.5)
    f = tc.TabularCalendar("fatimid")

    def fat_jd(y, m, dd):
        return (1948438.5 + (y - 1) * 354 + sum(1 for yy in range(1, y) if (11 * yy + 11) % 30 < 11)
                + math.ceil(29.5 * (m - 1)) + dd - 1)
    nf = badf = 0
    for mo in f.months:
        for dd in (1, mo.length):
            nf += 1
            jd = fat_jd(mo.year, mo.month, dd)
            g = date.fromordinal(int(jd - 1721424.5))
            badf += g != mo.start + timedelta(days=dd - 1)
    # Fatimid vs Kuwaiti day offsets
    off = Counter()
    d = date(1850, 2, 1)
    while d <= date(2149, 11, 30):
        a, b = k.from_gregorian(d), f.from_gregorian(d)
        ja = tc.to_ordinal(a.year, a.month, a.day, "kuwaiti")
        jb = tc.to_ordinal(b.year, b.month, b.day, "kuwaiti")
        off[jb - ja] += 1
        d += timedelta(days=1)
    R["tabular"] = {"kuwaiti_vs_convertdate_days": n, "mismatches": bad, "first_mismatches": first_bad,
                    "round_trip_failures": rt, "years": [k.years()[0], k.years()[-1]],
                    "fatimid_vs_formula_checks": nf, "fatimid_mismatches": badf,
                    "fatimid_minus_kuwaiti_day_count": dict(sorted(off.items()))}


# ------------------------------------------------------------------ 3. solar Hijri
def solar():
    import jdatetime
    from persiantools.jdatetime import JalaliDate
    out = {}
    for rule in shc.RULES:
        cal = shc.SolarHijriCalendar(rule)
        ys = cal.years()
        dj, dp = [], []
        for y in ys:
            nz = cal.nowruz(y)
            a = jdatetime.date(y, 1, 1).togregorian()
            b = JalaliDate(y, 1, 1).to_gregorian()
            if a != nz:
                dj.append((y, str(nz), str(a)))
            if b != nz:
                dp.append((y, str(nz), str(b)))
        out[rule] = {"years": [ys[0], ys[-1]], "n": len(ys), "vs_jdatetime": dj, "vs_persiantools": dp}
    # day-by-day for the default rule
    cal = shc.SolarHijriCalendar()
    d, n, bad = cal.first_day, 0, 0
    while d <= cal.last_day:
        h = cal.from_gregorian(d)
        j = jdatetime.date.fromgregorian(date=d)
        n += 1
        bad += (h.year, h.month, h.day) != (j.year, j.month, j.day)
        d += timedelta(days=1)
    out["daybyday_vs_jdatetime"] = {"days": n, "mismatches": bad}
    # how close the deciding cases are: equinox minus noon (minutes) where rules disagree
    df = shc.season_table()
    eq = df[df["kind"] == 0]
    close = []
    for _, r in eq.iterrows():
        vals = {r["nowruz_true_noon_52.5"], r["nowruz_mean_noon_52.5"], r["nowruz_true_noon_tehran"]}
        if len(vals) > 1:
            n525 = datetime.fromisoformat(r["true_noon_52.5_utc"])
            close.append({"sh_year": int(r["utc"].year - 621), "equinox_utc": r["utc"].strftime("%Y-%m-%d %H:%M"),
                          "minus_true_noon_52.5_min": round((r["utc"].to_pydatetime() - n525).total_seconds() / 60, 1),
                          "true_noon_52.5": r["nowruz_true_noon_52.5"], "mean_noon_52.5": r["nowruz_mean_noon_52.5"],
                          "true_noon_tehran": r["nowruz_true_noon_tehran"]})
    out["rules_disagree"] = close
    out["published_checks"] = {str(y): str(cal.nowruz(y)) for y in (1354, 1358, 1400, 1403, 1404, 1405)}
    R["solar_hijri"] = out


# ------------------------------------------------------------------ 4. prayer times
def praytimes_ref(lat, lon, tzname, d, fajr, isha, maghrib=0.0, isha_min=None, asr_factor=1, midnight="standard"):
    """PrayTimes.org 2.3 algorithm (H. Hosseini), one iteration, as published."""
    rad, deg = math.radians, math.degrees
    fix = lambda a, b: a - b * math.floor(a / b)  # noqa: E731
    dsin = lambda x: math.sin(rad(x))  # noqa: E731
    dcos = lambda x: math.cos(rad(x))  # noqa: E731
    dtan = lambda x: math.tan(rad(x))  # noqa: E731
    darccos = lambda x: deg(math.acos(x))  # noqa: E731
    y, m, dd = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd0 = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + dd + B - 1524.5
    jdate = jd0 - lon / (15 * 24.0)

    def sunpos(jd):
        D = jd - 2451545.0
        g = fix(357.529 + 0.98560028 * D, 360)
        q = fix(280.459 + 0.98564736 * D, 360)
        L = fix(q + 1.915 * dsin(g) + 0.020 * dsin(2 * g), 360)
        e = 23.439 - 0.00000036 * D
        RA = deg(math.atan2(dcos(e) * dsin(L), dcos(L))) / 15
        eqt = q / 15 - fix(RA, 24)
        decl = deg(math.asin(dsin(e) * dsin(L)))
        return decl, eqt

    def midday(t):
        return fix(12 - sunpos(jdate + t)[1], 24)

    def angle_time(angle, t, ccw=False):
        decl = sunpos(jdate + t)[0]
        noon = midday(t)
        x = (-dsin(angle) - dsin(decl) * dsin(lat)) / (dcos(decl) * dcos(lat))
        tt = darccos(x) / 15
        return noon + (-tt if ccw else tt)

    def asr_time(f, t):
        decl = sunpos(jdate + t)[0]
        ang = -deg(math.atan(1 / (f + dtan(abs(lat - decl)))))
        return angle_time(ang, t)

    T = {k: v / 24 for k, v in dict(fajr=5, sunrise=6, dhuhr=12, asr=13, sunset=18, maghrib=18, isha=18).items()}
    out = {"fajr": angle_time(fajr, T["fajr"], True), "sunrise": angle_time(0.833, T["sunrise"], True),
           "dhuhr": midday(T["dhuhr"]), "asr": asr_time(asr_factor, T["asr"]),
           "sunset": angle_time(0.833, T["sunset"]),
           "maghrib": angle_time(maghrib, T["maghrib"]) if maghrib else None,
           "isha": angle_time(isha, T["isha"]) if isha_min is None else None}
    tzoff = datetime(d.year, d.month, d.day, 12, tzinfo=ZoneInfo(tzname)).utcoffset().total_seconds() / 3600
    for k in out:
        if out[k] is not None:
            out[k] += tzoff - lon / 15
    if out["maghrib"] is None:
        out["maghrib"] = out["sunset"]
    if out["isha"] is None:
        out["isha"] = out["maghrib"] + isha_min / 60
    if midnight == "jafari":
        out["midnight"] = out["sunset"] + fix(out["fajr"] - out["sunset"], 24) / 2
    else:
        out["midnight"] = out["sunset"] + fix(out["sunrise"] - out["sunset"], 24) / 2
    return out


CITIES = [("Mecca", 21.4225, 39.8262, "Asia/Riyadh"), ("Cairo", 30.0444, 31.2357, "Africa/Cairo"),
          ("Jakarta", -6.2088, 106.8456, "Asia/Jakarta"), ("New York", 40.7128, -74.0060, "America/New_York"),
          ("Tehran", 35.6892, 51.3890, "Asia/Tehran"), ("Najaf", 31.9961, 44.3146, "Asia/Baghdad")]


def prayers():
    from adhanpy.PrayerTimes import PrayerTimes
    from adhanpy.calculation.CalculationParameters import CalculationParameters
    from adhanpy.calculation.HighLatitudeRule import HighLatitudeRule
    from adhanpy.calculation.Madhab import Madhab
    days = [date(2026, 1, 1) + timedelta(days=i) for i in range(365)]
    res = {"adhanpy": {}, "praytimes": {}, "timing_s": {}}
    sunni = ["mwl", "isna", "egypt", "umm_al_qura", "karachi", "kuwait", "qatar", "singapore"]
    for city, lat, lon, tzname in CITIES:
        zone = ZoneInfo(tzname)
        # adhanpy (rounds to the nearest minute)
        for meth in sunni + ["mwl_hanafi"]:
            mkey = "mwl" if meth == "mwl_hanafi" else meth
            M = pt.METHODS[mkey]
            t0 = time.time()
            ours = pt.times_for_days(lat, lon, tzname, days, method=mkey, high_lat="middle_of_night",
                                     asr="hanafi" if meth == "mwl_hanafi" else "standard", ramadan_dates=set())
            res["timing_s"][f"{city}/{meth}/365d"] = round(time.time() - t0, 3)
            worst = Counter()
            for d, o in zip(days, ours):
                p = CalculationParameters(fajr_angle=M["fajr"], isha_angle=M.get("isha", 0.0),
                                          isha_interval=M.get("isha_min", 0))
                p.high_latitude_rule = HighLatitudeRule.MIDDLE_OF_THE_NIGHT
                if meth == "mwl_hanafi":
                    p.madhab = Madhab.HANAFI
                a = PrayerTimes((lat, lon), datetime(d.year, d.month, d.day), calculation_parameters=p,
                                time_zone=zone)
                for k in ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
                    diff = abs((o[k] - getattr(a, k)).total_seconds()) / 60
                    worst[k] = max(worst[k], diff)
            res["adhanpy"][f"{city}/{meth}"] = {k: round(v, 2) for k, v in worst.items()}
        # PrayTimes.org reference: Shia methods and MWL
        for mkey in ("jafari", "tehran", "mwl"):
            M = pt.METHODS[mkey]
            ours = pt.times_for_days(lat, lon, tzname, days, method=mkey, high_lat="none", ramadan_dates=set())
            worst = Counter()
            for d, o in zip(days, ours):
                ref = praytimes_ref(lat, lon, tzname, d, M["fajr"], M.get("isha"), M.get("maghrib", 0.0),
                                    M.get("isha_min"), 1, M["midnight"])
                # compare in UT: PrayTimes adds one zone offset (taken at noon) to every time
                base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
                tzoff = datetime(d.year, d.month, d.day, 12, tzinfo=zone).utcoffset().total_seconds() / 3600
                for k in ("fajr", "sunrise", "dhuhr", "asr", "sunset", "maghrib", "isha", "midnight"):
                    ours_h = (o[k] - base).total_seconds() / 3600
                    worst[k] = max(worst[k], abs(ours_h - (ref[k] - tzoff)) * 60)
            res["praytimes"][f"{city}/{mkey}"] = {k: round(v, 2) for k, v in worst.items()}
    t0 = time.time()
    pt.month_table(51.5074, -0.1278, "Europe/London", 2026, 6, method="mwl")
    res["timing_s"]["London/mwl/one month incl. high-latitude rule"] = round(time.time() - t0, 3)
    R["prayer_times"] = res


# ------------------------------------------------------------------ 5. qibla
def qibla_check():
    """Against geographiclib (WGS-84 ellipsoid, Karney 2013) and widely published values."""
    from geographiclib.geodesic import Geodesic
    places = {"London": (51.5074, -0.1278, 118.99), "New York": (40.7128, -74.0060, 58.48),
              "Jakarta": (-6.2088, 106.8456, 295.15), "Kuala Lumpur": (3.1390, 101.6869, None),
              "Istanbul": (41.0082, 28.9784, None), "Tehran": (35.6892, 51.3890, None),
              "Cape Town": (-33.9249, 18.4241, None), "Tokyo": (35.6762, 139.6503, None),
              "Los Angeles": (34.0522, -118.2437, None)}
    out = {}
    for n, (la, lo, pub) in places.items():
        b, dkm = qb.qibla(la, lo)
        g = Geodesic.WGS84.Inverse(la, lo, *qb.KAABA)
        out[n] = {"ours_deg": round(b, 2), "ours_km": round(dkm), "wgs84_deg": round(g["azi1"] % 360, 2),
                  "wgs84_km": round(g["s12"] / 1000), "published_deg": pub}
    R["qibla"] = out


# ------------------------------------------------------------------ 6. sighting calendar
def sighting():
    out = {}
    for crit in sc.CRITERIA:
        t0 = time.time()
        c = sc.SightingCalendar(criterion=crit)
        dt = time.time() - t0
        lens = Counter(m.length for m in c.months)
        out[crit] = {"months": len(c.months), "years": [c.years()[0], c.years()[-1]],
                     "len29": lens[29], "len30": lens[30], "start_minus_ummalqura": c.stats["start_minus_ummalqura"],
                     "beyond_3_days": c.stats["beyond_3_days"], "build_s": round(dt, 2)}
    # stability of the on-demand chain: London with two different spans, overlapping months
    L = sc.PRESETS_BY_NAME["London"]
    t0 = time.time()
    a = sc.SightingCalendar(L, span=(date(2023, 1, 1), date(2029, 12, 31)))
    ta = time.time() - t0
    b = sc.SightingCalendar(L, span=(date(2024, 6, 1), date(2031, 12, 31)))
    common = [(m.year, m.month) for m in a.months if b.get_month(m.year, m.month)]
    diff = [k for k in common if a.get_month(*k).start != b.get_month(*k).start]
    out["london_span_stability"] = {"common_months": len(common), "different_starts": len(diff), "build_s_7y": round(ta, 2),
                                    "start_minus_ummalqura": a.stats["start_minus_ummalqura"]}
    R["sighting"] = out


if __name__ == "__main__":
    for f in (uaq, tabular, solar, prayers, qibla_check, sighting):
        t0 = time.time()
        f()
        print(f.__name__, round(time.time() - t0, 1), "s")
    path = os.path.join(HERE, "docs", "validation_results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(R, fh, indent=1, default=str, ensure_ascii=False)
    print("written:", path)
