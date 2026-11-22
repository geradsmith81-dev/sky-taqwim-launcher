"""Arabic (and Persian) spellings of the proper nouns shown in the app, and small script helpers.

Arabic is given unpointed for the interface. A pointed variant is kept only where it helps a reader
(the month names). Persian script is used for the solar Hijri months and the Iranian festivals.
"""
from __future__ import annotations

import html

# ---- Hijri months (index 0 unused) ----
MONTHS = [
    ("", ""),
    ("Muharram", "محرم"),
    ("Safar", "صفر"),
    ("Rabi' al-Awwal", "ربيع الأول"),
    ("Rabi' al-Thani", "ربيع الثاني"),
    ("Jumada al-Ula", "جمادى الأولى"),
    ("Jumada al-Akhirah", "جمادى الآخرة"),
    ("Rajab", "رجب"),
    ("Sha'ban", "شعبان"),
    ("Ramadan", "رمضان"),
    ("Shawwal", "شوال"),
    ("Dhu al-Qa'dah", "ذو القعدة"),
    ("Dhu al-Hijjah", "ذو الحجة"),
]
MONTHS_POINTED = [
    "", "مُحَرَّم", "صَفَر", "رَبِيع الأَوَّل", "رَبِيع الثَّانِي", "جُمَادَى الأُولَى", "جُمَادَى الآخِرَة",
    "رَجَب", "شَعْبَان", "رَمَضَان", "شَوَّال", "ذُو القَعْدَة", "ذُو الحِجَّة",
]
# Other common forms. The Umm al-Qura calendar writes month 4 as Rabi' al-Akhir.
MONTH_ALT = {
    4: ("Rabi' al-Akhir", "ربيع الآخر"),
    5: ("Jumada al-Awwal", "جمادى الأول"),
    6: ("Jumada al-Thani", "جمادى الثاني"),
}
# Honorific epithets often joined to the month names in letters, sermons and printed calendars.
MONTH_EPITHETS = {
    1: ("Muharram al-Haram", "محرم الحرام"),
    2: ("Safar al-Khayr", "صفر الخير"),
    3: ("Rabi' al-Anwar", "ربيع الأنوار"),
    7: ("Rajab al-Murajjab", "رجب المرجب"),
    8: ("Sha'ban al-Mu'azzam", "شعبان المعظم"),
    9: ("Ramadan al-Mubarak", "رمضان المبارك"),
    10: ("Shawwal al-Mukarram", "شوال المكرم"),
    11: ("Dhu al-Qa'dah al-Haram", "ذو القعدة الحرام"),
    12: ("Dhu al-Hijjah al-Haram", "ذو الحجة الحرام"),
}
# The four sacred months, al-ashhur al-hurum (Qur'an 9:36): Dhu al-Qa'dah, Dhu al-Hijjah, Muharram, Rajab.
SACRED_MONTHS = frozenset({1, 7, 11, 12})
SACRED_MONTHS_TERM = ("the sacred months", "الأشهر الحرم")


def is_sacred_month(m: int) -> bool:
    return m in SACRED_MONTHS


def month_name(m: int, script: str = "en") -> str:
    """'en' transliteration, 'ar' unpointed Arabic, 'ar_pointed'."""
    if script == "ar":
        return MONTHS[m][1]
    if script == "ar_pointed":
        return MONTHS_POINTED[m]
    return MONTHS[m][0]


# ---- solar Hijri months (Iran, since the law of 11 Farvardin 1304 / 31 March 1925) ----
SOLAR_MONTHS = [
    ("", ""),
    ("Farvardin", "فروردین"), ("Ordibehesht", "اردیبهشت"), ("Khordad", "خرداد"),
    ("Tir", "تیر"), ("Mordad", "مرداد"), ("Shahrivar", "شهریور"),
    ("Mehr", "مهر"), ("Aban", "آبان"), ("Azar", "آذر"),
    ("Dey", "دی"), ("Bahman", "بهمن"), ("Esfand", "اسفند"),
]
# Afghanistan uses the same solar year with the zodiac (burj) names, in Dari and in Pashto.
SOLAR_MONTHS_DARI = [
    ("", ""),
    ("Hamal", "حمل"), ("Sawr", "ثور"), ("Jawza", "جوزا"), ("Saratan", "سرطان"),
    ("Asad", "اسد"), ("Sunbula", "سنبله"), ("Mizan", "میزان"), ("Aqrab", "عقرب"),
    ("Qaws", "قوس"), ("Jadi", "جدی"), ("Dalw", "دلو"), ("Hut", "حوت"),
]
SOLAR_MONTHS_PASHTO = [
    ("", ""),
    ("Wray", "وری"), ("Ghwayay", "غویی"), ("Ghargolay", "غبرګولی"), ("Chungakh", "چنګاښ"),
    ("Zmaray", "زمری"), ("Wazhay", "وږی"), ("Tala", "تله"), ("Laram", "لړم"),
    ("Lindai", "لیندۍ"), ("Marghumay", "مرغومی"), ("Salwagha", "سلواغه"), ("Kab", "کب"),
]

