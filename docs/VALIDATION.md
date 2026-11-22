# Sky Taqwim engine — validation report

Generated 2026-11-14 with Skyfield 1.54, ephemeris JPL DE440s, hijri-converter 2.3.2.post1, convertdate 2.5.1, jdatetime 6.1.1, persiantools 6.2.0, adhanpy 1.0.5, geographiclib 2.1. All numbers come from `tools/validate.py`, which writes them to `docs/validation_results.json`.

The astronomy itself (new moons, sunsets, moonsets, crescent geometry) is Sky Luach's engine. It was checked there against NASA JPL Horizons: ARCV and ARCL agree within 0.5″ for 1850–2040, sunsets within 0.55 s, and conjunctions within 0.1 s (Sky Luach, docs/VALIDATION.md, section 2). The only change here is the sign test for "the Moon sets after the Sun". It now uses Skyfield's own moonset altitude (−34′ refraction minus the Moon's apparent radius) instead of a fixed −0.8°.

## 1. Umm al-Qura — the current rule against the official table

Rule (since 1423 AH, after R. H. van Gent): on the 29th day, if the geocentric conjunction is before sunset at Mecca and the Moon sets after the Sun, the next day is the 1st. Otherwise the month has 30 days. The rule was applied with JPL DE440s at the Kaaba (sea-level horizon, standard refraction). The computed month starts were compared with the official table in hijri-converter.

| Period | Rule in force then | Months | Computed start ≠ official | Computed − official (days: count) |
|---|---|---|---|---|
| 1423–1500 AH (2002–2077) | current rule | 936 | **4** | -1: 1, 0: 932, +1: 3 |
| 1420–1422 AH (1999–2002) | moonset after sunset only | 36 | 2 | 0: 34, +1: 2 |
| 1420–1422 AH, recomputed with *that* period's rule | moonset after sunset only | 36 | **0** | |
| 1343–1419 AH (1924–1999) | older rules (Moon's age at sunset, not for Mecca) | 924 | 334 | -1: 81, 0: 590, +1: 253 |

The four mismatches since 1423 AH are all knife-edge cases (UT; the "29th day" is the official one):

| Month (official start) | Conjunction | Sunset at Mecca | Moonset − sunset | Official | Computed |
|---|---|---|---|---|---|
| 6/1427 AH (2006-06-27) | 2006-06-25 16:05:15 | 16:06:21 | +6.3 min | 30-day month | new month (1 day early) |
| 6/1446 AH (2024-12-02) | 2024-12-01 06:21:25 | 14:37:27 | -0.0 min | new month | 30-day month (1 day late) |
| 11/1475 AH (2053-06-17) | 2053-06-16 10:51:37 | 16:04:39 | +0.0 min | new month | 30-day month (1 day late) |
| 10/1485 AH (2063-01-30) | 2063-01-29 12:23:40 | 15:08:38 | -0.1 min | new month | 30-day month (1 day late) |

- **6/1427:** the conjunction came 66 s before sunset. The official table did not start the month, so KACST's sunset was probably earlier, or its conjunction later, by about a minute.
- **The other three:** the Moon set within 6 s of the Sun (lag −0.1 to 0.0 min). KACST counted the Moon as setting after the Sun; our horizon model put it a few seconds before.
- **Why the cases cannot be settled:** KACST does not publish its horizon model (elevation, refraction, upper limb or centre).
- **What the app does:** in "auto" mode it shows the official table wherever it exists, so these cases only matter for the computed years after 1500 AH (2077).

1420–1422 AH: the two months that differ under the current rule (7/1421, 8/1422) both began *before* the conjunction (it came 4.5–4.7 h after sunset on the 29th). Recomputed with that period's rule, all 36 months match. This confirms van Gent's account of the rule change.

Before 1420 AH the table followed other rules, so a third of months differ. Most often the computed start is a day later. The official table also has some irregular month lengths. Over 1343–1500 AH: 5 months of 28 days, 882 months of 29 days, 1006 months of 30 days, 3 months of 31 days. The calendar's `source="auto"` keeps them as published.

## 2. Tabular calendars

| Check | Span | Items | Mismatches |
|---|---|---|---|
| Kuwaiti (Type II, civil epoch) vs **convertdate.islamic**, every civil day | 1850–2149 (1267–1574 AH) | 109,558 days | **0** |
| Round trip Hijri → civil → Hijri (Kuwaiti) | same | 109,558 days | **0** |
| Fatimid (Type III, astronomical epoch) vs an independent closed formula (leap if (11y + 11) mod 30 < 11; JD 1948438.5) — first and last day of every month | 1850–2149 | 7,420 days | **0** |

The Fatimid date runs ahead of the Kuwaiti one by 1 day on 98,552 days and by 2 days on 10,974 days (1850–2149). One day comes from the earlier epoch; the second from the different leap years. No published Bohra table was available to check against.

## 3. Solar Hijri (Iran) — JPL equinox against two arithmetic implementations

Nowruz was computed for every year 1229–1527 SH (299 years, March 1850 to March 2149). The year begins on the day of the March equinox if the equinox falls before true solar noon on the 52.5° E meridian; otherwise on the next day. The result was compared with **jdatetime** and **persiantools**. Both use arithmetic leap-year rules, not astronomy.

| Rule | Years differing from jdatetime | Years differing from persiantools |
|---|---|---|
| True noon at 52.5° E (default) | 1: 1503 SH (ours 2124-03-20, theirs 2124-03-21) | 0: none |
| 12:00 Iran Standard Time | 0: none | 1: 1503 SH (ours 2124-03-21, theirs 2124-03-20) |
| True noon at Tehran (51.39° E) | 1: 1503 SH (ours 2124-03-20, theirs 2124-03-21) | 0: none |

Only one year in 300 is in doubt: **1503 SH**. The March equinox of 2124-03-20 08:38 UT falls 6 s before true noon at 52.5° E. The three noon definitions disagree only in that year, and the two libraries also disagree with each other. Everywhere else the JPL calendar and both libraries agree to the day.
Day by day against jdatetime (109,208 days), the only mismatches are the 366 days of that one year.

Published Nowruz dates, checked by hand: 1 Farvardin 1354 = 1975-03-21; 1 Farvardin 1358 = 1979-03-21; 1 Farvardin 1400 = 2021-03-21; 1 Farvardin 1403 = 2024-03-20; 1 Farvardin 1404 = 2025-03-21; 1 Farvardin 1405 = 2026-03-21. They match Iranian calendars, including 1404, whose equinox (20 Mar 2025, 12:31 IRST) fell after noon, so Nowruz was 21 March.

## 4. Prayer times — against two independent implementations

Every day of 2026 was compared for six cities: Mecca, Cairo, Jakarta, New York, Tehran and Najaf. The figures are the largest absolute difference in minutes over the year.

**a) adhanpy** (Python port of the Adhan library; its own solar theory after Meeus). Only the raw method angles were used, without adhanpy's +1 min Dhuhr adjustments. adhanpy rounds every time to the nearest minute, so up to 0.5 min of each difference is rounding.

| Method | Fajr | Sunrise | Dhuhr | Asr | Maghrib | Isha |
|---|---|---|---|---|---|---|
| egypt | 0.88 | 0.99 | 0.96 | 1.41 | 0.98 | 0.92 |
| isna | 0.97 | 0.99 | 0.96 | 1.41 | 0.98 | 1.02 |
| karachi | 0.95 | 0.99 | 0.96 | 1.41 | 0.98 | 1.02 |
| kuwait | 0.95 | 0.99 | 0.96 | 1.41 | 0.98 | 0.92 |
| mwl | 0.95 | 0.99 | 0.96 | 1.41 | 0.98 | 0.99 |
| MWL with Hanafi Asr | 0.95 | 0.99 | 0.96 | 1.00 | 0.98 | 0.99 |
| qatar | 0.95 | 0.99 | 0.96 | 1.41 | 0.98 | 0.87 |
| singapore | 0.97 | 0.99 | 0.96 | 1.41 | 0.98 | 1.02 |
| umm_al_qura | 0.99 | 0.99 | 0.96 | 1.41 | 0.98 | 0.87 |
| **all** | **0.99** | **0.99** | **0.96** | **1.41** | **0.98** | **1.02** |

**b) The PrayTimes.org 2.3 algorithm** (H. Hosseini), ported as published (low-precision solar formulae, one iteration). This covers the two Shia methods, which adhanpy lacks, plus MWL. Times are compared in UT. PrayTimes adds one zone offset, taken at noon, to every time, which would otherwise create false one-hour differences on daylight-saving days.

