"""Find the user's location automatically.

1. Before anything else, the browser's time zone (st.context.timezone) gives a starting place: the
   largest city in that time zone.
2. A small browser component asks the device for its position (GPS on phones, Wi-Fi position on
   computers) once per visit. The browser shows its own permission prompt. The position is then
   matched to the nearest town for its name, Arabic name and time zone, and sunset times use the exact
   coordinates.
3. A place the user chooses by hand is never overwritten by the automatic request.
Nothing is stored: the position lives only in this browser session.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
import streamlit as st

import places

JS = r"""
function locate(S, auto) {
  if (!('geolocation' in navigator)) {
    S.status.textContent = 'This browser cannot share its location. Search for your town in the settings.';
    return;
  }
  S.status.textContent = auto ? 'Finding your location... (allow location if the browser asks)'
                              : 'Asking your device for its position...';
  navigator.geolocation.getCurrentPosition((p) => {
    const c = p.coords;
    S.status.textContent = 'Found you (within ' + Math.round(c.accuracy) + ' m). Updating times...';
    S.send('pick', { lat: c.latitude, lon: c.longitude, acc: c.accuracy, src: 'gps', auto: !!auto, ts: Date.now() });
  }, (err) => {
    let why;
    if (err.code === 1) {
      const framed = window.top !== window.self;
      if (framed) {
        S.status.textContent = 'The page frame blocked location. ';
        const a = document.createElement('a');
        a.textContent = 'Open Sky Taqwim full-screen'; a.href = window.location.href; a.target = '_top';
        S.status.appendChild(a);
        S.status.appendChild(document.createTextNode(', then press "Use my location".'));
        return;
      }
      why = 'Location permission was refused. Allow location for this site in the browser settings, or search for your town.';
    } else if (err.code === 3) {
      why = 'The device took too long to find you. Press "Use my location" to try again.';
    } else {
      why = 'Your position is not available right now. Press "Use my location" to try again.';
    }
    S.status.textContent = (auto ? 'Using a starting place. ' : '') + why;
  }, { enableHighAccuracy: false, timeout: 20000, maximumAge: 600000 });
}

function autoLocate(S) {
  if (S.autoTried) return;
  S.autoTried = true;
  try {
    if (sessionStorage.getItem('skytaqwim-auto-located')) return;
    sessionStorage.setItem('skytaqwim-auto-located', '1');
  } catch (e) { /* storage blocked: still try once for this page */ }
  const go = () => locate(S, true);
  if (navigator.permissions && navigator.permissions.query) {
    navigator.permissions.query({ name: 'geolocation' }).then((st) => {
      if (st.state === 'denied') {
        S.status.textContent = 'Location is blocked for this site in the browser settings: using a starting place. '
          + 'Search for your town in the settings.';
      } else go();
    }).catch(go);
  } else go();
}

export default function (component) {
  const { data, parentElement, setTriggerValue } = component;
  let S = parentElement.__skytaqwimLoc;
  if (!S) {
    const root = document.createElement('div'); root.className = 'sl-loc';
    const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'sl-loc-btn';
    btn.textContent = 'Use my location';
    const place = document.createElement('span'); place.className = 'sl-loc-place';
    const status = document.createElement('span'); status.className = 'sl-loc-status';
    root.append(btn, place, status);
    parentElement.appendChild(root);
    S = { root, btn, place, status, autoTried: false, label: null };
    btn.addEventListener('click', () => locate(S, false));
    parentElement.__skytaqwimLoc = S;
  }
  S.send = setTriggerValue;
  const label = (data && data.label) || '';
  if (label !== S.label) { S.label = label; S.place.textContent = label; S.status.textContent = ''; }
  if (data && data.auto) autoLocate(S);
}
"""

from theme import LOCATOR_CSS as CSS  # noqa: E402

_COMPONENT = st.components.v2.component("skytaqwim_locator", js=JS, css=CSS, isolate_styles=False)


def show(label: str, auto: bool, on_pick, key: str = "locator"):
    return _COMPONENT(data={"label": label, "auto": bool(auto)}, key=key, on_pick_change=on_pick,
                      width="stretch", height="content")


# ---------------------------------------------------------------------------------------------- places
@lru_cache(maxsize=1)
def _arrays():
    cs = places._cities()
    lat = np.radians(np.array([c["lat"] for c in cs]))
    lon = np.radians(np.array([c["lon"] for c in cs]))
    return cs, lat, lon


def nearest_city(lat: float, lon: float) -> tuple[dict | None, float]:
    """The town that names a position: the largest town of 50,000+ people within 15 km if there is one
    (so a point in the Old City is 'Jerusalem', not a district), otherwise the nearest town."""
    cs, la, lo = _arrays()
    if not cs:
        return None, float("inf")
    p1, l1 = math.radians(lat), math.radians(lon)
    a = np.sin((la - p1) / 2) ** 2 + np.cos(p1) * np.cos(la) * np.sin((lo - l1) / 2) ** 2
    d = 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
    near = np.where(d <= 15.0)[0]
    big = [i for i in near if cs[i]["pop"] >= 50000]
    i = max(big, key=lambda k: cs[k]["pop"]) if big else int(np.argmin(d))
    return cs[i], float(d[i])


def place_from_device(lat: float, lon: float, acc: float | None, browser_tz: str | None) -> dict:
    """A place dict for the device's exact position, named after its town. The time zone is the
    device's own (the browser's), falling back to the town's."""
    c, dist = nearest_city(lat, lon)
    tz = browser_tz or (c["tz"] if c is not None else "UTC")
    if c is not None and dist <= 30:
        name = c["name"]
        label = places.label(c) + ("" if dist < 3 else f" (about {dist:.0f} km from the centre)")
        ar = c.get("ar", "")
        country = c["country"]
    else:
        name = f"{lat:.3f}°, {lon:.3f}°"
        label = f"Your position {lat:.3f}°, {lon:.3f}°" + (f", nearest town {c['name']}" if c else "")
        ar, country = "", (c["country"] if c is not None and dist <= 250 else "")
    return {"name": name, "ar": ar, "country": country, "lat": float(lat), "lon": float(lon), "tz": tz,
            "label": label, "src": "gps", "acc": acc}


def place_from_timezone(tz: str | None) -> dict | None:
    """The largest city in the browser's time zone (a first guess before the device answers)."""
    if not tz:
        return None
    cs = [c for c in places._cities() if c["tz"] == tz]
    if not cs:
        return None
    c = max(cs, key=lambda r: r["pop"])
    return {"name": c["name"], "ar": c.get("ar", ""), "country": c["country"], "lat": c["lat"], "lon": c["lon"],
            "tz": c["tz"], "label": places.label(c), "src": "timezone"}