# ---- weekdays: date.weekday() order, Monday=0 ... Sunday=6 ----
WEEKDAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
WEEKDAY_TR = ["al-Ithnayn", "al-Thulatha'", "al-Arbi'a'", "al-Khamis", "al-Jumu'ah", "al-Sabt", "al-Ahad"]
WEEKDAY_FA = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]
FRIDAY = 4
# Month grid: Saturday first, as in most of the Middle East; Friday, the weekly holiday, ends the row.
GRID_WEEK_START = 5          # date.weekday() of Saturday
GRID_WEEK = [("Sat", "السبت"), ("Sun", "الأحد"), ("Mon", "الاثنين"), ("Tue", "الثلاثاء"),
             ("Wed", "الأربعاء"), ("Thu", "الخميس"), ("Fri", "الجمعة")]

# ---- the Twelve Imams of the Twelver Shia: (number, short name, full name, Arabic, title, Arabic title) ----
IMAMS = [
    (1, "Imam Ali", "Ali ibn Abi Talib", "علي بن أبي طالب", "al-Murtada", "المرتضى"),
    (2, "Imam Hasan", "al-Hasan ibn Ali", "الحسن بن علي", "al-Mujtaba", "المجتبى"),
    (3, "Imam Husayn", "al-Husayn ibn Ali", "الحسين بن علي", "Sayyid al-Shuhada'", "سيد الشهداء"),
    (4, "Imam al-Sajjad", "Ali ibn al-Husayn Zayn al-Abidin", "علي بن الحسين زين العابدين", "al-Sajjad", "السجاد"),
    (5, "Imam al-Baqir", "Muhammad ibn Ali al-Baqir", "محمد بن علي الباقر", "al-Baqir", "الباقر"),
    (6, "Imam al-Sadiq", "Ja'far ibn Muhammad al-Sadiq", "جعفر بن محمد الصادق", "al-Sadiq", "الصادق"),
    (7, "Imam al-Kazim", "Musa ibn Ja'far al-Kazim", "موسى بن جعفر الكاظم", "al-Kazim", "الكاظم"),
    (8, "Imam al-Rida", "Ali ibn Musa al-Rida", "علي بن موسى الرضا", "al-Rida", "الرضا"),
    (9, "Imam al-Jawad", "Muhammad ibn Ali al-Jawad", "محمد بن علي الجواد", "al-Taqi", "التقي"),
    (10, "Imam al-Hadi", "Ali ibn Muhammad al-Hadi", "علي بن محمد الهادي", "al-Naqi", "النقي"),
    (11, "Imam al-Askari", "al-Hasan ibn Ali al-Askari", "الحسن بن علي العسكري", "al-Askari", "العسكري"),
    (12, "Imam al-Mahdi", "Muhammad ibn al-Hasan al-Mahdi", "محمد بن الحسن المهدي", "al-Qa'im", "القائم"),
]

