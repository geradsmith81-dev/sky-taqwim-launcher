"""The app's pages. Each render_* function draws one page."""
from __future__ import annotations

import html
import os
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

import arabic_names as an  # noqa: E402
import calendars as cv  # noqa: E402
import device  # noqa: E402
import holiday_history as hh  # noqa: E402
import holidays as hol  # noqa: E402
import prayer_times as pt  # noqa: E402
import qibla as qb  # noqa: E402
import qibla_live  # noqa: E402
import sects  # noqa: E402
import sighting_calendar as sc  # noqa: E402
import sky_engine as se  # noqa: E402
import tabular_calendar as tc  # noqa: E402
import theme  # noqa: E402
from arabic_names import bi  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
WEEK = an.GRID_WEEK                       # Saturday first
WEEK_START = an.GRID_WEEK_START           # date.weekday() of Saturday
FRIDAY = an.FRIDAY
RAMADAN = 9
JUMUAH = "Jumu'ah"
PHASE_NAMES = ["New moon", "First quarter", "Full moon", "Last quarter"]
PRAYERS = [("imsak", "Imsak"), ("fajr", "Fajr"), ("sunrise", "Sunrise"), ("dhuhr", "Dhuhr"), ("asr", "Asr"),
           ("sunset", "Sunset"), ("maghrib", "Maghrib"), ("isha", "Isha"), ("midnight", "Midnight")]
PRAYER_AR = {"imsak": "الإمساك", "fajr": "الفجر", "sunrise": "الشروق", "dhuhr": "الظهر", "asr": "العصر",
             "sunset": "الغروب", "maghrib": "المغرب", "isha": "العشاء", "midnight": "منتصف الليل"}


# ----------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------
def t12(dt) -> str:
    if dt is None:
        return "-"
    return dt.strftime("%I:%M %p").lstrip("0").lower()


def esc(s) -> str:
    return html.escape(str(s))


def rel(dd: int, ref: str) -> str:
    """'the same day as X' / '1 day after X' / '2 days before X'."""
    if dd == 0:
        return f"the same day as {ref}"
    n = abs(dd)
    return f"{n} day{'s' if n > 1 else ''} {'after' if dd > 0 else 'before'} {ref}"


def card(title: str, body: str) -> str:
    return f"<div class='tq-card'><h3>{title}</h3>{body}</div>"


def ttl(en: str, ar: str) -> str:
    return f"{esc(en)} · <span class='tq-ar' lang='ar' dir='rtl'>{esc(ar)}</span>"


def sky_ok() -> bool:
    try:
        se.load()
        return True
    except Exception as exc:
        st.warning(f"Prayer times and the Moon need the JPL file de440s.bsp, which could not be loaded: {exc}. "
                   "The tabular calendar still works.")
        return False


def hijri_text(h, arabic=True) -> str:
    if h is None:
        return "<span class='tq-muted'>outside the range of this calendar</span>"
    out = esc(str(h))
    if arabic:
        c = "solar" if type(h).__name__ == "SolarDay" else getattr(h, "calendar", "lunar")
        a = h.arabic() if callable(h.arabic) else h.arabic
        out += f" <span class='tq-ar' lang='{ {'solar': 'fa', 'ahmadi': 'ur'}.get(c, 'ar') }' dir='rtl'>{esc(a)}</span>"
    return out


def chip_for(h, align_right=False) -> str:
    c = theme.chip(h.kind, h.name, h.arabic)
    return hh.clickable(h.key or h.name, c, align_right=align_right)


@st.cache_data(max_entries=64, show_spinner=False)
def prayer_days(lat, lon, tz, start: date, end: date, method, asr, high_lat, imsak) -> dict:
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    rows = pt.times_for_days(lat, lon, tz, days, method=method, asr=asr, high_lat=high_lat, imsak_minutes=imsak)
    return {r["date"]: r for r in rows}


def prayers(ctx, start: date, end: date) -> dict:
    p = ctx["place"]
    return prayer_days(float(p["lat"]), float(p["lon"]), p["tz"], start, end, ctx["method"], ctx["asr"],
                       ctx["high_lat"], ctx["imsak"])


@st.cache_data(max_entries=48, show_spinner=False)
def moon_days(start: date, end: date, tz: str) -> dict:
    """Moon illumination at local 8 pm and the principal phases (local dates) for each day."""
    zt = ZoneInfo(tz)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    when = [datetime(d.year, d.month, d.day, 20, tzinfo=zt).astimezone(timezone.utc) for d in days]
    illum = se.moon_illumination(when)
    elong = se.moon_elongation(when)
    out = {d: {"illum": float(i), "waxing": float(e) < 180.0, "event": None, "event_time": None}
           for d, i, e in zip(days, illum, elong)}
    for t, ph in se.moon_phase_events(start - timedelta(days=1), end + timedelta(days=2)):
        ld = t.astimezone(zt)
        if ld.date() in out:
            out[ld.date()]["event"] = PHASE_NAMES[ph]
            out[ld.date()]["event_time"] = ld
    return out


@st.cache_data(max_entries=64, show_spinner=False)
def crescent_rows(lat, lon, tz, name, start: date, end: date) -> list[dict]:
    df = se.crescent_table(start, end, {"name": name, "lat": lat, "lon": lon, "tz": tz}, days_before=0, days_after=3)
    return df.to_dict("records") if len(df) else []


def visible(row, crit) -> bool:
    try:
        return bool(sc.visible(row, crit))
    except Exception:
        return False


def verdict(row) -> str:
    if row is None or pd.isna(row.get("q")):
        return "Moon sets before the Sun, or before the new moon"
    return f"Yallop {row['yallop']}: {se.YALLOP_TEXT[row['yallop']]}; Odeh {row['odeh']}: {se.ODEH_TEXT[row['odeh']]}"


def year_label(view, y: int) -> str:
    ms = view.year_months(y)
    if not ms:
        return f"{y} {view.era}"
    a, b = ms[0].start.year, ms[-1].end.year
    return f"{y} {view.era} ({a}–{b})" if a != b else f"{y} {view.era} ({a})"


