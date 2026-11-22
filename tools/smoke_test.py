"""Smoke test: every calendar for today and for 1 Ramadan 1447, prayer times and the qibla.

Run from the engine folder:  python tools/smoke_test.py
"""
import os
import sys
import time
from collections import Counter
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prayer_times as pt  # noqa: E402
import qibla as qb  # noqa: E402
import sighting_calendar as sc  # noqa: E402
import sky_engine as se  # noqa: E402
from solar_hijri_calendar import SolarHijriCalendar  # noqa: E402
from tabular_calendar import TabularCalendar  # noqa: E402
from ummalqura_calendar import UmmAlQuraCalendar  # noqa: E402


def timed(label, f):
    t = time.time()
    v = f()
    print(f"  [{time.time() - t:5.2f} s] {label}")
    return v


def main():
    today = date.today()
    print("Ephemeris:", se.load()[2], se.ephemeris_range())
    cals = {
        "Umm al-Qura (auto)": timed("Umm al-Qura auto", lambda: UmmAlQuraCalendar("auto")),
        "Umm al-Qura (computed)": timed("Umm al-Qura computed", lambda: UmmAlQuraCalendar("computed")),
        "Tabular Kuwaiti": timed("tabular kuwaiti", lambda: TabularCalendar("kuwaiti")),
        "Tabular Fatimid": timed("tabular fatimid", lambda: TabularCalendar("fatimid")),
        "Sighting Mecca (Yallop B)": timed("sighting Mecca", lambda: sc.SightingCalendar()),
        "Sighting Najaf (Odeh A)": timed("sighting Najaf 6 y", lambda: sc.SightingCalendar(
            sc.PRESETS_BY_NAME["Najaf"], "odeh_A")),
        "Sighting London (Odeh C)": timed("sighting London 6 y", lambda: sc.SightingCalendar(
            sc.PRESETS_BY_NAME["London"], "odeh_C")),
    }
    print(f"\nToday {today:%a %d %b %Y}:")
    for name, c in cals.items():
        h = c.from_gregorian(today)
        m = c.month_of(today)
        print(f"  {name:28s} {h!s:28s} {h.arabic():24s} month {m.start}..{m.end} ({m.length} d)")
        assert c.to_gregorian(h.year, h.month, h.day) == today
    print("\n1 Ramadan 1447:")
    for name, c in cals.items():
        g = c.to_gregorian(1447, 9, 1)
        m = c.get_month(1447, 9)
        print(f"  {name:28s} {g:%a %d %b %Y}  ({m.length} days)  {m.note[:110]}")
        assert c.from_gregorian(g) is not None and c.from_gregorian(g).day == 1
    s = timed("solar Hijri", SolarHijriCalendar)
    h = s.from_gregorian(today)
    print(f"\nSolar Hijri today: {h}  {h.arabic()};  Nowruz {h.year}: {s.nowruz(h.year)}  "
          f"({s.get_month(h.year, 1).note})")
    assert s.to_gregorian(h.year, h.month, h.day) == today
    for name, c in list(cals.items())[:4] + [("Solar Hijri", s)]:
        ys = c.years()
        lens = Counter(c.year_length(y) for y in ys)
        assert set(lens) <= {353, 354, 355, 356, 365, 366}, (name, lens)
        print(f"  {name:28s} complete years {ys[0]}..{ys[-1]}; year lengths {dict(sorted(lens.items()))}")
    print("\nPrayer times today:")
    for place, meth in [("Mecca", "umm_al_qura"), ("Najaf", "jafari"), ("Tehran", "tehran"),
                        ("Istanbul", "diyanet"), ("London", "mwl"), ("Jakarta", "singapore")]:
        p = sc.PRESETS_BY_NAME[place]
        r = timed(f"{place} {meth} 1 day", lambda: pt.times_for_days(p["lat"], p["lon"], p["tz"], [today], method=meth))[0]
        print("   ", place, meth, " ".join(f"{k}={r[k]:%H:%M}" if r[k] else f"{k}=-" for k in pt.KEYS))
    m = timed("one month, London MWL", lambda: pt.month_table(51.5074, -0.1278, "Europe/London", today.year, 6))
    assert len(m) == 30 and all(r["fajr"] for r in m)
    print("\nQibla:")
    for place in ("London", "New York", "Jakarta", "Najaf", "Mecca"):
        p = sc.PRESETS_BY_NAME[place]
        print(f"  {place:10s} {qb.describe(p['lat'], p['lon'])}")
    info = sc.evening_info(cals["Umm al-Qura (auto)"].to_gregorian(1447, 9, 1) - timedelta(days=1))
    print("\nCrescent at Mecca on the eve of 1 Ramadan 1447 (Umm al-Qura):",
          {k: info[k] for k in ("evening", "lag_min", "age_h", "q", "yallop", "v", "odeh")} if info else None)
    print("\nOK")


if __name__ == "__main__":
    main()
