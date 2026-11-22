"""Short histories of the holy days, opened by clicking a holiday's name.

Each entry: title, Arabic title, a few sentences of history, and the main sources. Qur'an
references are sura:verse. Hadith numbers follow the common numbering of the collections (the
Fath al-Bari numbering for al-Bukhari, the Abd al-Baqi numbering for Muslim). Where Sunni and Shia
accounts differ, each is given in its own terms. Where an archaeological link is debated, the text
says so.
"""
from __future__ import annotations

import html

H = {
    # ------------------------------------------------------------------ the calendar itself
    "hijri_new_year": ("Hijri New Year", "رأس السنة الهجرية",
        "The Islamic era counts years from the Hijra, the Prophet's emigration from Mecca to Medina in "
        "622 CE. According to al-Tabari, the caliph Umar ibn al-Khattab adopted the era in 16 or 17 AH "
        "(637–638) after consulting the Companions, and the year was made to start with Muharram. "
        "Al-Bukhari reports that they counted neither from the Prophet's mission nor from his death, but "
        "from his arrival in Medina. The era is attested within a few years. The papyrus PERF 558 from "
        "Herakleopolis in Egypt, a Greek–Arabic receipt for 65 sheep, is dated Jumada al-Ula of the year "
        "22 (April 643). A rock inscription at Qa' al-Mu'tadil near al-'Ula was written by one Zuhayr 'at "
        "the time Umar died, in the year 24' (644–645). The mosaic inscription inside the Dome of the "
        "Rock in Jerusalem gives the year 72 (691–692).",
        "Qur'an 9:36; al-Bukhari, Sahih, Manaqib al-Ansar (no. 3934); al-Tabari, Ta'rikh, year 16 AH; "
        "A. Grohmann, From the World of Arabic Papyri (Cairo 1952) 113–15 (PERF 558); A. I. al-Ghabban and "
        "R. Hoyland, Arabian Archaeology and Epigraphy 19 (2008) 210–237 (Zuhayr); C. Kessler, Journal of "
        "the Royal Asiatic Society 1970, 2–14 (Dome of the Rock)"),
    "lunar_year": ("The lunar year and the end of intercalation", "السنة القمرية والنسيء",
        "The Islamic year has twelve lunar months and 354 or 355 days, so it moves back through the solar "
        "seasons about every 33 years. The Qur'an says that the number of months with God is twelve, four "
        "of them sacred, and condemns the nasi', the 'postponement' practised before Islam. At the Farewell "
        "Pilgrimage of 10 AH the Prophet announced that time had come round again to its form on the day "
        "God created the heavens and the earth. What the nasi' was is debated. Al-Biruni and many modern "
        "scholars read it as adding a month to keep the year in step with the seasons; others see a "
        "shifting of the sacred months. Since then no month is added, so Ramadan and the Hajj pass through "
        "every season in a lifetime.",
        "Qur'an 9:36–37; al-Bukhari, Sahih, Tafsir Surat al-Tawba (no. 4662); al-Biruni, al-Athar "
        "al-baqiya (tr. E. Sachau, The Chronology of Ancient Nations, 1879); Encyclopaedia of Islam, 2nd "
        "ed., 'Nasī''"),
    "sacred_months": ("The four sacred months", "الأشهر الحرم",
        "The Qur'an names four of the twelve months as sacred (hurum), when fighting is forbidden. The "
        "Prophet's sermon at the Farewell Pilgrimage names them: Dhu al-Qa'dah, Dhu al-Hijjah and "
        "Muharram, one after another, and 'Rajab of Mudar, between Jumada and Sha'ban'. The truce is "
        "older than Islam: it let the tribes travel safely to the markets and to the pilgrimage at Mecca. "
        "Jurists later differed on whether the ban on fighting still binds, but the months keep a special "
        "standing in Sunni and Shia devotion. Rajab, which stands alone, was called al-Fard, 'the single "
        "one', and al-Asamm, 'the deaf', because no clash of arms was heard in it.",
        "Qur'an 2:194, 2:217, 9:2, 9:36; al-Bukhari, Sahih (no. 4662); Ibn Hisham, al-Sira al-nabawiyya"),
    "hilal": ("The crescent and the new month", "رؤية الهلال",
        "An Islamic month begins with the first sighting of the new crescent (hilal) after sunset. The "
        "Qur'an calls the crescents 'times appointed for people and for the pilgrimage'. The hadith says: "
        "'Fast when you see it and break the fast when you see it; if it is hidden from you, complete "
        "thirty days.' Whether a sighting holds everywhere or only where the horizon is shared (ikhtilaf "
        "al-matali') was asked early: in a report in Muslim, Ibn Abbas in Medina did not follow the "
        "sighting made in Syria. The Sunni schools and Ja'fari Shia jurists differ on this and on the use "
        "of calculation. Saudi Arabia's Umm al-Qura calendar is computed in advance for civil use; since "
        "1423 AH (2002) a month starts if the Moon sets after the Sun at Mecca on the evening after "
        "conjunction, while Ramadan and the Eids follow sightings accepted by the Supreme Court. Modern "
        "astronomers such as Yallop and Odeh have published criteria for when a crescent can be seen.",
        "Qur'an 2:185, 2:189; al-Bukhari, Sahih (no. 1909); Muslim, Sahih (nos. 1081, 1087); B. D. Yallop, "
        "NAO Technical Note 69 (1997); M. Sh. Odeh, Experimental Astronomy 18 (2004) 39–64; R. H. van Gent, "
        "'The Umm al-Qura calendar of Saudi Arabia' (Utrecht University, web page)"),
    "jumuah": ("Friday, al-Jumu'ah", "يوم الجمعة",
        "Friday, al-Jumu'ah ('the gathering'), is the day of the congregational noon prayer. It replaces "
        "the Dhuhr prayer and includes a sermon (khutba). The Qur'an tells believers to hurry to the "
        "remembrance of God when the call is made on Friday and to leave trade, and afterwards to go out "
        "and seek God's bounty, so Friday was not at first a day of rest. A hadith in Muslim calls it the "
        "best day on which the sun rises, the day Adam was created. Shia jurists long debated whether the "
        "Friday prayer is required while the twelfth Imam is in Occultation; today it is held widely, and "
        "in Iran as an official institution. Friday is the weekly holiday in most of the Middle East, so "
        "the app's month grid ends on Friday.",
        "Qur'an 62:9–11; Muslim, Sahih, Kitab al-Jumu'a (no. 854); al-Bukhari, Sahih, Kitab al-Jumu'a"),

    # ------------------------------------------------------------------ Ramadan and Shawwal
    "ramadan": ("Ramadan", "شهر رمضان",
        "The fast of Ramadan was prescribed in the second year after the Hijra (624 CE). The Qur'an calls "
        "Ramadan the month in which the Qur'an was sent down, and sets the fast from the moment the white "
        "thread of dawn can be told from the black until nightfall. The battle of Badr was fought on 17 "
        "Ramadan 2 AH. In Sunni practice the night prayer, tarawih, is prayed in congregation; al-Bukhari "
        "traces this to Umar gathering the people behind one reciter. Shia practice keeps the extra night "
        "prayers of Ramadan individually, and in Ja'fari law the fast ends a little after sunset, when the "
        "redness of the eastern sky has gone. Both traditions begin and end the month with the crescent.",
        "Qur'an 2:183–187; al-Bukhari, Sahih (nos. 1909, 2010); Muslim, Sahih (no. 1081); Ibn Hisham, "
        "al-Sira (Badr); al-Hurr al-'Amili, Wasa'il al-Shi'a, Kitab al-Sawm"),
    "last_ten": ("The last ten nights of Ramadan", "العشر الأواخر",
        "Aisha reports that when the last ten nights of Ramadan began, the Prophet worshipped through the "
        "night, woke his family and 'tightened his waist-wrapper'. He spent these days in retreat "
        "(i'tikaf) in the mosque. Laylat al-Qadr is sought among these nights. I'tikaf in the last ten days "
        "is still widely kept, including in the two Holy Mosques of Mecca and Medina. Shia practice also "
        "values i'tikaf, and in Iran it is kept above all in the white days of Rajab (13–15).",
        "al-Bukhari, Sahih, Fadl Laylat al-Qadr (no. 2024) and Kitab al-I'tikaf; Muslim, Sahih, Kitab "
        "al-I'tikaf; al-Kulayni, al-Kafi, Kitab al-Siyam"),
    "laylat_al_qadr": ("Laylat al-Qadr", "ليلة القدر",
        "Sura 97 of the Qur'an calls the Night of Decree 'better than a thousand months'. It is the night "
        "on which the Qur'an was sent down and the angels and the Spirit descend. The Qur'an does not give "
        "its date. In Sunni hadith the Prophet told his Companions to seek it in the odd nights of the last "
        "ten of Ramadan. Ubayy ibn Ka'b held that it is the 27th, and that night is the most widely kept, "
        "often with the whole Qur'an completed in the prayers. In Shia tradition reports from the Imams "
        "point to the nights of the 19th, 21st and 23rd, with the 23rd most emphasised. They are kept as "
        "nights of vigil (ihya'), with the long prayer al-Jawshan al-Kabir and the Qur'an held over the "
        "head; the 19th and 21st also mourn Imam Ali.",
        "Qur'an 97; 44:3–4; 2:185; al-Bukhari, Sahih (no. 2017); Muslim, Sahih (no. 762); al-Kulayni, "
        "al-Kafi, Kitab al-Siyam; Abbas Qummi, Mafatih al-jinan"),
    "eid_al_fitr": ("Eid al-Fitr", "عيد الفطر",
        "The 'feast of breaking the fast' on 1 Shawwal ends Ramadan. Before the Eid prayer each household "
        "pays zakat al-fitr, a measure of staple food or its value, for the poor. Anas ibn Malik reports "
        "that the people of Medina had two days of festivity when the Prophet arrived, and that he told "
        "them God had given them two better days, the Fitr and the Adha. The Eid prayer is held in the "
        "morning, often in an open prayer ground, followed by visits, new clothes and sweets. Because the "
        "date depends on the crescent, the Eid can fall on different days in neighbouring countries. "
        "Fasting on the day of Eid is forbidden in Sunni and Shia law.",
        "al-Bukhari, Sahih, Kitab al-Zakat (no. 1503) and Kitab al-'Idayn; Abu Dawud, Sunan (no. 1134); "
        "al-Hurr al-'Amili, Wasa'il al-Shi'a"),
    "six_shawwal": ("Six days of Shawwal", "صيام ست من شوال",
        "A hadith of Abu Ayyub al-Ansari in Muslim says that whoever fasts Ramadan and follows it with six "
        "days of Shawwal is as if he had fasted the whole year. Scholars explain this by the tenfold reward: "
        "36 days count as 360. The days may be fasted together or apart, from 2 Shawwal on, since fasting "
        "on the Eid is forbidden. The Shafi'i and Hanbali schools recommend the fast. Malik ibn Anas is "
        "reported in the Muwatta' to have disliked it, lest people think it part of Ramadan, though many "
        "later Maliki scholars accepted it.",
        "Muslim, Sahih, Kitab al-Siyam (no. 1164); Malik, al-Muwatta', Kitab al-Siyam; al-Nawawi, Sharh "
        "Sahih Muslim"),
    "white_days": ("The white days", "الأيام البيض",
        "The 'white days' (al-ayyam al-bid) are the 13th, 14th and 15th of each lunar month, when the moon "
        "is full or nearly full and the nights are bright. Hadith in al-Tirmidhi and al-Nasa'i report that "
        "the Prophet told Abu Dharr to fast these three days. Fasting three days a month is compared to "
        "fasting all year, since each good deed counts tenfold. It is a common voluntary fast in Sunni "
        "practice. Shia tradition also recommends three fast days a month, and the white days of Rajab are "
        "kept with i'tikaf. The 13th of Dhu al-Hijjah is a Day of Tashriq, when fasting is forbidden, so "
        "the app does not mark it.",
        "al-Tirmidhi, Jami' (no. 761); al-Nasa'i, Sunan, Kitab al-Siyam; al-Bukhari, Sahih, Kitab al-Sawm "
        "(fasting three days a month); al-Kulayni, al-Kafi, Kitab al-Siyam"),

    # ------------------------------------------------------------------ Hajj and Eid al-Adha
    "first_ten": ("The first ten days of Dhu al-Hijjah", "العشر الأوائل من ذي الحجة",
        "The first ten days of Dhu al-Hijjah are among the most honoured of the year. Many commentators "
        "read the Qur'an's oath 'by the ten nights' as these days. A hadith in al-Bukhari says no good "
        "deeds are dearer to God than those done in them. Many Muslims fast the first nine days, or at "
        "least the Day of Arafah. Following a hadith of Umm Salama in Muslim, many Sunnis who will offer a "
        "sacrifice leave their hair and nails uncut until it is made. Shia reports also place the marriage "
        "of Ali and Fatima in these days.",
        "Qur'an 89:1–2, 22:28; al-Bukhari, Sahih (no. 969); Muslim, Sahih, Kitab al-Adahi (no. 1977); "
        "al-Tusi, Misbah al-mutahajjid"),
    "hajj": ("The Hajj", "الحج",
        "The Hajj, the pilgrimage to Mecca in Dhu al-Hijjah, is required once in a lifetime of every adult "
        "Muslim who is able to make it. The Qur'an traces its rites to Abraham and Ishmael, who raised the "
        "foundations of the Kaaba. Its form follows the Prophet's Farewell Pilgrimage of 10 AH, described "
        "step by step by Jabir ibn Abd Allah. On the 8th, the Day of Tarwiyah ('watering', when pilgrims "
        "once took on water), pilgrims go to Mina. On the 9th they stand at Arafat. On the 10th they stone "
        "the pillar of Aqaba, sacrifice and cut their hair, and on the following days stone the three "
        "pillars at Mina. Shia memory adds that on 8 Dhu al-Hijjah 60 AH Imam Husayn left Mecca for Iraq.",
        "Qur'an 2:125–127, 2:196–203, 3:96–97, 22:26–29; Muslim, Sahih, Kitab al-Hajj (no. 1218, the "
        "hadith of Jabir); al-Tabari, Ta'rikh, year 60 AH"),
    "arafah": ("The Day of Arafah", "يوم عرفة",
        "On 9 Dhu al-Hijjah the pilgrims stand (wuquf) on the plain of Arafat east of Mecca from noon to "
        "sunset; a hadith says 'the Hajj is Arafah'. Here the Prophet gave his Farewell Sermon in 10 AH. "
        "Sunni reports, from Umar in al-Bukhari, place the verse 'Today I have perfected your religion for "
        "you' (5:3) on this day; Shia tradition places it at Ghadir Khumm. For those not on pilgrimage "
        "Sunni tradition strongly recommends the fast: Muslim reports that it expiates the sins of the year "
        "before and the year after. Shia jurists also count the fast as recommended unless it would weaken "
        "one for the day's prayers, and the day's great supplication is the Du'a 'Arafa of Imam Husayn.",
        "Qur'an 2:198–199, 5:3; al-Bukhari, Sahih (no. 45); Muslim, Sahih (nos. 1162, 1218); al-Tirmidhi, "
        "Jami' (no. 889); Abbas Qummi, Mafatih al-jinan"),
    "eid_al_adha": ("Eid al-Adha", "عيد الأضحى",
        "The 'feast of sacrifice' on 10 Dhu al-Hijjah recalls Abraham's readiness to sacrifice his son and "
        "the ram given in his place, told in sura 37. Pilgrims sacrifice at Mina. Muslims everywhere who "
        "can afford it offer a sheep, goat, cow or camel (udhiya), and share the meat with family, "
        "neighbours and the poor. The Qur'an says that neither the flesh nor the blood reaches God, but the "
        "devotion of those who offer it. Most Muslim tradition names the son as Ishmael; some early "
        "authorities, al-Tabari among them, said Isaac. It is the larger of the two feasts: Kurban Bayramı "
        "in Turkish, Eid-e Qorban in Persian.",
        "Qur'an 37:99–111, 22:34–37; al-Bukhari, Sahih, Kitab al-Adahi; al-Tabari, Ta'rikh (Abraham)"),
    "tashriq": ("The Days of Tashriq", "أيام التشريق",
        "The three days after Eid al-Adha (11–13 Dhu al-Hijjah) are the Days of Tashriq. The name is "
        "usually explained by the drying of sacrificial meat in the sun. The Qur'an tells the pilgrims to "
        "remember God 'in the counted days' and lets those in a hurry leave Mina after two. Each day the "
        "pilgrims stone the three pillars (jamarat), recalling Abraham's rejection of Satan. A hadith in "
        "Muslim calls them days of eating, drinking and remembrance of God, and fasting is forbidden on "
        "them. Sunni and Shia practice both add special takbirs after the prayers of these days.",
        "Qur'an 2:200–203; Muslim, Sahih (no. 1141); Ibn Manzur, Lisan al-'Arab (sh-r-q)"),

    # ------------------------------------------------------------------ Muharram and Safar
    "ashura": ("Ashura", "عاشوراء",
        "Ashura, the tenth of Muharram, was a fast day before the Ramadan fast was prescribed; Aisha says "
        "Quraysh fasted it before Islam. Ibn Abbas reports that in Medina the Prophet found the Jews "
        "fasting on it in memory of God saving Moses from Pharaoh, and he fasted it and told others to "
        "fast. After Ramadan was prescribed the fast became voluntary; a hadith in Muslim says it expiates "
        "the year before. The Prophet said that if he lived to the next year he would fast the ninth as "
        "well, so Sunnis commonly fast the 9th and 10th, or the 10th and 11th. Ashura is also the "
        "anniversary of the killing of the Prophet's grandson al-Husayn at Karbala in 61 AH (680 CE), "
        "mourned above all by the Shia.",
        "al-Bukhari, Sahih, Kitab al-Sawm (nos. 2002, 2004); Muslim, Sahih, Kitab al-Siyam (nos. 1130, "
        "1134, 1162)"),
    "ashura_karbala": ("Ashura and Karbala", "عاشوراء وكربلاء",
        "On 10 Muharram 61 AH (10 October 680) al-Husayn, son of Ali and Fatima and grandson of the "
        "Prophet, was killed at Karbala in Iraq with some seventy companions and members of his family. "
        "He had refused allegiance to the Umayyad caliph Yazid and set out for Kufa at the call of its "
        "people; the army of Kufa's governor, Ubayd Allah ibn Ziyad, stopped him by the Euphrates. For "
        "Shia Muslims Ashura is the central day of mourning: majalis retell the events, processions mourn, "
        "and in Iran the ta'ziyeh passion play is performed. The genre of mourning recitation, rawda-khwani, "
        "is named after Husayn Va'iz Kashifi's Rawdat al-shuhada' (c. 1502). The Buyid ruler Mu'izz "
        "al-Dawla ordered public mourning in Baghdad on Ashura 352 AH (963 CE). Husayn's shrine at Karbala "
        "is among the most visited places in the Muslim world.",
        "al-Tabari, Ta'rikh, year 61 AH (from Abu Mikhnaf); al-Mufid, al-Irshad; Ibn al-Athir, al-Kamil, "
        "year 352 AH; Kashifi, Rawdat al-shuhada'; Encyclopaedia Iranica, 'ʿĀšūrā''"),
    "tasua": ("Tasu'a", "تاسوعاء",
        "Tasu'a, the ninth of Muharram, is the eve of the battle of Karbala. Shia tradition, from the early "
        "account of Abu Mikhnaf preserved by al-Tabari, holds that on the afternoon of the 9th the army of "
        "Umar ibn Sa'd advanced, and al-Husayn asked for one night's delay to spend in prayer. The day is "
        "dedicated to al-Abbas ibn Ali, Husayn's half-brother and standard-bearer, who was killed on Ashura "
        "trying to bring water from the Euphrates. In Iran and Iraq it is a public day of mourning with "
        "processions. In Sunni practice the 9th is a recommended fast joined to Ashura.",
        "al-Tabari, Ta'rikh, year 61 AH; al-Mufid, al-Irshad; Muslim, Sahih (no. 1134)"),
    "arbain": ("Arba'in", "الأربعين",
        "Arba'in, 'the fortieth', falls on 20 Safar, forty days after Ashura, following the custom of "
        "marking the fortieth day after a death. Shia tradition holds that the Companion Jabir ibn Abd "
        "Allah al-Ansari came to Karbala on this day in 61 AH to visit Husayn's grave. Some reports add "
        "that the women of Husayn's family, returning from captivity, reached Karbala on the same day. A "
        "saying of Imam al-Hasan al-Askari counts the Arba'in ziyara among the signs of a believer. Since "
        "2003 the walk to Karbala, much of it from Najaf about 80 km away, has become one of the largest "
        "annual gatherings in the world, with pilgrims fed and housed free in roadside stations (mawakib).",
        "al-Tusi, Tahdhib al-ahkam, Kitab al-Mazar; al-Tusi, Misbah al-mutahajjid; Ibn Tawus, al-Luhuf"),
    "prophet_death": ("The death of the Prophet", "وفاة النبي",
        "The Prophet died in Medina in 11 AH (June 632) in Aisha's room, where he was buried; the place is "
        "now inside his mosque. Sunni sources, following Ibn Ishaq, give Monday 12 Rabi' al-Awwal, the "
        "same date as his birth; others give the 1st or 2nd of that month. Shia scholars such as al-Mufid "
        "and al-Tusi give 28 Safar, and in Iran that day is a public day of mourning. Iran joins to it the "
        "martyrdom of Imam al-Hasan; Iraqi Shia also mark Imam Hasan on 7 Safar, following another report. "
        "In Sunni practice the Prophet's death is not kept as a separate observance.",
        "Ibn Hisham, al-Sira al-nabawiyya; al-Bukhari, Sahih, Kitab al-Maghazi (the Prophet's illness and "
        "death); al-Tabari, Ta'rikh, year 11 AH; al-Mufid, Masar al-Shi'a; al-Tusi, Tahdhib al-ahkam"),

    # ------------------------------------------------------------------ the Prophet
    "mawlid": ("Mawlid al-Nabi", "المولد النبوي",
        "The Prophet was born in Mecca in Rabi' al-Awwal of the Year of the Elephant, about 570 CE. Ibn "
        "Ishaq gives Monday 12 Rabi' al-Awwal, the date kept by most Sunnis. Al-Kulayni also gives the "
        "12th, but al-Mufid and al-Tusi give the 17th, the date kept by Twelver Shia. Public celebration "
        "is first recorded at the Fatimid court in Cairo, described by al-Maqrizi. It spread in the Sunni "
        "world after Muzaffar al-Din Gökböri, ruler of Irbil (d. 630/1233), held great yearly mawlids, "
        "described by Ibn Khallikan. Scholars have long debated it: al-Suyuti defended it as a good "
        "innovation; Ibn Taymiyya criticised it, and many Salafi scholars today do not keep it. Since the "
        "1980s Iran has marked the days from the 12th to the 17th as Islamic Unity Week.",
        "Ibn Hisham, al-Sira al-nabawiyya; al-Kulayni, al-Kafi, Kitab al-Hujja; al-Mufid, Masar al-Shi'a; "
        "al-Maqrizi, al-Khitat; Ibn Khallikan, Wafayat al-a'yan (Kukburi); al-Suyuti, Husn al-maqsid fi "
        "'amal al-mawlid; N. J. G. Kaptein, Muhammad's Birthday Festival (Leiden 1993)"),
    "isra_miraj": ("al-Isra' wa'l-Mi'raj", "الإسراء والمعراج",
        "Sura 17 opens with God taking His servant by night from the Sacred Mosque to 'the furthest "
        "mosque' (al-masjid al-aqsa), and sura 53 describes a vision 'at the lote tree of the boundary'. "
        "Hadith in al-Bukhari and Muslim tell of the Night Journey on the mount Buraq to Jerusalem and the "
        "Ascension (Mi'raj) through the seven heavens, where the five daily prayers were prescribed. Its "
        "date is uncertain: early reports place it in different months, from about one to five years "
        "before the Hijra, and Ibn Hajar lists many opinions. 27 Rajab became the most widely kept date; in "
        "Turkey it is Miraç Kandili. The Dome of the Rock (72 AH) stands over the rock later linked with the "
        "Ascension, but its own mosaic inscriptions do not mention the Night Journey, and scholars debate "
        "how early the link was made.",
        "Qur'an 17:1, 53:1–18; al-Bukhari, Sahih (no. 3887); Muslim, Sahih, Kitab al-Iman (no. 162); Ibn "
        "Hisham, al-Sira; Ibn Hajar, Fath al-bari; O. Grabar, The Shape of the Holy (Princeton 1996)"),
    "mabath": ("al-Mab'ath", "المبعث النبوي",
        "Al-Mab'ath, 'the sending', marks the start of Muhammad's prophethood, when the first verses of sura "
        "96, 'Recite in the name of your Lord', came to him in the cave of Hira near Mecca, about 610 CE. "
        "Aisha's account in al-Bukhari tells of the angel's command and of the Prophet returning, trembling, "
        "to Khadija. Twelver Shia tradition, through reports from the Imams in al-Kafi, dates this to 27 "
        "Rajab, and it is a public holiday in Iran. Most Sunni scholars place the first revelation in "
        "Ramadan, linking it with Laylat al-Qadr, and keep 27 Rajab as the night of the Isra' and Mi'raj.",
        "Qur'an 96:1–5, 2:185, 97:1; al-Bukhari, Sahih, Bad' al-wahy (no. 3); al-Kulayni, al-Kafi; al-Tusi, "
        "Misbah al-mutahajjid"),

    # ------------------------------------------------------------------ nights
    "nisf_shaban": ("The night of mid-Sha'ban", "ليلة النصف من شعبان",
        "The night of mid-Sha'ban (14–15 Sha'ban) is called Laylat al-Bara'a, 'the night of release', and "
        "Shab-e Barat in South Asia. Hadith in al-Tirmidhi and Ibn Majah say that God looks upon His "
        "creation on this night and forgives all but a few; Aisha tells of finding the Prophet praying at "
        "the cemetery of al-Baqi'. Hadith scholars differ on how strong these reports are, and a minority "
        "of commentators read the 'blessed night' of Qur'an 44:3 as this night rather than Laylat al-Qadr. "
        "It is kept with prayer, Qur'an reading and visits to graves in much of the Sunni world (Berat "
        "Kandili in Turkey), while many Salafi scholars do not single it out. For the Shia it is also the "
        "birthday of the twelfth Imam, and a night of vigil with the ziyara of Imam Husayn.",
        "Qur'an 44:3–4; al-Tirmidhi, Jami' (no. 739); Ibn Majah, Sunan (nos. 1388–1390); Abbas Qummi, "
        "Mafatih al-jinan"),
    "raghaib": ("Laylat al-Raghaib", "ليلة الرغائب",
        "Laylat al-Raghaib, 'the night of wishes', is the eve of the first Friday of Rajab, after a fast on "
        "the first Thursday of the month. A special prayer for this night is described in al-Ghazali's "
        "Ihya'. In 7th/13th-century Damascus Izz al-Din ibn Abd al-Salam attacked it as an innovation while "
        "Ibn al-Salah defended it, and al-Nawawi later called the prayer a blameworthy innovation. It is "
        "still widely kept in Turkey and the Balkans as Regaip Kandili, one of the five kandil nights. In "
        "Shia devotion the night and its prayer are given in Ibn Tawus's Iqbal al-a'mal and in Abbas "
        "Qummi's Mafatih al-jinan.",
        "al-Ghazali, Ihya' 'ulum al-din, Kitab asrar al-salat; al-Nawawi, al-Majmu'; Ibn Tawus, Iqbal "
        "al-a'mal; Abbas Qummi, Mafatih al-jinan"),

    # ------------------------------------------------------------------ Ghadir and Mubahala
    "ghadir": ("Ghadir Khumm", "غدير خم",
        "On 18 Dhu al-Hijjah 10 AH, returning from the Farewell Pilgrimage, the Prophet halted at the pool "
        "(ghadir) of Khumm between Mecca and Medina. Hadith in both Sunni and Shia collections report that "
        "he took Ali's hand and said, 'Whoever's mawla I am, Ali is his mawla.' Muslim records his words "
        "there about the 'two weighty things', the Book of God and his family. Sunni scholars accept many "
        "versions of the hadith and read mawla as 'friend' or 'ally', a statement of Ali's merit. Shia "
        "tradition holds that here the Prophet appointed Ali as his successor and that Qur'an 5:3 was "
        "revealed on this day; al-Amini's al-Ghadir gathers the reports. The Buyid ruler Mu'izz al-Dawla "
        "made the day a public festival in Baghdad in 352 AH (963 CE).",
        "Muslim, Sahih, Fada'il al-Sahaba (no. 2408); Ahmad ibn Hanbal, al-Musnad (hadith of Zayd ibn Arqam "
        "and of al-Bara' ibn 'Azib); al-Tirmidhi, Jami' (no. 3713); Ibn Majah, Sunan (no. 116); al-Kulayni, "
        "al-Kafi; 'A. H. al-Amini, al-Ghadir; Ibn al-Athir, al-Kamil, year 352 AH; Encyclopaedia of Islam, "
        "2nd ed., 'Ghadīr Khumm' (L. Veccia Vaglieri)"),
    "mubahala": ("The Mubahala", "المباهلة",
        "In 10 AH (some say 9) a delegation of Christians from Najran in southern Arabia came to Medina and "
        "debated with the Prophet about Jesus. Qur'an 3:61 then told him to invite them to a mutual curse "
        "(mubahala), calling 'our sons and your sons, our women and your women, ourselves and yourselves'. "
        "Muslim reports from Sa'd ibn Abi Waqqas that when the verse came the Prophet called Ali, Fatima, "
        "Hasan and Husayn and said, 'O God, these are my family.' The Christians declined the ordeal and "
        "made a treaty instead. Shia tradition keeps the day, 24 Dhu al-Hijjah in most reports, as a proof "
        "of the standing of the Ahl al-Bayt.",
        "Qur'an 3:59–63; Muslim, Sahih, Fada'il al-Sahaba (no. 2404); Ibn Hisham, al-Sira (the Najran "
        "delegation); al-Tusi, Misbah al-mutahajjid"),

    # ------------------------------------------------------------------ the family of the Prophet and the Imams
    "fatima": ("Fatima al-Zahra", "فاطمة الزهراء",
        "Fatima, daughter of the Prophet and Khadija, wife of Ali and mother of Hasan and Husayn, is "
        "honoured by all Muslims. Al-Bukhari reports the Prophet saying 'Fatima is a part of me' and "
        "calling her the chief of the women of Paradise. Shia tradition dates her birth to 20 Jumada "
        "al-Akhirah, five years after the start of the Prophet's mission, and calls her al-Zahra', 'the "
        "radiant'. Sunni sources such as Ibn Sa'd more often place her birth some years before the mission. "
        "In Iran her birthday is Mothers' Day and Women's Day.",
        "al-Bukhari, Sahih (nos. 3624, 3714); Ibn Sa'd, al-Tabaqat al-kubra; al-Kulayni, al-Kafi; al-Mufid, "
        "Masar al-Shi'a; Encyclopaedia of Islam, 2nd ed., 'Fāṭima' (L. Veccia Vaglieri)"),
    "fatimiyya": ("The Fatimiyya", "الفاطمية",
        "Fatima died in Medina in 11 AH (632), a short time after the Prophet. The reports differ on how "
        "long she outlived him. A report in al-Kafi gives 75 days, pointing to 13 Jumada al-Ula; other Shia "
        "reports give 95 days, pointing to 3 Jumada al-Akhirah. Sunni sources, citing Aisha in al-Bukhari, "
        "give about six months. Shia Muslims therefore keep two periods of mourning, the Fatimiyya, and Iran "
        "observes 3 Jumada al-Akhirah as a public day of mourning. Shia tradition holds that she died of "
        "injuries suffered in the dispute after the Prophet's death; Sunni sources describe an illness. She "
        "was buried at night at her wish, and the place of her grave is not known.",
        "al-Bukhari, Sahih, Kitab al-Maghazi (nos. 4240–4241); al-Kulayni, al-Kafi, Kitab al-Hujja; al-Tabari, "
        "Ta'rikh, year 11 AH; Encyclopaedia of Islam, 2nd ed., 'Fāṭima'"),
    "imam_ali": ("Imam Ali", "الإمام علي",
        "Ali ibn Abi Talib, the Prophet's cousin and son-in-law, was among the first to accept Islam. Shia "
        "tradition, and some Sunni authors such as al-Hakim al-Nishapuri, say he was born inside the Kaaba; "
        "the Shia date is 13 Rajab, about 600 CE. For Sunnis he is the fourth caliph (35–40 AH); for the "
        "Shia he is the first Imam. While leading the dawn prayer in the mosque of Kufa on 19 Ramadan 40 AH "
        "(661) he was struck with a poisoned sword by the Kharijite Abd al-Rahman ibn Muljam, and died two "
        "days later. His shrine at Najaf became a great centre of Shia learning. The sermons and letters "
        "attributed to him were collected by al-Sharif al-Radi as Nahj al-balagha.",
        "al-Mufid, al-Irshad; al-Tabari, Ta'rikh, year 40 AH; al-Hakim, al-Mustadrak; al-Sharif al-Radi, Nahj "
        "al-balagha; Encyclopaedia of Islam, 2nd ed., ''Alī b. Abī Ṭālib' (L. Veccia Vaglieri)"),
    "imam_hasan": ("Imam Hasan", "الإمام الحسن",
        "Al-Hasan ibn Ali, the Prophet's elder grandson, was born in Medina on 15 Ramadan 3 AH (625). Hadith "
        "in both traditions call him and his brother 'the lords of the youth of Paradise'. After his "
        "father's death he was acknowledged as caliph in Kufa, but within months he made peace with "
        "Mu'awiya. Sunni sources see the peace as fulfilling the Prophet's words that through him God would "
        "reconcile two great parties of Muslims. He died in Medina in 49 or 50 AH; Shia sources, and some "
        "Sunni ones, say he was poisoned. He is buried at al-Baqi' and is the second Imam, al-Mujtaba, 'the "
        "chosen'.",
        "al-Bukhari, Sahih (no. 2704); al-Tirmidhi, Jami' (no. 3768); al-Mufid, al-Irshad; al-Tabari, Ta'rikh; "
        "Encyclopaedia of Islam, 2nd ed., '(al-)Ḥasan b. 'Alī' (L. Veccia Vaglieri)"),
    "imam_husayn": ("Imam Husayn", "الإمام الحسين",
        "Al-Husayn ibn Ali, younger son of Ali and Fatima, was born in Medina in Sha'ban 4 AH (626). The "
        "Iranian calendar and al-Tusi give 3 Sha'ban; al-Mufid's al-Irshad gives the 5th. Hadith in both "
        "traditions tell of the Prophet's love for his two grandsons. His death at Karbala in 61 AH is "
        "mourned on Ashura. His birthday opens three days of celebration in early Sha'ban: Husayn on the "
        "3rd, his half-brother al-Abbas on the 4th and his son Ali Zayn al-Abidin on the 5th.",
        "al-Mufid, al-Irshad; al-Tusi, Misbah al-mutahajjid; al-Tirmidhi, Jami', Kitab al-Manaqib"),
    "al_sajjad": ("Imam al-Sajjad", "الإمام السجاد",
        "Ali ibn al-Husayn, the fourth Imam, is called Zayn al-Abidin, 'ornament of the worshippers', and "
        "al-Sajjad, 'the one who prostrates'. He survived Karbala because he was too ill to fight. He lived "
        "on in Medina devoted to prayer; the supplications of al-Sahifa al-Sajjadiyya are attributed to him. "
        "Sunni scholars such as al-Zuhri praised his learning and piety. He died in 94 or 95 AH (713–714) "
        "and is buried at al-Baqi'. The Iranian calendar keeps his birth on 5 Sha'ban and his death on 25 "
        "Muharram; other reports give 12 or 18 Muharram.",
        "al-Mufid, al-Irshad; al-Sahifa al-Sajjadiyya; Ibn Sa'd, al-Tabaqat al-kubra"),
    "al_baqir": ("Imam al-Baqir", "الإمام الباقر",
        "Muhammad ibn Ali al-Baqir, the fifth Imam, was born in Medina in 57 AH and was a small child at "
        "Karbala. His title comes from baqir al-'ilm, 'the one who splits knowledge open'. He taught in "
        "Medina, and many of the legal and Qur'anic reports in the Shia collections go back to him and to "
        "his son Ja'far. Sunni hadith collections also transmit from him. He died in Medina, the year being "
        "given as 114 to 118 AH, and is buried at al-Baqi'. The Iranian calendar keeps his birth on 1 Rajab "
        "and his death on 7 Dhu al-Hijjah.",
        "al-Mufid, al-Irshad; al-Kulayni, al-Kafi; Encyclopaedia Iranica, 'Bāqer, Abū Jaʿfar Moḥammad' "
        "(W. Madelung)"),
    "jafar_sadiq": ("Imam Ja'far al-Sadiq", "الإمام جعفر الصادق",
        "Ja'far al-Sadiq (83–148 AH, 702–765 CE), great-grandson of al-Husayn, was the sixth Imam and one of "
        "the most respected scholars of Medina. Under the late Umayyads and early Abbasids he taught a large "
        "circle, and the Ja'fari school of Shia law is named after him. Sunni scholars respect him as a "
        "transmitter of hadith: Malik ibn Anas relates from him, and Abu Hanifa is reported to have studied "
        "with him. He died in Medina in Shawwal 148; Shia sources say he was poisoned on the order of the "
        "caliph al-Mansur. In the Shia reckoning he was born on 17 Rabi' al-Awwal, the Prophet's birthday. "
        "He is buried at al-Baqi'.",
        "al-Mufid, al-Irshad; al-Kulayni, al-Kafi; Malik, al-Muwatta'; Encyclopaedia Iranica, 'Jaʿfar "
        "al-Ṣādeq'"),
    "al_kazim": ("Imam al-Kazim", "الإمام الكاظم",
        "Musa ibn Ja'far al-Kazim, 'the one who restrains his anger', the seventh Imam, was born in 128 AH "
        "at al-Abwa' between Mecca and Medina. The Abbasid caliph Harun al-Rashid had him arrested and held "
        "in Basra and then Baghdad. He died in prison in Baghdad in 183 AH (799); Shia sources say he was "
        "poisoned. His shrine, shared with his grandson al-Jawad, is at al-Kazimiyya in Baghdad. The Iranian "
        "calendar keeps his birth on 7 Safar and his death on 25 Rajab.",
        "al-Mufid, al-Irshad; al-Kulayni, al-Kafi; al-Tabari, Ta'rikh, year 183 AH; Encyclopaedia of Islam, "
        "2nd ed., 'Mūsā al-Kāẓim'"),
    "al_rida": ("Imam al-Rida", "الإمام الرضا",
        "Ali ibn Musa al-Rida, the eighth Imam, was born in Medina in 148 AH; the Iranian calendar keeps 11 "
        "Dhu al-Qa'dah. In 201 AH the caliph al-Ma'mun called him to Khurasan and named him heir to the "
        "caliphate, a step that shocked the Abbasid family in Baghdad. He died at Tus in 203 AH (818). Shia "
        "sources hold that al-Ma'mun had him poisoned; other historians report a sudden illness. He was "
        "buried beside the grave of Harun al-Rashid, and the village of Sanabad grew into Mashhad, 'the "
        "place of martyrdom', now Iran's second city and its greatest shrine. Iran marks his death on the "
        "last day of Safar; other reports give 17 Safar or 23 Dhu al-Qa'dah.",
        "al-Mufid, al-Irshad; Ibn Babawayh, 'Uyun akhbar al-Rida; al-Tabari, Ta'rikh, years 201–203 AH; "
        "Encyclopaedia Iranica, 'ʿAlī al-Reżā' (W. Madelung)"),
    "al_jawad": ("Imam al-Jawad", "الإمام الجواد",
        "Muhammad ibn Ali al-Jawad, also called al-Taqi, the ninth Imam, was born in Medina in 195 AH. He "
        "became Imam at about seven, on his father's death, and Shia sources tell of the scholars of "
        "Baghdad testing the boy. The caliph al-Ma'mun married him to his daughter Umm al-Fadl. He died in "
        "Baghdad in 220 AH (835), aged about 25, and is buried beside his grandfather at al-Kazimiyya. The "
        "Iranian calendar keeps his birth on 10 Rajab and his death on the last day of Dhu al-Qa'dah.",
        "al-Mufid, al-Irshad; al-Kulayni, al-Kafi; al-Mas'udi, Muruj al-dhahab"),
    "al_hadi": ("Imam al-Hadi", "الإمام الهادي",
        "Ali ibn Muhammad al-Hadi, also called al-Naqi, the tenth Imam, was born near Medina in 212 AH. "
        "Al-Kulayni, al-Mufid and al-Tusi give the middle of Dhu al-Hijjah, and the 15th is kept; some "
        "reports give 2 or 5 Rajab. The caliph al-Mutawakkil brought him to the garrison city of Samarra, "
        "where he and his son lived under watch in the military quarter (al-'Askar). He died there in Rajab "
        "254 AH (868); 3 Rajab is kept, though some sources give late Jumada al-Akhirah. The shrine of the "
        "two 'Askari Imams in Samarra was badly damaged by bombings in 2006 and 2007 and has since been "
        "rebuilt.",
        "al-Kulayni, al-Kafi; al-Mufid, al-Irshad; al-Tusi, Misbah al-mutahajjid; al-Mas'udi, Muruj al-dhahab"),
    "al_askari": ("Imam al-Askari", "الإمام العسكري",
        "Al-Hasan ibn Ali al-Askari, the eleventh Imam, was born in Medina in 232 AH and spent most of his "
        "life confined in Samarra, which gives him his title. He kept in touch with his followers largely "
        "through agents and letters. He died on 8 Rabi' al-Awwal 260 AH (874), aged about 28, and was "
        "buried beside his father. Twelver Shia hold that his young son Muhammad, the twelfth Imam, then "
        "went into Occultation. The Iranian calendar keeps his birth on 8 Rabi' al-Thani; other reports "
        "give 10 Rabi' al-Thani.",
        "al-Kulayni, al-Kafi; al-Mufid, al-Irshad; Encyclopaedia Iranica, 'ʿAskarī, Abū Moḥammad Ḥasan'"),
    "mahdi": ("Imam al-Mahdi", "الإمام المهدي",
        "Twelver Shia hold that Muhammad ibn al-Hasan, son of the eleventh Imam, was born in Samarra on 15 "
        "Sha'ban 255 AH (869). After his father's death in 260 AH he entered the Minor Occultation, speaking "
        "through four deputies in turn. In 329 AH the Major Occultation began, which continues; he is "
        "awaited as al-Mahdi and al-Qa'im, who will fill the earth with justice. His birthday is a festival "
        "of lights and charity, and in Iran many visit the Jamkaran mosque near Qom. The 9th of Rabi' "
        "al-Awwal, the day after his father's death, is kept as the start of his Imamate. Sunni hadith "
        "collections such as Abu Dawud's also speak of a Mahdi from the Prophet's family, but most Sunnis do "
        "not identify him with the twelfth Imam.",
        "al-Kulayni, al-Kafi, Kitab al-Hujja; al-Mufid, al-Irshad; Ibn Babawayh, Kamal al-din; Abu Dawud, "
        "Sunan, Kitab al-Mahdi; Encyclopaedia of Islam, 2nd ed., 'al-Mahdī' (W. Madelung)"),
    "zaynab": ("Zaynab bint Ali", "السيدة زينب",
        "Zaynab, daughter of Ali and Fatima, was at Karbala with her brother Husayn. Taken captive to Kufa "
        "and Damascus with the women and children, she is remembered for her speeches before the governor "
        "Ibn Ziyad and the caliph Yazid. Her shrine at al-Sayyida Zaynab, south of Damascus, is a major "
        "place of Shia pilgrimage. A mosque in Cairo also bears her name and is much loved by Egyptian "
        "Sunnis and Sufis. The Iranian calendar keeps her birth on 5 Jumada al-Ula, which is also Nurses' "
        "Day in Iran.",
        "al-Tabari, Ta'rikh, year 61 AH; Ibn Abi Tahir Tayfur, Balaghat al-nisa'; al-Mufid, al-Irshad"),
    "abbas": ("al-Abbas ibn Ali", "أبو الفضل العباس",
        "Al-Abbas, son of Ali and Umm al-Banin, was Husayn's half-brother and his standard-bearer at "
        "Karbala. Shia tradition calls him Abu al-Fadl and al-Saqqa', 'the water-carrier': he was killed on "
        "Ashura trying to bring water from the Euphrates to the thirsty camp. His shrine faces Husayn's at "
        "Karbala, across the open space called Bayn al-Haramayn. The Iranian calendar keeps his birth on 4 "
        "Sha'ban.",
        "al-Tabari, Ta'rikh, year 61 AH; al-Mufid, al-Irshad; Abu al-Faraj al-Isfahani, Maqatil al-Talibiyyin"),

    # ------------------------------------------------------------------ the Iranian solar year
    "nowruz": ("Nowruz", "نوروز",
        "Nowruz, 'new day', is the Iranian New Year at the spring equinox, 1 Farvardin of the solar Hijri "
        "calendar. It is very old, but its earliest history is uncertain. The idea that the Persepolis "
        "reliefs of gift-bearers show an Achaemenid New Year ceremony was proposed in the 20th century and "
        "is debated; other archaeologists, such as M. C. Root, read the reliefs as an image of empire with "
        "no fixed festival. Middle Persian and early Islamic texts describe the feast fully, and al-Biruni "
        "records its customs in the 11th century. The Jalali calendar of the Seljuk sultan Malik-Shah "
        "(1079), on which Omar Khayyam worked, tied the year to the equinox. Iran's law of 1925 (Farvardin "
        "1304) set the modern solar Hijri calendar. UNESCO inscribed Nowruz in 2009, and the United Nations "
        "declared 21 March the International Day of Nowruz in 2010.",
        "al-Biruni, al-Athar al-baqiya (tr. E. Sachau, 1879); Encyclopaedia Iranica, 'Nowruz'; M. C. Root, "
        "The King and Kingship in Achaemenid Art (Leiden 1979); UNESCO Representative List 2009; UN General "
        "Assembly resolution 64/253 (2010)"),
    "sizdah_bedar": ("Sizdah Bedar", "سیزده‌بدر",
        "Sizdah Bedar, 'thirteen out of doors', on 13 Farvardin ends the Nowruz holidays. Families spend the "
        "day outdoors in parks and the countryside to leave behind the bad luck of the thirteenth. At the "
        "end of the day the sprouted greens (sabzeh) of the New Year table are thrown into running water, "
        "and young unmarried women knot the blades with a wish. Its origins are not well documented. In Iran "
        "it is a public holiday, officially called Nature Day (Ruz-e Tabi'at).",
        "Encyclopaedia Iranica, 'Nowruz'; Iranian official calendar (Institute of Geophysics, University of "
        "Tehran)"),
    "yalda": ("Shab-e Yalda", "شب یلدا",
        "Shab-e Yalda or Shab-e Chelleh is the night between the last day of autumn (30 Azar) and 1 Dey, "
        "the longest night of the year. The word yalda comes from Syriac and means 'birth'; it is usually "
        "connected with Syriac-speaking Christians and the Nativity. Families stay up late with their "
        "elders, eating pomegranates, watermelon and nuts and reading the poems of Hafez, to see the long "
        "night through. Links with ancient sun cults or with Mithra are often claimed but rest on little "
        "direct evidence. UNESCO inscribed Yalda/Chella, for Iran and Afghanistan, in 2022.",
        "al-Biruni, al-Athar al-baqiya; Dehkhoda, Loghatnameh ('Yalda'); UNESCO Representative List 2022 "
        "(Yaldā/Chella)"),
    "chaharshanbe_suri": ("Chaharshanbe Suri", "چهارشنبه‌سوری",
        "Chaharshanbe Suri, 'festive Wednesday', is kept on the evening before the last Wednesday of the "
        "Iranian year. People jump over small bonfires and say, 'My yellowness to you, your redness to me', "
        "giving their pallor to the fire and taking its warmth. Children go from door to door banging "
        "spoons on bowls (qashoq-zani). Scholars link the festival with the pre-Islamic days at the end of "
        "the year when the spirits of the dead were thought to return; its Wednesday timing comes from the "
        "later seven-day week.",
        "Encyclopaedia Iranica, 'Čahāršanba-sūrī'; al-Biruni, al-Athar al-baqiya"),
}

