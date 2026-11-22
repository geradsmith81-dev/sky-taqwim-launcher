"""The live qibla compass (Today page).

The dial (N, E, S, W) and a gold arrow toward the Kaaba are drawn in Python; a small browser component turns
them with the phone, like a compass:

* the phone's compass gives its heading from MAGNETIC north (iPhone/iPad: webkitCompassHeading after the user
  allows "Motion & Orientation"; Android: the absolute device-orientation event, heading = 360 - alpha);
* the magnetic declination of the place (World Magnetic Model WMM2025, via pygeomag) turns that into a heading
  from TRUE north, the reference of the great-circle qibla bearing;
* the dial is turned by -heading (so N points to true north) and the arrow by (qibla - heading), so the arrow
  points to the Kaaba however the phone is turned. When the arrow points to the top of the phone (within 5
  degrees) the card says so.

Held upright the phone's compass is unreliable, so the card asks for the phone to be held flat. Computers have
no compass: the dial then stays with north at the top, the arrow at the qibla bearing (the static drawing).
Nothing leaves the browser: the readings are used only to turn the drawing.
"""
from __future__ import annotations

import html
from datetime import datetime, timezone

import streamlit as st

import ornaments as orn
from theme import QIBLA_LIVE_CSS as CSS

try:   # World Magnetic Model (NOAA/BGS, public domain) through pygeomag (MIT)
    from pygeomag import GeoMag
    _GM = GeoMag(coefficients_file="wmm/WMM_2025.COF")
except Exception:   # pragma: no cover - the compass still works, only uncorrected for declination
    _GM = None


def declination(lat: float, lon: float, when: datetime | None = None) -> float | None:
    """Magnetic declination in degrees (east positive) from WMM2025, or None if the model is unavailable."""
    if _GM is None:
        return None
    t = when or datetime.now(timezone.utc)
    year = t.year + (t.timetuple().tm_yday - 0.5) / (366 if t.year % 4 == 0 else 365)
    try:
        return float(_GM.calculate(glat=float(lat), glon=float(lon), alt=0, time=year,
                                   allow_date_outside_lifespan=True).d)
    except Exception:
        return None


