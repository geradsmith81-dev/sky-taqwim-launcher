"""Place search (GeoNames cities with 15,000+ people, via geonamescache) with time zones."""
from __future__ import annotations

import unicodedata
from functools import lru_cache

from arabic_names import arabic_place_name
import sighting_calendar as _sc

_ORDER = ["Mecca", "Medina", "Jerusalem", "Cairo", "Istanbul", "Najaf", "Karbala", "Baghdad", "Qom", "Tehran",
          "Mashhad", "Kabul", "Karachi", "Dhaka", "Kuala Lumpur", "Jakarta", "Rabat", "London", "New York"]
_CC = {"Mecca": "SA", "Medina": "SA", "Jerusalem": "", "Cairo": "EG", "Istanbul": "TR", "Najaf": "IQ", "Karbala": "IQ",
       "Baghdad": "IQ", "Qom": "IR", "Tehran": "IR", "Mashhad": "IR", "Kabul": "AF", "Karachi": "PK", "Dhaka": "BD",
       "Kuala Lumpur": "MY", "Jakarta": "ID", "Rabat": "MA", "London": "GB", "New York": "US"}
PRESETS = [{"name": n, "ar": _sc.PRESETS_BY_NAME[n].get("name_ar", ""), "country": _CC.get(n, ""),
            "lat": _sc.PRESETS_BY_NAME[n]["lat"], "lon": _sc.PRESETS_BY_NAME[n]["lon"], "tz": _sc.PRESETS_BY_NAME[n]["tz"]}
           for n in _ORDER if n in _sc.PRESETS_BY_NAME]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower().strip()


@lru_cache(maxsize=1)
def _cities() -> list[dict]:
    try:
        import geonamescache
    except ImportError:
        return []
    gc = geonamescache.GeonamesCache()
    countries = gc.get_countries()
    states = gc.get_us_states()
    out = []
    for c in gc.get_cities().values():
        cc = c["countrycode"]
        region = states.get(c.get("admin1code", ""), {}).get("name", "") if cc == "US" else ""
        out.append({"name": c["name"], "country": cc,
                    "country_name": countries.get(cc, {}).get("name", cc), "region": region,
                    "lat": float(c["latitude"]), "lon": float(c["longitude"]), "tz": c["timezone"],
                    "pop": int(c["population"]), "key": _norm(c["name"]),
                    "ar": arabic_place_name(c.get("alternatenames", []), c["name"]),
                    "alt": "|" + "|".join(_norm(a) for a in c.get("alternatenames", []) if a) + "|"})
    out.sort(key=lambda r: -r["pop"])
    return out


def search(query: str, limit: int = 12) -> list[dict]:
    """Exact name matches first, then alternate names, then prefixes; larger cities first."""
    q = _norm(query)
    if not q:
        return []
    cities = _cities()
    exact = [c for c in cities if c["key"] == q]
    alt = [c for c in cities if c["key"] != q and f"|{q}|" in c["alt"]]
    pref = [c for c in cities if c["key"] != q and c["key"].startswith(q) and f"|{q}|" not in c["alt"]]
    seen, out = set(), []
    for c in exact + alt + pref:
        k = (c["name"], c["country"], round(c["lat"], 2))
        if k not in seen:
            seen.add(k)
            out.append(c)
        if len(out) >= limit:
            break
    return out


def label(p: dict) -> str:
    parts = [p["name"]]
    if p.get("region"):
        parts.append(p["region"])
    parts.append(p.get("country_name") or p.get("country", ""))
    return ", ".join(x for x in parts if x)