# Name prefixes as holidays.py produces them; longer prefixes first.
_RULES = [
    ("Hijri New Year", "hijri_new_year"),
    ("New month: Muharram", "sacred_months"), ("New month: Rajab", "sacred_months"),
    ("New month: Dhu al-Qa'dah", "sacred_months"), ("New month: Dhu al-Hijjah", "sacred_months"),
    ("New month", "hilal"),
    ("Fast of Tasu'a", "ashura"), ("Fast of Ashura", "ashura"), ("Fast of Arafah", "arafah"),
    ("Tasu'a", "tasua"), ("Ashura: martyrdom", "ashura_karbala"), ("Ashura", "ashura"),
    ("Martyrdom of Imam al-Sajjad", "al_sajjad"), ("Birth of Imam al-Sajjad", "al_sajjad"),
    ("Birth of Imam al-Kazim", "al_kazim"), ("Martyrdom of Imam al-Kazim", "al_kazim"),
    ("Arba'in", "arbain"), ("Death of the Prophet", "prophet_death"),
    ("Martyrdom of Imam al-Rida", "al_rida"), ("Birth of Imam al-Rida", "al_rida"),
    ("Martyrdom of Imam al-Askari", "al_askari"), ("Birth of Imam al-Askari", "al_askari"),
    ("Start of the Imamate of Imam al-Mahdi", "mahdi"), ("Birth of Imam al-Mahdi", "mahdi"),
    ("Mawlid", "mawlid"), ("Birth of Zaynab", "zaynab"), ("Fatimiyya", "fatimiyya"),
    ("Birth of Fatima", "fatima"), ("Birth of Imam al-Baqir", "al_baqir"), ("Martyrdom of Imam al-Baqir", "al_baqir"),
    ("Martyrdom of Imam al-Hadi", "al_hadi"), ("Birth of Imam al-Hadi", "al_hadi"),
    ("Birth of Imam al-Jawad", "al_jawad"), ("Martyrdom of Imam al-Jawad", "al_jawad"),
    ("Birth of Imam Ali", "imam_ali"), ("Imam Ali struck", "imam_ali"), ("Martyrdom of Imam Ali", "imam_ali"),
    ("al-Mab'ath", "mabath"), ("Mab'ath", "mabath"), ("al-Isra'", "isra_miraj"), ("Isra'", "isra_miraj"),
    ("Laylat al-Raghaib", "raghaib"), ("Birth of Imam Husayn", "imam_husayn"), ("Birth of al-Abbas", "abbas"),
    ("Laylat al-Bara'a", "nisf_shaban"), ("Night of mid-Sha'ban", "nisf_shaban"), ("Nisf Sha'ban", "nisf_shaban"),
    ("Ramadan", "ramadan"), ("Birth of Imam Hasan", "imam_hasan"), ("Laylat al-Qadr", "laylat_al_qadr"),
    ("Last ten nights", "last_ten"), ("Eid al-Fitr", "eid_al_fitr"), ("Six days of Shawwal", "six_shawwal"),
    ("Martyrdom of Imam al-Sadiq", "jafar_sadiq"), ("First ten days", "first_ten"),
    ("Day of Tarwiyah", "hajj"), ("Hajj", "hajj"), ("Day of Arafah", "arafah"), ("Eid al-Adha", "eid_al_adha"),
    ("Days of Tashriq", "tashriq"), ("Eid al-Ghadir", "ghadir"), ("Ghadir", "ghadir"),
    ("Day of Mubahala", "mubahala"), ("Mubahala", "mubahala"), ("White days", "white_days"),
    ("Nowruz", "nowruz"), ("Sizdah Bedar", "sizdah_bedar"), ("Shab-e Yalda", "yalda"), ("Yalda", "yalda"),
    ("Chaharshanbe Suri", "chaharshanbe_suri"), ("Friday", "jumuah"), ("Jumu'ah", "jumuah"),
    ("Sacred months", "sacred_months"), ("Lunar year", "lunar_year"),
]