JS = r"""
const G = (window.__skytaqwimQibla = window.__skytaqwimQibla || {
  heading: null, shown: null, beta: 0, gamma: 0, acc: null, got: false, started: false, loop: false,
  view: null, facing: false
});

function norm180(a) { return ((a % 360) + 540) % 360 - 180; }
function screenAngle() {
  if (screen.orientation && typeof screen.orientation.angle === 'number') return screen.orientation.angle;
  if (typeof window.orientation === 'number') return window.orientation;
  return 0;
}

function onIOS(e) {          // iPhone / iPad: heading of the top of the device from magnetic north
  if (typeof e.webkitCompassHeading !== 'number' || isNaN(e.webkitCompassHeading)) return;
  G.heading = e.webkitCompassHeading + screenAngle();
  G.acc = (typeof e.webkitCompassAccuracy === 'number') ? e.webkitCompassAccuracy : null;
  G.beta = e.beta || 0; G.gamma = e.gamma || 0; G.got = true;
}
function onAbs(e) {          // Android: absolute orientation, alpha counter-clockwise from magnetic north
  if (e.alpha === null || e.alpha === undefined) return;
  G.heading = (360 - e.alpha) + screenAngle();
  G.beta = e.beta || 0; G.gamma = e.gamma || 0; G.got = true;
}
function onRel(e) { if (e.absolute === true) onAbs(e); }

function status(text, cls) {
  const V = G.view; if (!V || !V.status) return;
  if (V.status.textContent !== text) V.status.textContent = text;
  V.status.className = 'tq-ql-status' + (cls ? ' ' + cls : '');
}

function frame() {
  const V = G.view;
  if (V && V.dial && V.dial.isConnected && G.heading !== null) {
    const target = G.heading + (V.decl || 0);                       // true heading of the top of the phone
    if (G.shown === null) G.shown = target;
    G.shown += norm180(target - G.shown) * 0.25;                    // smooth, and never spin the long way round
    const h = G.shown;
    V.dial.style.transform = 'rotate(' + (-h).toFixed(2) + 'deg)';
    V.arrow.style.transform = 'rotate(' + (V.bearing - h).toFixed(2) + 'deg)';
    const rel = norm180(V.bearing - h);
    const flat = Math.abs(G.beta) < 35 && Math.abs(G.gamma) < 35;
    const facing = flat && Math.abs(rel) <= 5;
    V.stage.classList.toggle('tq-ql-on', facing);
    if (facing && !G.facing && navigator.vibrate) { try { navigator.vibrate(40); } catch (err) {} }
    G.facing = facing;
    if (!flat) status('Hold the phone flat, screen up, for a true reading.', 'tq-ql-warn');
    else if (G.acc !== null && (G.acc < 0 || G.acc > 25)) status('The compass needs calibrating: move the phone in a figure of eight, then hold it flat.', 'tq-ql-warn');
    else if (facing) status('You are facing the qibla.', 'tq-ql-good');
    else {
      const turn = Math.round(Math.abs(rel));
      status('Turn ' + turn + '\u00b0 to the ' + (rel > 0 ? 'right' : 'left') + ' to face the qibla (the arrow shows the way).', '');
    }
  }
  requestAnimationFrame(frame);
}

function start(manual) {
  if (G.started) return;
  G.started = true;
  if ('ondeviceorientationabsolute' in window) window.addEventListener('deviceorientationabsolute', onAbs, true);
  else window.addEventListener('deviceorientation', onRel, true);
  window.addEventListener('deviceorientation', onIOS, true);
  if (!G.loop) { G.loop = true; requestAnimationFrame(frame); }
  status('Reading the compass... hold the phone flat.', '');
  setTimeout(function () {
    if (G.got) return;
    G.started = false;
    const V = G.view; if (!V) return;
    status('No compass reading from this device. The dial shows the qibla with north at the top.', 'tq-ql-warn');
    if (window.self !== window.top && V.tab) V.tab.style.display = 'inline-block';
    if (V.btn) V.btn.style.display = manual ? 'inline-block' : 'none';
  }, 3000);
}

function askAndStart() {     // iPhone / iPad must ask, from a tap
  const D = window.DeviceOrientationEvent;
  if (D && typeof D.requestPermission === 'function') {
    D.requestPermission().then(function (r) {
      if (r === 'granted') { G.view.btn.style.display = 'none'; start(true); }
      else status('Compass not allowed. Close and reopen the app, then tap the button again and choose Allow. If iOS does not ask again: Settings > Apps > Safari > Advanced > Website Data, delete streamlit.app, and try again.', 'tq-ql-warn');
    }).catch(function () { status('The compass could not be started on this device.', 'tq-ql-warn'); });
  } else { G.view.btn.style.display = 'none'; start(true); }
}

export default function (component) {
  const { data, parentElement } = component;
  let V = parentElement.__skytaqwimQibla;
  const key = (data && data.html) || '';
  if (!V || V.key !== key) {
    parentElement.innerHTML = key;
    V = { key: key,
          stage: parentElement.querySelector('.tq-ql-stage'),
          dial: parentElement.querySelector('.tq-ql-dial'),
          arrow: parentElement.querySelector('.tq-ql-arrow'),
          status: parentElement.querySelector('.tq-ql-status'),
          btn: parentElement.querySelector('.tq-ql-btn'),
          tab: parentElement.querySelector('.tq-ql-tab') };
    parentElement.__skytaqwimQibla = V;
    if (V.btn) V.btn.addEventListener('click', askAndStart);
    if (V.tab) V.tab.href = window.location.href;
  }
  V.bearing = Number(data && data.bearing) || 0;
  V.decl = Number(data && data.decl) || 0;
  G.view = V; G.shown = null;
  if (G.heading === null) {            // not turning yet: the static drawing (north up)
    V.dial.style.transform = 'rotate(0deg)';
    V.arrow.style.transform = 'rotate(' + V.bearing.toFixed(2) + 'deg)';
  }
  const D = window.DeviceOrientationEvent;
  const touch = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  if (G.got) { if (V.btn) V.btn.style.display = 'none'; if (!G.loop) { G.loop = true; requestAnimationFrame(frame); } return; }
  if (!D) { status('This browser has no compass. The dial shows the qibla with north at the top.', ''); if (V.btn) V.btn.style.display = 'none'; return; }
  if (typeof D.requestPermission === 'function') {          // iPhone / iPad (and Safari on Mac)
    if (touch) { V.btn.style.display = 'inline-block'; status('Tap the button, allow Motion & Orientation, and hold the phone flat.', ''); }
    else { V.btn.style.display = 'none'; status('On a phone or tablet the arrow turns with the device, like a compass.', ''); }
  } else if (touch) {                                       // Android: no permission needed
    if (V.btn) V.btn.style.display = 'none';
    start(false);
  } else {
    if (V.btn) V.btn.style.display = 'none';
    status('On a phone or tablet the arrow turns with the device, like a compass.', '');
  }
}
"""