TERMS = {
    # the app and its calendars
    "Sky Taqwim": "تقويم السماء",
    "Hijri": "هجري", "Hijri calendar": "التقويم الهجري", "Hijra": "الهجرة", "AH": "هـ",
    "Umm al-Qura": "أم القرى", "Umm al-Qura calendar": "تقويم أم القرى",
    "tabular": "الحسابي", "Tabular (hisabi)": "التقويم الهجري الحسابي", "hisabi": "حسابي",
    "crescent sighting": "رؤية الهلال", "Crescent sighting": "رؤية الهلال", "ru'yat al-hilal": "رؤية الهلال",
    "crescent": "الهلال", "new month": "غرة الشهر",
    "solar Hijri": "الهجري الشمسي", "hijri shamsi": "الهجري الشمسي",
    "lunar Hijri": "الهجري القمري", "hijri qamari": "الهجري القمري",
    "Jalali calendar": "التقويم الجلالي",
    # astronomy
    "conjunction": "الاقتران", "al-iqtiran": "الاقتران", "al-muhaq": "المحاق", "dark of the moon": "المحاق",
    "new moon": "الهلال", "full moon": "البدر", "sunset": "غروب الشمس", "moonset": "غروب القمر",
    "lag time": "مكث القمر", "moon age": "عمر القمر", "elongation": "الاستطالة",
    "crescent visibility": "إمكانية رؤية الهلال", "ikhtilaf al-matali'": "اختلاف المطالع",
    "Yallop": "يالوب", "Odeh": "عودة", "equinox": "الاعتدال", "solstice": "الانقلاب",
    # places
    "Mecca": "مكة المكرمة", "Medina": "المدينة المنورة", "Kaaba": "الكعبة", "qibla": "القبلة",
    "Sacred Mosque": "المسجد الحرام", "Prophet's Mosque": "المسجد النبوي",
    "Jerusalem": "القدس", "al-Aqsa Mosque": "المسجد الأقصى", "Dome of the Rock": "قبة الصخرة",
    "Arafat": "عرفات", "Mina": "منى", "Muzdalifah": "مزدلفة", "Hira": "غار حراء",
    "Ghadir Khumm": "غدير خم", "al-Baqi'": "البقيع", "Karbala": "كربلاء", "Najaf": "النجف",
    "Kufa": "الكوفة", "Samarra": "سامراء", "Kazimiyya": "الكاظمية", "Mashhad": "مشهد", "Qom": "قم",
    "Tus": "طوس", "al-'Ula": "العلا", "Herakleopolis": "أهناس", "Najran": "نجران", "Irbil": "أربيل",
    # prayer times
    "Fajr": "الفجر", "Sunrise": "الشروق", "Dhuhr": "الظهر", "Asr": "العصر", "Maghrib": "المغرب",
    "Isha": "العشاء", "Midnight": "منتصف الليل", "imsak": "الإمساك", "Imsak": "الإمساك",
    "suhur": "السحور", "iftar": "الإفطار", "Jumu'ah": "الجمعة", "Friday prayer": "صلاة الجمعة",
    "the five prayers": "الصلوات الخمس", "prayer times": "مواقيت الصلاة", "adhan": "الأذان",
    "dawn angle": "زاوية الفجر", "dusk angle": "زاوية العشاء", "shadow length": "طول الظل",
    "Muslim World League": "رابطة العالم الإسلامي", "Umm al-Qura University": "جامعة أم القرى",
    "Egyptian General Authority of Survey": "الهيئة المصرية العامة للمساحة",
    "University of Islamic Sciences, Karachi": "جامعة العلوم الإسلامية بكراتشي",
    "ISNA": "الجمعية الإسلامية لأمريكا الشمالية", "Diyanet": "رئاسة الشؤون الدينية",
    "Institute of Geophysics, University of Tehran": "معهد الجيوفيزياء بجامعة طهران",
    # traditions and schools of law
    "Sunni": "أهل السنة", "Ahl al-Sunnah": "أهل السنة والجماعة", "Shia": "الشيعة", "Shi'ah": "الشيعة",
    "Twelver": "الإمامية الاثنا عشرية", "the Twelve Imams": "الأئمة الاثنا عشر",
    "Ja'fari": "الجعفري", "Hanafi": "الحنفي", "Shafi'i": "الشافعي", "Maliki": "المالكي", "Hanbali": "الحنبلي",
    "madhhab": "المذهب", "Ahl al-Bayt": "أهل البيت", "Sufi": "صوفي", "Salafi": "سلفي",
    # people
    "the Prophet": "النبي", "Prophet Muhammad": "النبي محمد", "Khadija": "خديجة",
    "Fatima al-Zahra": "فاطمة الزهراء", "Fatima": "فاطمة", "Zaynab": "زينب", "al-Abbas ibn Ali": "العباس بن علي",
    "Abu Bakr": "أبو بكر الصديق", "Umar ibn al-Khattab": "عمر بن الخطاب", "Uthman ibn Affan": "عثمان بن عفان",
    "Ali ibn Abi Talib": "علي بن أبي طالب", "Aisha": "عائشة", "Ibn Abbas": "عبد الله بن عباس",
    "Abu Hurayra": "أبو هريرة", "Ubayy ibn Ka'b": "أبي بن كعب", "Anas ibn Malik": "أنس بن مالك",
    "Jabir ibn Abd Allah al-Ansari": "جابر بن عبد الله الأنصاري", "Zayd ibn Arqam": "زيد بن أرقم",
    "al-Bara' ibn 'Azib": "البراء بن عازب", "Sa'd ibn Abi Waqqas": "سعد بن أبي وقاص",
    "Abu Qatada": "أبو قتادة", "Abu Ayyub al-Ansari": "أبو أيوب الأنصاري", "Abu Dharr": "أبو ذر الغفاري",
    "Umm Salama": "أم سلمة", "Kurayb": "كريب", "Mu'awiya": "معاوية بن أبي سفيان", "Yazid": "يزيد بن معاوية",
    "Muslim ibn Aqil": "مسلم بن عقيل", "Abraham": "إبراهيم", "Ishmael": "إسماعيل", "Moses": "موسى",
    "Abd al-Malik": "عبد الملك بن مروان", "al-Ma'mun": "المأمون", "Harun al-Rashid": "هارون الرشيد",
    "al-Mutawakkil": "المتوكل", "al-Mansur": "المنصور", "Mu'izz al-Dawla": "معز الدولة",
    "Muzaffar al-Din Gökböri": "مظفر الدين كوكبوري",
    # authors and collections
    "Qur'an": "القرآن الكريم", "hadith": "الحديث", "Sunnah": "السنة", "al-Bukhari": "البخاري",
    "Muslim": "مسلم", "Abu Dawud": "أبو داود", "al-Tirmidhi": "الترمذي", "al-Nasa'i": "النسائي",
    "Ibn Majah": "ابن ماجه", "Ahmad ibn Hanbal": "أحمد بن حنبل", "Malik ibn Anas": "مالك بن أنس",
    "Ibn Ishaq": "ابن إسحاق", "Ibn Hisham": "ابن هشام", "al-Tabari": "الطبري", "al-Kulayni": "الكليني",
    "al-Mufid": "الشيخ المفيد", "al-Tusi": "الشيخ الطوسي", "Ibn Babawayh": "ابن بابويه", "Ibn Tawus": "ابن طاووس",
    "al-Biruni": "البيروني", "al-Maqrizi": "المقريزي", "Ibn Khallikan": "ابن خلكان", "Ibn al-Athir": "ابن الأثير",
    "Ibn Hajar": "ابن حجر العسقلاني", "al-Nawawi": "النووي", "al-Suyuti": "السيوطي", "al-Ghazali": "الغزالي",
    "Mafatih al-jinan": "مفاتيح الجنان", "al-Irshad": "الإرشاد", "al-Kafi": "الكافي",
    # observances and practices
    "Hajj": "الحج", "Umrah": "العمرة", "Eid": "العيد", "zakat al-fitr": "زكاة الفطر", "tarawih": "التراويح",
    "i'tikaf": "الاعتكاف", "udhiya": "الأضحية", "white days": "الأيام البيض", "sacred months": "الأشهر الحرم",
    "nasi'": "النسيء", "majlis": "مجلس العزاء", "ziyara": "الزيارة", "ta'ziyeh": "التعزية",
    "Laylat al-Qadr": "ليلة القدر", "Ashura": "عاشوراء", "Arba'in": "الأربعين", "Mawlid": "المولد",
    "khutba": "الخطبة", "takbir": "التكبير", "Occultation": "الغيبة",
    # Persian-calendar festivals (Arabic forms; Persian forms are in TERMS_FA)
    "Nowruz": "النوروز", "Yalda": "ليلة يلدا",
}
# Persian spellings for the solar-calendar terms (use bp()).
TERMS_FA = {
    "Nowruz": "نوروز", "Sizdah Bedar": "سیزده‌بدر", "Shab-e Yalda": "شب یلدا", "Yalda": "یلدا",
    "Chaharshanbe Suri": "چهارشنبه‌سوری", "haft-sin": "هفت‌سین", "solar Hijri": "هجری خورشیدی",
    "hijri shamsi": "هجری شمسی", "Iranian calendar": "گاه‌شماری ایرانی", "Nature Day": "روز طبیعت",
}

