"""
Two solar calendars kept by particular communities, and their fixed days.

* AhmadiHijriShamsiCalendar - the Hijri Shamsi (solar Hijra) calendar of the Ahmadiyya Muslim Community,
  introduced in 1940 under Mirza Bashir-ud-Din Mahmud Ahmad. Its months have the lengths and limits of the
  Gregorian months and are named after events in the Prophet's life; years are counted from the Hijra of
  622 in solar years, so 2000 CE = 1379 HS and 2008 CE = 1387 HS (Gregorian year minus 621). Month order
  as printed by The Review of Religions (July 2008); some lists swap Tabuk (Sept) and Ikha (Oct).
  Ahmadi religious months (Ramadan, the Eids) still follow the lunar Hijri calendar.

* JulianCalendar - the Julian ('Eastern', in the Ottoman state 'Rumi') reckoning with the Syriac-derived
  month names of the Levant and Iraq. Several folk and religious days kept by Alevi-Bektashi and Alawite
  communities are fixed in it, e.g. Hidirellez on 23 Nisan (April) Julian = 6 May Gregorian (1900-2099),
  and the Alawite Nawruz (4 Nisan) and Mihrajan (16 Tishrin al-Awwal) of the Nusayri solar calendar
  (Y. Friedman, The Nusayri-Alawis, Brill 2010, ch. 2).
  Days run midnight to midnight.
"""
from __future__ import annotations

from datetime import date, timedelta

from hijri_core import HDate, HMonth, LunarCalendar

FIRST, LAST = date(1850, 1, 1), date(2149, 12, 31)


def _greg_month_len(y: int, m: int) -> int:
    nxt = date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - date(y, m, 1)).days


class AhmadiHijriShamsiCalendar(LunarCalendar):
    kind = "ahmadi"
    label = "Hijri Shamsi (Ahmadiyya)"
    label_ar = "التقويم الهجري الشمسي الأحمدي"
    calendar = "ahmadi"
    OFFSET = 621

    def __init__(self):
        months = []
        for y in range(FIRST.year, LAST.year + 1):
            for m in range(1, 13):
                months.append(HMonth(y - self.OFFSET, m, date(y, m, 1), _greg_month_len(y, m),
                                     "Hijri Shamsi: the month has the same days as the Gregorian month", {}, "ahmadi"))
        self._set_months(months)


def julian_to_gregorian(y: int, m: int, d: int) -> date:
    """Civil (proleptic Gregorian) date of a Julian calendar date."""
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
    return date.fromordinal(jdn - 1721425)


def julian_month_len(y: int, m: int) -> int:
    return [31, 29 if y % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]


class JulianCalendar(LunarCalendar):
    kind = "julian"
    label = "Julian (Eastern / Rumi)"
    label_ar = "التقويم اليولياني (الشرقي)"
    calendar = "julian"

    def __init__(self):
        months = []
        for y in range(FIRST.year, LAST.year + 1):
            for m in range(1, 13):
                s = julian_to_gregorian(y, m, 1)
                diff = (s - date(y, m, 1)).days
                months.append(HMonth(y, m, s, julian_month_len(y, m),
                                     f"Julian reckoning: {diff} days behind the Gregorian calendar this month", {}, "julian"))
        self._set_months(months)


# ---------------------------------------------------------------------------------------------- fixed days
def _hol(d, name, ar, note, key, h):
    import holidays as hol
    return hol.Holiday(d, name, ar, "civil", h, note, key, False, "both")


def ahmadi_days(cal: AhmadiHijriShamsiCalendar, year: int) -> list:
    """Days the Ahmadiyya Muslim Community marks on fixed Gregorian dates, in Hijri Shamsi year `year`."""
    gy = year + cal.OFFSET
    out = []
    for (m, d, name, ar, note) in [
        (2, 20, "Musleh Maud Day", "یوم مصلح موعود",
         "Recalls the prophecy of 20 February 1886 of a 'Promised Son', fulfilled for Ahmadis in Mirza Bashir-ud-Din Mahmud Ahmad."),
        (3, 23, "Promised Messiah Day", "یوم مسیح موعود",
         "The first oath of allegiance (bai'at) to Mirza Ghulam Ahmad at Ludhiana, 23 March 1889."),
        (5, 27, "Khilafat Day", "یوم خلافت",
         "The election of the first successor (Khalifat al-Masih I), Hakim Nur-ud-Din, on 27 May 1908."),
    ]:
        g = date(gy, m, d)
        out.append(_hol(g, name, ar, note, "", cal.from_gregorian(g)))
    return out


def julian_days(cal: JulianCalendar, year: int) -> list:
    """Fixed days of the Julian (Rumi) year `year` kept by Alevi-Bektashi and other Anatolian and Levantine
    communities, and the Gregorian-dated Alevi Nevruz."""
    out = []
    g = julian_to_gregorian(year, 4, 23)
    out.append(_hol(g, "Hidirellez (Ruz-i Hizir)", "خضر إلياس",
                    "23 Nisan (April) by the Julian reckoning: the day Hizir (al-Khidr) and Ilyas (Elijah) are said to meet. "
                    "Alevi-Bektashi tradition links Hizir with Ali.", "", cal.from_gregorian(g)))
    g = julian_to_gregorian(year, 4, 4)
    out.append(_hol(g, "Nawruz (Alawite)", "النوروز",
                    "Fixed on 4 Nisan of the Nusayri solar calendar (Friedman 2010, ch. 2); kept by Alawites with "
                    "Mihrajan as the feasts of the spring and autumn equinoxes.", "", cal.from_gregorian(g)))
    g = julian_to_gregorian(year, 10, 16)
    out.append(_hol(g, "Mihrajan (Alawite)", "المهرجان",
                    "The autumn feast, fixed on 16 Tishrin al-Awwal (October) of the Nusayri solar calendar, in place of "
                    "the Zoroastrian 16 Mihr (Friedman 2010, ch. 2).", "", cal.from_gregorian(g)))
    g = date(year, 3, 21)
    out.append(_hol(g, "Nevruz (Alevi: birthday of Ali)", "نوروز",
                    "Kept on 21 March (Gregorian) by Alevis as Nevruz and as the birthday of Ali.", "", cal.from_gregorian(g)))
    return sorted(out, key=lambda h: h.date)
