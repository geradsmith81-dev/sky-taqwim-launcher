"""Sky Taqwim · تقويم السماء — the Islamic calendar, Sunni and Shia, from NASA JPL astronomy.

Run:  streamlit run app.py
"""
import os
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import streamlit as st  # noqa: E402

st.set_page_config(page_title="Sky Taqwim · تقويم السماء", page_icon=os.path.join(HERE, "assets", "taqwim_icon.png"),
                   layout="wide", initial_sidebar_state="auto")

import desktop as dk  # noqa: E402  (desktop-only controls; inert on the hosted copy)

dk.require_password(st)

import calendars as cv  # noqa: E402
import device  # noqa: E402
import extra_calendars as xc  # noqa: E402
import locator  # noqa: E402
import pages  # noqa: E402
import places  # noqa: E402
import prayer_times as pt  # noqa: E402
import sighting_calendar as sc  # noqa: E402
import solar_hijri_calendar as shc  # noqa: E402
import tabular_calendar as tc  # noqa: E402
import theme  # noqa: E402
import ummalqura_calendar as uq  # noqa: E402
import unified_hijri_calendar as uh  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

theme.apply()

PAGES = {
    "Today": ("Today · اليوم", pages.render_today),
    "Traditions": ("Traditions · المذاهب", pages.render_traditions),
    "Month": ("Month · الشهر", pages.render_month),
    "Year": ("Year & holy days · السنة والمناسبات", pages.render_year),
    "Prayer": ("Prayer times · مواقيت الصلاة", pages.render_prayer),
    "Crescent": ("Crescent · الهلال", pages.render_crescent),
    "Compare": ("Compare · مقارنة", pages.render_compare),
    "About": ("How it works · الشرح", pages.render_about),
}


# ---------------------------------------------------------------------------------------------- calendars (cached)
@st.cache_resource(show_spinner="Reading the Umm al-Qura calendar…", max_entries=4)
def ummalqura_cal(source):
    return uq.UmmAlQuraCalendar(source)


@st.cache_resource(show_spinner=False, max_entries=4)
def tabular_cal(variant):
    return tc.TabularCalendar(variant)


@st.cache_resource(show_spinner="Working out when the crescent can be seen…", max_entries=16)
def sighting_cal(lat, lon, tz, name, criterion, span):
    if lat is None:
        return sc.SightingCalendar(None, criterion)
    return sc.SightingCalendar({"name": name, "lat": lat, "lon": lon, "tz": tz}, criterion, span)


@st.cache_resource(show_spinner=False, max_entries=4)
def solar_cal(rule):
    return shc.SolarHijriCalendar(rule)


@st.cache_resource(show_spinner="Reading the Unified Hijri Calendar…", max_entries=1)
def unified_cal():
    return uh.UnifiedHijriCalendar()


@st.cache_resource(show_spinner=False, max_entries=1)
def ahmadi_cal():
    return xc.AhmadiHijriShamsiCalendar()


@st.cache_resource(show_spinner=False, max_entries=1)
def julian_cal():
    return xc.JulianCalendar()


def _idx(key, options, default):
    """index= for a widget, unless a preset has already put its value in session state."""
    return {} if key in st.session_state else {"index": list(options).index(default)}


# ---------------------------------------------------------------------------------------------- where the user is
def _browser_tz():
    """The browser's time zone, if it is one this computer knows (the browser can send any text)."""
    try:
        tz = st.context.timezone
    except Exception:
        return None
    if not isinstance(tz, str) or not tz or len(tz) > 64:
        return None
    try:
        ZoneInfo(tz)
    except Exception:
        return None
    return tz


if "place" not in st.session_state:
    guess = locator.place_from_timezone(_browser_tz())
    if guess is None:
        guess = dict(places.PRESETS[0], label="Mecca, Saudi Arabia", src="default")
    st.session_state["place"] = guess
    st.session_state["place_src"] = guess["src"]


def _on_pick():
    v = st.session_state.get("locator")
    p = v.get("pick") if hasattr(v, "get") else getattr(v, "pick", None)
    if not isinstance(p, dict) or "lat" not in p:
        return
    try:
        lat, lon = float(p["lat"]), float(p["lon"])
    except (TypeError, ValueError):
        return
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return
    if p.get("auto") and st.session_state.get("place_src") == "manual":
        return   # the user already chose a place by hand: keep it
    acc = p.get("acc") if isinstance(p.get("acc"), (int, float)) else None
    st.session_state["place"] = locator.place_from_device(lat, lon, acc, _browser_tz())
    st.session_state["place_src"] = "gps"


def _set_manual(pl: dict):
    st.session_state["place"] = dict(pl, src="manual")
    st.session_state["place_src"] = "manual"


# ---------------------------------------------------------------------------------------------- tradition
if "branch" not in st.session_state:
    st.session_state["branch"] = "sunni"
branch = st.session_state["branch"]
theme.header(branch=branch)

