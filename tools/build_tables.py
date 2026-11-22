"""Rebuild the precomputed tables from the JPL ephemeris.

  data/crescents_mecca.csv.gz   crescent parameters at Mecca, 1850-2150   (about 1.5 minutes)
  data/seasons.csv              equinoxes and solstices                    (seconds)
  data/unified_hijri_starts.csv month starts of the Unified Hijri Calendar (about 9 minutes)

Run from the app folder:  python tools/build_tables.py
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sighting_calendar as sc  # noqa: E402
import solar_hijri_calendar as shc  # noqa: E402
import unified_hijri_calendar as uh  # noqa: E402

if __name__ == "__main__":
    sc.build_mecca_table(date(1850, 1, 1), date(2150, 1, 10))
    print("written:", sc.MECCA_FILE)
    shc.build_seasons()
    print("written:", shc.SEASONS_FILE)
    uh.build_table()
    print("written:", uh.STARTS_FILE)