| Method | Fajr | Sunrise | Dhuhr | Asr | Sunset | Maghrib | Isha | Midnight |
|---|---|---|---|---|---|---|---|---|
| jafari | 0.10 | 0.08 | 0.04 | 0.24 | 0.09 | 0.09 | 0.17 | 0.92 |
| tehran | 0.12 | 0.08 | 0.04 | 0.24 | 0.09 | 0.09 | 0.17 | 0.93 |
| mwl | 0.13 | 0.08 | 0.04 | 0.24 | 0.09 | 0.09 | 0.21 | 0.86 |

All prayers agree within 0.25 min. Midnight differs by up to 0.93 min because PrayTimes takes *today's* sunrise or Fajr plus 24 h; the engine uses the *next* morning's. The Ja'fari Maghrib (4° and 4.5°) and Ja'fari midnight (sunset to Fajr) agree.

**Method angles** (fajr / isha; maghrib): MWL 18/17; ISNA 15/15; Egypt 19.5/17.5; Umm al-Qura 18.5 / 90 min (120 min in Ramadan); Karachi 18/18; Diyanet 18/17 plus offsets (adhan-js approximation); Gulf 19.5 / 90 min; Kuwait 18/17.5; Qatar 18 / 90 min; Dubai 18.2/18.2; Singapore–JAKIM–KEMENAG 20/18; Ja'fari (Leva Institute, Qum) 16/14, Maghrib 4°; Tehran (Institute of Geophysics) 17.7/14, Maghrib 4.5°. These follow PrayTimes.org "Calculation Methods", the AlAdhan method list and adhan-js. National authorities sometimes publish timetables with their own minute offsets (ihtiyat or temkin), which no general method reproduces exactly.

