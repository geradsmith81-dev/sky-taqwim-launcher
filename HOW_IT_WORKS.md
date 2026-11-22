## How Sky Taqwim works · كيف يعمل تقويم السماء

Sky Taqwim shows the Islamic calendar seven ways, for **Sunni** or **Shia** practice, and lists which calendar each school, branch and movement uses (the **Traditions** page). The positions of
the Sun and the Moon come from NASA's Jet Propulsion Laboratory ephemeris **DE440s** (1850–2149), read with the
Skyfield library. Nothing is looked up online except the one-time download of that file.

### 1. The lunar year · السنة القمرية

The Hijri year has twelve lunar months of 29 or 30 days, about 354 days in all. The Qur'an fixes the number of
months at twelve, four of them sacred (9:36). It condemns the *nasi'*, the pre-Islamic practice of postponing
months (9:37). So the Islamic year is never adjusted to the Sun, and Ramadan moves through the seasons, about
11 days earlier each solar year. Years are counted from the Hijra, the Prophet's emigration to Medina in
622 CE. The count was adopted under the caliph Umar about 17 AH (638 CE). The earliest dated documents to use it
are the papyrus PERF 558 (22 AH) and the Zuhayr inscription near al-'Ula (24 AH).

**The day begins at sunset.** A date in the app (for example *Friday 13 March*) is the Islamic day whose
daytime falls on that date. It began at sunset the evening before. In Ja'fari (Shia) practice the evening
begins at Maghrib, once the redness has left the eastern sky, a little after sunset.

### 2. The calendars · التقاويم

**Umm al-Qura · تقويم أم القرى** is the official calendar of Saudi Arabia, worked out in advance for Mecca. Since
1423 AH (2002) its rule is: on the 29th day of a month, if the new moon (the conjunction) comes before sunset at
Mecca *and* the Moon sets after the Sun, the next day begins the new month; otherwise the month has 30 days. The
app uses the published table for 1343–1500 AH (1924–2077) and computes the rule from JPL outside it. Since
1423 AH the computation agrees with the table in 932 of 936 months; the 4 others are cases where the Moon set
within seconds of the Sun. **Ramadan, the Eids and the Hajj** are not taken from this table. The Saudi Supreme
Court declares them from reported sightings, so they can fall a day later.

**Crescent sighting · رؤية الهلال**. Here the month begins as the Prophet's saying instructs: "fast when you see
it, and break the fast when you see it; if it is hidden from you, complete the count at thirty". For every month,
the app asks whether the young crescent would be visible from the chosen place on the evening ending the 29th
day. If it would, the next day is the 1st. If not, the month is given 30 days. Visibility is judged by the two
standard models:

- **Yallop** (B. D. Yallop 1997, *NAO Technical Note* 69). It combines how far the Moon stands above the Sun at
  the best time to look with the width of the crescent. Zone A means easily visible, B visible to the naked eye
  in perfect conditions, C needs optical aid to find, D is visible with optical aid only, and E and F are not
  visible.
- **Odeh** (M. Odeh 2004, *Experimental Astronomy* 18:39–64). It was fitted to 737 recorded observations.
  Zone A means visible to the naked eye, B visible with optical aid and possibly by eye, C visible with optical
  aid only, and D not visible.

Whose sighting counts is a matter of law, and the app offers the main positions:

