"""One interface over the four calendars, used by the pages, and the Sunni / Shia defaults.

Calendars (keys):
  ummalqura  Umm al-Qura, the official calendar of Saudi Arabia (table, or the current rule from JPL)
  sighting   crescent sighting: a month begins after the evening on which the young crescent is
             predicted visible from the chosen place (else the month is completed to 30 days)
  tabular    the arithmetic (30-year cycle) calendar: Kuwaiti / standard, or Fatimid (Bohra)
  solar      the solar Hijri calendar of Iran and Afghanistan (Nowruz at the March equinox)
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from datetime import date, timedelta

import arabic_names as an
import extra_calendars as xc
import hijri_core as hcore
import holidays as hol
import sighting_calendar as sc
import solar_hijri_calendar as shc
import tabular_calendar as tc
import ummalqura_calendar as uq

UMMALQURA, SIGHTING, UNIFIED, TABULAR = "ummalqura", "sighting", "unified", "tabular"
SOLAR, AHMADI, JULIAN = "solar", "ahmadi", "julian"
ALL = [UMMALQURA, SIGHTING, UNIFIED, TABULAR, SOLAR, AHMADI, JULIAN]
LUNAR = [UMMALQURA, SIGHTING, UNIFIED, TABULAR]

NAME = {UMMALQURA: "Umm al-Qura", SIGHTING: "Crescent sighting", UNIFIED: "Unified Hijri", TABULAR: "Tabular",
        SOLAR: "Solar Hijri", AHMADI: "Hijri Shamsi", JULIAN: "Julian (Rumi)"}
NAME_AR = {UMMALQURA: "تقويم أم القرى", SIGHTING: "رؤية الهلال", UNIFIED: "التقويم الهجري الموحد",
           TABULAR: "التقويم الحسابي", SOLAR: "التقويم الهجري الشمسي", AHMADI: "التقويم الهجري الشمسي الأحمدي",
           JULIAN: "التقويم اليولياني (الرومي)"}
HELP = {
    UMMALQURA: "The official calendar of Saudi Arabia, computed in advance for Mecca. The religious dates "
               "(Ramadan, the Eids, the Hajj) are declared there from sightings and can differ by a day.",
    SIGHTING: "Each month begins after the evening on which the young crescent is predicted visible from the "
              "chosen place; if it is not visible on the evening ending the 29th, the month has 30 days.",
    UNIFIED: "One date for the whole world (Istanbul 2016): a month begins when somewhere on Earth, before "
             "midnight UT, the Moon is 5 deg high and 8 deg from the Sun at sunset (or on the Americas mainland "
             "if the new moon came before dawn in New Zealand). Used by Turkey's Diyanet and by Muhammadiyah.",
    TABULAR: "A fixed arithmetic calendar: months of 30 and 29 days in turn, and 11 leap years in every 30.",
    SOLAR: "The official calendar of Iran (and of Afghanistan until 2022). The year begins at the March "
           "equinox (Nowruz). It is a civil calendar; religious days follow the lunar months.",
    AHMADI: "The Ahmadiyya Muslim Community's solar calendar (1940): Gregorian-length months named after events "
            "in the Prophet's life, years counted from the Hijra (2026 = 1405 HS).",
    JULIAN: "The Julian (Eastern, Ottoman 'Rumi') calendar with the Syriac month names of the Levant, 13 days "
            "behind the Gregorian; some Alevi and Alawite feasts are fixed in it.",
}

# ---------------------------------------------------------------------------------------------- branches
BRANCHES = ["sunni", "shia"]
BRANCH_NAME = {"sunni": ("Sunni", "أهل السنة"), "shia": ("Shia", "الشيعة")}

# where the crescent is looked for: "Mecca", "local" (your own place) or a sighting_calendar preset place
DEFAULTS = {
    "sunni": {"calendar": UMMALQURA, "ref": "Mecca", "crit": "yallop_B", "tabular": "kuwaiti", "method": "mwl"},
    "shia": {"calendar": SIGHTING, "ref": "local", "crit": "yallop_B", "tabular": "kuwaiti", "method": "jafari"},
}
CRIT_NOTES = {
    "yallop_B": "naked eye (e.g. Ayatollah Sistani; the Saudi Supreme Court seeks naked-eye or binocular sightings)",
    "odeh_C": "optical aid accepted (e.g. Ayatollah Khamenei)",
    "mabims": "Brunei, Indonesia, Malaysia, Singapore since 2021",
    "wujud": "Muhammadiyah until 2024; the Umm al-Qura rule applied at your place",
    "conjunction": "some groups that count from the astronomical new moon",
}


# ---------------------------------------------------------------------------------------------- views
@dataclass
class View:
    """A calendar plus the holidays of one tradition."""
    key: str
    cal: object
    branch: str
    opts: dict = field(default_factory=dict)
    detail: str = ""          # e.g. "from Mecca, Yallop B"

    @property
    def name(self) -> str:
        if self.key == TABULAR:
            return "Tabular (Fatimid)" if getattr(self.cal, "variant", "") == "fatimid" else "Tabular"
        return NAME[self.key]

    @property
    def name_ar(self) -> str:
        return NAME_AR[self.key]

    @property
    def short(self) -> str:
        return {UMMALQURA: "Umm al-Qura", SIGHTING: "Sighting", UNIFIED: "Unified", TABULAR: "Tabular",
                SOLAR: "Solar", AHMADI: "HS", JULIAN: "Julian"}[self.key]

    @property
    def lunar(self) -> bool:
        return self.key in LUNAR

    @property
    def solar(self) -> bool:
        """True for the civil-day (solar) calendars: solar Hijri, Hijri Shamsi, Julian."""
        return not self.lunar

    @property
    def era(self) -> str:
        return hcore.ERA.get(getattr(self.cal, "calendar", "lunar"), "AH")

    @property
    def lang(self) -> str:
        return {SOLAR: "fa", AHMADI: "ur"}.get(self.key, "ar")

    def digits(self, n) -> str:
        return an.to_persian_digits(n) if self.key in (SOLAR, AHMADI) else an.to_arabic_digits(n)

    @property
    def first_day(self) -> date:
        return self.cal.first_day

    @property
    def last_day(self) -> date:
        return self.cal.last_day

    def covers(self, d: date) -> bool:
        return self.cal.covers(d)

    def hdate(self, d: date):
        return self.cal.from_gregorian(d) if self.cal.covers(d) else None

    def month_at(self, d: date):
        return self.cal.month_of(d)

    def get_month(self, y: int, m: int):
        return self.cal.get_month(y, m)

    def year_months(self, y: int):
        return self.cal.year_months(y)

    def years(self) -> list[int]:
        return self.cal.years()

    def year_of(self, d: date) -> int | None:
        h = self.hdate(d)
        return h.year if h else None

    def month_name(self, m: int) -> tuple[str, str]:
        if self.key == SOLAR:
            return an.SOLAR_MONTHS[m][0], an.SOLAR_MONTHS[m][1]
        if self.lunar:
            return an.MONTHS[m][0], an.MONTHS[m][1]
        c = getattr(self.cal, "calendar", "lunar")
        return hcore.month_name(m, c), hcore.month_ar(m, c)

    def holidays_for_year(self, y: int) -> list:
        if self.key == SOLAR:
            return hol.solar_holidays_for_year(self.cal, y)
        if self.key == AHMADI:
            return xc.ahmadi_days(self.cal, y)
        if self.key == JULIAN:
            return xc.julian_days(self.cal, y)
        return hol.holidays_for_year(self.cal, y, self.branch, **self.opts)

    def holidays_between(self, start: date, end: date) -> list:
        if self.solar:
            out = []
            for y in {self.year_of(start), self.year_of(end)} - {None}:
                out += [h for h in self.holidays_for_year(y) if start <= h.date <= end]
            return sorted(out, key=lambda h: h.date)
        return hol.holidays_between(self.cal, start, end, self.branch, **self.opts)


def sighting_place(ref: str, place: dict) -> tuple[dict | None, str]:
    """The reference place of the sighting calendar: None = Mecca (precomputed), else a place dict."""
    if ref == "Mecca":
        return None, "Mecca"
    if ref == "local":
        return {"name": place.get("name", ""), "lat": float(place["lat"]), "lon": float(place["lon"]),
                "tz": place["tz"]}, place.get("label", place.get("name", "your place"))
    p = sc.PRESETS_BY_NAME[ref]
    return p, p["name"]


def local_span(today: date, years: int = 6) -> tuple[date, date]:
    """The span computed for a sighting calendar at a place other than Mecca."""
    return (date(today.year - years, 1, 1), date(today.year + years, 12, 31))


# ---------------------------------------------------------------------------------------------- export
def to_ics(holidays: list, calname: str) -> str:
    """All-day iCalendar events (the Islamic day starts the evening before; noted in each event)."""
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Sky Taqwim//Islamic calendar//EN",
             "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{esc(calname)}"]
    stamp = date.today().strftime("%Y%m%dT000000Z")
    for h in holidays:
        slug = "".join(c for c in h.name.lower() if c.isalnum())[:40]
        desc = f"{h.hdate} ({calname})" if h.hdate else calname
        if h.begins_evening_before:
            desc += ". Begins at sunset the evening before."
        if h.note:
            desc += f" {h.note}"
        lines += ["BEGIN:VEVENT",
                  f"UID:{h.date:%Y%m%d}-{slug}-{zlib.crc32(calname.encode('utf-8')):08x}@sky-taqwim",
                  f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{h.date:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{(h.date + timedelta(days=1)):%Y%m%d}",
                  f"SUMMARY:{esc(h.name)}",
                  f"DESCRIPTION:{esc(desc)}",
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