**Speed:** a full year for one place and one method takes 0.29–0.40 s. One month (London, June, high-latitude rule) takes 0.04 s.

## 5. Qibla

The engine gives the initial great-circle bearing on a sphere, the convention of most qibla tables. It was compared with the geodesic on the WGS-84 ellipsoid (geographiclib, Karney 2013) and with widely published values.

| City | Engine (sphere) | WGS-84 geodesic | Published | Distance (sphere / WGS-84) |
|---|---|---|---|---|
| London | 118.99° | 118.87° | 118.99° | 4,794 / 4,795 km |
| New York | 58.48° | 58.40° | 58.48° | 10,306 / 10,324 km |
| Jakarta | 295.15° | 295.02° | 295.15° | 7,920 / 7,922 km |
| Kuala Lumpur | 292.54° | 292.44° | — | 6,974 / 6,979 km |
| Istanbul | 151.62° | 151.51° | — | 2,405 / 2,400 km |
| Tehran | 218.40° | 218.54° | — | 1,944 / 1,941 km |
| Cape Town | 23.35° | 23.47° | — | 6,558 / 6,532 km |
| Tokyo | 293.00° | 293.07° | — | 9,472 / 9,488 km |
| Los Angeles | 23.86° | 23.77° | — | 13,424 / 13,443 km |

The sphere and the ellipsoid differ by at most 0.14° in bearing and about 0.4% in distance. That is far below what a phone compass can resolve. The published values (London, New York, Jakarta) match the spherical bearing to 0.01°.

## 6. Sighting calendar — internal checks

The precomputed Mecca table holds 18,561 evenings (one before to three after each of the 3,711 new moons of 1850–2150); building it takes about one minute. Each month of the sighting chain is given the Hijri number of the Umm al-Qura month in the same place in the sequence. The table shows how the predicted month starts at Mecca compare with Umm al-Qura ("auto"), 1850–2149:

| Criterion | Months | Start − Umm al-Qura start (days: count) | Beyond ±3 days |
|---|---|---|---|
| yallop_A | 3710 | -1: 2, 0: 400, +1: 3037, +2: 271 | 0 |
| yallop_B | 3710 | -1: 5, 0: 825, +1: 2753, +2: 127 | 0 |
| yallop_C | 3710 | -1: 8, 0: 1133, +1: 2480, +2: 89 | 0 |
| odeh_A | 3710 | -1: 2, 0: 391, +1: 3046, +2: 271 | 0 |
| odeh_B | 3710 | -1: 7, 0: 1112, +1: 2499, +2: 92 | 0 |
| odeh_C | 3710 | -1: 12, 0: 1852, +1: 1820, +2: 26 | 0 |

- **Visibility comes later than Umm al-Qura:** with naked-eye criteria a predicted sighting usually comes one day after the Umm al-Qura start. The Umm al-Qura rule needs only the conjunction and moonset before and after sunset, not a visible crescent.
- **Telescope sightings bring the start forward:** accepting them (Odeh C) moves about half of the months to the Umm al-Qura day.
- **The chain for other places is stable:** for London it was computed twice, with spans 2023–2029 and 2024–2031. The 72 months common to both start on the same day in both (0 differences), so the settling period before the span is enough. A 7-year span takes 0.0 s.

## 7. What is *not* validated

