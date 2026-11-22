"""
The qibla: the direction of the Kaaba in Mecca from any place, and the distance to it.

The bearing is the initial direction of the great circle (the shortest path on the globe) from
the place to the Kaaba, in degrees clockwise from true north; this is the convention of most
published qibla tables. The distance is along the same great circle on a sphere of radius
6371.0 km (mean Earth radius); it differs from the ellipsoidal distance by up to about 0.5%.
"""
from __future__ import annotations

import math

KAABA = (21.42252, 39.82621)
EARTH_RADIUS_KM = 6371.0
POINTS_16 = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
             "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def qibla(lat: float, lon: float) -> tuple[float, float]:
    """(initial great-circle bearing to the Kaaba in degrees from true north, distance in km)."""
    p1, p2 = math.radians(lat), math.radians(KAABA[0])
    dl = math.radians(KAABA[1] - lon)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    bearing = math.degrees(math.atan2(y, x)) % 360.0
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    dist = 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))
    return bearing, dist


def compass_point(bearing: float) -> str:
    return POINTS_16[int((bearing % 360) / 22.5 + 0.5) % 16]


def describe(lat: float, lon: float) -> str:
    """e.g. '118.99° (ESE), 4,794 km'."""
    b, d = qibla(lat, lon)
    if d < 0.05:
        return "You are at the Kaaba"
    return f"{b:.2f}° ({compass_point(b)}), {d:,.0f} km"


def describe_bearing(bearing: float) -> str:
    """e.g. '118° (ESE)'."""
    return f"{bearing:.0f}° ({compass_point(bearing)})"