_COMPONENT = st.components.v2.component("skytaqwim_qibla", js=JS, css=CSS, isolate_styles=False)


# The layout is also written on the elements themselves: on Streamlit Community Cloud the component's own
# stylesheet was not applied, and without "position:absolute" the arrow fell below the dial instead of on it.
_WRAP = "position:relative;padding-top:14px;flex:0 0 auto;"
_LUBBER = ("position:absolute;top:0;left:50%;transform:translateX(-50%);width:0;height:0;"
           "border-left:9px solid transparent;border-right:9px solid transparent;border-top:13px solid #b5412c;")
_STAGE = "position:relative;border-radius:50%;"
_LAYER = "position:absolute;top:0;left:0;width:100%;height:100%;transform-origin:50% 50%;line-height:0;"


def _html(bearing: float, place: str, distance_km: float | None, decl: float | None, size: int, title_html: str) -> str:
    b = float(bearing) % 360.0
    pts = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
    word = pts[int((b + 22.5) // 45) % 8]
    where = f" from {html.escape(place)}" if place else ""
    dist = f"<div class='tq-qibla-text'>Mecca is {distance_km:,.0f} km away (great-circle).</div>" if distance_km else ""
    if decl is None:
        dec = ("<div class='tq-qibla-text'>A magnetic compass differs from true north by the local declination "
               "(not available here, so the live arrow is not corrected for it).</div>")
    else:
        side = "east" if decl >= 0 else "west"
        dec = (f"<div class='tq-qibla-text'>Magnetic north here is {abs(decl):.1f}° {side} of true north "
               f"(World Magnetic Model 2025); the live arrow allows for it, so it points along the true bearing.</div>")
    dial = orn.qibla_compass_svg(0, size, needle=False)
    arrow = orn.qibla_arrow_svg(size)
    return (f"<div class='tq-card tq-ql-card'><h3>{title_html}</h3><div class='tq-qibla tq-ql'>"
            f"<div class='tq-ql-wrap' style='{_WRAP}'>"
            f"<div class='tq-ql-lubber' title='The top of your phone' style='{_LUBBER}'></div>"
            f"<div class='tq-ql-stage' style='{_STAGE}width:{size}px;height:{size}px'>"
            f"<div class='tq-ql-dial' style='{_LAYER}'>{dial}</div>"
            f"<div class='tq-ql-arrow' style='{_LAYER}'>{arrow}</div></div></div>"
            f"<div class='tq-ql-info'>"
            f"<div class='tq-qibla-deg'>{b:.1f}° <span class='tq-ar' lang='ar' dir='rtl'>القبلة</span></div>"
            f"<div class='tq-qibla-text'>Qibla{where}: {b:.1f}° from true north, toward the {word}.</div>{dist}{dec}"
            f"<button type='button' class='tq-ql-btn' style='display:none'>Turn on the live compass</button>"
            f"<div class='tq-ql-status' aria-live='polite'></div>"
            f"<a class='tq-ql-tab' target='_blank' rel='noopener' style='display:none'>Open the app in its own tab for the compass</a>"
            f"</div></div></div>")


def show(bearing: float, place: str, distance_km: float | None, lat: float, lon: float, title_html: str,
         size: int = 170, key: str = "qibla_live"):
    decl = declination(lat, lon)
    markup = _html(bearing, place, distance_km, decl, size, title_html)
    return _COMPONENT(data={"html": markup, "bearing": float(bearing) % 360.0, "decl": decl or 0.0},
                      key=key, width="stretch", height="content")