def year_picker(view, ctx, key: str) -> int:
    years = view.years()
    cur = view.year_of(ctx["today"]) or years[len(years) // 2]
    cur = min(max(cur, years[0]), years[-1])
    return st.selectbox(f"{'Hijri' if view.lunar else view.name} year", years, index=years.index(cur),
                        key=f"{key}_{view.key}", format_func=lambda y: year_label(view, y))


def range_note(view):
    if view.key == cv.SIGHTING and view.cal.first_day > date(1900, 1, 1):
        st.caption(f"Sighting from this place is computed for {view.first_day:%b %Y} – {view.last_day:%b %Y}. "
                   "Choose a rule seen from Mecca for 1850–2149.")


# ----------------------------------------------------------------------------------------------
# Today
# ----------------------------------------------------------------------------------------------
def render_today(ctx):
    place, view, branch = ctx["place"], ctx["view"], ctx["branch"]
    tz = ZoneInfo(place["tz"])
    now = datetime.now(tz)
    today = now.date()
    have_sky = sky_ok()
    z = prayers(ctx, today - timedelta(days=1), today + timedelta(days=1)) if have_sky else {}
    zt = z.get(today, {})
    after_sunset = bool(zt.get("sunset")) and now >= zt["sunset"]

    cols = st.columns(1 if device.phone() else 2)
    with cols[0]:
        wd = today.weekday()
        body = (f"<div class='tq-big'>{bi(an.WEEKDAY_EN[wd], an.WEEKDAY_AR[wd])}, {today:%d %B %Y}</div>"
                f"<div class='tq-muted'>{bi(place['label'], place.get('ar', ''))} · local time {now:%H:%M}</div>")
        if after_sunset:
            body += ("<div class='tq-obs'>The sun has set: the next Islamic day has begun "
                     "(the solar calendars change day at midnight).</div>")
        st.html(card(ttl("Today", "اليوم"), body))
        for v in (view,):   # only the calendar chosen in the settings (the Compare page sets them side by side)
            title = ttl(v.name, v.name_ar)
            h = v.hdate(today)
            if h is None:
                st.html(card(title, "<span class='tq-muted'>Outside the range of this calendar.</span>"))
                continue
            line = f"<div class='tq-big'>{esc(h)}</div><div class='tq-ar-big' lang='{v.lang}' dir='rtl'>{esc(h.arabic())}</div>"
            if not v.solar:
                ep = an.MONTH_EPITHETS.get(h.month)
                if ep:
                    line += f"<div class='tq-muted'>{bi(ep[0], ep[1])}"
                    line += (" · one of the four sacred months</div>" if an.is_sacred_month(h.month) else "</div>")
                n = v.hdate(today + timedelta(days=1))
                if n is not None and zt.get("sunset"):
                    when = "began at sunset" if after_sunset else "begins at sunset"
                    line += f"<div class='tq-muted'>{esc(n)} {when} this evening ({t12(zt.get('sunset'))}).</div>"
            line += f"<div class='tq-muted' style='font-size:.82rem'>{esc(v.detail)}</div>"
            st.html(card(title, line))
    with cols[-1]:
        if have_sky and zt:
            ram = ctx["view"].hdate(today)
            ram = ram is not None and not view.solar and ram.month == RAMADAN
            nxt = None
            for k, _ in PRAYERS:
                if k in ("imsak", "sunset", "midnight", "sunrise"):
                    continue
                if zt.get(k) and zt[k] > now:
                    nxt = k
                    break
            rows = []
            for k, en in PRAYERS:
                if k == "sunset" and zt.get("maghrib") == zt.get("sunset"):
                    continue
                v = zt.get(k)
                lab = bi(en, PRAYER_AR[k])
                if ram and k == "imsak":
                    lab += " <span class='tq-muted'>(suhur ends)</span>"
                if ram and k == "maghrib":
                    lab += " <span class='tq-muted'>(iftar)</span>"
                style = " style='color:#ebc25f'" if k == nxt else ""
                rows.append(f"<tr><td{style}>{lab}{' ◀ next' if k == nxt else ''}</td><td{style}><b>{t12(v)}</b></td></tr>")
            m = pt.METHODS[ctx["method"]]
            body = ("<table class='tq-table'>" + "".join(rows) + "</table>"
                    f"<div class='tq-muted'>Method: {bi(m['label'], m.get('label_ar', ''))}"
                    + (f", Asr {'Hanafi' if ctx['asr'] == 'hanafi' else 'standard'}" if branch == "sunni" else "")
                    + ".</div>")
            if branch == "shia":
                body += ("<div class='tq-muted'>Ja'fari practice: Maghrib once the redness has left the eastern sky; "
                         "Dhuhr with Asr, and Maghrib with Isha, may be prayed together.</div>")
            st.html(card(ttl("Prayer times today", "مواقيت الصلاة اليوم"), body))
        b, dist = qb.qibla(float(place["lat"]), float(place["lon"]))
        if dist < 0.5:
            st.html(card(ttl("Qibla", "القبلة"), "<div>You are at the Kaaba.</div>"))
        else:
            qibla_live.show(b, place.get("name", ""), dist, float(place["lat"]), float(place["lon"]),
                            ttl("Qibla", "القبلة"), size=200 if device.phone() else 170)
    if have_sky:
        _moon_card(ctx, now, tz)
    hs = [h for h in view.holidays_between(today, today + timedelta(days=75)) if h.kind != "month"][:14]
    if hs:
        rows = [f"<tr><td>{h.date:%a %d %b}</td><td>{chip_for(h)}</td>"
                f"<td class='tq-muted'>{esc(h.hdate) if h.hdate else ''}</td></tr>" for h in hs]
        st.html(card(ttl(f"Coming up — {view.name}", "قريبًا"), "<table class='tq-table'>" + "".join(rows) + "</table>"
                     "<div class='tq-muted'>Click a name for a short history of the day.</div>"))


def _moon_card(ctx, now, tz):
    today = now.date()
    md = moon_days(today, today, ctx["place"]["tz"])[today]
    conj = se.new_moons(today - timedelta(days=31), today + timedelta(days=31))
    nowu = now.astimezone(timezone.utc)
    past = [c for c in conj if c <= nowu]
    fut = [c for c in conj if c > nowu]
    body = f"<div>{theme.moon(md['illum'], md['waxing'], 26)} Moon {md['illum'] * 100:.0f}% lit this evening"
    if past:
        age = (nowu - past[-1]).total_seconds() / 86400
        body += f", {age:.1f} days since the new moon ({past[-1].astimezone(tz):%d %b %H:%M})"
    body += ".</div>"
    if fut:
        body += f"<div>Next new moon (conjunction): <b>{fut[0].astimezone(tz):%a %d %b %Y, %H:%M}</b> your time.</div>"
        sview = ctx["views"][cv.SIGHTING]
        cal = sview.cal
        for k in range(0, 4):
            e = fut[0].astimezone(ZoneInfo(cal.place["tz"])).date() + timedelta(days=k)
            try:
                info = cal.evening_info(e)
            except Exception:
                info = None
            if info and visible(info, ctx["crit"]):
                body += (f"<div class='tq-obs'>First crescent predicted {esc(sview.detail)} on the evening of "
                         f"<b>{e:%a %d %b}</b> ({esc(verdict(info))}).</div>")
                break
    st.html(card(ttl("The Moon", "القمر"), body))


# ----------------------------------------------------------------------------------------------
# Month
# ----------------------------------------------------------------------------------------------
def render_month(ctx):
    view, place = ctx["view"], ctx["place"]
    today = ctx["today"]
    akey = "anchor"
    if akey not in st.session_state:
        st.session_state[akey] = today
    anchor = st.session_state[akey]
    if not view.covers(anchor):
        anchor = min(max(anchor, view.first_day), view.last_day)
        st.session_state[akey] = anchor
    m = view.month_at(anchor)

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.4])
    if c1.button("◀ Previous", key="prev_m", width="stretch"):
        st.session_state[akey] = m.start - timedelta(days=1)
        st.rerun()
    if c2.button("This month", key="today_m", width="stretch"):
        st.session_state[akey] = today
        st.rerun()
    if c3.button("Next ▶", key="next_m", width="stretch"):
        st.session_state[akey] = m.end + timedelta(days=1)
        st.rerun()
    picked = c4.date_input("Go to a date", value=anchor, min_value=view.first_day, max_value=view.last_day,
                           key=f"goto_{anchor.isoformat()}", label_visibility="collapsed", format="DD/MM/YYYY")
    if picked != anchor:
        st.session_state[akey] = picked
        st.rerun()

    en, ar = view.month_name(m.month)
    num = view.digits(m.year)
    extra = ""
    if not view.solar:
        ep = an.MONTH_EPITHETS.get(m.month)
        if ep:
            extra = f"<div class='tq-obs'>{bi(ep[0], ep[1])}"
            extra += " · one of the four sacred months (Qur'an 9:36)</div>" if an.is_sacred_month(m.month) else "</div>"
    st.html(f"<div class='tq-big'>{esc(en)} {m.year} {view.era} <span class='tq-ar-big' lang='{view.lang}' "
            f"dir='rtl'>{esc(ar)} {num}</span></div>{extra}"
            f"<div class='tq-muted'>{bi(view.name, view.name_ar)} ({esc(view.detail)}) · {m.start:%d %b %Y} – "
            f"{m.end:%d %b %Y} · {m.length} days</div>")
    range_note(view)

    days = [m.start + timedelta(days=i) for i in range(m.length)]
    have_sky = sky_ok()
    z = prayers(ctx, m.start, m.end) if have_sky else {}
    moon = moon_days(m.start, m.end, place["tz"]) if have_sky else {}
    hols = {}
    for h in view.holidays_between(m.start, m.end):
        hols.setdefault(h.date, []).append(h)
    is_ram = (not view.solar) and m.month == RAMADAN

    def cell_lines(d):
        out = []
        for h in hols.get(d, []):
            out.append(chip_for(h, align_right=((d.weekday() - WEEK_START) % 7 >= 4 and not device.phone())))
        zz = z.get(d)
        if zz:
            if is_ram:
                out.append(f"<span class='tq-line'>Imsak <b>{t12(zz.get('imsak'))}</b> · Iftar <b>{t12(zz.get('maghrib'))}</b></span>")
            elif d.weekday() == FRIDAY:
                out.append(f"<span class='tq-line'>{bi(JUMUAH, 'الجمعة')} <b>{t12(zz.get('dhuhr'))}</b></span>")
        mi = moon.get(d)
        if mi and mi["event"]:
            illum = {"New moon": 0.0, "First quarter": 0.5, "Full moon": 1.0, "Last quarter": 0.5}[mi["event"]]
            out.append(f"<span class='tq-line'>{theme.moon(illum, mi['event'] != 'Last quarter', 14)} "
                       f"{esc(mi['event'])} {mi['event_time']:%H:%M}</span>")
        return "".join(out)

    def hd(h):
        if h is None:
            return ""
        dig = view.digits(h.day)
        return f"<span class='tq-hd'>{dig} <small>{h.day}</small></span>"

    if device.phone():
        rows = []
        for d in days:
            h = view.hdate(d)
            cls = " tq-fri" if d.weekday() == FRIDAY else ""
            cls += " tq-ram" if is_ram and d.weekday() != FRIDAY else ""
            cls += " tq-today" if d == today else ""
            rows.append(f"<tr><td class='{cls}' style='width:34%'><span class='tq-civ'>{h.day}</span> "
                        f"<span class='tq-ar'>{view.digits(h.day)}</span><br>"
                        f"<span class='tq-muted'>{an.WEEKDAY_EN[d.weekday()][:3]} {d:%d %b}</span></td>"
                        f"<td class='{cls}'>{cell_lines(d)}</td></tr>")
        st.html("<table class='tq-list'>" + "".join(rows) + "</table>")
    else:
        lead = (m.start.weekday() - WEEK_START) % 7
        cells = ["<td class='tq-empty'></td>"] * lead
        for d in days:
            h = view.hdate(d)
            cls = []
            if d.weekday() == FRIDAY:
                cls.append("tq-fri")
            elif is_ram:
                cls.append("tq-ram")
            if d == today:
                cls.append("tq-today")
            civm = f"<span class='tq-civm'>{d:%b}</span>" if (d.day == 1 or d == m.start) else ""
            cells.append(f"<td class='{' '.join(cls)}'><span class='tq-civ'>{d.day}</span>{civm}{hd(h)}"
                         f"{cell_lines(d)}</td>")
        while len(cells) % 7:
            cells.append("<td class='tq-empty'></td>")
        rows = "".join("<tr>" + "".join(cells[i:i + 7]) + "</tr>" for i in range(0, len(cells), 7))
        st.html("<table class='tq-grid'><tr>" + "".join(f"<th>{w} <span class='tq-ar'>{a}</span></th>" for w, a in WEEK)
                + "</tr>" + rows + "</table>")
    st.html(theme.legend(set(h.kind for hs in hols.values() for h in hs) or None)
            + "<div class='tq-muted' style='margin-top:.3rem'>Large numbers: the civil date. Corner: the "
            f"{'Hijri' if view.lunar else view.name} day. Click a holy day's name for a short history. "
            + ("Each Islamic day begins at the sunset before." if not view.solar else "") + "</div>")
    _month_began(ctx, view, m)
    st.caption("Only the calendar chosen in the settings is shown. The Compare page sets the calendars side by side.")


