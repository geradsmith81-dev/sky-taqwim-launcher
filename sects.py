"""
Schools, branches and movements of Islam, and the calendars by which each fixes its months.

Each entry gives the calendars a community uses, with a preset of the app's settings that models its
practice (tradition for the holy days, calendar, where the crescent is looked for and by which rule,
prayer method). Practice varies inside every group and changes over time; the presets are models, and the
notes say whose practice they follow. Where a group is a political or militant movement rather than a
school of law, that is said plainly and no calendar of its own is implied.

Sources: news reports, rulings and official pages named for each entry were read when this list was made
(November 2026); the general reference works (Encyclopaedia of Islam entries, Lauziere 2016, Musa 2008,
Reingold and Dershowitz) are cited as standard background and were not checked page by page.

Calendar keys (calendars.py): ummalqura, sighting, unified, tabular, solar, ahmadi, julian.
Preset keys: branch ("sunni"|"shia"), calendar, ref ("Mecca", "local", or a sighting_calendar preset
place name), crit (sighting_calendar.CRITERIA key), tabular ("kuwaiti"|"fatimid"), method
(prayer_times.METHODS key), asr ("standard"|"hanafi"), imams (bool, Shia only).
"""
from __future__ import annotations

GROUPS = [("Sunni", "أهل السنة"), ("Shia", "الشيعة"), ("Other branches and movements", "فرق وحركات أخرى")]

