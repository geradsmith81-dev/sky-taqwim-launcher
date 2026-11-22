# Sky Taqwim · Content track notes

This folder holds the names, holiday rules and holiday histories for Sky Taqwim. It follows the
patterns of Sky Luach's `hebrew_names.py` and `holiday_history.py`.

| File | What it holds |
|---|---|
| `arabic_names.py` | Month names (unpointed, pointed, variants, epithets); the sacred months; solar Hijri months (Iranian Persian, Afghan Dari and Pashto); weekdays (English, Arabic, transliteration, Persian); the Saturday-first `GRID_WEEK`; the Twelve Imams; `TERMS`, `TERMS_FA`, `KIND_AR`, `KIND_EN`, `PLACE_AR`; helpers `bi`, `bt`, `bp`, `month_bi`, `solar_month_bi`, `to_arabic_digits`, `to_persian_digits`, `hijri_date_ar`, `solar_date_fa`, `arabic_place_name`, `persian_place_name`, `normalise_persian`, `is_rtl_text` |
| `holidays.py` | `Holiday`, `HijriDay`, `SolarDay`; the tables `SHARED`, `SUNNI`, `SHIA`; `holidays_for_year`, `holidays_between`, `solar_holidays_for_year`, `COMPARE_HOLIDAYS`, `COMPARE_HOLIDAYS_BY_BRANCH`, `compare_holidays` |
| `holiday_history.py` | `H`: 48 histories, each (title, Arabic title, text, sources); `key_for`, `body_html`, `clickable`; `PERSIAN_TITLES` |
| `tests/test_content.py` | 12 tests with a tabular stand-in calendar. Run with `python tests/test_content.py` from this folder. |

## Contract notes for the integrator

- **Holiday fields**, in order: `date, name, arabic, kind, hdate, note, key, begins_evening_before, branch`.
  `arabic` holds Persian script for the solar festivals. `hdate` is a `HijriDay(year, month, day)`
  (or a `SolarDay`). Both are NamedTuples with `str()` such as "10 Muharram 1447" and an `.arabic`
  property such as "١٠ محرم ١٤٤٧ هـ".
- **Calendar interface**: the code only uses `cal.to_gregorian(y, m, d)`, which returns a date or
  None, and `cal.get_month(y, m).length`. Days that a calendar lacks are skipped: the 30th of a
  29-day month, or a year outside its range (ValueError, KeyError, IndexError, LookupError and
  OverflowError are caught). "Last day of the month" rules (`LAST`) use `get_month(...).length`.
- **Evening rule**: `begins_evening_before=True` for every Islamic day except fast entries, which
  run from dawn to sunset. "Ramadan begins" stays True because tarawih starts the evening before.
  A night such as Laylat al-Qadr (27th night) carries the date of the 27th and begins the evening
  before. The solar festivals have False. Shab-e Yalda and Chaharshanbe Suri are dated to the day
  on whose evening they fall.
- **Branch**: `holidays_for_year(cal, year, "sunni" | "shia", month_starts=, imams=, fasts=, nights=)`.
  Shared days carry `branch="both"`, with a note worded for the chosen branch. An unknown branch
  raises ValueError.
- **Holiday kinds**: the shared set, `KINDS = eid, sacred, fast, night, mourning, birth, month, hajj, civil`.
  `KIND_AR` and `KIND_EN` in arabic_names give labels. Sort order within a day: eid, sacred,
  mourning, birth, night, hajj, fast, month, civil.
- **Popovers**: `clickable(key_or_name, chip_html, align_right=False)` takes either a `Holiday.key`
  or a holiday name. Classes used: `tq-pop`, `tq-pop-r`, `tq-popbody`, `tq-pop-title`, `tq-pop-text`,
  `tq-pop-src`, and `tq-ar` for the Arabic (with `lang='fa'` for the four Persian festival titles).
  All text passes through `html.escape`.
- **Compare page**: `COMPARE_HOLIDAYS` is the Sunni list (the contract asked for a list).
  `compare_holidays(branch)` gives the branch's list: Mawlid on 12 or 17 Rabi' al-Awwal, Laylat
  al-Qadr on the 27th or 23rd. The Shia list adds Arba'in and Eid al-Ghadir.
- **Month grid**: `GRID_WEEK` starts on Saturday and ends on Friday. `GRID_WEEK_START = 5`
  (date.weekday() of Saturday).