# Holiday kinds shared with holidays.py and theme.py.
KIND_EN = {
    "eid": "Eid", "sacred": "Holy day", "fast": "Fast", "night": "Special night", "mourning": "Mourning",
    "birth": "Birth", "month": "New month", "hajj": "Hajj days", "civil": "Solar calendar",
}
KIND_AR = {
    "eid": "عيد", "sacred": "مناسبة دينية", "fast": "صيام", "night": "ليلة مباركة", "mourning": "عزاء",
    "birth": "مولد", "month": "غرة الشهر", "hajj": "أيام الحج", "civil": "مناسبة شمسية",
}

BRANCH_LABEL = {"sunni": ("Sunni", "أهل السنة"), "shia": ("Shia", "الشيعة"), "both": ("Sunni and Shia", "السنة والشيعة")}


def term(en: str) -> str:
    return TERMS.get(en, "")


def bi(en: str, ar: str, cls: str = "tq-ar", lang: str = "ar") -> str:
    """'English <arabic>' as HTML; the Arabic is isolated so it reads right-to-left inside English text."""
    if not ar:
        return html.escape(en)
    return f"{html.escape(en)} <span class='{cls}' lang='{lang}' dir='rtl'>{html.escape(ar)}</span>"


def bt(en: str) -> str:
    """bi() for a term in TERMS."""
    return bi(en, TERMS.get(en, ""))