SECTS = [
    # ------------------------------------------------------------------------------------------ Sunni
    {"key": "hanafi", "name": "Hanafi", "ar": "الحنفية", "group": "Sunni",
     "where": "Turkey, the Balkans, Central and South Asia, the Levant, Egypt (with the Shafi'i school)",
     "how": "The school's classical position (Ibn Abidin, Radd al-muhtar) is that a sighting anywhere binds all "
            "who hear of it; many later Hanafi jurists let distant lands follow their own sighting. In practice "
            "each state decides: Turkey's Diyanet publishes the Unified Hijri Calendar in advance, while Pakistan, "
            "India and Bangladesh announce from naked-eye sightings, and many Hanafis in the Gulf follow Saudi "
            "announcements.",
     "uses": [("unified", "Turkey (Diyanet)", {"branch": "sunni", "calendar": "unified", "method": "diyanet", "asr": "hanafi"}),
              ("sighting", "South Asia: national naked-eye sighting", {"branch": "sunni", "calendar": "sighting", "ref": "Karachi", "crit": "yallop_B", "method": "karachi", "asr": "hanafi"}),
              ("sighting", "Classical: the first sighting anywhere (modelled from Mecca)", {"branch": "sunni", "calendar": "sighting", "ref": "Mecca", "crit": "yallop_B", "asr": "hanafi"})],
     "src": "Ibn Abidin, Radd al-muhtar, Kitab al-Sawm; Diyanet bulletin 'Beginning of the month of Ramadan 1447 AH' (2026)"},
    {"key": "deobandi", "name": "Deobandi", "ar": "الديوبندية", "group": "Sunni", "parent": "Hanafi",
     "where": "Pakistan, India, Bangladesh, Afghanistan, and their diasporas",
     "how": "A Hanafi reform movement (Darul Uloom Deoband, 1866). Months begin by naked-eye sighting. In Pakistan "
            "the Central Ruet-e-Hilal Committee announces for the country, and since the Ruet-e-Hilal Act 2023 only "
            "it may do so; before that the Masjid Qasim Ali Khan in Peshawar often announced a day earlier. In "
            "Britain some follow local sighting, others Saudi Arabia.",
     "uses": [("sighting", "Pakistan: Central Ruet-e-Hilal Committee", {"branch": "sunni", "calendar": "sighting", "ref": "Karachi", "crit": "yallop_B", "method": "karachi", "asr": "hanafi"})],
     "src": "Pakistan Ruet-i-Hilal Act 2023 (Dawn, 2026); Dawn, '190 years of controversy: the Qasim Ali mosque' (2015)"},
    {"key": "taliban", "name": "Taliban", "ar": "طالبان", "group": "Sunni", "parent": "Deobandi",
     "where": "Afghanistan",
     "how": "A Deobandi-derived political and militant movement, not a school of law. Its government made the lunar "
            "Hijri calendar the official calendar of Afghanistan in 2022, in place of the solar Hijri calendar used "
            "since 1922; religious months are declared from sightings in Afghanistan. The solar Hijri calendar "
            "remains in everyday use.",
     "uses": [("sighting", "Afghanistan: lunar Hijri, local sighting", {"branch": "sunni", "calendar": "sighting", "ref": "Kabul", "crit": "yallop_B", "method": "karachi", "asr": "hanafi"}),
              ("solar", "Solar Hijri, the civil calendar before 2022 and still widely used", {"branch": "sunni", "calendar": "solar"})],
     "src": "Hasht-e Subh (8am.media), 26 March 2022; Afghanistan Analysts Network translation of decrees (2023)"},
    {"key": "barelvi", "name": "Barelvi", "ar": "البريلوية", "group": "Sunni", "parent": "Hanafi",
     "where": "Pakistan, India, Bangladesh, Britain",
     "how": "A Hanafi and Sufi-inclined movement named after Ahmad Raza Khan of Bareilly (d. 1921). It keeps the "
            "Mawlid and the death anniversaries ('urs) of saints by their Hijri dates. Months begin by naked-eye "
            "sighting; the Barelvi scholar Mufti Muneeb-ur-Rehman long chaired Pakistan's Central Ruet-e-Hilal "
            "Committee.",
     "uses": [("sighting", "Pakistan and India: national naked-eye sighting", {"branch": "sunni", "calendar": "sighting", "ref": "Karachi", "crit": "yallop_B", "method": "karachi", "asr": "hanafi"})],
     "src": "Wikipedia, 'Muneeb-ur-Rehman' and 'Ruet-e-Hilal Committee'"},
    {"key": "shafii", "name": "Shafi'i", "ar": "الشافعية", "group": "Sunni",
     "where": "Indonesia, Malaysia, Brunei, Singapore, East Africa, Yemen, Egypt, Kurdistan",
     "how": "The school holds that each region follows its own sighting, because horizons differ (the report of "
            "Kurayb, Sahih Muslim 1087). Brunei, Indonesia, Malaysia and Singapore (MABIMS) since 2021 begin a month "
            "when the Moon is at least 3 degrees high and 6.4 degrees from the Sun at sunset, confirmed where "
            "possible by sighting. Indonesia's Muhammadiyah adopted the Unified Hijri Calendar in 2025.",
     "uses": [("sighting", "South-East Asia: Neo-MABIMS (Indonesia's Ministry of Religious Affairs, JAKIM)", {"branch": "sunni", "calendar": "sighting", "ref": "Jakarta", "crit": "mabims", "method": "singapore"}),
              ("sighting", "Classical: local sighting on your own horizon", {"branch": "sunni", "calendar": "sighting", "ref": "local", "crit": "yallop_B"}),
              ("unified", "Muhammadiyah (Indonesia), from 1446 AH", {"branch": "sunni", "calendar": "unified", "method": "singapore"})],
     "src": "Sahih Muslim 1087; MABIMS decision of 8 Dec 2021 (Kemenag); Muhammadiyah, 'The Unified Global Hijri Calendar' (2025)"},
    {"key": "maliki", "name": "Maliki", "ar": "المالكية", "group": "Sunni",
     "where": "North and West Africa, Upper Egypt, Sudan, Kuwait, Bahrain",
     "how": "Malik held that a sighting binds those who learn of it; some Maliki authorities favour local sighting. "
            "Morocco's Ministry of Habous and Islamic Affairs announces from naked-eye sightings in Morocco, "
            "often a day after Saudi Arabia.",
     "uses": [("sighting", "Morocco: national naked-eye sighting", {"branch": "sunni", "calendar": "sighting", "ref": "Rabat", "crit": "yallop_B", "method": "mwl"})],
     "src": "Sohail Hanif, 'Why can't we unite? A brief overview of moon-sighting wars', SeekersGuidance (2022)"},
    {"key": "hanbali", "name": "Hanbali", "ar": "الحنابلة", "group": "Sunni",
     "where": "Saudi Arabia, Qatar",
     "how": "The school holds that a sighting anywhere binds all. Saudi Arabia keeps the Umm al-Qura calendar for "
            "civil purposes; its Supreme Court declares Ramadan, Shawwal and Dhu al-Hijjah from testimony of "
            "sightings by eye or binoculars, which can fall a day from the Umm al-Qura date.",
     "uses": [("ummalqura", "Saudi civil calendar (Umm al-Qura)", {"branch": "sunni", "calendar": "ummalqura", "method": "umm_al_qura"}),
              ("sighting", "Saudi religious months: sighting from Mecca", {"branch": "sunni", "calendar": "sighting", "ref": "Mecca", "crit": "yallop_B", "method": "umm_al_qura"})],
     "src": "Gulf News, Saudi Supreme Court call to sight the Shawwal moon (2024); van Gent, 'The Umm al-Qura calendar of Saudi Arabia'"},
    {"key": "salafi", "name": "Wahhabi / Salafi", "ar": "الوهابية / السلفية", "group": "Sunni",
     "where": "Saudi Arabia, the Gulf, and worldwide",
     "how": "A reform current within Sunni Islam, Hanbali in Saudi Arabia (the name Wahhabi is mostly used by "
            "others). It follows the Saudi practice of sighting; many Salafis abroad follow Saudi announcements, "
            "others their local sighting. Many Salafi scholars do not keep the Mawlid or the night of mid-Sha'ban "
            "as festivals.",
     "uses": [("ummalqura", "Saudi civil calendar (Umm al-Qura)", {"branch": "sunni", "calendar": "ummalqura", "method": "umm_al_qura"}),
              ("sighting", "Following Saudi sighting (modelled from Mecca)", {"branch": "sunni", "calendar": "sighting", "ref": "Mecca", "crit": "yallop_B", "method": "umm_al_qura"})],
     "src": "H. Lauzière, The Making of Salafism (Columbia UP, 2016); IslamQA, 'How is Eid determined?'"},
    {"key": "salafi_jihadi", "name": "Salafist jihadism", "ar": "السلفية الجهادية", "group": "Sunni", "parent": "Wahhabi / Salafi",
     "where": "—",
     "how": "A militant political movement, not a school of law or a community with a calendar of its own. Shown "
            "because it appears on the chart; it is not modelled.",
     "uses": [], "src": "—"},
    # ------------------------------------------------------------------------------------------ Shia
    {"key": "twelver", "name": "Twelvers (Ithna 'Ashari, Ja'fari)", "ar": "الاثنا عشرية", "group": "Shia",
     "where": "Iran, Iraq, Bahrain, Azerbaijan, Lebanon, Pakistan, India, the Gulf",
     "how": "Months begin by an actual sighting on the local horizon, valid for places that share it; calculation "
            "alone is not accepted. Ayatollah Sistani requires the naked eye (Islamic Laws, ruling 1699); "
            "Ayatollah Khamenei accepts sighting through a telescope. Iran's civil calendar is the solar Hijri "
            "calendar.",
     "uses": [("sighting", "Naked eye on the local horizon (Ayatollah Sistani)", {"branch": "shia", "calendar": "sighting", "ref": "local", "crit": "yallop_B", "method": "jafari", "imams": True}),
              ("sighting", "Optical aid accepted (Ayatollah Khamenei)", {"branch": "shia", "calendar": "sighting", "ref": "local", "crit": "odeh_C", "method": "tehran", "imams": True}),
              ("solar", "Iran's civil calendar (solar Hijri)", {"branch": "shia", "calendar": "solar", "method": "tehran", "imams": True})],
     "src": "sistani.org, Islamic Laws, ruling 1699; Khamenei's answer on sighting with instruments (Shafaqna)"},
    {"key": "alawite", "name": "Alawites (Nusayris)", "ar": "العلويون (النصيرية)", "group": "Shia", "parent": "Twelvers",
     "where": "Syria (the coastal mountains), Lebanon, southern Turkey (Hatay)",
     "how": "Alawite religious life combines lunar feasts (Eid al-Fitr, Eid al-Adha, Ghadir, Ashura) with feasts of "
            "Christian and Persian origin, such as Christmas (Laylat al-Milad), Nawruz and Mihrajan. The Nusayri "
            "solar calendar, with the Syriac month names, fixes Nawruz on 4 Nisan and Mihrajan on 16 Tishrin "
            "al-Awwal. The lunar months follow the sighting announced in Syria.",
     "uses": [("sighting", "Lunar feasts: sighting in Syria", {"branch": "shia", "calendar": "sighting", "ref": "Damascus", "crit": "yallop_B", "imams": True}),
              ("julian", "Solar feasts kept by the Julian reckoning", {"branch": "shia", "calendar": "julian", "imams": True})],
     "src": "Y. Friedman, The Nusayri-Alawis (Brill, 2010), ch. 2, the Nusayri holidays and calendar (Nawruz on 4 Nisan, Mihrajan on 16 Tishrin al-Awwal); H. Halm, 'Nusayriyya', Encyclopaedia of Islam, 2nd ed."},
    {"key": "ismaili", "name": "Isma'ilis", "ar": "الإسماعيلية", "group": "Shia",
     "where": "Nizaris: Pakistan, India, Central Asia, East Africa, Syria, diaspora; Tayyibi Musta'lis (Dawoodi Bohras): India, Pakistan, Yemen",
     "how": "The Dawoodi Bohras keep the Fatimid tabular calendar, which fixes every month in advance, so their "
            "dates often come a day or two earlier than the sighting calendars'. The Nizaris, led by the Aga Khan, mark Eid al-Fitr "
            "traditionally by the sighting of the new moon.",
     "uses": [("tabular", "Dawoodi Bohra: Fatimid (Misri) tabular calendar", {"branch": "shia", "calendar": "tabular", "tabular": "fatimid", "imams": False}),
              ("sighting", "Nizari: sighting of the new moon", {"branch": "shia", "calendar": "sighting", "ref": "local", "crit": "yallop_B", "imams": False})],
     "src": "Reingold and Dershowitz, Calendrical Calculations; the.ismaili, 'Eid al-Fitr' (2024)"},
    {"key": "alevi", "name": "Alevi-Bektashi", "ar": "العلوية البكتاشية", "group": "Shia",
     "where": "Turkey, the Balkans, and the Turkish and Kurdish diaspora in Europe",
     "how": "Alevis keep the twelve-day Muharram fast (Muharrem orucu) for the martyrs of Karbala, from 1 Muharram, "
            "with the Masum-u Pak and Fatma Ana fasts before it, and Ashura; their published calendars follow "
            "Turkey's calculated Hijri dates. Hidirellez falls on 23 April by the Julian reckoning (6 May), and "
            "Nevruz on 21 March is kept as the birthday of Ali.",
     "uses": [("unified", "Muharram fast and lunar days: Turkey's calendar (Diyanet)", {"branch": "shia", "calendar": "unified", "imams": True}),
              ("julian", "Hidirellez and other days by the Julian reckoning", {"branch": "shia", "calendar": "julian", "imams": True})],
     "src": "Alevi calendars 2026-2028 (alevitakvimi.com); Wikipedia, 'Hidirellez'"},
    {"key": "zaidi", "name": "Zaydis", "ar": "الزيدية", "group": "Shia",
     "where": "Northern Yemen",
     "how": "Zaydi Shia (Fivers) begin months by sighting; in Yemen the religious authorities in Sanaa announce "
            "Ramadan and the Eids from local sightings. They keep Ghadir and Ashura but not the later Twelver "
            "Imams' days.",
     "uses": [("sighting", "Yemen: local sighting (Sanaa)", {"branch": "shia", "calendar": "sighting", "ref": "Sanaa", "crit": "yallop_B", "imams": False})],
     "src": "Amman Message (2005) on the Zaydi school; Encyclopaedia of Islam, 2nd ed., 'Zaydiyya'"},
    # ------------------------------------------------------------------------------------------ others
    {"key": "ibadi", "name": "Ibadis", "ar": "الإباضية", "group": "Other branches and movements",
     "where": "Oman, Mzab (Algeria), Jerba (Tunisia), Jabal Nafusa (Libya), Zanzibar",
     "how": "The one living branch descended from the early Kharijite movement, though Ibadis reject that name. "
            "Oman's Ministry of Endowments and Religious Affairs announces months from local naked-eye sighting "
            "and often begins Ramadan or Eid a day after Saudi Arabia.",
     "uses": [("sighting", "Oman: local naked-eye sighting (Muscat)", {"branch": "sunni", "calendar": "sighting", "ref": "Muscat", "crit": "yallop_B", "method": "gulf"})],
     "src": "Muscat Daily (2026); Geo News (2025); Middle East Eye (2026)"},
    {"key": "kharijite", "name": "Kharijites", "ar": "الخوارج", "group": "Other branches and movements",
     "where": "Historical (7th-10th centuries)",
     "how": "The early movement that broke with Ali after the arbitration of Siffin (37 AH / 657). No community "
            "of that name survives except the Ibadis, who reject it; nothing is modelled separately.",
     "uses": [], "src": "Encyclopaedia of Islam, 2nd ed., 'Khāridjites'"},
    {"key": "ahmadi", "name": "Ahmadiyya", "ar": "الأحمدية", "group": "Other branches and movements",
     "where": "Pakistan, India, West Africa, Indonesia, and worldwide (headquarters in Britain)",
     "how": "Months begin when the crescent can be seen with the naked eye in perfect conditions on one's own "
            "horizon, worked out by calculation and confirmed by sighting; where a government committee announces, "
            "Ahmadis follow it. The community also dates its affairs by its own Hijri Shamsi solar calendar (1940).",
     "uses": [("sighting", "Naked-eye visibility on your horizon, by calculation", {"branch": "sunni", "calendar": "sighting", "ref": "local", "crit": "yallop_B"}),
              ("ahmadi", "Hijri Shamsi (Ahmadiyya solar calendar)", {"branch": "sunni", "calendar": "ahmadi"})],
     "src": "Al Hakam, 'Why do Eid and Ramadan start on different dates' (2021); The Review of Religions, July 2008"},
    {"key": "quranist", "name": "Quranists", "ar": "القرآنيون", "group": "Other branches and movements",
     "where": "Small, scattered groups and individuals",
     "how": "Those who take the Qur'an as the only source reject the hadith that set the sighting rule, and have "
            "no common authority. Most keep the lunar months by sighting; some count from the astronomical new "
            "moon; a minority argue for a solar or lunisolar Ramadan, which others reject on the strength of "
            "Qur'an 9:36-37.",
     "uses": [("sighting", "Lunar months by local sighting", {"branch": "sunni", "calendar": "sighting", "ref": "local", "crit": "yallop_B"}),
              ("sighting", "Months from the astronomical new moon", {"branch": "sunni", "calendar": "sighting", "ref": "local", "crit": "conjunction"})],
     "src": "Qur'an 2:189, 9:36-37; A. Y. Musa, Hadith as Scripture (Palgrave, 2008)"},
    {"key": "sufi", "name": "Sufis", "ar": "الصوفية", "group": "Other branches and movements",
     "where": "Within Sunni and Shia Islam everywhere",
     "how": "Sufism is a mystical path within both branches, not a separate sect; Sufi orders follow the calendar "
            "of their community and add the Mawlid and the death anniversaries ('urs) of their saints by Hijri "
            "dates.",
     "uses": [], "src": "Encyclopaedia of Islam, 2nd ed., 'Tasawwuf'"},
]

# the calendars, in the order the page lists them, with a short description
CAL_ORDER = [
    ("ummalqura", "Umm al-Qura (Saudi Arabia)"),
    ("sighting", "Crescent sighting (local, national or from Mecca)"),
    ("unified", "Unified Hijri Calendar (Istanbul 2016)"),
    ("tabular", "Tabular (arithmetic)"),
    ("solar", "Solar Hijri (Iran, Afghanistan)"),
    ("ahmadi", "Hijri Shamsi (Ahmadiyya)"),
    ("julian", "Julian (Eastern / Rumi)"),
]


def by_calendar() -> dict[str, list[tuple[dict, str, dict]]]:
    out = {k: [] for k, _ in CAL_ORDER}
    for s in SECTS:
        for cal, label, preset in s["uses"]:
            out.setdefault(cal, []).append((s, label, preset))
    return out
