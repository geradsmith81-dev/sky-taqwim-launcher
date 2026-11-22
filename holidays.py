"""Islamic holy days for the Sunni and the (Twelver) Shia tradition, and the Iranian solar festivals.

The rules work on any Hijri calendar object with
    to_gregorian(y, m, d) -> date | None      and      get_month(y, m) -> obj with .length, .start
so the same lists serve the Umm al-Qura, tabular and crescent-sighting calendars. A date the
calendar does not have (30th of a 29-day month, a year outside its range) is skipped.

Day convention: an Islamic day begins at the sunset before. A Holiday's `date` is the Gregorian
day whose daytime is that Islamic day. begins_evening_before=True means it starts at sunset the
evening before (a night such as Laylat al-Qadr is the night before `date`). Fast days are dawn to
sunset, so they have begins_evening_before=False.

Where the sources give more than one date, the date kept by the main living tradition is used:
for Sunni days the widely kept dates; for Shia days the Iranian official calendar (Institute of
Geophysics, University of Tehran), which mostly follows al-Mufid and al-Tusi. `note` gives the
other dates. See CONTENT_NOTES.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import NamedTuple

from arabic_names import MONTHS, SOLAR_MONTHS, SACRED_MONTHS

KINDS = ("eid", "sacred", "fast", "night", "mourning", "birth", "month", "hajj", "civil")
_KIND_ORDER = {k: i for i, k in enumerate(("eid", "sacred", "mourning", "birth", "night", "hajj", "fast",
                                           "month", "civil"))}
BRANCHES = ("sunni", "shia")

MUHARRAM, SAFAR, RABI1, RABI2, JUMADA1, JUMADA2, RAJAB, SHABAN, RAMADAN, SHAWWAL, DHUQADAH, DHUHIJJAH = range(1, 13)
LAST = -1          # "last day of the month" (29 or 30, whichever the calendar has)


class HijriDay(NamedTuple):
    year: int
    month: int
    day: int

    def __str__(self) -> str:
        return f"{self.day} {MONTHS[self.month][0]} {self.year}"

    @property
    def arabic(self) -> str:
        from arabic_names import hijri_date_ar
        return hijri_date_ar(self.year, self.month, self.day)


class SolarDay(NamedTuple):
    year: int
    month: int
    day: int

    def __str__(self) -> str:
        return f"{self.day} {SOLAR_MONTHS[self.month][0]} {self.year}"

    @property
    def arabic(self) -> str:        # Persian script
        from arabic_names import solar_date_fa
        return solar_date_fa(self.year, self.month, self.day)


@dataclass
class Holiday:
    date: date
    name: str
    arabic: str            # Arabic script (Persian script for the solar festivals)
    kind: str              # one of KINDS
    hdate: HijriDay | SolarDay | None = None
    note: str = ""
    key: str = ""          # holiday_history.H key, or ""
    begins_evening_before: bool = True
    branch: str = "both"   # "both", "sunni" or "shia"

    def as_dict(self) -> dict:
        return {"date": self.date, "name": self.name, "arabic": self.arabic, "kind": self.kind,
                "hijri_date": str(self.hdate) if self.hdate else "", "note": self.note, "key": self.key,
                "begins_evening_before": self.begins_evening_before, "branch": self.branch}


# ----------------------------------------------------------------------------------------------
# the tables
# (month, day, name, arabic, kind, key, note, option, evening)
#   note: a string, or a dict {"sunni": ..., "shia": ...} for shared days
#   option: None (always), "imams", "fasts" or "nights" - the switch of holidays_for_year that shows it
# ----------------------------------------------------------------------------------------------
_SACRED_NOTE = "One of the four sacred months (Qur'an 9:36)."

SHARED = [
    (RAMADAN, 1, "Ramadan begins", "بداية شهر رمضان", "fast", "ramadan",
     {"sunni": "The fast runs from dawn to sunset. Tarawih prayers begin the evening before. The start "
               "depends on the crescent and can differ by a day between countries.",
      "shia": "The fast runs from dawn until the redness of the eastern sky has gone after sunset. The "
              "start depends on the crescent and on each jurist's rules for sighting."}, None, True),
    (RAMADAN, 21, "Last ten nights of Ramadan begin", "العشر الأواخر من رمضان", "night", "last_ten",
     "The night of the 21st opens the last ten nights, when Laylat al-Qadr is sought and many keep "
     "retreat (i'tikaf) in the mosque.", "nights", True),
    (SHAWWAL, 1, "Eid al-Fitr", "عيد الفطر", "eid", "eid_al_fitr",
     {"sunni": "Zakat al-fitr is paid before the Eid prayer. Fasting on this day is forbidden. Public "
               "holidays usually last two to four days; only the first is shown.",
      "shia": "Zakat al-fitr (fitra) is paid before the Eid prayer. Fasting on this day is forbidden. "
              "Public holidays usually last one to three days; only the first is shown."}, None, True),
    (DHUHIJJAH, 1, "First ten days of Dhu al-Hijjah", "العشر الأوائل من ذي الحجة", "sacred", "first_ten",
     {"sunni": "Ten days honoured in the Qur'an (89:2) and hadith. Many fast the first nine days, or "
               "at least the Day of Arafah. One of the four sacred months.",
      "shia": "Ten days of special devotion. Shia reports date the marriage of Ali and Fatima to 1 "
              "Dhu al-Hijjah (other reports: the 6th). One of the four sacred months."}, None, True),
    (DHUHIJJAH, 8, "Day of Tarwiyah", "يوم التروية", "hajj", "hajj",
     {"sunni": "Pilgrims go to Mina for the start of the Hajj.",
      "shia": "Pilgrims go to Mina. On this day in 60 AH Imam Husayn left Mecca for Iraq."}, None, True),
    (DHUHIJJAH, 9, "Day of Arafah", "يوم عرفة", "sacred", "arafah",
     {"sunni": "Pilgrims stand at Arafat from noon to sunset, the central rite of the Hajj.",
      "shia": "Pilgrims stand at Arafat. The Du'a 'Arafa of Imam Husayn is recited. Shia tradition "
              "also marks the death of Muslim ibn Aqil in Kufa on this day in 60 AH."}, None, True),
    (DHUHIJJAH, 10, "Eid al-Adha", "عيد الأضحى", "eid", "eid_al_adha",
     "Pilgrims stone the pillar of Aqaba and sacrifice at Mina; Muslims everywhere offer a sacrifice "
     "if they can. Public holidays usually last three or four days.", None, True),
    (DHUHIJJAH, 11, "Days of Tashriq (1st)", "أول أيام التشريق", "hajj", "tashriq",
     "Pilgrims stone the three pillars at Mina. Fasting is forbidden on the Days of Tashriq.", None, True),
    (DHUHIJJAH, 12, "Days of Tashriq (2nd)", "ثاني أيام التشريق", "hajj", "tashriq",
     "Pilgrims in a hurry may leave Mina after the stoning (Qur'an 2:203).", None, True),
    (DHUHIJJAH, 13, "Days of Tashriq (3rd)", "ثالث أيام التشريق", "hajj", "tashriq",
     "The last day of stoning at Mina.", None, True),
]

SUNNI = [
    (MUHARRAM, 1, "Hijri New Year", "رأس السنة الهجرية", "sacred", "hijri_new_year",
     "The year count begins with the Hijra of 622 CE. " + _SACRED_NOTE, None, True),
    (MUHARRAM, 9, "Fast of Tasu'a", "صيام تاسوعاء", "fast", "ashura",
     "Recommended (sunna) with the Ashura fast; some fast the 11th instead.", "fasts", False),
    (MUHARRAM, 10, "Ashura", "عاشوراء", "sacred", "ashura",
     "The day God saved Moses from Pharaoh, in the hadith. Also the anniversary of the killing of "
     "al-Husayn at Karbala (61 AH).", None, True),
    (MUHARRAM, 10, "Fast of Ashura", "صيام عاشوراء", "fast", "ashura",
     "A recommended (sunna) fast; a hadith in Muslim says it expiates the year before.", "fasts", False),
    (RABI1, 12, "Mawlid al-Nabi", "المولد النبوي", "birth", "mawlid",
     "The Prophet's birthday, widely celebrated, a public holiday in many countries. Some scholars, "
     "notably Salafi ones, do not observe it. Ibn Ishaq gives this date for both the Prophet's "
     "birth and his death.", None, True),
    (RAJAB, 27, "al-Isra' wa'l-Mi'raj", "الإسراء والمعراج", "night", "isra_miraj",
     "The Night Journey and Ascension, kept on the night of 26/27 Rajab. Early sources disagree on "
     "the date; 27 Rajab is the most widely kept.", None, True),
    (SHABAN, 15, "Laylat al-Bara'a (Nisf Sha'ban)", "ليلة البراءة (النصف من شعبان)", "night", "nisf_shaban",
     "The night of mid-Sha'ban (night of 14/15), kept with prayer and visits to graves (Shab-e Barat, "
     "Berat Kandili). Many Salafi scholars do not single it out.", "nights", True),
    (RAMADAN, 27, "Laylat al-Qadr (27th night)", "ليلة القدر (ليلة السابع والعشرين)", "night", "laylat_al_qadr",
     "Sought in the odd nights of the last ten (21, 23, 25, 27, 29). The night of the 27th, the "
     "opinion of Ubayy ibn Ka'b, is the most widely kept.", None, True),
    (SHAWWAL, 2, "Six days of Shawwal (may begin)", "صيام ست من شوال", "fast", "six_shawwal",
     "A recommended fast of any six days in Shawwal after the Eid (hadith in Muslim). Shown on the "
     "first day on which it may be kept.", "fasts", False),
    (DHUHIJJAH, 9, "Fast of Arafah", "صيام يوم عرفة", "fast", "arafah",
     "Recommended for those not on pilgrimage; a hadith in Muslim says it expiates two years.",
     "fasts", False),
]

SHIA = [
    (MUHARRAM, 1, "Hijri New Year; Muharram mourning begins", "رأس السنة الهجرية وبدء العزاء الحسيني",
     "mourning", "hijri_new_year",
     "Shia communities open the first ten days of Muharram with nightly mourning gatherings "
     "(majalis) leading to Ashura. " + _SACRED_NOTE, None, True),
    (MUHARRAM, 9, "Tasu'a", "تاسوعاء", "mourning", "tasua",
     "The eve of the battle of Karbala, dedicated to al-Abbas ibn Ali. A public day of mourning in "
     "Iran and Iraq.", None, True),
    (MUHARRAM, 10, "Ashura: martyrdom of Imam Husayn", "عاشوراء، استشهاد الإمام الحسين", "mourning",
     "ashura_karbala",
     "Imam Husayn was killed at Karbala on 10 Muharram 61 AH (10 October 680). A full fast on "
     "Ashura is discouraged in Shia law; many abstain from food until the afternoon.", None, True),
    (MUHARRAM, 25, "Martyrdom of Imam al-Sajjad", "استشهاد الإمام السجاد", "mourning", "al_sajjad",
     "Date of the Iranian calendar; other reports give 12 or 18 Muharram. Year 94 or 95 AH.", "imams", True),
    (SAFAR, 7, "Birth of Imam al-Kazim", "ولادة الإمام الكاظم", "birth", "al_kazim",
     "Born at al-Abwa' in 128 AH, by the date of the Iranian calendar. In Iraq, 7 Safar is also kept "
     "for the martyrdom of Imam Hasan, following another report.", "imams", True),
    (SAFAR, 20, "Arba'in", "الأربعين", "mourning", "arbain",
     "Forty days after Ashura. Millions walk to Karbala, many of them from Najaf.", None, True),
    (SAFAR, 28, "Death of the Prophet; martyrdom of Imam Hasan", "وفاة النبي واستشهاد الإمام الحسن",
     "mourning", "prophet_death",
     "The date of al-Mufid and al-Tusi and of the Iranian calendar for the Prophet's death (11 AH). "
     "Imam Hasan's death (49 or 50 AH) is also kept on this day in Iran; Iraqi Shia also mark it on "
     "7 Safar. Sunni sources date the Prophet's death to 12 Rabi' al-Awwal.", None, True),
    (SAFAR, LAST, "Martyrdom of Imam al-Rida", "استشهاد الإمام الرضا", "mourning", "al_rida",
     "Kept on the last day of Safar, 29th or 30th (Iranian calendar), in 203 AH at Tus, now Mashhad. "
     "Other reports give 17 Safar or 23 Dhu al-Qa'dah.", None, True),
    (RABI1, 8, "Martyrdom of Imam al-Askari", "استشهاد الإمام الحسن العسكري", "mourning", "al_askari",
     "Died in Samarra on 8 Rabi' al-Awwal 260 AH (al-Mufid).", "imams", True),
    (RABI1, 9, "Start of the Imamate of Imam al-Mahdi", "بداية إمامة الإمام المهدي", "sacred", "mahdi",
     "The day after the eleventh Imam's death, kept as the start of the twelfth Imam's Imamate "
     "(Iranian calendar). Some communities also keep it as a popular festival under other names.",
     "imams", True),
    (RABI1, 17, "Mawlid al-Nabi; birth of Imam al-Sadiq", "المولد النبوي وولادة الإمام جعفر الصادق", "birth",
     "mawlid",
     "The Shia date of the Prophet's birthday (al-Mufid, al-Tusi); al-Kulayni gives the 12th. Imam "
     "Ja'far al-Sadiq was born on the same day in 83 AH. In Iran, 12-17 Rabi' al-Awwal is Islamic "
     "Unity Week.", None, True),
    (RABI2, 8, "Birth of Imam al-Askari", "ولادة الإمام الحسن العسكري", "birth", "al_askari",
     "Born in Medina in 232 AH, by the date of the Iranian calendar; other reports give 10 Rabi' "
     "al-Thani.", "imams", True),
    (JUMADA1, 5, "Birth of Zaynab bint Ali", "ولادة السيدة زينب", "birth", "zaynab",
     "Date of the Iranian calendar; the year is given as 5 or 6 AH.", "imams", True),
    (JUMADA1, 13, "Fatimiyya (first): martyrdom of Fatima al-Zahra", "الفاطمية الأولى: استشهاد فاطمة الزهراء",
     "mourning", "fatimiyya",
     "The report of 75 days after the Prophet's death (al-Kafi). Many communities mourn on both "
     "dates.", None, True),
    (JUMADA2, 3, "Fatimiyya (second): martyrdom of Fatima al-Zahra", "الفاطمية الثانية: استشهاد فاطمة الزهراء",
     "mourning", "fatimiyya",
     "The report of 95 days after the Prophet's death; a public day of mourning in Iran.", None, True),
    (JUMADA2, 20, "Birth of Fatima al-Zahra", "ولادة فاطمة الزهراء", "birth", "fatima",
     "Shia date, five years after the start of the Prophet's mission. In Iran it is also Mothers' "
     "Day and Women's Day.", None, True),
    (RAJAB, 1, "Birth of Imam al-Baqir", "ولادة الإمام الباقر", "birth", "al_baqir",
     "Born in Medina in 57 AH, by the date of the Iranian calendar; another report gives 3 Safar.",
     "imams", True),
    (RAJAB, 3, "Martyrdom of Imam al-Hadi", "استشهاد الإمام الهادي", "mourning", "al_hadi",
     "Died in Samarra in Rajab 254 AH; some sources give 25 or 26 Jumada al-Akhirah.", "imams", True),
    (RAJAB, 10, "Birth of Imam al-Jawad", "ولادة الإمام الجواد", "birth", "al_jawad",
     "Born in Medina in 195 AH.", "imams", True),
    (RAJAB, 13, "Birth of Imam Ali", "ولادة الإمام علي", "birth", "imam_ali",
     "Born in the Kaaba, in Shia tradition, about 600 CE. A public holiday in Iran (Fathers' Day). "
     "13-15 Rajab are the white days, when many keep i'tikaf.", None, True),
    (RAJAB, 25, "Martyrdom of Imam al-Kazim", "استشهاد الإمام الكاظم", "mourning", "al_kazim",
     "Died in prison in Baghdad in 183 AH. Date of the Iranian calendar; other reports give an "
     "earlier day in Rajab.", "imams", True),
    (RAJAB, 27, "al-Mab'ath", "المبعث النبوي", "sacred", "mabath",
     "The start of the Prophet's mission with the first revelation (Qur'an 96:1-5). A public holiday "
     "in Iran; fasting on this day is recommended. Most Sunni scholars place the first revelation in "
     "Ramadan.", None, True),
    (SHABAN, 3, "Birth of Imam Husayn", "ولادة الإمام الحسين", "birth", "imam_husayn",
     "Born in Medina in 4 AH. Date of the Iranian calendar and of al-Tusi; al-Mufid gives 5 Sha'ban.",
     None, True),
    (SHABAN, 4, "Birth of al-Abbas ibn Ali", "ولادة أبي الفضل العباس", "birth", "abbas",
     "Date of the Iranian calendar.", "imams", True),
    (SHABAN, 5, "Birth of Imam al-Sajjad", "ولادة الإمام السجاد", "birth", "al_sajjad",
     "Born in 38 AH, by the date of the Iranian calendar; some reports give 15 Jumada al-Ula.",
     "imams", True),
    (SHABAN, 15, "Birth of Imam al-Mahdi", "ولادة الإمام المهدي", "birth", "mahdi",
     "Born in Samarra on 15 Sha'ban 255 AH, in Twelver belief. A public holiday in Iran.", None, True),
    (SHABAN, 15, "Night of mid-Sha'ban", "ليلة النصف من شعبان", "night", "nisf_shaban",
     "A night of prayer and vigil (night of 14/15), with the ziyara of Imam Husayn.", "nights", True),
    (RAMADAN, 15, "Birth of Imam Hasan", "ولادة الإمام الحسن", "birth", "imam_hasan",
     "Born in Medina in 3 AH.", None, True),
    (RAMADAN, 19, "Laylat al-Qadr (19th night)", "ليلة القدر (ليلة التاسع عشر)", "night", "laylat_al_qadr",
     "The first of the three nights of Qadr in Shia tradition (19, 21, 23).", None, True),
    (RAMADAN, 19, "Imam Ali struck in the mosque of Kufa", "ضربة الإمام علي", "mourning", "imam_ali",
     "Imam Ali was struck at the dawn prayer on 19 Ramadan 40 AH; some Sunni histories give the 17th.",
     None, True),
    (RAMADAN, 21, "Martyrdom of Imam Ali", "استشهاد الإمام علي", "mourning", "imam_ali",
     "Imam Ali died of his wound on 21 Ramadan 40 AH (661 CE). A public day of mourning in Iran.",
     None, True),
    (RAMADAN, 21, "Laylat al-Qadr (21st night)", "ليلة القدر (ليلة الحادي والعشرين)", "night", "laylat_al_qadr",
     "The second night of Qadr, joined with mourning for Imam Ali.", None, True),
    (RAMADAN, 23, "Laylat al-Qadr (23rd night)", "ليلة القدر (ليلة الثالث والعشرين)", "night", "laylat_al_qadr",
     "The most emphasised of the three nights of Qadr in reports from the Imams.", None, True),
    (SHAWWAL, 25, "Martyrdom of Imam al-Sadiq", "استشهاد الإمام جعفر الصادق", "mourning", "jafar_sadiq",
     "Died in Medina in Shawwal 148 AH (al-Mufid). The 25th is the date of the Iranian calendar, "
     "where it is a public day of mourning.",
     None, True),
    (DHUQADAH, 11, "Birth of Imam al-Rida", "ولادة الإمام الرضا", "birth", "al_rida",
     "Born in Medina in 148 AH, by the date of the Iranian calendar. " + _SACRED_NOTE, None, True),
    (DHUQADAH, LAST, "Martyrdom of Imam al-Jawad", "استشهاد الإمام الجواد", "mourning", "al_jawad",
     "Died in Baghdad in 220 AH; kept on the last day of Dhu al-Qa'dah (Iranian calendar).", "imams", True),
    (DHUHIJJAH, 7, "Martyrdom of Imam al-Baqir", "استشهاد الإمام الباقر", "mourning", "al_baqir",
     "Died in Medina, by the date of the Iranian calendar; the year is given as 114 to 118 AH.",
     "imams", True),
    (DHUHIJJAH, 9, "Fast of Arafah", "صيام يوم عرفة", "fast", "arafah",
     "Recommended, unless it would weaken one for the day's prayers or the date is in doubt.",
     "fasts", False),
    (DHUHIJJAH, 15, "Birth of Imam al-Hadi", "ولادة الإمام الهادي", "birth", "al_hadi",
     "Born near Medina in 212 AH (al-Kulayni, al-Mufid, al-Tusi); some reports give 2 or 5 Rajab.",
     "imams", True),
    (DHUHIJJAH, 18, "Eid al-Ghadir", "عيد الغدير", "eid", "ghadir",
     "The Prophet's words about Ali at Ghadir Khumm on 18 Dhu al-Hijjah 10 AH. Fasting on this day "
     "is recommended. A public holiday in Iran and parts of Iraq.", None, True),
    (DHUHIJJAH, 24, "Day of Mubahala", "يوم المباهلة", "sacred", "mubahala",
     "The meeting with the Christians of Najran (Qur'an 3:61). Most reports give the 24th; others "
     "the 21st, 25th or 27th.", None, True),
]

_TABLES = {"sunni": SUNNI, "shia": SHIA}

# Months whose first day already has its own holiday, so no separate new-month entry is added.
_NO_MONTH_ENTRY = {MUHARRAM, RAMADAN, SHAWWAL}

_WHITE_DAYS_AR = {13: "الأيام البيض (الثالث عشر)", 14: "الأيام البيض (الرابع عشر)", 15: "الأيام البيض (الخامس عشر)"}

_RAGHAIB_NOTE = {
    "sunni": "The eve of the first Friday of Rajab, after the first Thursday of the month. Kept in "
             "Turkey and the Balkans as Regaip Kandili. Many jurists, among them al-Nawawi, rejected "
             "its special prayer.",
    "shia": "The eve of the first Friday of Rajab, after the first Thursday of the month. Its prayer "
            "is given by Ibn Tawus and in Mafatih al-jinan.",
}


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
_CAL_ERRORS = (ValueError, KeyError, IndexError, LookupError, OverflowError)


def _month_length(cal, y: int, m: int) -> int | None:
    try:
        return int(cal.get_month(y, m).length)
    except _CAL_ERRORS:
        return None
    except AttributeError:
        return None


def _greg(cal, y: int, m: int, d: int) -> date | None:
    """The Gregorian date of Hijri y-m-d in `cal`, or None if the calendar has no such day."""
    if d < 1 or d > 30:
        return None
    if d == 30:
        n = _month_length(cal, y, m)
        if n is not None and n < 30:
            return None
    try:
        return cal.to_gregorian(y, m, d)
    except _CAL_ERRORS:
        return None


def _note_for(note, branch: str) -> str:
    return note.get(branch, "") if isinstance(note, dict) else note


def _check_branch(branch: str) -> str:
    b = (branch or "").strip().lower()
    if b not in BRANCHES:
        raise ValueError(f"branch must be 'sunni' or 'shia', not {branch!r}")
    return b


def _sort(hs: list[Holiday]) -> list[Holiday]:
    return sorted(hs, key=lambda h: (h.date, _KIND_ORDER.get(h.kind, 99), h.name))


# ----------------------------------------------------------------------------------------------
# public
# ----------------------------------------------------------------------------------------------
def holidays_for_year(cal, year: int, branch: str, *, month_starts: bool = True, imams: bool = True,
                      fasts: bool = True, nights: bool = True) -> list[Holiday]:
    """The holy days of Hijri `year` (1 Muharram to the end of Dhu al-Hijjah) for one branch.

    month_starts: a 'New month' entry on the 1st of each month (except Muharram, Ramadan, Shawwal,
                  whose first days have their own entries).
    imams:        (Shia) the births and deaths of the Imams, Zaynab and al-Abbas beyond the main days.
    fasts:        recommended fasts (Sunni: Tasu'a and Ashura, Arafah, the white days, six of Shawwal;
                  Shia: Arafah).
    nights:       special nights beyond the main ones (last ten nights, mid-Sha'ban, al-Raghaib).
    """
    branch = _check_branch(branch)
    enabled = {None: True, "imams": imams, "fasts": fasts, "nights": nights}
    out: list[Holiday] = []

    def add(m, d, name, ar, kind, key, note, evening, who):
        if d == LAST:
            d = _month_length(cal, year, m)
            if d is None:
                return
        g = _greg(cal, year, m, d)
        if g is None:
            return
        out.append(Holiday(g, name, ar, kind, HijriDay(year, m, d), note, key, evening, who))

    for m, d, name, ar, kind, key, note, opt, evening in SHARED:
        if enabled[opt]:
            add(m, d, name, ar, kind, key, _note_for(note, branch), evening, "both")
    for m, d, name, ar, kind, key, note, opt, evening in _TABLES[branch]:
        if enabled[opt]:
            add(m, d, name, ar, kind, key, note, evening, branch)

    # Laylat al-Raghaib: the night before the first Friday of Rajab that follows the month's first Thursday.
    if nights:
        for d in range(1, 8):
            g = _greg(cal, year, RAJAB, d)
            if g is not None and g.weekday() == 3:          # Thursday
                fri = _greg(cal, year, RAJAB, d + 1)
                if fri is not None:
                    out.append(Holiday(fri, "Laylat al-Raghaib", "ليلة الرغائب", "night",
                                       HijriDay(year, RAJAB, d + 1), _RAGHAIB_NOTE[branch], "raghaib",
                                       True, "both"))
                break

    # White days (Sunni recommended fast): 13-15 of each month, except Ramadan (already a fast)
    # and 13 Dhu al-Hijjah (a Day of Tashriq, when fasting is forbidden).
    if fasts and branch == "sunni":
        for m in range(1, 13):
            if m == RAMADAN:
                continue
            for d in (13, 14, 15):
                if m == DHUHIJJAH and d == 13:
                    continue
                note = "Recommended fast of the full-moon days (al-Tirmidhi)."
                if m == DHUHIJJAH and d == 14:
                    note += " The 13th is a Day of Tashriq, when fasting is forbidden."
                add(m, d, f"White days fast ({d}th)", _WHITE_DAYS_AR[d], "fast", "white_days", note, False, "sunni")

    if month_starts:
        for m in range(2, 13):
            if m in _NO_MONTH_ENTRY:
                continue
            tr, ar = MONTHS[m]
            sacred = m in SACRED_MONTHS
            add(m, 1, f"New month: {tr}", f"غرة {ar}", "month", "sacred_months" if sacred else "hilal",
                _SACRED_NOTE if sacred else "", True, "both")
    return _sort(out)


# 16 July 622 (Julian) = 19 July 622 (proleptic Gregorian): 1 Muharram 1 AH in the tabular calendar.
_EPOCH = date(622, 7, 19).toordinal()


def _approx_hijri_year(d: date) -> int:
    return int((d.toordinal() - _EPOCH) / 354.36707) + 1


def holidays_between(cal, start: date, end: date, branch: str, **opts) -> list[Holiday]:
    """All holidays with start <= date <= end. `opts` are those of holidays_for_year."""
    branch = _check_branch(branch)
    out = []
    for y in range(_approx_hijri_year(start) - 1, _approx_hijri_year(end) + 2):
        if y < 1:
            continue
        try:
            hs = holidays_for_year(cal, y, branch, **opts)
        except _CAL_ERRORS:
            continue                      # a year outside the calendar's range
        out.extend(h for h in hs if start <= h.date <= end)
    return _sort(out)


# ----------------------------------------------------------------------------------------------
# Iranian solar Hijri festivals (`solar_cal` has to_gregorian(y, m, d) for the solar Hijri year)
# ----------------------------------------------------------------------------------------------
def solar_holidays_for_year(solar_cal, year: int) -> list[Holiday]:
    """Nowruz (1-4 Farvardin), Sizdah Bedar (13 Farvardin), Shab-e Yalda (evening of 30 Azar) and
    Chaharshanbe Suri (Tuesday evening before the last Wednesday of the year) of solar Hijri `year`.
    The solar day runs from midnight, so these do not begin the evening before; the two evening
    festivals are dated to the day on whose evening they fall."""
    out: list[Holiday] = []

    def g(m, d):
        try:
            return solar_cal.to_gregorian(year, m, d)
        except _CAL_ERRORS:
            return None

    nowruz = [("Nowruz (New Year)", "نوروز",
               "The Iranian New Year at the spring equinox. 1-4 Farvardin are public holidays in Iran; "
               "Afghanistan keeps 1 Hamal."),
              ("Nowruz holiday (2nd day)", "نوروز (روز دوم)", ""),
              ("Nowruz holiday (3rd day)", "نوروز (روز سوم)", ""),
              ("Nowruz holiday (4th day)", "نوروز (روز چهارم)", "")]
    for i, (name, fa, note) in enumerate(nowruz, start=1):
        d = g(1, i)
        if d:
            out.append(Holiday(d, name, fa, "civil", SolarDay(year, 1, i), note, "nowruz", False, "both"))
    d = g(1, 13)
    if d:
        out.append(Holiday(d, "Sizdah Bedar", "سیزده‌بدر", "civil", SolarDay(year, 1, 13),
                           "The 13th day of the New Year, spent outdoors; Nature Day in Iran.",
                           "sizdah_bedar", False, "both"))
    d = g(9, 30)
    if d:
        out.append(Holiday(d, "Shab-e Yalda (evening)", "شب یلدا", "civil", SolarDay(year, 9, 30),
                           "The longest night: the evening of 30 Azar into 1 Dey.", "yalda", False, "both"))
    # last Wednesday of Esfand (29 or 30 days)
    for day in (30, 29, 28, 27, 26, 25, 24):
        w = g(12, day)
        if w is not None and w.weekday() == 2:
            tue = w - timedelta(days=1)
            out.append(Holiday(tue, "Chaharshanbe Suri (evening)", "چهارشنبه‌سوری", "civil",
                               SolarDay(year, 12, day - 1),
                               "Bonfires on the evening before the last Wednesday of the year.",
                               "chaharshanbe_suri", False, "both"))
            break
    return _sort(out)


# ----------------------------------------------------------------------------------------------
# Compare page: the same Hijri date in each calendar
# ----------------------------------------------------------------------------------------------
COMPARE_HOLIDAYS_BY_BRANCH = {
    "sunni": [
        ("Hijri New Year", MUHARRAM, 1), ("Ashura", MUHARRAM, 10), ("Mawlid al-Nabi", RABI1, 12),
        ("Ramadan begins", RAMADAN, 1), ("Laylat al-Qadr (27th night)", RAMADAN, 27),
        ("Eid al-Fitr", SHAWWAL, 1), ("Day of Arafah", DHUHIJJAH, 9), ("Eid al-Adha", DHUHIJJAH, 10),
    ],
    "shia": [
        ("Hijri New Year", MUHARRAM, 1), ("Ashura: martyrdom of Imam Husayn", MUHARRAM, 10),
        ("Arba'in", SAFAR, 20), ("Mawlid al-Nabi", RABI1, 17),
        ("Ramadan begins", RAMADAN, 1), ("Laylat al-Qadr (23rd night)", RAMADAN, 23),
        ("Eid al-Fitr", SHAWWAL, 1), ("Day of Arafah", DHUHIJJAH, 9), ("Eid al-Adha", DHUHIJJAH, 10),
        ("Eid al-Ghadir", DHUHIJJAH, 18),
    ],
}
COMPARE_HOLIDAYS = COMPARE_HOLIDAYS_BY_BRANCH["sunni"]


def compare_holidays(branch: str) -> list[tuple[str, int, int]]:
    """[(name, month, day)] for the Compare page, with the branch's dates for Mawlid and Laylat al-Qadr."""
    return COMPARE_HOLIDAYS_BY_BRANCH[_check_branch(branch)]
