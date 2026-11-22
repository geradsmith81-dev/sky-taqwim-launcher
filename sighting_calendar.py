"""
A sighting (ru'yat al-hilal) calendar predicted from NASA JPL astronomy, for Mecca or any place.

Rules (each is a modelling choice, shown in the app):
1. The day begins at sunset. A civil date d stands for the Islamic day whose daytime is d.
2. A month has 29 or 30 days. On the evening that ends day 29 (after the sunset of the 29th
   day's daytime), if the young crescent is predicted visible from `place` by the chosen
   criterion, the next day is the 1st of the new month. Otherwise the month is completed to
   30 days (ikmal al-'iddah) and the next month begins regardless.
3. Months are named and numbered by matching them to the Umm al-Qura calendar: every month of
   the chain is given the Hijri month and year of the Umm al-Qura month at the same place in
   the sequence. The start dates usually agree within a day or two.

The criteria are published models, not records of sightings: Yallop 1997 (NAO Technical Note
69) and Odeh 2004 (Experimental Astronomy 18:39-64). Real announcements depend on weather,
witnesses, the authority that accepts them, and whether sightings from other countries count.

Mecca is precomputed for 1850-2150 (data/crescents_mecca.csv.gz). Any other place is computed
on demand for a span of years (about 0.3 s per year).
"""
from __future__ import annotations

from datetime import date, timedelta
from functools import lru_cache

import crescent_data as cdat
import sky_engine as se
from crescent_data import MECCA_FILE, build_mecca_table  # noqa: F401  (re-exported)
from hijri_core import MONTHS, HMonth, LunarCalendar

CRITERIA = {
    "yallop_A": "Yallop zone A: easily visible to the naked eye (q > +0.216)",
    "yallop_B": "Yallop zone A or B: naked eye in perfect conditions (q > -0.014)",
    "yallop_C": "Yallop A-C: may need optical aid to find, then naked eye (q > -0.160)",
    "odeh_A": "Odeh zone A: visible to the naked eye (V >= 5.65)",
    "odeh_B": "Odeh A-B: visible with optical aid, may be seen by naked eye (V >= 2.00)",
    "odeh_C": "Odeh A-C: optical aid accepted, e.g. telescope sightings (V >= -0.96)",
    "mabims": "Neo-MABIMS 2021 (Brunei, Indonesia, Malaysia, Singapore): Moon at least 3 deg high and 6.4 deg "
              "from the Sun at sunset (calculated, topocentric)",
    "wujud": "Wujud al-hilal: new moon before sunset and the Moon sets after the Sun (calculated)",
    "conjunction": "New moon (conjunction) before sunset on the 29th (calculated)",
}
DEFAULT_CRITERION = "yallop_B"
CRITERIA_SHORT = {
    "yallop_A": "Yallop A", "yallop_B": "Yallop B", "yallop_C": "Yallop C",
    "odeh_A": "Odeh A", "odeh_B": "Odeh B", "odeh_C": "Odeh C",
    "mabims": "Neo-MABIMS", "wujud": "wujud al-hilal", "conjunction": "conjunction",
}