def bp(en: str) -> str:
    """bi() for a Persian term in TERMS_FA (lang='fa')."""
    return bi(en, TERMS_FA.get(en, ""), lang="fa")


def month_bi(m: int) -> str:
    return bi(*MONTHS[m])


def solar_month_bi(m: int, style: str = "iran") -> str:
    table = {"iran": SOLAR_MONTHS, "dari": SOLAR_MONTHS_DARI, "pashto": SOLAR_MONTHS_PASHTO}[style]
    lang = "ps" if style == "pashto" else "fa"
    return bi(*table[m], lang=lang)


# ---- digits ----
_AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_arabic_digits(n) -> str:
    """Western digits to Arabic-Indic digits (U+0660-0669): 1447 -> '١٤٤٧'."""
    return str(n).translate(_AR_DIGITS)


def to_persian_digits(n) -> str:
    """Western digits to Extended Arabic-Indic (Persian) digits (U+06F0-06F9): 1405 -> '۱۴۰۵'."""
    return str(n).translate(_FA_DIGITS)


def hijri_date_ar(y: int, m: int, d: int) -> str:
    """'١٠ محرم ١٤٤٧ هـ'."""
    return f"{to_arabic_digits(d)} {MONTHS[m][1]} {to_arabic_digits(y)} هـ"


def solar_date_fa(y: int, m: int, d: int) -> str:
    """'۱ فروردین ۱۴۰۵'."""
    return f"{to_persian_digits(d)} {SOLAR_MONTHS[m][1]} {to_persian_digits(y)}"


# ---- choosing a place name from GeoNames alternate names ----
# GeoNames gives alternate names without reliable language tags, so Arabic, Persian, Urdu, Pashto,
# Kurdish and Uyghur forms are mixed together. All use the Arabic script. These letter sets tell
# them apart:
_NON_ARABIC = set("پچژگکیےٹڈڑںہۃھۀەټډړږښګڼۍېڵۆێڕۇۈۋ")    # letters that Arabic itself does not use
_PERSIAN = set("پچژگکی")                                  # Persian letters (also used in Urdu etc.)
_URDU_PASHTO = set("ےٹڈڑںہۃھەټډړږښګڼۍېڵۆێڕۇۈۋ")            # Urdu, Pashto, Kurdish, Uyghur letters not used in Persian
_ARABIC_ONLY = set("ةيكى")                                 # Arabic forms that Persian writes differently
_ARABIC_HAMZA = set("أإ")                                   # rare in Persian spellings of place names
_HARAKAT = {chr(c) for c in range(0x064B, 0x0653)} | {"\u0670"}
_FOLD = str.maketrans({"ی": "ي", "ى": "ي", "ے": "ي", "ک": "ك", "ہ": "ه", "ھ": "ه", "ۀ": "ه",
                       "أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه"})


def _is_arabic_script(a: str) -> bool:
    return bool(a) and any("\u0600" <= c <= "\u06ff" or "\u0750" <= c <= "\u077f" for c in a) \
        and not any("a" <= c.lower() <= "z" for c in a)


def _fold(a: str) -> str:
    """Spelling skeleton: vowel signs removed, letter variants shared by the languages merged."""
    return "".join(c for c in a if c not in _HARAKAT and c != "\u200c").translate(_FOLD)


def _candidates(alternates) -> list[str]:
    return [a.strip() for a in (alternates or []) if _is_arabic_script(a)]