phone = device.phone()
c0, c1, c2 = (st.columns([1.0, 2.3, 3.4]) if not phone else (st.container(), st.container(), st.container()))
with c0:
    branch = st.radio("Tradition · المذهب", cv.BRANCHES, key="branch", horizontal=True,
                      format_func=lambda b: f"{cv.BRANCH_NAME[b][0]} · {cv.BRANCH_NAME[b][1]}",
                      help="Sunni or Shia (Twelver) practice: this sets the holy days, the default calendar and "
                           "sighting rule, and the prayer-time methods. Each can still be changed in the settings.")
D = cv.DEFAULTS[branch]
with c1:
    cal_key = st.radio("Calendar · التقويم", cv.ALL, key=f"cal_{branch}", **_idx(f"cal_{branch}", cv.ALL, D["calendar"]),
                       horizontal=True, format_func=lambda k: f"{cv.NAME[k]} · {cv.NAME_AR[k]}",
                       help=" ".join(f"{cv.NAME[k]}: {cv.HELP[k]}" for k in cv.ALL))
with c2:
    page = st.radio("Page", list(PAGES), key="page", horizontal=True, format_func=lambda k: PAGES[k][0],
                    label_visibility="collapsed" if not phone else "visible")

_pl = st.session_state["place"]
_how = {"gps": "from your device", "timezone": "first guess from your time zone",
        "manual": "chosen by you", "default": "starting place"}.get(st.session_state.get("place_src"), "")
locator.show(f"{_pl.get('label', _pl['name'])}" + (f" · {_pl['ar']}" if _pl.get("ar") else "") + f"  ({_how})",
             auto=st.session_state.get("place_src") in ("default", "timezone"), on_pick=_on_pick)

# ---------------------------------------------------------------------------------------------- settings
device.switch()
panel = device.input_panel("Settings: place, prayer times, sighting · الإعدادات")
with panel:
    st.subheader("Your place · المكان")
    q = st.text_input("Search for a town or city", key="place_q", placeholder="e.g. Birmingham, Karbala, Lahore")
    if q.strip():
        res = places.search(q)
        if res:
            pick = st.selectbox("Matches", range(len(res)), key="place_pick",
                                format_func=lambda i: places.label(res[i]) + (f" · {res[i]['ar']}" if res[i].get("ar") else ""))
            if st.button("Use this place", key="place_use", width="stretch"):
                r = res[pick]
                _set_manual({"name": r["name"], "ar": r.get("ar", ""), "country": r["country"],
                             "lat": r["lat"], "lon": r["lon"], "tz": r["tz"], "label": places.label(r)})
                st.rerun()
        else:
            st.caption("No town of 15,000+ people by that name. Try a nearby city, or enter coordinates below.")
    pre = st.selectbox("…or a preset", ["—"] + [p["name"] for p in places.PRESETS], key="place_preset")
    if pre != "—" and st.session_state.get("_last_preset") != pre:
        st.session_state["_last_preset"] = pre
        p = dict(next(x for x in places.PRESETS if x["name"] == pre))
        p["label"] = p["name"]
        _set_manual(p)
        st.rerun()
    place = st.session_state["place"]
    place.setdefault("label", place["name"])
    with st.expander("Exact coordinates"):
        lat = st.number_input("Latitude (° north, negative = south)", -89.0, 89.0, float(place["lat"]), 0.0001,
                              format="%.4f", key=f"lat_{place['name']}_{place['lat']:.4f}")
        lon = st.number_input("Longitude (° east, negative = west)", -180.0, 180.0, float(place["lon"]), 0.0001,
                              format="%.4f", key=f"lon_{place['name']}_{place['lon']:.4f}")
        place = dict(place, lat=lat, lon=lon)
        st.caption(f"Time zone: {place['tz']}")
    st.caption(f"Using: {place['label']}" + (f" · {place['ar']}" if place.get("ar") else ""))

    st.subheader("Prayer times · مواقيت الصلاة")
    meths = list(pt.methods_for(branch))
    if st.session_state.get(f"method_{branch}") not in meths:
        st.session_state.pop(f"method_{branch}", None)
    method = st.selectbox("Calculation method", meths, key=f"method_{branch}", **_idx(f"method_{branch}", meths, D["method"]),
                          format_func=lambda k: pt.METHODS[k]["label"] + ("" if pt.METHODS[k]["branch"] == branch
                                                                         else f" ({pt.METHODS[k]['branch'].capitalize()})"))
    if branch == "sunni":
        asr = st.radio("Asr", ["standard", "hanafi"], key="asr", horizontal=True, **_idx("asr", ["standard", "hanafi"], "standard"),
                       format_func=lambda k: {"standard": "Shafi'i, Maliki, Hanbali (shadow = length)",
                                              "hanafi": "Hanafi (shadow = twice the length)"}[k])
    else:
        asr = "standard"
    high_lat = st.selectbox("Far north or south", list(pt.HIGH_LAT), key="high_lat", format_func=lambda k: pt.HIGH_LAT[k],
                            help="How Fajr and Isha are found when the Sun does not go far enough below the horizon "
                                 "(summer above about 48° latitude).")
    imsak = st.number_input("Imsak: minutes before Fajr", 0, 30, 10, 1, key="imsak",
                            help="The time to stop eating before the fast, a precaution before dawn.")

    st.subheader("Holy days · المناسبات")
    o_fasts = st.toggle("Recommended fasts" if branch == "sunni" else "Fast days", value=(branch == "sunni"),
                        key=f"fasts_{branch}")
    o_nights = st.toggle("Holy nights", value=True, key=f"nights_{branch}")
    o_imams = (st.toggle("Births and martyrdoms of the Twelve Imams", key="imams",
                         **({} if "imams" in st.session_state else {"value": True}))
               if branch == "shia" else False)
    o_month = st.toggle("First day of each month", value=True, key=f"months_{branch}")

    st.subheader("Crescent sighting · رؤية الهلال")
    refs = ["Mecca", "local"] + [q["name"] for q in sc.PRESET_PLACES if q["name"] != "Mecca"]
    ref = st.selectbox("Where the crescent is looked for", refs, key=f"sref_{branch}", **_idx(f"sref_{branch}", refs, D["ref"]),
                       format_func=lambda r: {"Mecca": "Mecca", "local": "Your own place (local horizon)"}.get(r, r),
                       help="Mecca: the first sighting is taken from there (Saudi practice, and the classical Hanafi, "
                            "Maliki and Hanbali view that one sighting binds all). Your own place: each region its "
                            "own horizon (the Shafi'i and the Twelver Shia view).")
    crits = list(sc.CRITERIA)
    crit = st.selectbox("Rule for the crescent", crits, key=f"crit_{branch}", **_idx(f"crit_{branch}", crits, D["crit"]),
                        format_func=lambda k: sc.CRITERIA[k] + (f" — {cv.CRIT_NOTES[k]}" if k in cv.CRIT_NOTES else ""),
                        help="Yallop 1997 (NAO Technical Note 69) and Odeh 2004 (Experimental Astronomy 18:39–64) predict "
                             "when the crescent can be seen; Neo-MABIMS, wujud al-hilal and the conjunction rule are "
                             "calculated criteria that do not ask whether it can be seen.")

    st.subheader("Other calendars · تقاويم أخرى")
    uq_src = st.selectbox("Umm al-Qura", list(uq.SOURCES), key="uq_src", format_func=lambda k: uq.SOURCES[k])
    tab = st.selectbox("Tabular", list(tc.VARIANTS), key="tab_var",
                       format_func=lambda k: {"kuwaiti": "Standard (Kuwaiti) 30-year cycle",
                                              "fatimid": "Fatimid / Dawoodi Bohra (Isma'ili Shia) reckoning"}[k])
    solar_rule = st.selectbox("Solar Hijri: when the year begins", list(shc.RULES), key="solar_rule",
                              format_func=lambda k: shc.RULES[k])