- **Crescent criteria:** the app uses the published models of Yallop 1997 (NAO Technical Note 69) and Odeh 2004 (*Experimental Astronomy* 18:39–64). It has not been tested against a sighting record. Real announcements depend on weather, witnesses, the authority that accepts them, and whether sightings from other countries count. The sighting calendar is a prediction, not a record of practice.
- **Saudi religious dates:** the starts of Ramadan, Shawwal and Dhu al-Hijjah are declared by the Supreme Court from reported sightings. They are not the Umm al-Qura table and can differ from it by a day; the engine does not model them.
- **Fatimid (Bohra) dates:** only the arithmetic was checked; no published Bohra table was compared.
- **Solar Hijri before 1925:** dates before the Iranian law of 1925 are proleptic, computed by the same rule; Afghanistan adopted the calendar in 1922.
- **Official prayer timetables:** the prayer times were compared with other algorithms, not with timetables published by national authorities, which often add precautionary minutes.
- **Dates outside 1850–2149** need the larger de440.bsp (1550–2650) in the ephem folder; the Mecca crescent table and data/seasons.csv would then need rebuilding (tools/build_tables.py).


## 8. Unified Hijri Calendar (Istanbul 2016) — against Diyanet and the North American and European councils

The month starts 1850–2149 were computed by a global search (`unified_hijri_calendar.py`). Clause A tries one
point per degree of latitude, 60 S to 60 N, where the Sun sets at 00:00 UT. Clause B tries the westernmost point
of the Americas mainland at each latitude, 53 S to 71 N, with dawn in Wellington at the Sun 18 deg below. A point
passes when the conjunction comes before its sunset, its topocentric unrefracted altitude is at least 5 deg and
its geocentric elongation at least 8 deg.

Over 3,711 new moons, clause A decided 3,392 starts and clause B 319.

| Check | Months | Agree |
|---|---|---|
| Diyanet's published calendar, 1 Jumada II 1442 – 1 Dhu al-Qa'dah 1457 (2021-01-14 – 2035-12-31), start and Hijri label | 186 | **184** |
| Fiqh Council of North America / ECFR announcements under the 5 + 8 rule (Shawwal 1441, 1444, 1445, 1446; Ramadan 1446) and Ramadan 1428 | 6 | **6** |

Notes on the table:
- **Diyanet's calendar** is the union of two Diyanet lists, from mobil.diyanet.gov.tr (2021–2028) and
  vakithesaplama.diyanet.gov.tr (2027–2035). The transcription is the one in the libmuslim project's
  `tests/test_hijri.c` (Apache-2.0), retrieved 2026-10-17.
- **The two misses** are 1 Dhu al-Qa'dah 1442 (Diyanet 2021-06-11, here a day later) and 1 Dhu al-Qa'dah 1444
  (Diyanet 2023-05-21, here a day earlier, decided by clause B at 55 N on the Alaskan coast with the Moon 5.3 deg
  high and 8.1 deg from the Sun). They are the same two months, missed the same way, as in libmuslim's own
  search. The published rule leaves the frames of the angles and the search open, so these borderline evenings
  cannot be settled.
- **Shawwal 1428** (2007): FCNA then used an earlier rule, the conjunction before 12:00 GMT, and announced
  13 October 2007. The 5 + 8 rule gives 12 October, so this month is not counted.

## 9. Neo-MABIMS and the other calculated sighting rules

The Neo-MABIMS rule uses the topocentric unrefracted altitude of the Moon's centre at sunset (at least 3 deg)
and the topocentric elongation at sunset (at least 6.4 deg), after the conjunction. A column for that elongation
was added to the crescent tables, and the Mecca table was rebuilt with it.
- **Checked against a source:** for Jakarta, 1 Shawwal 1447 comes out as 21 March 2026. Indonesia's Ministry
  of Religious Affairs (Kemenag) said on 19 March 2026 that no province met the MABIMS criteria that evening (VOI, citing ANTARA, 'Kemenag: Height of the Crescent in Indonesia Has Not Met the MABIMS Criteria', voi.id/en/amp/565456).
- **Computed only, not checked here against an announcement:** 1 Ramadan 1447 = 19 February 2026,
  1 Shawwal 1446 = 31 March 2025 and 1 Shawwal 1445 = 10 April 2024.

## 10. Hijri Shamsi (Ahmadiyya) and Julian

- **Hijri Shamsi:** 1 January 2000 = 1 Sulh 1379 HS and 15 June 2008 = 15 Ihsan 1387 HS. This agrees with
  AhmadiPedia, 'Hijri–Shamsi Calendar' (ahmadipedia.org/content/scheme/14: 2000 = 1379 HS) and with Wikipedia's article
  on Mirza Bashir-ud-Din Mahmood Ahmad (2008 = 1387 HS).
- **Julian:** 23 April (Julian) falls on 6 May (Gregorian) in every year from 1900 to 2099, the date of
  Hıdırellez. The Alawite Nawruz (4 Nisan) falls on 17 April and Mihrajan (16 Tishrin al-Awwal) on
  29 October (2026), matching the dates in Friedman 2010, ch. 2. 14 November 2026 = 1 Tishrin al-Thani (November) 2026 by the Julian reckoning. The conversion is
  the standard Julian Day Number formula.
