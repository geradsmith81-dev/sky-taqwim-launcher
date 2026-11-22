"""
The Umm al-Qura calendar of Saudi Arabia (التقويم أم القرى).

The civil calendar of the Kingdom, computed in advance by King Abdulaziz City for Science and
Technology (KACST) for the Kaaba in Mecca. Rule in force since 1423 AH (15 March 2002), as
documented by R. H. van Gent ("The Umm al-Qura calendar of Saudi Arabia", Utrecht University):

    If on the 29th day of the month (a) the geocentric conjunction occurs before sunset at
    Mecca and (b) the Moon sets after the Sun at Mecca, the next day is the 1st of the new
    month. Otherwise the month has 30 days.

Earlier rules: 1420-1422 AH, moonset after sunset at Mecca only (so a month could begin before
the conjunction); before 1420 AH, a rule based on the Moon's age at sunset (12 hours or more),
apparently not computed for Mecca. The published tables of those years also contain a few
months of 28 or 31 days.

Sources of dates (option `source`):
* "official"  the published table as carried by the hijri-converter package
              (1 Muharram 1343 = 1 Aug 1924 .. 30 Dhu al-Hijjah 1500 = 16 Nov 2077);
* "computed"  the current rule applied with NASA JPL DE440s to every month 1850-2150;
* "auto"      (default) the official table where it exists, computed elsewhere.

The Saudi religious dates - the start of Ramadan, the Eids, the days of the Hajj - are not
taken from this table. The Supreme Court declares them from reported sightings of the
crescent, so they can differ from Umm al-Qura by a day (usually a day earlier or later at
the start of Ramadan, Shawwal or Dhu al-Hijjah).

Computation notes: sunset and moonset are for a sea-level horizon at the Kaaba
(21.4225 N, 39.8262 E) with standard refraction; KACST's exact horizon model is not published.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from functools import lru_cache

import crescent_data as cdat
import sky_engine as se
from hijri_core import MONTHS, HMonth, LunarCalendar

SOURCES = {
    "auto": "Official table where published (1343-1500 AH), JPL computation elsewhere",
    "official": "Official table only (1343-1500 AH, 1924-2077)",
    "computed": "Computed from NASA JPL with the current rule (1850-2150)",
}
RULE_SINCE = (1423, 1)        # first month of the current rule


def _fmt_utc(x) -> str:
    return f"{x:%H:%M} UT" if x is not None else "?"


# ----------------------------------------------------------------------------------------------
# official table (hijri-converter)
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _official() -> dict:
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            from hijridate import Hijri            # the maintained name of the same package
        except ImportError:
            from hijri_converter import Hijri      # its earlier name (deprecated)
    out = {}
    for y in range(1343, 1501):
        for m in range(1, 13):
            h = Hijri(y, m, 1)
            out[(y, m)] = (h.to_gregorian(), h.month_length())
    return out


def official_table_month(y: int, m: int) -> HMonth | None:
    """Month (y, m) as published in the official Umm al-Qura table, or None outside 1343-1500 AH."""
    v = _official().get((y, m))
    if v is None:
        return None
    s, n = v
    s = date(s.year, s.month, s.day)
    return HMonth(y, m, s, n, note="Official Umm al-Qura table (KACST), as published",
                  extra={"source": "official"})


# ----------------------------------------------------------------------------------------------
# computation with the current rule
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _index() -> cdat.EveningIndex:
    return cdat.EveningIndex(cdat.mecca_crescents())


def rule_on(day29: date) -> tuple[bool, dict]:
    """Apply the current rule on the civil date `day29` (the 29th day of a month).
    Returns (new month tomorrow?, details)."""
    ix = _index()
    r = ix.row(day29)
    if r is None:
        k = ix.days_since_conj(day29)
        ok = k is not None and k >= 3          # Moon well past conjunction
        return ok, {"day29": day29, "conj_utc": None, "sunset_utc": None, "moonset_utc": None,
                    "lag_min": None, "conj_before_sunset": ok, "moon_sets_after_sun": ok}
    conj = r["conj_utc"].to_pydatetime()
    sunset = r["sunset_utc"].to_pydatetime()
    lag = r["lag_min"]
    c1 = conj < sunset
    c2 = bool(lag == lag and lag > 0)
    ms = r["moonset_utc"]
    return c1 and c2, {"day29": day29, "conj_utc": conj, "sunset_utc": sunset,
                       "moonset_utc": None if ms is None or ms != ms else ms.to_pydatetime(),
                       "lag_min": None if lag != lag else float(lag),
                       "conj_before_sunset": c1, "moon_sets_after_sun": c2}


def _note(ok: bool, info: dict, prev_name: str) -> str:
    d29 = info["day29"]
    if info["conj_utc"] is None:
        return (f"Umm al-Qura rule met on 29 {prev_name} ({d29:%a %d %b %Y}): Moon well past new moon"
                if ok else f"Umm al-Qura rule not met on 29 {prev_name} ({d29:%a %d %b %Y}): "
                           "new moon still to come; month completed to 30 days")
    parts = [f"new moon {info['conj_utc']:%d %b %H:%M} UT "
             f"{'before' if info['conj_before_sunset'] else 'after'} sunset ({_fmt_utc(info['sunset_utc'])})"]
    lag = info["lag_min"]
    if lag is not None:
        parts.append(f"Moon set {abs(lag):.0f} min {'after' if lag > 0 else 'before'} the Sun")
    else:
        parts.append("Moon set before the Sun")
    head = (f"Umm al-Qura rule met on 29 {prev_name} ({d29:%a %d %b %Y}) at Mecca: " if ok else
            f"Umm al-Qura rule not met on 29 {prev_name} ({d29:%a %d %b %Y}) at Mecca: ")
    return head + "; ".join(parts) + ("" if ok else ". The month before was completed to 30 days")


def _chain(start: date, year: int, month: int, until: date) -> list[HMonth]:
    """Months computed with the current rule from a known 1st day (start = 1 month/year)."""
    out = []
    d1, y, m = start, year, month
    note, extra = "", {}
    while True:
        day29 = d1 + timedelta(days=28)
        if day29 > _index().last_evening or d1 > until:
            break
        ok, info = rule_on(day29)
        n = 29 if ok else 30
        out.append(HMonth(y, m, d1, n, note=note, extra=extra))
        note = _note(ok, info, MONTHS[m - 1][0])
        extra = {"source": "computed", **info, "rule_met": ok}
        d1 = d1 + timedelta(days=n)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


@lru_cache(maxsize=1)
def computed_months() -> tuple:
    """All months 1850-2150 with the current rule, numbered from the tabular calendar."""
    from tabular_calendar import to_ordinal
    ix = _index()
    df = ix.df
    # first month start: the day after the first evening that meets the rule
    first = None
    for e in df["evening"]:
        ok, _ = rule_on(e)
        if ok:
            first = e + timedelta(days=1)
            break
    # name it after the tabular month starting nearest to it
    best = None
    for y in range(1265, 1268):
        for m in range(1, 13):
            s = date.fromordinal(to_ordinal(y, m, 1))
            if best is None or abs((s - first).days) < abs((best[2] - first).days):
                best = (y, m, s)
    y, m, _ = best
    months = _chain(first, y, m, cdat.MECCA_SPAN[1])
    for mo in months:
        mo.extra.setdefault("source", "computed")
    return tuple(months)


def computed_month(y: int, m: int) -> HMonth | None:
    for mo in computed_months():
        if (mo.year, mo.month) == (y, m):
            return mo
    return None


# ----------------------------------------------------------------------------------------------
class UmmAlQuraCalendar(LunarCalendar):
    kind = "ummalqura"
    label = "Umm al-Qura (Saudi Arabia)"
    label_ar = "تقويم أم القرى"

    def __init__(self, source: str = "auto"):
        if source not in SOURCES:
            raise ValueError(f"source must be one of {list(SOURCES)}")
        self.source = source
        self._set_months(list(_build(source)))

    def is_official(self, y: int, m: int) -> bool:
        return (y, m) in _official()


@lru_cache(maxsize=3)
def _build(source: str) -> tuple:
    comp = list(computed_months())
    if source == "computed":
        return tuple(comp)
    off = [official_table_month(y, m) for (y, m) in sorted(_official())]
    if source == "official":
        return tuple(off)
    # auto: computed months before 1343, official 1343-1500, computed again after 1500
    o0, o1 = off[0], off[-1]
    before = [replace(mo, extra=dict(mo.extra)) for mo in comp if mo.start < o0.start]
    if before:
        last = before[-1]
        n = (o0.start - last.start).days
        if n != last.length:
            last.note += f" (length set to {n} days to meet the official table)"
            last.length = n
        before = [mo for mo in before if mo.length > 0]
    after = _chain(o1.end + timedelta(days=1), 1501, 1, cdat.MECCA_SPAN[1])
    if after:
        after[0].note = "First month after the official table; computed with the current rule from here on"
    return tuple(before + off + after)