# ---------------------------------------------------------------------------------------------- build the views
today = datetime.now(ZoneInfo(place["tz"])).date()
opts = {"month_starts": o_month, "imams": o_imams, "fasts": o_fasts, "nights": o_nights}
sp, sp_name = cv.sighting_place(ref, place)
if sp is None:
    s_cal = sighting_cal(None, None, None, "Mecca", crit, None)
else:
    span = cv.local_span(today)
    s_cal = sighting_cal(round(sp["lat"], 2), round(sp["lon"], 2), sp["tz"], sp.get("name", ""), crit, span)
views = {
    cv.UMMALQURA: cv.View(cv.UMMALQURA, ummalqura_cal(uq_src), branch, opts, uq.SOURCES[uq_src]),
    cv.SIGHTING: cv.View(cv.SIGHTING, s_cal, branch, opts, f"from {sp_name}, {sc.CRITERIA_SHORT[crit]}"),
    cv.TABULAR: cv.View(cv.TABULAR, tabular_cal(tab), branch, opts,
                        "Fatimid (Bohra)" if tab == "fatimid" else "standard Kuwaiti cycle"),
    cv.UNIFIED: cv.View(cv.UNIFIED, unified_cal(), branch, opts, "one date worldwide, Istanbul 2016"),
    cv.SOLAR: cv.View(cv.SOLAR, solar_cal(solar_rule), branch, opts, "Iran and Afghanistan"),
    cv.AHMADI: cv.View(cv.AHMADI, ahmadi_cal(), branch, opts, "Ahmadiyya Muslim Community"),
    cv.JULIAN: cv.View(cv.JULIAN, julian_cal(), branch, opts, "Eastern reckoning, Syriac month names"),
}
ctx = {
    "place": place, "branch": branch, "today": today, "views": views, "view": views[cal_key],
    "method": method, "asr": asr, "high_lat": high_lat, "imsak": int(imsak), "crit": crit, "ref": ref,
    "sighting_place": sp, "sighting_place_name": sp_name, "opts": opts,
}

PAGES[page][1](ctx)

st.html("<div class='tq-frieze' role='presentation' style='margin-top:1.2rem'></div>"
        "<div class='tq-muted' style='font-size:.8rem'>Astronomy: NASA JPL DE440s via Skyfield. The sighting "
        "calendar is a prediction of when the crescent can be seen, not an announcement; follow your community "
        "or marja' for the dates you keep.</div>")

dk.desktop_controls(st)
