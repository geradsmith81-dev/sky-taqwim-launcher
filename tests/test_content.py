"""Tests for the Content track: arabic_names, holidays, holiday_history.

Run from the content/ folder:   python tests/test_content.py      (or: python -m pytest tests)

The Engine's calendars are built in parallel, so a small tabular (hisabi) Hijri calendar stands in
for them here. It has the same interface: to_gregorian(y, m, d) -> date | None, get_month(y, m)
-> object with .start and .length.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import arabic_names as an          # noqa: E402
import holiday_history as hh       # noqa: E402
import holidays as hol             # noqa: E402


# ---------------------------------------------------------------------------- stand-in calendars
class TabularCalendar:
    """Arithmetical Hijri calendar: 30-year cycle with leap years 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29
    (the common 'Kuwaiti' scheme), civil epoch 16 July 622 Julian = 19 July 622 Gregorian."""
    EPOCH = date(622, 7, 19).toordinal()

    class Month:
        def __init__(self, start, length):
            self.start, self.length = start, length
            self.end = start + timedelta(days=length - 1)

    @staticmethod
    def is_leap(y):
        return (14 + 11 * y) % 30 < 11

    def month_length(self, y, m):
        return 30 if m % 2 == 1 or (m == 12 and self.is_leap(y)) else 29

    def to_gregorian(self, y, m, d):
        if y < 1 or not 1 <= m <= 12 or not 1 <= d <= self.month_length(y, m):
            return None
        return date.fromordinal(self.EPOCH + (y - 1) * 354 + (3 + 11 * y) // 30 + (59 * (m - 1) + 1) // 2 + d - 1)

    def get_month(self, y, m):
        return self.Month(self.to_gregorian(y, m, 1), self.month_length(y, m))


class SolarCalendar:
    """Solar Hijri stand-in using convertdate.persian (if installed)."""
    def __init__(self):
        from convertdate import persian
        self.p = persian

    def to_gregorian(self, y, m, d):
        return date(*self.p.to_gregorian(y, m, d))


CAL = TabularCalendar()
YEAR = 1447


# ---------------------------------------------------------------------------- helpers
def _all(branch, **kw):
    return hol.holidays_for_year(CAL, YEAR, branch, **kw)


def _find(hs, name_prefix):
    return [h for h in hs if h.name.startswith(name_prefix)]


EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")


# ---------------------------------------------------------------------------- arabic_names
def test_names_tables():
    assert len(an.MONTHS) == 13 and an.MONTHS[0] == ("", "")
    assert len(an.MONTHS_POINTED) == 13 and len(an.SOLAR_MONTHS) == 13
    assert len(an.SOLAR_MONTHS_DARI) == 13 and len(an.SOLAR_MONTHS_PASHTO) == 13
    for table in (an.MONTHS, an.SOLAR_MONTHS, an.SOLAR_MONTHS_DARI, an.SOLAR_MONTHS_PASHTO):
        for en, ar in table[1:]:
            assert en and an.is_rtl_text(ar), (en, ar)
    for p in an.MONTHS_POINTED[1:]:
        assert an.is_rtl_text(p)
    assert an.MONTHS[9][0] == "Ramadan" and an.MONTHS[12][1] == "ذو الحجة"
    assert an.SACRED_MONTHS == {1, 7, 11, 12}
    assert len(an.WEEKDAY_EN) == len(an.WEEKDAY_AR) == len(an.WEEKDAY_FA) == 7
    assert an.WEEKDAY_AR[date(2026, 3, 20).weekday()] == "الجمعة"      # a Friday
    assert an.GRID_WEEK[0][0] == "Sat" and an.GRID_WEEK[-1][1] == "الجمعة"
    assert date(2026, 3, 21).weekday() == an.GRID_WEEK_START             # a Saturday
    assert len(an.IMAMS) == 12 and [i[0] for i in an.IMAMS] == list(range(1, 13))
    for d in (an.TERMS, an.KIND_AR, an.TERMS_FA, an.PLACE_AR):
        for k, v in d.items():
            assert an.is_rtl_text(v), (k, v)
    assert set(an.KIND_AR) == set(hol.KINDS) == set(an.KIND_EN)


def test_names_helpers():
    assert an.to_arabic_digits(1447) == "١٤٤٧"
    assert an.to_persian_digits("1405/01/01") == "۱۴۰۵/۰۱/۰۱"
    assert an.hijri_date_ar(1447, 1, 10) == "١٠ محرم ١٤٤٧ هـ"
    assert an.bi("Kaaba", "الكعبة") == "Kaaba <span class='tq-ar' lang='ar' dir='rtl'>الكعبة</span>"
    assert an.bt("Mecca").endswith("مكة المكرمة</span>")
    assert an.bi("x<y", "") == "x&lt;y"
    assert "lang='fa'" in an.bp("Nowruz")
    # place names: Persian/Urdu letters avoided for Arabic, chosen for Persian
    alts = ["Paris", "باريس", "پارىژ", "پاريس", "پاریس", "پیرس"]
    assert an.arabic_place_name(alts) == "باريس"
    assert an.persian_place_name(alts) == "پاریس"
    alts = ["Karachi", "كراتشي", "کراچی", "کراچى"]
    assert an.arabic_place_name(alts) == "كراتشي" and an.persian_place_name(alts) == "کراچی"
    assert an.arabic_place_name(["تهران", "طهران"], name="Tehran") == "طهران"
    assert an.arabic_place_name(["London"]) == "" and an.persian_place_name([]) == ""


# ---------------------------------------------------------------------------- stand-in calendar
def test_stand_in_calendar():
    assert CAL.to_gregorian(1, 1, 1) == date(622, 7, 19)
    assert sum(CAL.is_leap(y) for y in range(1, 31)) == 11
    assert CAL.to_gregorian(1447, 2, 30) is None                       # Safar has 29 days
    # within two days of the Umm al-Qura dates for 1447 (if hijri-converter is installed)
    try:
        from hijri_converter import Hijri
    except ImportError:
        return
    for m, d in ((1, 1), (9, 1), (10, 1), (12, 10)):
        uq = Hijri(YEAR, m, d).to_gregorian()
        assert abs((CAL.to_gregorian(YEAR, m, d) - uq).days) <= 2, (m, d)


# ---------------------------------------------------------------------------- holidays
def test_holidays_both_branches():
    for branch in hol.BRANCHES:
        hs = _all(branch)
        assert len(hs) > 30
        assert hs == sorted(hs, key=lambda h: (h.date, hol._KIND_ORDER[h.kind], h.name))
        seen = set()
        for h in hs:
            assert h.kind in hol.KINDS, h
            assert h.key == "" or h.key in hh.H, (h.name, h.key)
            assert hh.key_for(h.name) == h.key, (h.name, h.key, hh.key_for(h.name))
            assert h.name and h.arabic and an.is_rtl_text(h.arabic), (h.name, h.arabic)
            assert h.branch in ("both", branch)
            assert isinstance(h.hdate, hol.HijriDay) and h.hdate.year == YEAR
            assert CAL.to_gregorian(*h.hdate) == h.date
            assert not EMOJI.search(h.name + h.note)
            if h.kind == "fast" and h.key != "ramadan":
                assert h.begins_evening_before is False, h.name
            assert (h.date, h.name) not in seen, h.name
            seen.add((h.date, h.name))
        start, end = CAL.get_month(YEAR, 1).start, CAL.get_month(YEAR, 12).end
        assert all(start <= h.date <= end for h in hs)


def test_branch_specific_days():
    s, sh = _all("sunni"), _all("shia")
    # shared days
    for name in ("Ramadan begins", "Eid al-Fitr", "Day of Arafah", "Eid al-Adha", "Days of Tashriq", "Day of Tarwiyah"):
        assert _find(s, name) and _find(sh, name), name
    assert len(_find(s, "Days of Tashriq")) == 3
    # Mawlid: 12 (Sunni) and 17 (Shia) Rabi' al-Awwal
    assert _find(s, "Mawlid")[0].hdate[1:] == (3, 12)
    assert _find(sh, "Mawlid")[0].hdate[1:] == (3, 17)
    # Ashura
    assert _find(s, "Ashura")[0].kind == "sacred" and _find(sh, "Ashura")[0].kind == "mourning"
    assert _find(sh, "Tasu'a")[0].hdate[1:] == (1, 9)
    # Laylat al-Qadr
    assert [h.hdate.day for h in _find(s, "Laylat al-Qadr")] == [27]
    assert [h.hdate.day for h in _find(sh, "Laylat al-Qadr")] == [19, 21, 23]
    # days of one branch only
    for name in ("Eid al-Ghadir", "Day of Mubahala", "Arba'in", "al-Mab'ath", "Birth of Imam al-Mahdi", "Fatimiyya"):
        assert _find(sh, name) and not _find(s, name), name
    for name in ("al-Isra' wa'l-Mi'raj", "Laylat al-Bara'a", "White days fast", "Six days of Shawwal"):
        assert _find(s, name) and not _find(sh, name), name
    assert _find(sh, "Eid al-Ghadir")[0].kind == "eid"
    assert len(_find(sh, "Fatimiyya")) == 2
    # last-day-of-month rules resolve to the month's real length
    rida = _find(sh, "Martyrdom of Imam al-Rida")[0]
    assert rida.hdate[1:] == (2, CAL.month_length(YEAR, 2))
    jawad = _find(sh, "Martyrdom of Imam al-Jawad")[0]
    assert jawad.hdate[1:] == (11, CAL.month_length(YEAR, 11))


def test_raghaib_and_white_days():
    for branch in hol.BRANCHES:
        r = _find(_all(branch), "Laylat al-Raghaib")
        assert len(r) == 1 and r[0].date.weekday() == 4 and r[0].hdate.month == 7 and r[0].hdate.day >= 2
        assert r[0].begins_evening_before
    wd = _find(_all("sunni"), "White days fast")
    assert not any(h.hdate.month == 9 for h in wd)
    assert not any(h.hdate[1:] == (12, 13) for h in wd)
    assert len(wd) == 11 * 3 - 1


def test_options():
    for branch in hol.BRANCHES:
        full = _all(branch)
        bare = _all(branch, month_starts=False, imams=False, fasts=False, nights=False)
        assert len(bare) < len(full)
        assert not any(h.kind == "month" for h in bare)
        assert all(h.key == "ramadan" for h in bare if h.kind == "fast")
        assert not _find(bare, "Laylat al-Raghaib") and not _find(bare, "Last ten nights")
    bare = _all("shia", imams=False)
    assert not _find(bare, "Birth of Imam al-Jawad") and _find(bare, "Birth of Imam Ali")
    months = [h for h in _all("sunni") if h.kind == "month"]
    assert [h.hdate.month for h in months] == [2, 3, 4, 5, 6, 7, 8, 11, 12]
    try:
        hol.holidays_for_year(CAL, YEAR, "other")
    except ValueError:
        pass
    else:
        raise AssertionError("bad branch accepted")


def test_missing_days_are_skipped():
    class Gappy(TabularCalendar):
        def to_gregorian(self, y, m, d):
            return None if m == 12 else super().to_gregorian(y, m, d)
    hs = hol.holidays_for_year(Gappy(), YEAR, "sunni")
    assert not _find(hs, "Eid al-Adha") and _find(hs, "Eid al-Fitr")


def test_between_and_compare():
    a, b = date(2026, 1, 1), date(2026, 12, 31)
    for branch in hol.BRANCHES:
        hs = hol.holidays_between(CAL, a, b, branch)
        assert hs and all(a <= h.date <= b for h in hs)
        assert {h.hdate.year for h in hs} == {1447, 1448}
        assert len(_find(hs, "Eid al-Fitr")) == 1
        for name, m, d in hol.compare_holidays(branch):
            assert hh.key_for(name) in hh.H, name
            assert 1 <= m <= 12 and 1 <= d <= 30
    assert hol.COMPARE_HOLIDAYS == hol.compare_holidays("sunni")


def test_solar_holidays():
    try:
        sc = SolarCalendar()
    except ImportError:
        return
    hs = hol.solar_holidays_for_year(sc, 1405)
    names = [h.name for h in hs]
    assert len(_find(hs, "Nowruz")) == 4 and "Sizdah Bedar" in names
    nowruz = _find(hs, "Nowruz (New Year)")[0]
    assert nowruz.date in (date(2026, 3, 20), date(2026, 3, 21))
    yalda = _find(hs, "Shab-e Yalda")[0]
    assert yalda.date.month == 12 and yalda.date.day in (20, 21)
    suri = _find(hs, "Chaharshanbe Suri")[0]
    assert suri.date.weekday() == 1 and suri.date.year == 2027
    for h in hs:
        assert h.kind == "civil" and h.key in hh.H and an.is_rtl_text(h.arabic)
        assert hh.key_for(h.name) == h.key and not h.begins_evening_before


# ---------------------------------------------------------------------------- holiday_history
def test_histories():
    assert len(hh.H) >= 40
    for key, entry in hh.H.items():
        assert len(entry) == 4, key
        title, ar, text, src = entry
        assert title and text and src, key
        assert an.is_rtl_text(ar), (key, ar)
        assert not EMOJI.search(title + text + src), key
        n = len(re.findall(r"[a-z0-9)'][.!?]['\"]?(?:\s|$)", text))
        assert 3 <= n <= 9, (key, n)
    for _, key in hh._RULES:
        assert key in hh.H, key


def test_popover_html():
    chip = "<span class='tq-chip'>Eid al-Fitr</span>"
    out = hh.clickable("Eid al-Fitr", chip)
    for cls in ("tq-pop", "tq-popbody", "tq-pop-title", "tq-pop-text", "tq-pop-src"):
        assert f"class='{cls}'" in out or f"class='{cls} " in out, cls
    assert out.startswith("<details class='tq-pop'>") and chip in out
    assert "<span class='tq-ar' lang='ar' dir='rtl'>عيد الفطر</span>" in out
    assert hh.clickable("ghadir", chip, align_right=True).startswith("<details class='tq-pop tq-pop-r'>")
    assert hh.clickable("", chip) == chip and hh.clickable("No such day", chip) == chip
    assert "lang='fa'" in hh.body_html("nowruz")
    assert "&#x27;" in hh.body_html("hilal") or "&#39;" in hh.body_html("hilal")   # quotes escaped


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in tests:
        try:
            f()
            print(f"ok    {n}")
        except Exception as e:          # report every failure, then exit non-zero
            failed += 1
            print(f"FAIL  {n}: {type(e).__name__}: {e}")
    for branch in hol.BRANCHES:
        hs = _all(branch)
        print(f"{branch}: {len(hs)} holidays in {YEAR} AH (tabular stand-in), "
              f"{len({h.key for h in hs if h.key})} distinct histories")
    print(f"{len(tests) - failed}/{len(tests)} tests passed")
    sys.exit(1 if failed else 0)