- **Additions** beyond the contract (all additive): `bp()` for Persian terms; `lang=` on `bi()`;
  the `name=` keyword on `arabic_place_name()` with the `PLACE_AR` overrides; `KIND_EN`; `IMAMS`;
  `TERMS_FA`; `MONTH_ALT`; `holidays.KINDS`, `BRANCHES`, month constants, `LAST`.

## Which date is used where sources differ

The rule throughout:

- Sunni days use the dates most widely kept today.
- Shia days use the Iranian official calendar (Institute of Geophysics, University of Tehran). It
  mostly follows al-Mufid (*al-Irshad*, *Masar al-Shi'a*) and al-Tusi (*Misbah al-mutahajjid*).
- Each other date is named in the holiday's `note` and in its history.

| Day | Date used | Other dates in the sources |
|---|---|---|
| Laylat al-Qadr (Sunni) | night of 27 Ramadan | any odd night of the last ten (21, 23, 25, 27, 29); the note says so |
| Laylat al-Qadr (Shia) | nights of 19, 21, 23 Ramadan (23rd most emphasised) | — |
| Mawlid al-Nabi | Sunni 12 Rabi' I; Shia 17 Rabi' I | al-Kulayni also gives the 12th; Iran keeps 12–17 as Unity Week |
| Death of the Prophet | Shia 28 Safar (al-Mufid, al-Tusi, Iran) | Sunni 12 Rabi' I (Ibn Ishaq), also 1st or 2nd; not a separate Sunni entry |
| Martyrdom of Imam Hasan | 28 Safar (Iran), joined to the Prophet's death | 7 Safar (kept in Iraq); noted |
| Martyrdom of Imam al-Rida | last day of Safar (29 or 30), Iran | 17 Safar; 23 Dhu al-Qa'dah |
| al-Isra' wa'l-Mi'raj | night of 26/27 Rajab (Sunni) | early reports put it in other months, 1–5 years before the Hijra |
| al-Mab'ath | 27 Rajab (Shia) | most Sunni scholars place the first revelation in Ramadan |
| Birth of Imam Husayn | 3 Sha'ban (Iran, al-Tusi) | 5 Sha'ban (al-Mufid) |
| Birth of Imam al-Sajjad | 5 Sha'ban (Iran) | 15 Jumada al-Ula |
| Martyrdom of Imam al-Sajjad | 25 Muharram (Iran) | 12 or 18 Muharram |
| Birth of Imam al-Baqir | 1 Rajab (Iran) | 3 Safar |
| Martyrdom of Imam al-Baqir | 7 Dhu al-Hijjah (Iran) | year 114–118 AH |
| Martyrdom of Imam al-Kazim | 25 Rajab (Iran) | an earlier day in Rajab in other reports |
| Birth of Imam al-Hadi | 15 Dhu al-Hijjah (al-Kulayni, al-Mufid, al-Tusi) | 2 or 5 Rajab |
| Martyrdom of Imam al-Hadi | 3 Rajab (Iran) | 25 or 26 Jumada al-Akhirah |
| Birth of Imam al-Askari | 8 Rabi' II (Iran) | 10 Rabi' II |
| Martyrdom of Imam al-Jawad | last day of Dhu al-Qa'dah (Iran) | — |
| Fatimiyya | both 13 Jumada I (75-day report, al-Kafi) and 3 Jumada II (95-day report; Iran's public day) | Sunni sources: about six months after the Prophet (al-Bukhari) |
| Imam Ali struck | 19 Ramadan | some Sunni histories give the 17th |
| Mubahala | 24 Dhu al-Hijjah | 21, 25 or 27 |
| Laylat al-Raghaib | night before the first Friday of Rajab that follows the month's first Thursday | when 1 Rajab is a Friday, some count that Friday; the rule follows the texts that join it to a fast on the first Thursday |
| Ashura fast (Sunni) | 9 and 10 Muharram | 10 and 11 |

## Other judgement calls

1. **Eid al-Zahra (9 Rabi' al-Awwal) is left out under that name.** The popular festival is
   linked to a story about the death of the caliph Umar. Historians reject that story (Umar died
   in Dhu al-Hijjah 23 AH), many leading Shia jurists discourage the festival, and it is offensive
   to Sunnis. The app shows the same day as the **Start of the Imamate of Imam al-Mahdi**, as in the
   Iranian official calendar. The note says that some communities also keep it as a popular
   festival under other names. This entry is under `imams=True`.
2. **Laylat al-Raghaib is a shared day ("both")**, with a note for each branch. It is a Sunni
   (Ottoman and Turkish Regaip Kandili) custom and also a Shia one (Ibn Tawus, *Mafatih al-jinan*).
   The Sunni note records that al-Nawawi and others rejected its special prayer.
3. **Sunni Ashura is a "sacred" day.** The recommended fasts are separate "fast" entries ("Fast of
   Tasu'a", "Fast of Ashura") shown only with `fasts=True`. The same applies to the Fast of Arafah,
   so a "fast" filter shows every fast.
4. **Shia Ashura** is "mourning". The note says that a full fast is discouraged in Shia law and that
   many abstain from food until the afternoon. Tasu'a is a mourning day dedicated to al-Abbas.
5. **The Shia fasts** shown with `fasts=True` are limited to the Fast of Arafah, with its
   conditions. The recommended Ghadir and Mab'ath fasts are mentioned in those days' notes. The
   white days are a Sunni entry only. Their history notes the Shia practice (three fast days a month,
   and i'tikaf in the white days of Rajab).
6. **White days** skip Ramadan (already a fast) and 13 Dhu al-Hijjah (a Day of Tashriq, when fasting
   is forbidden). The 14th carries a note about this.
7. **Six days of Shawwal** appears as one "fast" entry on 2 Shawwal, the first day it may be kept,
   rather than only as a note. This way the history can be opened. It is shown only with `fasts=True`.
8. **The 19th and 21st of Ramadan (Shia)** each have two entries: Laylat al-Qadr (night) and the
   wounding or martyrdom of Imam Ali (mourning). They are distinct observances on the same day.
9. **15 Sha'ban (Shia)** has the birth of the Mahdi (birth). The night of vigil is a separate entry
   with `nights=True`.
10. **New-month entries** are skipped for Muharram, Ramadan and Shawwal, whose 1st already has its
    own entry. Rajab, Dhu al-Qa'dah and Dhu al-Hijjah link to the sacred-months history; the other
    months link to the crescent history.
11. **Under `imams=True`** (Shia) come the remaining Imams' births and deaths, plus Zaynab (5 Jumada
    I) and al-Abbas (4 Sha'ban). These two are in the Iranian calendar and are widely kept. The
    main days are always shown: Ali, Hasan, Husayn, al-Sadiq, al-Rida, Fatima and the Mahdi.
12. **Not included**: Islamic Republic Day, the anniversary of the Revolution and other political
    days in Iran; 1 Dhu al-Hijjah as the marriage of Ali and Fatima (only noted); 7 Safar as a
    separate entry; Mondays and Thursdays as recommended fasts. The aim was to avoid state-political
    days and clutter.
13. **Solar festivals**: Nowruz (1–4 Farvardin; Iran's public holidays; Afghanistan keeps 1 Hamal),
    Sizdah Bedar, Shab-e Yalda (evening of 30 Azar) and Chaharshanbe Suri (the Tuesday evening
    before the last Wednesday of Esfand). These were asked for, apart from Chaharshanbe Suri, which
    was added as the best-known fire festival of the year's end.
14. **The Rabi' II Arabic form**: the UI uses ربيع الثاني to match the transliteration "Rabi'
    al-Thani". `MONTH_ALT[4]` gives ربيع الآخر, the Umm al-Qura form.

## Histories: sources policy

- The histories cite only works and editions that exist and are standard. These are the Qur'an
  (sura:verse); the hadith collections of al-Bukhari, Muslim, Abu Dawud, al-Tirmidhi, al-Nasa'i,
  Ibn Majah and Ahmad, and Malik's *Muwatta'*; Ibn Ishaq/Ibn Hisham, al-Tabari, Ibn Sa'd, al-Mas'udi
  and Ibn al-Athir; al-Kulayni, al-Mufid, al-Tusi, Ibn Babawayh, Ibn Tawus and Abbas Qummi; and
  al-Biruni, al-Maqrizi, Ibn Khallikan, al-Suyuti, al-Ghazali and al-Nawawi.
- The reference works are the Encyclopaedia of Islam (2nd ed.) and the Encyclopaedia Iranica,
  cited by entry.
- Hadith numbers follow the common numbering (Fath al-Bari for al-Bukhari, Abd al-Baqi for Muslim).
  They are given only where I am confident of them; elsewhere the book (kitab) is named.
- The epigraphy and archaeology citations were checked before writing:
  - **PERF 558**: Greek–Arabic receipt for 65 sheep, Herakleopolis (Ihnas), Jumada al-Ula 22 AH =
    25 April 643. Vienna, Austrian National Library, Erzherzog Rainer collection. Published by
    A. Grohmann, *From the World of Arabic Papyri* (Cairo 1952) 113–15.
  - **The Zuhayr inscription**, Qa' al-Mu'tadil near al-'Ula, "at the time Umar died, in the year 24".
    A. I. al-Ghabban, translated with remarks by R. Hoyland, *Arabian Archaeology and Epigraphy*
    19 (2008) 210–237. Some citations give the pages as 209–236.
  - **The Dome of the Rock**: the date 72 AH in the mosaic band. C. Kessler, *JRAS* 1970; O. Grabar,
    *The Shape of the Holy* (1996).
  - **Yalda/Chella** was put on UNESCO's Representative List in 2022 (Iran and Afghanistan). Nowruz
    was put on it in 2009.
- **Debated links are stated as debated**: the Persepolis reliefs as a Nowruz ceremony; Yalda and
  Mithra; how early the Dome of the Rock was linked with the Mi'raj; the strength of the mid-Sha'ban
  hadith; the nature of the pre-Islamic nasi'.
- **Sunni and Shia accounts are each attributed.** This covers Ghadir, Arafah and Qur'an 5:3, the
  Mab'ath and the first revelation, the death of the Prophet, Fatima's birth and death, and the
  Friday prayer during the Occultation. No account is judged against the other.
- A few details rest on standard secondary knowledge and not on a source opened in this session:
  the Supreme Court's role in Saudi sighting decisions, the Fiqh Council of North America's 2006
  move to calculation (not cited in the text), the Samarra shrine bombings of 2006–2007, and the
  scale of the Arba'in walk (stated without a number). They are worded cautiously.

## Arabic place-name heuristic (GeoNames)

GeoNames mixes Arabic, Persian, Urdu, Pashto, Kurdish and Uyghur alternate names without language
tags. `arabic_place_name(alternates, name=None)` works in this order:

1. Use `PLACE_AR[name]` if the city is in the override table (36 cities the app shows often:
   Mecca, Medina, Tehran → طهران, Riyadh → الرياض, Najaf → النجف, ...).
2. Keep Arabic-script names with no Latin letters.
3. Prefer names with no letters foreign to Arabic (پ چ ژ گ ک ی ے ٹ ڈ ڑ ں ہ ۃ ھ ە and the Pashto/Kurdish letters).
4. Prefer names with an Arabic-only form (ة ي ك ى).
5. Prefer the spelling shared by the most entries once letter variants are merged. This drops one-off transcriptions and old names (e.g. سناباد for Mashhad).
6. Then unpointed forms; then the shortest.

`persian_place_name()` does the reverse:

1. Avoid Urdu, Pashto and Kurdish letters, and Arabic-only forms (ة ي ك ى أ إ).
2. Prefer the most widely shared spelling (پاریس, not the Urdu پیرس).
3. Normalise ي/ك to ی/ک.

Tested on 24 large cities from geonamescache. The remaining weakness: a Persian spelling made only
of letters shared with Arabic (تهران) can win the Arabic choice. This is why the override table
exists.

## Test result

`python tests/test_content.py`: 12/12 tests pass. For 1447 AH on the tabular stand-in calendar,
with all options on:

- Sunni: 62 entries (32 of them white-day fasts), linking to 19 distinct histories.
- Shia: 61 entries, linking to 38 distinct histories.

The tests check:

- every `Holiday.key` exists in `H`, and `key_for(name)` gives the same key;
- every Arabic string is non-empty and in Arabic script;
- the kinds, the sort order, and that dates round-trip through the calendar;
- the branch-specific days and the option switches;
- that missing days are skipped;
- the solar festivals (with convertdate.persian);
- the popover HTML;
- that the stand-in stays within 2 days of Umm al-Qura (hijri-converter) for four dates.