def _month_began(ctx, view, m):
    tz = ZoneInfo(ctx["place"]["tz"])
    if view.key == cv.UMMALQURA:
        body = f"<div>{esc(m.note)}.</div>"
        x = m.extra or {}
        if x.get("source") == "computed" and x.get("conj_utc"):
            body += (f"<div class='tq-muted'>On the 29th day ({x['day29']:%a %d %b %Y}): new moon "
                     f"{x['conj_utc'].astimezone(tz):%d %b %H:%M} your time; Moon set "
                     f"{abs(x.get('lag_min') or 0):.0f} min {'after' if (x.get('lag_min') or 0) > 0 else 'before'} the Sun at Mecca.</div>")
        elif x.get("source") == "official":
            body += ("<div class='tq-muted'>From the table published by the King Abdulaziz City for Science and "
                     "Technology (KACST). The rule since 1423 AH: if on the 29th the new moon comes before sunset at "
                     "Mecca and the Moon sets after the Sun, the next day begins the month.</div>")
        st.html(card(ttl("How this month began", "بداية الشهر"), body))
    elif view.key == cv.SIGHTING:
        body = f"<div>{esc(m.note)}.</div>"
        rows = []
        for k in (2, 1, 0):
            e = m.start - timedelta(days=k)
            try:
                info = view.cal.evening_info(e)
            except Exception:
                info = None
            if info is None:
                continue
            if pd.isna(info.get("q")):
                qtxt, vtxt, vd = "-", "-", "Moon sets before the Sun or before the new moon"
            else:
                qtxt = f"{info['q']:+.3f} ({info['yallop']})"
                vtxt = f"{info['v']:+.2f} ({info['odeh']})"
                vd = "visible by the rule in use" if visible(info, ctx["crit"]) else "not visible by the rule in use"
            vd = "passes the rule in use" if visible(info, ctx["crit"]) else "does not pass the rule in use"
            alt0, el0 = info.get("moon_alt_sunset"), info.get("elong_sunset_topo")
            rows.append(f"<tr><td>{e:%a %d %b}</td><td>{qtxt}</td><td>{vtxt}</td><td>{info['lag_min']:.0f}</td>"
                        f"<td>{info['age_h']:.1f}</td>"
                        f"<td>{'-' if alt0 is None or alt0 != alt0 else f'{alt0:.1f}°'}</td>"
                        f"<td>{'-' if el0 is None or el0 != el0 else f'{el0:.1f}°'}</td><td>{esc(vd)}</td></tr>")
        if rows:
            body += ("<table class='tq-table'><tr><th>Evening</th><th>Yallop q</th><th>Odeh V</th><th>Moon sets after "
                     "the Sun (min)</th><th>Moon age (h)</th><th>Moon height at sunset</th><th>Elongation at sunset</th>"
                     "<th>Verdict</th></tr>"
                     + "".join(rows) + "</table>")
        body += f"<div class='tq-muted'>Rule in use: {esc(sc.CRITERIA[ctx['crit']])}, seen {esc(view.detail.split(',')[0])}.</div>"
        st.html(card(ttl("How this month began", "رؤية الهلال"), body))
    elif view.key == cv.TABULAR:
        var = view.cal.variant
        leaps = tc.VARIANTS[var]["leaps"]
        pos = (m.year - 1) % 30 + 1
        cyc = "".join(f"<span class='tq-cycle {'leap' if k in leaps else 'common'}{' now' if k == pos else ''}'>{k}</span>"
                      for k in range(1, 31))
        body = (f"<div>{esc(m.note)}. Odd months have 30 days and even months 29; in a leap year Dhu al-Hijjah has 30.</div>"
                f"<div>Year {m.year} is year <b>{pos}</b> of 30 in the cycle; gold = leap years "
                f"({', '.join(map(str, leaps))}). {'A leap year: 355 days.' if view.cal.is_leap(m.year) else 'A common year: 354 days.'}</div>"
                f"<div style='margin:.4rem 0'>{cyc}</div>"
                f"<div class='tq-muted'>Epoch: {esc(tc.VARIANTS[var].get('epoch_note', ''))}.</div>")
        st.html(card(ttl("The 30-year cycle", "الدورة الثلاثينية"), body))
    elif view.key == cv.UNIFIED:
        body = f"<div>{esc(m.note)}.</div>"
        body += ("<div class='tq-muted'>Clause A: the Moon at least 5 deg high and 8 deg from the Sun at a sunset "
                 "anywhere before 00:00 UT. Clause B: the same on the Americas mainland after 00:00 UT, if the new "
                 "moon came before dawn in Wellington. The same day is the 1st everywhere on Earth.</div>")
        st.html(card(ttl("How this month began", "التقويم الموحد"), body))
    elif view.key in (cv.AHMADI, cv.JULIAN):
        if view.key == cv.AHMADI:
            body = ("<div>Hijri Shamsi months have the same days as the Gregorian months; the year is the Gregorian "
                    "year minus 621, counted from the Hijra in solar years. Ramadan and the Eids still follow the "
                    "lunar months.</div>")
        else:
            body = (f"<div>{esc(m.note)}.</div><div class='tq-muted'>The Julian year has a leap day every fourth "
                    "year without exception, so it falls one day further behind the Gregorian calendar in 2100. "
                    "Days run from midnight.</div>")
        st.html(card(ttl("About this calendar", "عن هذا التقويم"), body))
    else:
        body = f"<div>{esc(m.note)}.</div>" if m.note else ""
        body += ("<div class='tq-muted'>Months 1–6 have 31 days, 7–11 have 30, and Esfand 29 (30 in a leap year). "
                 "The year begins on the day of the March equinox if it comes before noon in Iran, otherwise the next "
                 "day. Religious days follow the lunar months.</div>")
        st.html(card(ttl("The solar year", "السنة الشمسية"), body))