def _persian_raw(cands: list[str]) -> str:
    if not cands:
        return ""
    folded = [_fold(a) for a in cands]

    def score(a):
        bad = sum(c in _URDU_PASHTO for c in a)                 # Urdu/Pashto/Kurdish letters
        arabic = any(c in _ARABIC_ONLY or c in _ARABIC_HAMZA for c in a)   # Arabic-only forms
        support = folded.count(_fold(a))                        # other entries with the same skeleton
        pointed = any(c in _HARAKAT for c in a)
        return (bad, arabic, -support, pointed, len(a))
    return min(cands, key=score)


# Standard Arabic names for cities the app shows often, where the GeoNames heuristic can miss
# (a Persian form, or a name without its article). Keyed by the GeoNames English name.
PLACE_AR = {
    "Mecca": "مكة المكرمة", "Medina": "المدينة المنورة", "Jerusalem": "القدس", "Riyadh": "الرياض",
    "Jeddah": "جدة", "Tehran": "طهران", "Najaf": "النجف", "Karbala": "كربلاء", "Kufa": "الكوفة",
    "Samarra": "سامراء", "Baghdad": "بغداد", "Basrah": "البصرة", "Mosul": "الموصل", "Mashhad": "مشهد",
    "Qom": "قم", "Isfahan": "أصفهان", "Shiraz": "شيراز", "Damascus": "دمشق", "Aleppo": "حلب",
    "Beirut": "بيروت", "Amman": "عمان", "Cairo": "القاهرة", "Alexandria": "الإسكندرية",
    "Khartoum": "الخرطوم", "Tunis": "تونس", "Algiers": "الجزائر", "Rabat": "الرباط",
    "Casablanca": "الدار البيضاء", "Kuwait City": "مدينة الكويت", "Doha": "الدوحة", "Manama": "المنامة",
    "Dubai": "دبي", "Abu Dhabi": "أبو ظبي", "Muscat": "مسقط", "Sanaa": "صنعاء", "Istanbul": "إسطنبول",
}


def arabic_place_name(alternates: list[str], name: str | None = None) -> str:
    """Best Arabic name among GeoNames alternate names.

    GeoNames mixes Arabic, Persian, Urdu, Pashto, Kurdish and Uyghur spellings without language
    tags. Heuristic, in order: keep Arabic-script names with no Latin letters; prefer names with no
    letters that Arabic does not use (پ چ ژ گ ک ی ے ٹ ڈ ڑ ں ہ ۃ ھ ە ...); prefer names with an
    Arabic-only letter form (ة ي ك ى), which marks a name as Arabic rather than Persian; prefer the
    spelling shared by the most entries once letter variants are merged (this drops one-off
    transcriptions and old names); then unpointed; then shortest.
    A Persian form written only with letters common to both languages can still win (تهران rather
    than the Arabic طهران)."""
    if name and name in PLACE_AR:
        return PLACE_AR[name]
    cands = _candidates(alternates)
    if not cands:
        return ""
    folded = [_fold(a) for a in cands]

    def score(a):
        foreign = sum(c in _NON_ARABIC for c in a)
        support = folded.count(_fold(a))
        arabic = any(c in _ARABIC_ONLY for c in a)
        pointed = any(c in _HARAKAT for c in a)
        return (foreign, not arabic, -support, pointed, len(a))
    return min(cands, key=score)


def normalise_persian(s: str) -> str:
    """Arabic ي ى ك written as the Persian letters ی ی ک."""
    return s.replace("ي", "ی").replace("ى", "ی").replace("ك", "ک")


def persian_place_name(alternates: list[str]) -> str:
    """Best Persian name among GeoNames alternate names: avoid Urdu/Pashto/Kurdish letters
    (ے ٹ ڈ ڑ ں ہ ھ ۃ ټ ...) and Arabic-only forms (ة ي ك ى أ إ); prefer the spelling shared by the
    most entries once letter variants are merged (پاریس ~ پاريس beats the Urdu پیرس); unpointed;
    shortest. The result is normalised to Persian ی and ک."""
    return normalise_persian(_persian_raw(_candidates(alternates)))


def is_rtl_text(s: str) -> bool:
    """True if `s` is non-empty and all its letters are Arabic-script (used by the tests)."""
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(
        "\u0600" <= c <= "\u06ff" or "\u0750" <= c <= "\u077f" or "\ufb50" <= c <= "\ufdff"
        or "\ufe70" <= c <= "\ufeff" for c in letters)