# Reference places (name, Arabic name, coordinates of the main mosque or shrine or city centre)
PRESET_PLACES = [
    {"name": "Mecca", "name_ar": "مكة المكرمة", "lat": 21.4225, "lon": 39.8262, "tz": "Asia/Riyadh", "elev": 277},
    {"name": "Muscat", "name_ar": "مسقط", "lat": 23.5880, "lon": 58.3829, "tz": "Asia/Muscat", "elev": 15},
    {"name": "Sanaa", "name_ar": "صنعاء", "lat": 15.3694, "lon": 44.1910, "tz": "Asia/Aden", "elev": 2250},
    {"name": "Damascus", "name_ar": "دمشق", "lat": 33.5113, "lon": 36.3066, "tz": "Asia/Damascus", "elev": 690},
    {"name": "Medina", "name_ar": "المدينة المنورة", "lat": 24.4672, "lon": 39.6112, "tz": "Asia/Riyadh", "elev": 608},
    {"name": "Najaf", "name_ar": "النجف", "lat": 31.9961, "lon": 44.3146, "tz": "Asia/Baghdad", "elev": 60},
    {"name": "Karbala", "name_ar": "كربلاء", "lat": 32.6165, "lon": 44.0324, "tz": "Asia/Baghdad", "elev": 30},
    {"name": "Baghdad", "name_ar": "بغداد", "lat": 33.3152, "lon": 44.3661, "tz": "Asia/Baghdad", "elev": 34},
    {"name": "Qom", "name_ar": "قم", "lat": 34.6416, "lon": 50.8790, "tz": "Asia/Tehran", "elev": 928},
    {"name": "Tehran", "name_ar": "طهران", "lat": 35.6892, "lon": 51.3890, "tz": "Asia/Tehran", "elev": 1190},
    {"name": "Mashhad", "name_ar": "مشهد", "lat": 36.2880, "lon": 59.6157, "tz": "Asia/Tehran", "elev": 985},
    {"name": "Jerusalem", "name_ar": "القدس", "lat": 31.7761, "lon": 35.2358, "tz": "Asia/Jerusalem", "elev": 740},
    {"name": "Cairo", "name_ar": "القاهرة", "lat": 30.0459, "lon": 31.2627, "tz": "Africa/Cairo", "elev": 23},
    {"name": "Rabat", "name_ar": "الرباط", "lat": 34.0209, "lon": -6.8416, "tz": "Africa/Casablanca", "elev": 50},
    {"name": "Istanbul", "name_ar": "إسطنبول", "lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul", "elev": 40},
    {"name": "Kabul", "name_ar": "كابل", "lat": 34.5553, "lon": 69.2075, "tz": "Asia/Kabul", "elev": 1790},
    {"name": "Karachi", "name_ar": "كراتشي", "lat": 24.8607, "lon": 67.0011, "tz": "Asia/Karachi", "elev": 10},
    {"name": "Dhaka", "name_ar": "دكا", "lat": 23.8103, "lon": 90.4125, "tz": "Asia/Dhaka", "elev": 4},
    {"name": "Kuala Lumpur", "name_ar": "كوالالمبور", "lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur", "elev": 60},
    {"name": "Jakarta", "name_ar": "جاكرتا", "lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta", "elev": 8},
    {"name": "London", "name_ar": "لندن", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "elev": 11},
    {"name": "New York", "name_ar": "نيويورك", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York", "elev": 10},
]
PRESETS_BY_NAME = {p["name"]: p for p in PRESET_PLACES}


def _conj_before_sunset(row: dict) -> bool:
    c, s_ = row.get("conj_utc"), row.get("sunset_utc")
    try:
        return c is not None and s_ is not None and c == c and s_ == s_ and c < s_
    except TypeError:
        return False


def visible(row: dict, criterion: str) -> bool:
    """True if the crescent in this table row passes `criterion` (False if q/V are undefined)."""
    q, v = row["q"], row["v"]
    if criterion.startswith("yallop"):
        if q != q:
            return False
        return q > {"yallop_A": 0.216, "yallop_B": -0.014, "yallop_C": -0.160}[criterion]
    if criterion.startswith("odeh"):
        if v != v:
            return False
        return v >= {"odeh_A": 5.65, "odeh_B": 2.0, "odeh_C": -0.96}[criterion]
    if criterion == "mabims":
        alt, el = row.get("moon_alt_sunset"), row.get("elong_sunset_topo")
        if alt is None or el is None or alt != alt or el != el:
            return False
        return _conj_before_sunset(row) and alt >= 3.0 and el >= 6.4
    if criterion == "wujud":
        lag = row.get("lag_min")
        return _conj_before_sunset(row) and lag is not None and lag == lag and lag > 0
    if criterion == "conjunction":
        return _conj_before_sunset(row)
    raise ValueError(f"unknown criterion {criterion!r}")


def default_span(today: date | None = None) -> tuple[date, date]:
    t = today or date.today()
    return date(t.year - 3, t.month, 1), date(t.year + 3, 12, 31)


def _place_name(place: dict | None) -> str:
    return (place or se.MECCA).get("name") or "your place"


def evening_info(evening: date, place: dict | None = None) -> dict | None:
    """Crescent parameters on the evening of `evening` (civil date of the sunset) at `place`
    (default Mecca). None if no conjunction lies within a day before to three days after."""
    if cdat.is_mecca(place):
        return _mecca_index().row(evening)
    df = cdat.crescents_for(place, evening - timedelta(days=5), evening + timedelta(days=5))
    if df.empty:
        return None
    hit = df[df["evening"] == evening]
    return None if hit.empty else hit.iloc[0].to_dict()


@lru_cache(maxsize=1)
def _mecca_index() -> cdat.EveningIndex:
    return cdat.EveningIndex(cdat.mecca_crescents())


@lru_cache(maxsize=16)
def _index_for(key: tuple, start: date | None, end: date | None) -> cdat.EveningIndex:
    if key is None:
        return _mecca_index()
    lat, lon, tz = key
    df = cdat.crescents_for({"lat": lat, "lon": lon, "tz": tz}, start, end)
    return cdat.EveningIndex(df)


def _visible_on(ix: cdat.EveningIndex, evening: date, criterion: str) -> tuple[bool, dict | None]:
    r = ix.row(evening)
    if r is not None:
        return visible(r, criterion), r
    k = ix.days_since_conj(evening)
    return (k is not None and k >= 3), None


def month_chain(ix: cdat.EveningIndex, criterion: str, place_name: str) -> list[HMonth]:
    """Successive months (unnamed: year=0, month=0) from the first sighting in the table."""
    df = ix.df
    first_conj = df["conj_utc"].iloc[0]
    start = None
    for r in df[df["conj_utc"] == first_conj].to_dict("records"):
        if visible(r, criterion):
            start = r["evening"] + timedelta(days=1)
            break
    if start is None:
        start = df[df["conj_utc"] == first_conj]["evening"].iloc[-1] + timedelta(days=1)
    months: list[HMonth] = []
    d1, note, extra = start, "First sighting in the table", {}
    while True:
        eve29 = d1 + timedelta(days=28)
        if eve29 > ix.last_evening:
            break
        vis, r = _visible_on(ix, eve29, criterion)
        n = 29 if vis else 30
        months.append(HMonth(0, 0, d1, n, note=note, extra=extra))
        q = v = None
        zone_y = zone_o = ""
        conj = None
        if r is not None:
            q = None if r["q"] != r["q"] else float(r["q"])
            v = None if r["v"] != r["v"] else float(r["v"])
            zone_y, zone_o = r["yallop"], r["odeh"]
            conj = r["conj_utc"].to_pydatetime()
        crit = CRITERIA_SHORT[criterion]
        if vis and q is not None:
            note = (f"Crescent predicted visible from {place_name} on the evening of {eve29:%a %d %b %Y} "
                    f"({crit}; Yallop q = {q:+.3f}, zone {zone_y}; Odeh V = {v:+.2f}, zone {zone_o})")
        elif vis:
            note = f"Crescent predicted visible from {place_name} on the evening of {eve29:%a %d %b %Y}"
        else:
            qtxt = (f" (Yallop q = {q:+.3f}, zone {zone_y}; Odeh V = {v:+.2f}, zone {zone_o})"
                    if q is not None else " (the Moon set before the Sun, or the new moon had not yet happened)")
            note = (f"Crescent not predicted visible from {place_name} on the evening of {eve29:%a %d %b %Y}, "
                    f"which ended day 29{qtxt}. The month before was completed to 30 days")
        extra = {"sighting_evening": eve29 if vis else None, "evening29": eve29, "seen": vis,
                 "q": q, "v": v, "yallop": zone_y, "odeh": zone_o, "conj_utc": conj, "criterion": criterion}
        d1 = d1 + timedelta(days=n)
    return months


def _name_months(chain: list[HMonth]) -> tuple[list[HMonth], dict]:
    """Give each chain month the Hijri (year, month) of the Umm al-Qura month in the same place
    of the sequence. Returns (named months, statistics of start differences)."""
    from ummalqura_calendar import UmmAlQuraCalendar
    uq = UmmAlQuraCalendar("auto")
    uq_starts = uq._starts
    # offset: chain month i <-> Umm al-Qura month i + k, from the first chain month that matches
    k = None
    for i, m in enumerate(chain):
        um = uq.month_of(m.start)
        if um is None:
            continue
        for cand in (uq.months.index(um), uq.months.index(um) + 1):
            if 0 <= cand < len(uq.months) and abs((uq.months[cand].start - m.start).days) <= 3:
                k = cand - i
                break
        if k is not None:
            break
    if k is None:
        raise RuntimeError("could not match the sighting chain to the Umm al-Qura calendar")
    out, diffs, far = [], {}, 0
    for i, m in enumerate(chain):
        j = i + k
        if not 0 <= j < len(uq.months):
            continue
        um = uq.months[j]
        dd = (m.start - um.start).days
        diffs[dd] = diffs.get(dd, 0) + 1
        if abs(dd) > 3:
            far += 1
        m.year, m.month = um.year, um.month
        m.extra = {**m.extra, "ummalqura_start": um.start, "diff_vs_ummalqura": dd}
        out.append(m)
    return out, {"start_minus_ummalqura": dict(sorted(diffs.items())), "beyond_3_days": far}


@lru_cache(maxsize=24)
def _calendar(key, criterion: str, span: tuple | None, place_name: str):
    if key is None:
        ix = _mecca_index()
    else:
        s, e = span
        ix = _index_for(key, s - timedelta(days=75), e + timedelta(days=40))
    chain = month_chain(ix, criterion, place_name)
    if span is not None:
        # drop the first months, while the chain settles (it starts 75 days before the span)
        chain = [m for m in chain if m.end >= span[0] - timedelta(days=20)]
    named, stats = _name_months(chain)
    return tuple(named), stats


class SightingCalendar(LunarCalendar):
    kind = "sighting"
    label = "Predicted sighting (ru'yah)"
    label_ar = "الرؤية المتوقعة للهلال"

    def __init__(self, place: dict | None = None, criterion: str = DEFAULT_CRITERION,
                 span: tuple[date, date] | None = None):
        if criterion not in CRITERIA:
            raise ValueError(f"criterion must be one of {list(CRITERIA)}")
        self.place = place or se.MECCA
        self.criterion = criterion
        self.mecca = cdat.is_mecca(place)
        if self.mecca:
            self.span = None
            key = None
        else:
            self.span = tuple(span) if span else default_span()
            key = cdat.place_key(self.place)
        months, self.stats = _calendar(key, criterion, self.span, _place_name(self.place))
        # copies, so callers can't change the cached months
        self._set_months([HMonth(m.year, m.month, m.start, m.length, m.note, dict(m.extra)) for m in months])

    def evening_info(self, evening: date) -> dict | None:
        return evening_info(evening, self.place)
