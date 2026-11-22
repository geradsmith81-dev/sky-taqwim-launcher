# Third-party material

Sky Taqwim's own code is under the MIT License (see LICENSE). The material below keeps its own licence.

- **NASA JPL DE440s** planetary ephemeris (ephem/de440s.bsp). It is downloaded from ssd.jpl.nasa.gov and is a work of the US government.
- **Noto Kufi Arabic and Noto Naskh Arabic** (subsets in assets/fonts/): © The Noto Project Authors, SIL Open Font License 1.1 (licence files alongside).
- **libmuslim** (https://github.com/muslimtify-org/libmuslim), Apache License 2.0 (text in `licenses/libmuslim_Apache-2.0.txt`):
  - `data/americas_west_coast.json` is the table `hijri__americas_west_coast` in `hijri.h`. It was derived there from Natural Earth 1:50m land (public domain).
  - The Diyanet month starts used for validation (docs/VALIDATION.md, section 8) are transcribed in `tests/test_hijri.c`.
  - The reading of the Istanbul 2016 rule follows `docs/research/2026-10-25-diyanet-global-rule.md`.
  - The code in Sky Taqwim is its own and is not derived from libmuslim's code.
- **Official Umm al-Qura table** (1343–1500 AH) via the hijridate package (MIT licence). The table itself is published by KACST.
- **World Magnetic Model 2025** (NOAA NCEI and the British Geological Survey; a US government work, public domain), used through the **pygeomag** package (MIT licence, https://github.com/boxpet/pygeomag) for the magnetic declination of the live qibla compass.
