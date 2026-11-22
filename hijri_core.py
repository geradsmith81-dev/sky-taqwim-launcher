"""
Shared types for the Islamic calendars of Sky Taqwim.

* HDate   a date in one of the calendars (lunar Hijri by default; solar Hijri if calendar="solar")
* HMonth  one month of a calendar: its first civil day and its length
* LunarCalendar  the interface every calendar implements, built on a list of HMonth

Day convention: a Gregorian (civil) date d maps to the Islamic day whose DAYTIME is d. The
Islamic day begins at the sunset before, so the evening of d already belongs to the next day.

The month names here are a minimal set so the engine is self-contained; arabic_names.py
(Content track) has the full names, meanings and alternative spellings.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass, field
from datetime import date, timedelta

# (transliteration, Arabic) for months 1..12
MONTHS = [
    ("Muharram", "محرم"),
    ("Safar", "صفر"),
    ("Rabi' al-Awwal", "ربيع الأول"),
    ("Rabi' al-Thani", "ربيع الآخر"),
    ("Jumada al-Ula", "جمادى الأولى"),
    ("Jumada al-Akhirah", "جمادى الآخرة"),
    ("Rajab", "رجب"),
    ("Sha'ban", "شعبان"),
    ("Ramadan", "رمضان"),
    ("Shawwal", "شوال"),
    ("Dhu al-Qa'dah", "ذو القعدة"),
    ("Dhu al-Hijjah", "ذو الحجة"),
]
# Iranian solar Hijri months (transliteration, Persian)
SOLAR_MONTHS = [
    ("Farvardin", "فروردین"),
    ("Ordibehesht", "اردیبهشت"),
    ("Khordad", "خرداد"),
    ("Tir", "تیر"),
    ("Mordad", "مرداد"),
    ("Shahrivar", "شهریور"),
    ("Mehr", "مهر"),
    ("Aban", "آبان"),
    ("Azar", "آذر"),
    ("Dey", "دی"),
    ("Bahman", "بهمن"),
    ("Esfand", "اسفند"),
]
# Ahmadiyya Hijri Shamsi months (same lengths as the Gregorian months), transliteration and Urdu script;
# order as in The Review of Religions (Ahmadiyya), July 2008: ... Zuhur, Tabuk, Ikha, Nabuwwat, Fatah
AHMADI_MONTHS = [
    ("Sulh", "صلح"), ("Tabligh", "تبلیغ"), ("Aman", "امان"), ("Shahadat", "شہادت"), ("Hijrat", "ہجرت"),
    ("Ihsan", "احسان"), ("Wafa", "وفا"), ("Zuhur", "ظہور"), ("Tabuk", "تبوک"), ("Ikha", "اخاء"),
    ("Nabuwwat", "نبوت"), ("Fatah", "فتح"),
]
# Julian (Eastern, 'Rumi') months with their Syriac-derived Arabic names, as used in the Levant and Iraq
JULIAN_MONTHS = [
    ("Kanun al-Thani", "كانون الثاني"), ("Shubat", "شباط"), ("Adhar", "آذار"), ("Nisan", "نيسان"),
    ("Ayyar", "أيار"), ("Huzayran", "حزيران"), ("Tammuz", "تموز"), ("Ab", "آب"), ("Aylul", "أيلول"),
    ("Tishrin al-Awwal", "تشرين الأول"), ("Tishrin al-Thani", "تشرين الثاني"), ("Kanun al-Awwal", "كانون الأول"),
]
CALENDAR_MONTHS = {"lunar": MONTHS, "solar": SOLAR_MONTHS, "ahmadi": AHMADI_MONTHS, "julian": JULIAN_MONTHS}
ERA = {"lunar": "AH", "solar": "SH", "ahmadi": "HS", "julian": "O.S."}

(MUHARRAM, SAFAR, RABI_I, RABI_II, JUMADA_I, JUMADA_II, RAJAB, SHABAN, RAMADAN, SHAWWAL,
 DHU_AL_QADAH, DHU_AL_HIJJAH) = range(1, 13)

ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")     # Arabic-Indic
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")    # Extended Arabic-Indic


def arabic_digits(n) -> str:
    return str(n).translate(ARABIC_DIGITS)


def persian_digits(n) -> str:
    return str(n).translate(PERSIAN_DIGITS)


def month_name(month: int, calendar: str = "lunar") -> str:
    return CALENDAR_MONTHS.get(calendar, MONTHS)[month - 1][0]


def month_ar(month: int, calendar: str = "lunar") -> str:
    return CALENDAR_MONTHS.get(calendar, MONTHS)[month - 1][1]


@dataclass(frozen=True, order=True)
class HDate:
    year: int
    month: int
    day: int
    calendar: str = "lunar"      # "lunar" (AH), "solar" (Iranian SH), "ahmadi" (HS) or "julian" (O.S.)

    @property
    def month_name(self) -> str:
        return month_name(self.month, self.calendar)

    @property
    def month_ar(self) -> str:
        """Month name in the original script (Arabic; Persian for the solar calendar)."""
        return month_ar(self.month, self.calendar)

    @property
    def era(self) -> str:
        return ERA.get(self.calendar, "AH")

    def __str__(self) -> str:
        return f"{self.day} {self.month_name} {self.year} {self.era}"

    def arabic(self) -> str:
        """'١٤ رمضان ١٤٤٧ هـ'; for the solar calendar Persian digits and 'ه‍.ش.'"""
        if self.calendar == "solar":
            return f"{persian_digits(self.day)} {self.month_ar} {persian_digits(self.year)} ه‍.ش."
        if self.calendar == "ahmadi":
            return f"{persian_digits(self.day)} {self.month_ar} {persian_digits(self.year)} ہش"
        if self.calendar == "julian":
            return f"{arabic_digits(self.day)} {self.month_ar} {arabic_digits(self.year)} (شرقي)"
        return f"{arabic_digits(self.day)} {self.month_ar} {arabic_digits(self.year)} هـ"


@dataclass
class HMonth:
    year: int
    month: int
    start: date              # civil date whose daytime is day 1
    length: int              # 29 or 30 (solar: 29-31)
    note: str = ""           # how the month began, in plain English
    extra: dict = field(default_factory=dict)
    calendar: str = "lunar"

    @property
    def end(self) -> date:
        return self.start + timedelta(days=self.length - 1)

    @property
    def name(self) -> str:
        return month_name(self.month, self.calendar)

    @property
    def name_ar(self) -> str:
        return month_ar(self.month, self.calendar)

    @property
    def title(self) -> str:
        return f"{self.name} {self.year}"


class LunarCalendar:
    """Base class: a calendar given as a gapless, ordered list of months (self.months).

    Subclasses set `kind`, `label`, `label_ar`, and call self._set_months(list_of_HMonth).
    Only complete years (all 12 months present) are listed by years().
    """
    kind = "base"
    label = ""
    label_ar = ""
    calendar = "lunar"

    def _set_months(self, months: list[HMonth]) -> None:
        months = sorted(months, key=lambda m: m.start)
        for a, b in zip(months, months[1:]):
            if a.start + timedelta(days=a.length) != b.start:
                raise RuntimeError(f"gap or overlap between {a.title} and {b.title}")
        self.months = months
        self._starts = [m.start for m in months]
        self._by = {(m.year, m.month): m for m in months}

    # coverage
    @property
    def first_day(self) -> date:
        return self.months[0].start

    @property
    def last_day(self) -> date:
        return self.months[-1].end

    def covers(self, d: date) -> bool:
        return self.first_day <= d <= self.last_day

    # conversion
    def month_of(self, d: date) -> HMonth | None:
        if not self.covers(d):
            return None
        return self.months[bisect.bisect_right(self._starts, d) - 1]

    def from_gregorian(self, d: date) -> HDate | None:
        m = self.month_of(d)
        if m is None:
            return None
        return HDate(m.year, m.month, (d - m.start).days + 1, self.calendar)

    def to_gregorian(self, year: int, month: int, day: int) -> date | None:
        m = self._by.get((year, month))
        if m is None or not 1 <= day <= m.length:
            return None
        return m.start + timedelta(days=day - 1)

    def get_month(self, year: int, month: int) -> HMonth | None:
        return self._by.get((year, month))

    # years
    def year_months(self, year: int) -> list[HMonth]:
        return [self._by[(year, m)] for m in range(1, 13) if (year, m) in self._by]

    def year_complete(self, year: int) -> bool:
        return all((year, m) in self._by for m in range(1, 13))

    def years(self) -> list[int]:
        return sorted({y for (y, m) in self._by if self.year_complete(y)})

    def year_length(self, year: int) -> int | None:
        if not self.year_complete(year):
            return None
        return sum(m.length for m in self.year_months(year))

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.kind} {self.first_day}..{self.last_day}>"
