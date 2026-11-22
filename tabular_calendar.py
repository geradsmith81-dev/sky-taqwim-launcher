"""
Tabular (arithmetical) Islamic calendars: a 30-year cycle of 19 common years (354 days) and
11 leap years (355 days). Odd months have 30 days, even months 29; in a leap year Dhu al-Hijjah
has 30 days. The mean month is 29.530556 days, 2.9 s longer than the mean synodic month, so the
scheme gains one day on the Moon in about 2,500 years.

Variants (names after R. H. van Gent, "The Islamic calendar - arithmetical schemes",
Utrecht University; E. M. Reingold and N. Dershowitz, Calendrical Calculations, 4th ed.,
Cambridge 2018, ch. 7):

* "kuwaiti"  van Gent's Type II, the most widely used scheme (also the "Kuwaiti algorithm" of
             Microsoft software and the arithmetic Islamic calendar of Reingold & Dershowitz).
             Leap years 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29 of each cycle. Civil epoch:
             1 Muharram 1 AH = Friday 16 July 622 (Julian). convertdate.islamic uses the same
             scheme and epoch (JD 1948439.5); docs/VALIDATION.md compares them day by day.
* "fatimid"  van Gent's Type III, the Fatimid or "Misri" reckoning kept by the Isma'ili
             Dawoodi Bohras. Leap years 2, 5, 8, 10, 13, 16, 19, 21, 24, 27, 29.
             Astronomical epoch: 1 Muharram 1 AH = Thursday 15 July 622 (Julian).
             Bohra practice also fixes its own festival rules; the dates here are the plain
             tabular dates.

The range is limited to 1 Jan 1850 - 31 Dec 2149, as for the other calendars of the app.
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

from hijri_core import HDate, HMonth, LunarCalendar

VARIANTS = {
    "kuwaiti": {
        "label": "Tabular (standard 30-year cycle)",
        "label_ar": "التقويم الهجري الحسابي",
        "leaps": (2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29),
        # 16 July 622 Julian = 19 July 622 proleptic Gregorian (a Friday)
        "epoch": date(622, 7, 19),
        "epoch_note": "civil epoch, Friday 16 July 622 (Julian)",
    },
    "fatimid": {
        "label": "Tabular, Fatimid (Misri) reckoning",
        "label_ar": "الحساب الفاطمي (المصري)",
        "leaps": (2, 5, 8, 10, 13, 16, 19, 21, 24, 27, 29),
        # 15 July 622 Julian = 18 July 622 proleptic Gregorian (a Thursday)
        "epoch": date(622, 7, 18),
        "epoch_note": "astronomical epoch, Thursday 15 July 622 (Julian)",
    },
}
RANGE = (date(1850, 1, 1), date(2149, 12, 31))


def _leaps_before(year: int, leaps: tuple) -> int:
    """Number of leap years among years 1 .. year-1."""
    cycles, r = divmod(year - 1, 30)
    return cycles * 11 + sum(1 for k in leaps if k <= r)


def is_leap(year: int, variant: str = "kuwaiti") -> bool:
    return ((year - 1) % 30 + 1) in VARIANTS[variant]["leaps"]


def month_length(year: int, month: int, variant: str = "kuwaiti") -> int:
    if month == 12:
        return 30 if is_leap(year, variant) else 29
    return 30 if month % 2 == 1 else 29


def to_ordinal(year: int, month: int, day: int, variant: str = "kuwaiti") -> int:
    """Python date ordinal of a tabular Hijri date (arithmetic, no range limit)."""
    v = VARIANTS[variant]
    days = (year - 1) * 354 + _leaps_before(year, v["leaps"])
    days += sum(30 if m % 2 == 1 else 29 for m in range(1, month))
    return v["epoch"].toordinal() + days + day - 1


@lru_cache(maxsize=4)
def _months(variant: str) -> tuple:
    lo, hi = RANGE
    # first year whose 1 Muharram is on or before lo
    y = int((lo.toordinal() - VARIANTS[variant]["epoch"].toordinal()) / 354.3667) - 1
    out = []
    while True:
        for m in range(1, 13):
            s = date.fromordinal(to_ordinal(y, m, 1, variant))
            n = month_length(y, m, variant)
            if s + timedelta(days=n - 1) < lo:
                continue
            if s > hi:
                return tuple(out)
            out.append(HMonth(y, m, s, n, note="Fixed arithmetic rule (30-year cycle)",
                              extra={"leap_year": is_leap(y, variant)}))
        y += 1


class TabularCalendar(LunarCalendar):
    def __init__(self, variant: str = "kuwaiti"):
        if variant not in VARIANTS:
            raise ValueError(f"unknown variant {variant!r}; choose from {list(VARIANTS)}")
        self.variant = variant
        self.kind = f"tabular_{variant}"
        self.label = VARIANTS[variant]["label"]
        self.label_ar = VARIANTS[variant]["label_ar"]
        months = list(_months(variant))
        # clip to whole months inside RANGE
        months = [m for m in months if m.start >= RANGE[0] and m.end <= RANGE[1]]
        self._set_months(months)

    def is_leap(self, year: int) -> bool:
        return is_leap(year, self.variant)

    def from_gregorian(self, d: date) -> HDate | None:
        return super().from_gregorian(d)