def key_for(name: str) -> str | None:
    """The history entry for a holiday name as holidays.py produces it (or for an H key itself)."""
    if name in H:
        return name
    for prefix, key in _RULES:
        if name.startswith(prefix):
            return key
    return None


# Entries whose original-script title is Persian rather than Arabic.
PERSIAN_TITLES = frozenset({"nowruz", "sizdah_bedar", "yalda", "chaharshanbe_suri"})


def body_html(key: str) -> str:
    title, ar, text, src = H[key]
    lang = "fa" if key in PERSIAN_TITLES else "ar"
    return (f"<div class='tq-pop-title'>{html.escape(title)} <span class='tq-ar' lang='{lang}' dir='rtl'>"
            f"{html.escape(ar)}</span></div><div class='tq-pop-text'>{html.escape(text)}</div>"
            f"<div class='tq-pop-src'>Sources: {html.escape(src)}</div>")


def clickable(key_or_name: str, chip_html: str, align_right: bool = False) -> str:
    """Wrap a holiday chip so that clicking it opens the holiday's history (no JavaScript needed).
    Pass a Holiday.key or a holiday name; an unknown or empty one returns the chip unchanged."""
    key = key_for(key_or_name) if key_or_name else None
    if key is None:
        return chip_html
    cls = "tq-pop tq-pop-r" if align_right else "tq-pop"
    return (f"<details class='{cls}'><summary title='Click for the history of this day'>{chip_html}</summary>"
            f"<div class='tq-popbody'>{body_html(key)}</div></details>")