# ----------------------------------------------------------------------------------------------
# Year
# ----------------------------------------------------------------------------------------------
def render_year(ctx):
    view, place = ctx["view"], ctx["place"]
    y = year_picker(view, ctx, "year_y")
    range_note(view)
    all_h = view.holidays_for_year(y)
    present = [k for k in theme.KIND_LABEL if any(h.kind == k for h in all_h)]
    kinds = st.multiselect("Show", present, default=[k for k in present if k != "month"],
                           format_func=lambda k: theme.KIND_LABEL[k], key=f"year_kinds_{ctx['branch']}_{view.key}")
    hs = [h for h in all_h if h.kind in kinds]
    if not hs:
        st.info("Nothing to show for this year with these choices.")
        return
    have_sky = sky_ok()
    z = prayers(ctx, hs[0].date - timedelta(days=1), hs[-1].date) if have_sky else {}
    rows, recs = [], []
    for h in hs:
        prev = z.get(h.date - timedelta(days=1), {})
        if h.begins_evening_before and not view.solar:
            starts = f"sunset the evening before ({t12(prev.get('maghrib') or prev.get('sunset'))})" if prev else "the evening before"
        elif h.kind == "fast":
            zz = z.get(h.date, {})
            starts = f"dawn (Fajr {t12(zz.get('fajr'))})" if zz else "dawn"
        else:
            starts = ""
        rows.append(f"<tr><td>{h.date:%a %d %b %Y}</td><td>{chip_for(h)}"
                    f"{'<br><span class=tq-muted>' + esc(h.note) + '</span>' if h.note else ''}</td>"
                    f"<td>{hijri_text(h.hdate) if h.hdate else ''}</td><td>{esc(starts)}</td></tr>")
        recs.append({"date": h.date.isoformat(), "weekday": h.date.strftime("%A"), "day": h.name, "arabic": h.arabic,
                     "hijri_date": str(h.hdate) if h.hdate else "", "kind": theme.KIND_LABEL.get(h.kind, h.kind),
                     "begins": starts, "note": h.note, "calendar": f"{view.name} ({view.detail})",
                     "tradition": cv.BRANCH_NAME[ctx["branch"]][0]})
    st.html(f"<div class='tq-big'>{esc(year_label(view, y))} — {bi(view.name, view.name_ar)}</div>"
            f"<div class='tq-muted'>{esc(view.detail)} · {cv.BRANCH_NAME[ctx['branch']][0]} holy days"
            + (f" · {view.cal.year_length(y)} days" if view.cal.year_length(y) else "") + "</div>")
    st.html("<table class='tq-table'><tr><th>Date</th><th>Day</th><th>Date in this calendar</th><th>Begins</th></tr>"
            + "".join(rows) + "</table>")
    df = pd.DataFrame(recs)
    c1, c2 = st.columns(2)
    nm = f"{view.name} {y} {view.era} ({cv.BRANCH_NAME[ctx['branch']][0]})"
    c1.download_button("Download for your calendar app (.ics)", cv.to_ics(hs, nm),
                       file_name=f"sky_taqwim_{view.key}_{ctx['branch']}_{y}.ics", mime="text/calendar", width="stretch")
    c2.download_button("Download as a spreadsheet (.csv)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"sky_taqwim_{view.key}_{ctx['branch']}_{y}.csv", mime="text/csv", width="stretch")
    st.caption("Click a name for a short history. Islamic days begin at sunset the evening before (for the Shia "
               "Maghrib time, after the redness has left the eastern sky); fasts run from dawn to sunset.")


# ----------------------------------------------------------------------------------------------
# Prayer times
# ----------------------------------------------------------------------------------------------
def render_prayer(ctx):
    place, branch = ctx["place"], ctx["branch"]
    if not sky_ok():
        return
    today = ctx["today"]
    c1, c2 = st.columns([1, 2])
    d0 = c1.date_input("Month starting", value=date(today.year, today.month, 1), key="pt_month", format="DD/MM/YYYY",
                       min_value=date(1850, 2, 1), max_value=date(2149, 11, 30))
    start = date(d0.year, d0.month, 1)
    end = (date(start.year + (start.month == 12), start.month % 12 + 1, 1) - timedelta(days=1))
    z = prayers(ctx, start, end)
    view = ctx["view"]
    rows = []
    for d in sorted(z):
        r = z[d]
        h = view.hdate(d)
        rec = {"date": d.strftime("%a %d %b"), "hijri": f"{h.day} {h.month_name}" if h else ""}
        for k, en in PRAYERS:
            if k == "sunset" and r.get("maghrib") == r.get("sunset"):
                continue
            rec[f"{en} {PRAYER_AR[k]}"] = r[k].strftime("%H:%M") if r.get(k) else "-"
        rows.append(rec)
    df = pd.DataFrame(rows)
    m = pt.METHODS[ctx["method"]]
    c2.html(card(ttl("Method", "طريقة الحساب"),
                 f"<div>{bi(m['label'], m.get('label_ar', ''))}</div>"
                 f"<div class='tq-muted'>Fajr: Sun {m['fajr']}° below the horizon · Isha: "
                 + (f"{m['isha']}° below" if m.get("isha") else f"{m.get('isha_min')} min after Maghrib")
                 + (f" · Maghrib: Sun {m['maghrib']}° below (after the eastern redness)" if m.get("maghrib") else " · Maghrib: sunset")
                 + f" · Midnight: {'sunset to Fajr' if m.get('midnight') == 'jafari' else 'sunset to sunrise'}"
                 + f"</div><div class='tq-muted' style='font-size:.8rem'>Source: {esc(m.get('source', ''))}</div>"))
    st.html(f"<div class='tq-big'>{start:%B %Y} · {bi(place['label'], place.get('ar', ''))}</div>")
    # An HTML table rather than st.dataframe: the data grid is drawn on a canvas in Streamlit's own colours,
    # which page CSS cannot reach, so in light mode it would not match (or would lose contrast).
    today_s = datetime.now(ZoneInfo(place["tz"])).date().strftime("%a %d %b") if place.get("tz") else ""
    head = "".join(f"<th>{esc(c)}</th>" for c in df.columns)
    body = "".join("<tr" + (" class='tq-today-row'" if r["date"] == today_s else "") + ">"
                   + "".join(f"<td>{esc(str(v))}</td>" for v in r.values()) + "</tr>" for r in rows)
    st.html(f"<div class='tq-scroll'><table class='tq-table tq-times'><thead><tr>{head}</tr></thead>"
            f"<tbody>{body}</tbody></table></div>")
    st.download_button("Download this timetable (.csv)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"sky_taqwim_prayer_{place.get('name', 'place')}_{start:%Y_%m}.csv", mime="text/csv")
    notes = [
        "Times are computed from the Sun's position in NASA JPL DE440s for the exact coordinates, with standard "
        "refraction and a sea-level horizon. Mosques often publish times with a few minutes of precaution added.",
        "Imsak is shown a set number of minutes before Fajr (change it in the settings).",
    ]
    if branch == "shia":
        notes.append("Ja'fari practice: Maghrib once the redness has left the eastern sky (the Sun about 4° below "
                     "the horizon); the 'midnight' that ends the time of Isha is halfway between sunset and Fajr. "
                     "Dhuhr and Asr, and Maghrib and Isha, may be prayed together.")
    else:
        notes.append("Asr: the Shafi'i, Maliki and Hanbali schools begin it when an object's shadow equals its "
                     "length (plus the noon shadow); the Hanafi school when it is twice the length.")
    st.html(card(ttl("Notes", "ملاحظات"), "".join(f"<p>{esc(n)}</p>" for n in notes)))


# ----------------------------------------------------------------------------------------------
# Crescent
# ----------------------------------------------------------------------------------------------
def render_crescent(ctx):
    if not sky_ok():
        return
    place, crit = ctx["place"], ctx["crit"]
    tz = ZoneInfo(place["tz"])
    now = datetime.now(tz)
    conj = se.new_moons(now.date() - timedelta(days=40), now.date() + timedelta(days=40))
    nowu = now.astimezone(timezone.utc)
    # the new moon whose crescent is due now: the last one if it was less than 4 days ago, else the next
    past = [c for c in conj if c <= nowu]
    fut = [c for c in conj if c > nowu]
    choices = conj
    default = past[-1] if past and (nowu - past[-1]).days < 4 else (fut[0] if fut else conj[-1])
    c = st.selectbox("New moon", choices, index=choices.index(default), key="cres_conj",
                     format_func=lambda c: f"{c.astimezone(tz):%a %d %b %Y, %H:%M} (your time)")
    st.html(f"<div class='tq-muted'>Predicted visibility on the evenings after the new moon of "
            f"{c.astimezone(tz):%d %B %Y}, for the rule in use: <b>{esc(sc.CRITERIA[crit])}</b>. "
            "✓ = visible by that rule. The letters give the Yallop and Odeh zones.</div>")
    start = c.date()
    end = start + timedelta(days=3)
    pl_list = [{"name": place.get("name", "Your place"), "name_ar": place.get("ar", ""), "lat": float(place["lat"]),
                "lon": float(place["lon"]), "tz": place["tz"], "yours": True}]
    pl_list += [dict(p, yours=False) for p in sc.PRESET_PLACES if p["name"] != place.get("name")]
    evenings = [start + timedelta(days=k) for k in range(0, 4)]
    head = "<tr><th>Place</th>" + "".join(f"<th>{e:%a %d %b}</th>" for e in evenings) + "</tr>"
    rows = []
    mine = []
    for p in pl_list:
        rs = crescent_rows(round(p["lat"], 3), round(p["lon"], 3), p["tz"], p["name"], start - timedelta(days=1), end)
        by = {r["evening"]: r for r in rs if abs((pd.Timestamp(r["conj_utc"]).to_pydatetime() - c).total_seconds()) < 86400 * 2}
        cells = []
        for e in evenings:
            r = by.get(e)
            if r is None or pd.isna(r.get("q")):
                cells.append("<td class='tq-muted'>—</td>")
            else:
                ok = visible(r, crit)
                cells.append(f"<td{' class=tq-diff' if ok else ''}>{'✓ ' if ok else ''}{r['yallop']} / {r['odeh']}</td>")
        lab = bi(p["name"], p.get("name_ar", "")) + (" <span class='tq-muted'>(you)</span>" if p["yours"] else "")
        rows.append(f"<tr><td>{lab}</td>{''.join(cells)}</tr>")
        if p["yours"]:
            mine = [by.get(e) for e in evenings]
    st.html(card(ttl("Where the crescent can be seen", "أين يُرى الهلال"),
                 "<table class='tq-table'>" + head + "".join(rows) + "</table>"
                 "<div class='tq-muted'>Each column is the evening (local date) after sunset. Yallop zones: A easily "
                 "visible, B naked eye in perfect conditions, C optical aid to find, D optical aid only, E/F not "
                 "visible. Odeh zones: A naked eye, B optical aid (may be seen by eye), C optical aid only, D not "
                 "visible.</div>"))
    rows = []
    for e, r in zip(evenings, mine):
        if r is None:
            continue
        if pd.isna(r.get("q")):
            rows.append(f"<tr><td>{e:%a %d %b}</td><td>{t12(pd.Timestamp(r['sunset_utc']).to_pydatetime().astimezone(tz))}</td>"
                        f"<td colspan=6 class='tq-muted'>{esc(verdict(r))}</td></tr>")
            continue
        rows.append(f"<tr><td>{e:%a %d %b}</td><td>{t12(pd.Timestamp(r['sunset_utc']).to_pydatetime().astimezone(tz))}</td>"
                    f"<td>{r['lag_min']:.0f}</td><td>{r['age_h']:.1f}</td><td>{r['arcl']:.1f}°</td>"
                    f"<td>{r['arcv']:.1f}°</td><td>{r['w']:.2f}′</td><td>{esc(verdict(r))}</td></tr>")
    if rows:
        st.html(card(ttl(f"From {place['label']}", "من مكانك"),
                     "<table class='tq-table'><tr><th>Evening</th><th>Sunset</th><th>Moon sets after the Sun (min)</th>"
                     "<th>Moon age (h)</th><th>Elongation</th><th>Moon above Sun</th><th>Crescent width</th>"
                     "<th>Verdict</th></tr>" + "".join(rows) + "</table>"
                     "<div class='tq-muted'>Measured at the 'best time', sunset plus 4/9 of the time until moonset "
                     "(Yallop). Elongation: the Moon's angular distance from the Sun. Haze, cloud and the observer's "
                     "eyesight matter as much as the geometry.</div>"))


# ----------------------------------------------------------------------------------------------
# Compare
# ----------------------------------------------------------------------------------------------
def render_compare(ctx):
    V = ctx["views"]
    lun = [V[k] for k in cv.LUNAR]
    branch = ctx["branch"]
    st.html("<div class='tq-muted'>The three lunar calendars side by side, for the "
            f"{cv.BRANCH_NAME[branch][0]} holy days. Differences are in days from Umm al-Qura.</div>")
    common = sorted(set.intersection(*[set(v.years()) for v in lun]))
    if not common:
        st.info("The calendars have no complete year in common.")
        return
    range_note(V[cv.SIGHTING])
    cur = V[cv.UMMALQURA].year_of(ctx["today"]) or common[len(common) // 2]
    cur = min(max(cur, common[0]), common[-1])
    y = st.selectbox("Hijri year", common, index=common.index(cur), key="cmp_y",
                     format_func=lambda y: year_label(V[cv.UMMALQURA], y))
    ref = V[cv.UMMALQURA]

    def dfmt(d):
        return d.strftime("%a %d %b %Y") if d else "—"

    def dcell(d, r):
        if d is None or r is None:
            return "<td>—</td>"
        n = (d - r).days
        txt = dfmt(d) + (f" <b>({n:+d})</b>" if n else "")
        return f"<td class='tq-diff'>{txt}</td>" if n else f"<td>{txt}</td>"

    head = "<tr><th></th>" + "".join(f"<th>{bi(v.name, v.name_ar)}<br><span class='tq-muted'>{esc(v.detail)}</span></th>"
                                     for v in lun) + "</tr>"
    rows = []
    for name, mo, d in hol.compare_holidays(branch):
        r = ref.cal.to_gregorian(y, mo, d)
        rows.append(f"<tr><td>{esc(name)} <span class='tq-muted'>({d} {an.MONTHS[mo][0]})</span></td>"
                    f"<td>{dfmt(r)}</td>" + "".join(dcell(v.cal.to_gregorian(y, mo, d), r) for v in lun[1:]) + "</tr>")
    st.html("<h4 style='margin:0'>Holy days · المناسبات</h4><table class='tq-table'>" + head + "".join(rows) + "</table>")
    mrows = []
    for mo in range(1, 13):
        r = ref.get_month(y, mo)
        cells = f"<td>{dfmt(r.start) if r else '—'} <span class='tq-muted'>{r.length if r else ''}</span></td>"
        for v in lun[1:]:
            om = v.get_month(y, mo)
            cells += dcell(om.start if om else None, r.start if r else None)
        mrows.append(f"<tr><td>{an.month_bi(mo)}</td>{cells}</tr>")
    st.html("<h4 style='margin:.6rem 0 0 0'>First day of each month · أوائل الشهور</h4><table class='tq-table'>" + head
            + "".join(mrows) + "</table>")
    why = [
        "Umm al-Qura starts a month when, on the 29th, the new moon comes before sunset at Mecca and the Moon sets "
        "after the Sun. The crescent then is often too thin and low to be seen, so Umm al-Qura is usually a day "
        "ahead of the sighting calendar.",
        "The sighting calendar waits for the crescent to be predicted visible. Accepting telescope sightings brings "
        "it closer to Umm al-Qura; requiring the naked eye, or a place further east, makes it later.",
        "The tabular calendar ignores the Moon and alternates 30- and 29-day months, so it drifts up to about two "
        "days either side of the real Moon.",
    ]
    st.html(card("Why they differ", "".join(f"<p>{esc(w)}</p>" for w in why)))

    # chart: 1 Ramadan, sighting and tabular minus Umm al-Qura, over the years they share
    xs, ys_s, ys_t = [], [], []
    for yy in common:
        r = ref.cal.to_gregorian(yy, RAMADAN, 1)
        s1 = V[cv.SIGHTING].cal.to_gregorian(yy, RAMADAN, 1)
        t1 = V[cv.TABULAR].cal.to_gregorian(yy, RAMADAN, 1)
        if r and s1 and t1:
            xs.append(r.year + (r.timetuple().tm_yday / 366))
            ys_s.append((s1 - r).days)
            ys_t.append((t1 - r).days)
    if len(xs) > 2:
        fig, ax = plt.subplots(figsize=(9, 3.2) if not device.phone() else (5, 3.4), dpi=120)
        fig.patch.set_facecolor(theme.BG)
        ax.set_facecolor(theme.CARD)
        ax.scatter(xs, [v + 0.08 for v in ys_s], s=12, c=theme.OBS, label=f"Sighting ({V[cv.SIGHTING].detail})", marker="o")
        ax.scatter(xs, [v - 0.08 for v in ys_t], s=10, c=theme.GOLD, label=V[cv.TABULAR].name, marker="^")
        ax.axhline(0, color=theme.MUTED, lw=0.8)
        ax.set_xlabel("Year (CE)", color=theme.TEXT)
        ax.set_ylabel("Minus Umm al-Qura (days)", color=theme.TEXT)
        ax.set_title("First day of Ramadan compared with Umm al-Qura", color=theme.TEXT, fontsize=11)
        ax.tick_params(colors=theme.TEXT)
        for spn in ax.spines.values():
            spn.set_color(theme.MUTED)
        ax.legend(facecolor=theme.CARD, edgecolor=theme.MUTED, labelcolor=theme.TEXT, fontsize=8)
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
        from collections import Counter
        cs = Counter(ys_s)
        st.caption("1 Ramadan by sighting minus Umm al-Qura over these years: "
                   + ", ".join(f"{k:+d} day{'s' if abs(k) != 1 else ''}: {cs[k]} years" for k in sorted(cs)) + ".")


# ----------------------------------------------------------------------------------------------
# Traditions
# ----------------------------------------------------------------------------------------------
def apply_preset(preset: dict, title: str):
    """Button callback: set the app's settings to model one community's practice."""
    b = preset["branch"]
    ss = st.session_state
    ss["branch"] = b
    ss[f"cal_{b}"] = preset["calendar"]
    for k, key in (("ref", f"sref_{b}"), ("crit", f"crit_{b}"), ("tabular", "tab_var"),
                   ("method", f"method_{b}"), ("asr", "asr"), ("imams", "imams")):
        if k in preset:
            ss[key] = preset[k]
    ss["_preset_msg"] = title


def _preset_text(pr: dict) -> str:
    parts = [cv.BRANCH_NAME[pr["branch"]][0] + " holy days", cv.NAME[pr["calendar"]]]
    if pr["calendar"] == cv.SIGHTING:
        ref = {"Mecca": "from Mecca", "local": "from your own place"}.get(pr.get("ref"), f"from {pr.get('ref')}")
        parts.append(f"{ref}, {sc.CRITERIA_SHORT.get(pr.get('crit', ''), '')}")
    if pr.get("tabular") == "fatimid":
        parts.append("Fatimid cycle")
    if pr.get("method"):
        parts.append("prayer times: " + pt.METHODS[pr["method"]]["label"])
    if pr.get("asr") == "hanafi":
        parts.append("Hanafi Asr")
    return " · ".join(parts)


def render_traditions(ctx):
    msg = st.session_state.pop("_preset_msg", None)
    if msg:
        st.success(f"Settings now model: {msg}. Open Today, Month or Year to see the dates.")
    st.html("<div class='tq-muted'>The schools, branches and movements of Islam, listed under the calendar each "
            "uses to fix its months. Press <b>Use</b> to set the app to model that practice: the tradition's holy "
            "days, the calendar, where and how the crescent is looked for, and the usual prayer-time method. "
            "Practice varies within every group, so these are models of the main practice named. Groups outside "
            "the Sunni and Shia lists are shown with the nearer list of holy days.</div>")
    groups = {g for g, _ in sects.GROUPS}
    byc = sects.by_calendar()
    phone = device.phone()
    n = 0
    for cal, cal_title in sects.CAL_ORDER:
        rows = byc.get(cal, [])
        if not rows:
            continue
        st.html(f"<h3 style='margin:.9rem 0 .1rem 0'>{bi(cal_title, cv.NAME_AR[cal])}</h3>"
                f"<div class='tq-muted' style='margin-bottom:.3rem'>{esc(cv.HELP[cal])}</div>")
        for s_, label, preset in rows:
            n += 1
            parent = f" <span class='tq-muted'>({esc(s_['parent'])})</span>" if s_.get("parent") else ""
            body = (f"<div class='tq-card' style='margin-bottom:.35rem;padding:.55rem .8rem'>"
                    f"<b>{bi(s_['name'], s_['ar'])}</b>{parent} · <span class='tq-muted'>{esc(s_['group'])}</span>"
                    f"<div>{esc(label)}</div>"
                    f"<div class='tq-muted' style='font-size:.82rem'>{esc(_preset_text(preset))}</div></div>")
            if phone:
                st.html(body)
                st.button("Use", key=f"use_{n}", on_click=apply_preset, args=(preset, f"{s_['name']} — {label}"),
                          width="stretch")
            else:
                c1, c2 = st.columns([6, 1], vertical_alignment="center")
                c1.html(body)
                c2.button("Use", key=f"use_{n}", on_click=apply_preset, args=(preset, f"{s_['name']} — {label}"),
                          width="stretch")
    none = [s_ for s_ in sects.SECTS if not s_["uses"]]
    if none:
        st.html("<h3 style='margin:.9rem 0 .1rem 0'>Without a calendar of their own · بلا تقويم خاص</h3>"
                + "".join(f"<div class='tq-card' style='margin-bottom:.35rem;padding:.55rem .8rem'><b>"
                          f"{bi(s_['name'], s_['ar'])}</b> · <span class='tq-muted'>{esc(s_['group'])}</span>"
                          f"<div>{esc(s_['how'])}</div></div>" for s_ in none))
    st.html("<h3 style='margin:.9rem 0 .1rem 0'>The traditions in detail · تفصيل</h3>")
    for g, g_ar in sects.GROUPS:
        for s_ in [x for x in sects.SECTS if x["group"] == g and x["uses"]]:
            with st.expander(f"{s_['name']} · {s_['ar']}  ({g})"):
                st.markdown(f"**Where:** {s_['where']}")
                st.markdown(s_["how"])
                st.caption(f"Sources: {s_['src']}")


# ----------------------------------------------------------------------------------------------
# How it works
# ----------------------------------------------------------------------------------------------
def render_about(ctx):
    path = os.path.join(HERE, "HOW_IT_WORKS.md")
    with open(path, encoding="utf-8") as f:
        st.markdown(f.read())
    st.markdown("### Guide to the holy days · دليل المناسبات")
    st.caption("The same short histories open when you click a day's name anywhere in the app.")
    for key, (title, ar, text, src) in hh.H.items():
        with st.expander(f"{title} · {ar}"):
            st.markdown(text)
            st.caption(f"Sources: {src}")
    try:
        lo, hi = se.ephemeris_range()
        _, _, name = se.load()
        st.caption(f"Ephemeris in use: {name}, valid {lo:%d %b %Y} – {hi:%d %b %Y}.")
    except Exception:
        st.caption("Ephemeris not loaded.")
