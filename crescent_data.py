"""
Crescent tables: the precomputed Mecca table (data/crescents_mecca.csv.gz, 1850-2150) and
tables computed on demand for any other place. Used by ummalqura_calendar and sighting_calendar.
"""
from __future__ import annotations

import bisect
import os
from datetime import date
from functools import lru_cache

import pandas as pd

import sky_engine as se

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
MECCA_FILE = os.path.join(DATA, "crescents_mecca.csv.gz")
MECCA_SPAN = (date(1850, 1, 1), date(2150, 1, 10))


def build_mecca_table(start: date = MECCA_SPAN[0], end: date = MECCA_SPAN[1]) -> None:
    """Compute data/crescents_mecca.csv.gz from the JPL ephemeris (about 1.5 minutes)."""
    os.makedirs(DATA, exist_ok=True)
    df = se.crescent_table(start, end, se.MECCA)
    df.to_csv(MECCA_FILE, index=False, compression="gzip")


def _parse(df: pd.DataFrame) -> pd.DataFrame:
    for c in ("conj_utc", "sunset_utc", "moonset_utc", "best_utc"):
        df[c] = pd.to_datetime(df[c], utc=True, format="ISO8601")
    df["evening"] = pd.to_datetime(df["evening"]).dt.date
    return df


@lru_cache(maxsize=1)
def mecca_crescents() -> pd.DataFrame:
    if not os.path.exists(MECCA_FILE):
        build_mecca_table()
    return _parse(pd.read_csv(MECCA_FILE, compression="gzip"))


def place_key(place: dict) -> tuple:
    return (round(float(place["lat"]), 4), round(float(place["lon"]), 4), place["tz"])


def is_mecca(place: dict | None) -> bool:
    return place is None or place_key(place) == place_key(se.MECCA)


@lru_cache(maxsize=16)
def _place_table(key: tuple, start: date, end: date) -> pd.DataFrame:
    lat, lon, tz = key
    df = se.crescent_table(start, end, {"name": "", "lat": lat, "lon": lon, "tz": tz})
    return df


def crescents_for(place: dict | None, start: date | None = None, end: date | None = None) -> pd.DataFrame:
    """Crescent table for `place`: the precomputed one for Mecca, else computed for start..end."""
    if is_mecca(place):
        return mecca_crescents()
    return _place_table(place_key(place), start, end)


class EveningIndex:
    """Fast lookup of a crescent-table row by evening (civil date of the sunset)."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.idx = {e: i for i, e in enumerate(df["evening"])}
        self.conj_dates = sorted({c.date() for c in df["conj_utc"].dt.to_pydatetime()})
        self.first_evening = df["evening"].iloc[0]
        self.last_evening = df["evening"].iloc[-1]
        self._rows = df.to_dict("records")

    def row(self, evening: date) -> dict | None:
        i = self.idx.get(evening)
        return None if i is None else self._rows[i]

    def days_since_conj(self, evening: date) -> int | None:
        """Whole days since the last conjunction date on or before `evening` (None if unknown)."""
        j = bisect.bisect_right(self.conj_dates, evening) - 1
        return (evening - self.conj_dates[j]).days if j >= 0 else None