- *Sunni:* sighting from Mecca (the default), as Saudi practice seeks. Or a local sighting, the view of those
  who hold that each region has its own horizon (*ikhtilaf al-matali'*).
- *Shia:* the local horizon. Most Twelver jurists hold that a sighting is valid for the place and places that
  share its horizon. Some, among them Ayatollah **Sistani** (*Islamic Laws*, ruling 1699), require the naked
  eye. Others, among them Ayatollah **Khamenei**, accept a sighting through a telescope. Most Shia
  authorities do not accept calculation alone, so the app keeps this a prediction of a sighting.

**Tabular · التقويم الحسابي** is the arithmetic calendar of medieval astronomers. Odd months have 30 days and
even months 29, and 11 years in every 30 add a day to Dhu al-Hijjah. The *standard (Kuwaiti)* form uses leap
years 2, 5, 7, 10, 13, 16, 18, 21, 24, 26 and 29 of the cycle and the civil epoch of 16 July 622. It agrees
with the convertdate library on all 109,558 days of 1850–2149. The *Fatimid* form is still used by the
Dawoodi Bohra, an Isma'ili Shia community; it is not the calendar of Twelver Shia. It uses leap years 2, 5, 8,
10, 13, 16, 19, 21, 24, 27 and 29 and the epoch of 15 July 622, and runs one or two days ahead of the
standard form.

**Unified Hijri Calendar · التقويم الهجري الموحد** is the calendar adopted at the Istanbul congress of
2016. The whole world is one sighting zone, and a month begins on the same day everywhere. Day D is the 1st when,
on the evening before, somewhere on Earth whose sunset comes before 00:00 UT the Moon is at least 5° above the
horizon and 8° from the Sun at sunset. It is also the 1st if that holds on the mainland of the Americas after
00:00 UT and the new moon came before dawn in Wellington. Turkey's Diyanet, Indonesia's Muhammadiyah (from
1446 AH) and, for Ramadan and Shawwal, the European Council for Fatwa and Research and the Fiqh Council of
North America use these 5° + 8° parameters. The app searches every latitude from 60° S to 60° N and the west
coast of the Americas. It uses topocentric altitude and geocentric elongation, the reading that reproduces
Diyanet's published calendar in 184 of 186 months (2021–2035).

**Solar Hijri · التقويم الهجري الشمسي** is the official civil calendar of Iran (since 1925) and of Afghanistan.
It counts solar years from the Hijra. The year begins with Nowruz, on the day of the March equinox if the
equinox comes before noon on the 52.5° E meridian, otherwise on the next day. The first six months have 31
days, the next five 30, and Esfand 29, or 30 in a leap year. The app finds every equinox from JPL. Over 300
years it agrees with two independent calendar libraries in every year but 1503 SH (2124), whose equinox falls
6 seconds before noon. Religious days in Iran and Afghanistan still follow the lunar months.

**Hijri Shamsi · الهجري الشمسي الأحمدي** is the solar calendar of the Ahmadiyya Muslim Community (1940). Its
months have the days of the Gregorian months and are named after events in the Prophet's life: Sulh, Tabligh,
Aman, Shahadat, Hijrat, Ihsan, Wafa, Zuhur, Tabuk, Ikha, Nabuwwat and Fatah. Its years are counted from the
Hijra in solar years (2026 = 1405 HS). Ahmadi Ramadan and Eids still follow the lunar months.

**Julian (Rumi) · اليولياني** is the Eastern reckoning, with the Syriac month names of the Levant and Iraq. It
was the Ottoman 'Rumi' calendar until 1917, and it now runs 13 days behind the Gregorian calendar. Some Alevi
and Alawite days are fixed in it: Hıdırellez on 23 April Julian is 6 May. The Alawite Nawruz
(4 Nisan) is 17 April, and Mihrajan (16 Tishrin al-Awwal) is 29 October (Friedman 2010).

**Sighting rules.** The crescent can be looked for from Mecca, from your own place, or from one of 21 cities.
The rules are:
- **Yallop** and **Odeh**: predictions of whether the crescent can be seen.
- **Neo-MABIMS** (Brunei, Indonesia, Malaysia and Singapore since 2021): the Moon at least 3° high and 6.4° from
  the Sun at sunset.
- **Wujud al-hilal**: the new moon before sunset and the Moon setting after the Sun. This is Umm al-Qura's rule
  applied at your place, and Muhammadiyah's rule until 2024.
- **Conjunction**: the new moon before sunset on the 29th.

The last three are calculated criteria. They do not ask whether the crescent can be seen.

### 2b. Traditions · المذاهب والفرق

The **Traditions** page lists the schools, branches and movements of Islam under the calendar each uses:

- **The four Sunni schools.** The Hanafi, Maliki and Hanbali schools hold that one sighting binds all who hear
  of it, while the Shafi'i school holds that each region follows its own horizon.
- **Sunni movements.** The Deobandi, Barelvi and Wahhabi/Salafi movements are listed with the practice of the
  states where they are strongest. The Taliban are a political movement rather than a school; Afghanistan's
  official calendar became the lunar Hijri in 2022.
- **Shia communities.**
  - **Twelvers** follow the local horizon. Sistani requires the naked eye; Khamenei accepts a telescope.
  - **Alawites** keep lunar feasts and some solar feasts by the Julian reckoning.
  - **Isma'ilis:** the Dawoodi Bohras keep the Fatimid tabular calendar; the Nizaris keep the sighting.
  - **Alevi-Bektashis** keep Turkey's calculated calendar for the Muharram fast, and the Julian calendar for
    Hıdırellez.
  - **Zaydis** keep the sighting in Yemen.
- **Other branches and movements.**
  - **Ibadis** keep local sighting in Oman.
  - **Ahmadis** keep naked-eye visibility worked out by calculation, and their Hijri Shamsi calendar.
  - **Quranists** have no common authority; most keep the sighting, and some count from the new moon.
- **Without a calendar of their own.** The Kharijites survive only in the Ibadis, who reject the name; Sufism is
  a path within both branches; Salafist jihadism is a militant movement.

Press **Use** beside any entry and the app's settings change to model that practice. Each entry gives its
sources. Practice varies inside every group, so the presets are models of the main practice named.

### 3. Sunni and Shia · السنة والشيعة

The switch at the top changes:

- **The holy days.** Both traditions keep Ramadan, Laylat al-Qadr, the two Eids, the Day of Arafah, the Hijri
  New Year and Ashura, but differently:
  - Ashura is a recommended fast in Sunni practice, and the day of mourning for Imam Husayn's martyrdom at
    Karbala (61 AH) in Shia practice.
  - Sunni practice seeks Laylat al-Qadr in the odd nights of the last ten, especially the 27th. Shia practice
    keeps the nights of the 19th, 21st and 23rd.
  - Sunni dates also include the Mawlid on 12 Rabi' al-Awwal (widely, though not universally, kept), the Isra'
    and Mi'raj, the night of mid-Sha'ban and the recommended fasts.
  - Shia dates also include the Mawlid on 17 Rabi' al-Awwal, Arba'in, Eid al-Ghadir, Mubahala, al-Mab'ath, the
    birth of the Mahdi on 15 Sha'ban, and the births and martyrdoms of the Imams and of Fatima al-Zahra. These
    follow the Iranian official calendar, which mostly follows al-Mufid's *al-Irshad*, and the notes give the
    other dates.

  Click any day's name for a short history with sources.
- **The default calendar.** Sunni mode starts with Umm al-Qura; Shia mode with the crescent seen from your
  own horizon.
- **Prayer times.**
  - Sunni methods: Muslim World League, ISNA, Egypt, Umm al-Qura, Karachi, Diyanet and the Gulf states,
    Singapore, Malaysia and Indonesia, with Shafi'i/Maliki/Hanbali or Hanafi Asr.
  - Shia methods: the Leva Institute of Qum (Fajr 16°, Isha 14°, Maghrib 4°) and the Institute of Geophysics,
    Tehran (17.7°, 14°, 4.5°). In both, midnight is halfway from sunset to Fajr.

Every choice can still be changed in the settings.

### 4. Prayer times and the qibla · المواقيت والقبلة

Each prayer time is the moment the Sun reaches a set angle below the horizon at your coordinates. Dhuhr is when
the Sun crosses the meridian; Asr is when a shadow reaches its length (or twice its length, Hanafi) beyond the noon
shadow. The times agree with two independent programs (adhanpy and the PrayTimes.org algorithm) to within about a
minute. Local mosques often add a few minutes of precaution. Near the poles in summer the Sun may not go deep
enough for Fajr and Isha, so the settings offer the usual adjustments.
The **qibla** is the initial direction of the great circle to the Kaaba (21.4225° N, 39.8262° E), measured
from true north. A magnetic compass needs correcting for the local magnetic declination.

On a phone or tablet the Today page's qibla card is a **live compass**. The device's compass reports the heading
of its top edge from *magnetic* north (iPhone and iPad after **Turn on the live compass** is tapped and Motion &
Orientation is allowed; Android without asking). The app adds the magnetic declination of your place, from the
World Magnetic Model 2025 (NOAA and the British Geological Survey), to get the heading from *true* north. It then
turns the dial so that N points to true north, and the gold arrow so that it points along the qibla bearing. The
red mark above the dial is the top of the phone: when the arrow points at it (within 5°) the card says you are
facing the qibla, and the phone gives a short vibration where it can. The phone must be held flat, screen up: held
upright, its compass is unreliable and the card says so. Steel, magnets and cars disturb any compass; if the
reading drifts, move the phone in a figure of eight to recalibrate it. Computers have no compass, so the dial stays
with north at the top. The compass readings are used only in the browser and are not sent anywhere.

### 5. Limits · حدود

- The sighting calendar **predicts** what can be seen in clear weather. Real announcements depend on weather,
  witnesses and the authority that accepts them. Follow your community or marja' for the dates you keep.
- Dates run from 1850 to 2149. Sighting from a place other than Mecca is computed for six years either side of
  today.
- Hadith numbers and dates in the histories follow the standard collections and reference works named with
  each entry; where traditions differ, both are given.

See `docs/VALIDATION.md` for every check and its numbers.
