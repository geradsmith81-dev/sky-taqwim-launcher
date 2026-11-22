"""
The Iranian solar Hijri calendar (گاه‌شماری هجری خورشیدی), from NASA JPL astronomy.

Official in Iran since the law of 31 March 1925 and used in Afghanistan (with zodiac month
names) since 1922. Year 1 began at the March equinox of 622, the year of the Hijra.

Rule: the year begins on the day of the March (northern spring) equinox if the equinox
falls before noon, otherwise on the next day. Months 1-6 have 31 days, months 7-11 have 30,
and Esfand has 29 days, or 30 when the next Nowruz requires it. There is no leap-year
arithmetic: leap years follow from the equinoxes.

Which noon? The 1925 law refers to the Sun's entry into Aries; the Calendar Center of the
Institute of Geophysics, University of Tehran, reckons the day from true (apparent) solar
noon on the 52.5 E meridian, the meridian of Iran Standard Time (UTC+03:30). That is the
default here ("true_noon_52.5"). Two alternatives can be chosen for comparison:
"mean_noon_52.5" (12:00 Iran Standard Time = 08:30 UT) and "true_noon_tehran" (apparent noon
at Tehran, 51.39 E). They differ only when the equinox falls within some 15 minutes of noon;
docs/VALIDATION.md lists those years.

Years 1229-1528 SH (1850-2150 CE) with de440s.bsp.
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache

import pandas as pd

import sky_engine as se
from hijri_core import HMonth, LunarCalendar

HERE = os.path.dirname(os.path.abspath(__file__))
SEASONS_FILE = os.path.join(HERE, "data", "seasons.csv")
IRST = timezone(timedelta(hours=3, minutes=30))
RULES = {
    "true_noon_52.5": "Equinox before true solar noon on the 52.5 E meridian (Calendar Center, Univ. of Tehran)",
    "mean_noon_52.5": "Equinox before 12:00 Iran Standard Time (mean noon at 52.5 E)",
    "true_noon_tehran": "Equinox before true solar noon in Tehran (51.39 E)",
}
DEFAULT_RULE = "true_noon_52.5"
# Afghan (Dari) month names: the same months named after the signs of the zodiac
AFGHAN_MONTHS = [("Hamal", "حمل"), ("Sawr", "ثور"), ("Jawza", "جوزا"), ("Saratan", "سرطان"),
                 ("Asad", "اسد"), ("Sunbula", "سنبله"), ("Mizan", "میزان"), ("Aqrab", "عقرب"),
                 ("Qaws", "قوس"), ("Jadi", "جدی"), ("Dalw", "دلو"), ("Hut", "حوت")]


def _apparent_noon_utc(d: date, lon: float, lat: float = 35.7) -> datetime:
    """UTC moment of the Sun's upper transit on the IRST civil date d at longitude lon."""
    from skyfield import almanac
    ts, eph, earth, sun, moon = se.bodies()
    topos = se._observer(lat, lon)
    start = datetime(d.year, d.month, d.day, tzinfo=IRST).astimezone(timezone.utc)
    t0, t1 = ts.from_datetime(start), ts.from_datetime(start + timedelta(days=1))
    t, y = almanac.find_discrete(t0, t1, almanac.meridian_transits(eph, sun, topos))
    return [ti.utc_datetime() for ti, yi in zip(t, y) if yi == 1][0]


def build_seasons(start: date = date(1850, 1, 1), end: date = date(2150, 1, 10)) -> None:
    """Write data/seasons.csv: every equinox and solstice, and for each March equinox the
    noons that decide Nowruz and the resulting Nowruz date under each rule."""
    rows = []
    for t, k in se.seasons(start, end):
        row = {"utc": t.isoformat(), "kind": k, "name": se.SEASON_NAMES[k]}
        if k == 0:
            d = t.astimezone(IRST).date()
            n525 = _apparent_noon_utc(d, 52.5)
            nteh = _apparent_noon_utc(d, 51.389)
            nmean = datetime(d.year, d.month, d.day, 12, tzinfo=IRST).astimezone(timezone.utc)
            row.update({"irst_date": d.isoformat(), "true_noon_52.5_utc": n525.isoformat(),
                        "true_noon_tehran_utc": nteh.isoformat(), "mean_noon_52.5_utc": nmean.isoformat()})
            for rule, noon in (("true_noon_52.5", n525), ("mean_noon_52.5", nmean), ("true_noon_tehran", nteh)):
                row[f"nowruz_{rule}"] = (d if t < noon else d + timedelta(days=1)).isoformat()
        rows.append(row)
    os.makedirs(os.path.dirname(SEASONS_FILE), exist_ok=True)
    pd.DataFrame(rows).to_csv(SEASONS_FILE, index=False)


@lru_cache(maxsize=1)
def season_table() -> pd.DataFrame:
    if not os.path.exists(SEASONS_FILE):
        build_seasons()
    df = pd.read_csv(SEASONS_FILE)
    df["utc"] = pd.to_datetime(df["utc"], utc=True, format="ISO8601")
    return df


@lru_cache(maxsize=3)
def nowruz_dates(rule: str = DEFAULT_RULE) -> dict[int, date]:
    """Solar Hijri year -> civil date of 1 Farvardin."""
    df = season_table()
    out = {}
    for _, r in df[df["kind"] == 0].iterrows():
        d = date.fromisoformat(r[f"nowruz_{rule}"])
        out[d.year - 621] = d
    return out


def equinox_utc(sh_year: int) -> datetime | None:
    """The March equinox that begins solar Hijri year `sh_year`."""
    df = season_table()
    sel = df[(df["kind"] == 0) & (df["utc"].dt.year == sh_year + 621)]
    return None if sel.empty else sel["utc"].iloc[0].to_pydatetime()


@lru_cache(maxsize=3)
def _months(rule: str) -> tuple:
    nz = nowruz_dates(rule)
    out = []
    for y in sorted(nz):
        if y + 1 not in nz:
            continue
        s, nxt = nz[y], nz[y + 1]
        eq = equinox_utc(y)
        for m in range(1, 13):
            n = 31 if m <= 6 else 30 if m <= 11 else (nxt - s).days
            note = ""
            if m == 1:
                note = (f"Nowruz: March equinox {eq.astimezone(IRST):%d %b %Y %H:%M} Iran Standard Time "
                        f"({eq:%H:%M} UT)") if eq else "Nowruz"
            out.append(HMonth(y, m, s, n, note=note, calendar="solar",
                              extra={"equinox_utc": eq if m == 1 else None, "leap_year": (nxt - nz[y]).days == 366}))
            s = s + timedelta(days=n)
        if s != nxt:
            raise RuntimeError(f"solar Hijri year {y} does not close")
    return tuple(out)


class SolarHijriCalendar(LunarCalendar):
    """Same interface as the lunar calendars; HDate.calendar == "solar"."""
    kind = "solar_hijri"
    label = "Solar Hijri (Iran, Afghanistan)"
    label_ar = "تقویم هجری خورشیدی"
    calendar = "solar"

    def __init__(self, rule: str = DEFAULT_RULE):
        if rule not in RULES:
            raise ValueError(f"rule must be one of {list(RULES)}")
        self.rule = rule
        self._set_months(list(_months(rule)))

    def is_leap(self, year: int) -> bool:
        return self.year_length(year) == 366

    def nowruz(self, year: int) -> date | None:
        return self.to_gregorian(year, 1, 1)
