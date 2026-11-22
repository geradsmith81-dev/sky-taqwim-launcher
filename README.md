# Sky Taqwim · تقويم السماء

The Islamic calendar for **Sunni or Shia** practice, from NASA JPL astronomy (DE440s via Skyfield).

- **A Sunni / Shia switch** sets the holy days, the default calendar and sighting rule, and the prayer-time methods.
- **Seven calendars:**
  - **Umm al-Qura · أم القرى**, the official Saudi calendar. It uses the published table for 1343–1500 AH and the current rule computed from JPL elsewhere. It matches the table in 932 of 936 months since 1423 AH.
  - **Crescent sighting · رؤية الهلال**. Months begin after the evening on which the crescent passes the chosen rule, seen from Mecca, from your own place or from one of 21 cities. The rules are Yallop, Odeh, Neo-MABIMS, wujud al-hilal and conjunction.
  - **Unified Hijri · الموحد** (Istanbul 2016: 5° + 8° anywhere on Earth), used by Turkey's Diyanet and by Muhammadiyah. It matches Diyanet's published calendar in 184 of 186 months.
  - **Tabular · الحسابي**, standard (Kuwaiti) or Fatimid/Bohra.
  - **Solar Hijri · الهجري الشمسي** of Iran and Afghanistan, with Nowruz from the JPL equinox.
  - **Hijri Shamsi**, the Ahmadiyya solar calendar.
  - **Julian (Rumi)**, with the Syriac month names; Hıdırellez and other Alevi and Alawite days are fixed in it.
- **Traditions page:** the Sunni schools and movements, the Shia branches, and the Ibadis, Ahmadis, Quranists, Sufis and Kharijites, each listed under the calendar it uses, with a **Use** button that sets the app to model that practice.
- **Prayer times:**
  - Sunni methods: MWL, ISNA, Egypt, Umm al-Qura, Karachi, Diyanet, the Gulf states, JAKIM and others, with Shafi'i or Hanafi Asr.
  - Shia methods: Leva Institute of Qum, and Tehran, with Ja'fari Maghrib and midnight.
  - Plus imsak, the Moon, and a live qibla compass: on a phone held flat the arrow turns with the phone and points to the Kaaba (corrected for magnetic declination).
- **Pages:** Today, Traditions, Month, Year & holy days (with .ics and .csv downloads), Prayer times, Crescent, Compare, How it works.
- **Sources:** each holy day opens a short sourced history (48 entries), and both traditions are presented in their own terms.
- **Location:** found automatically (the browser asks once). Proper nouns are also shown in Arabic script (Persian for the solar months). The design follows early Islamic (Umayyad and Abbasid) art.

See `HOW_IT_WORKS.md` for the rules and sources, and `docs/VALIDATION.md` for the checks.

## Put it online (GitHub + Streamlit Community Cloud)

1. On github.com, create a new **public** repository named `sky-taqwim`.
2. Choose **Add file → Upload files** and drag in *everything in this folder*. Upload the `assets`, `data`, `docs`, `ephem`, `tests` and `tools` folders as folders.
3. Browsers often skip the hidden `.streamlit` folder. If it is missing after the upload, choose **Add file → Create new file**, type the name `.streamlit/config.toml`, and paste the *contents* of `config.toml for GitHub (paste).txt` (not its file name). The app reads correctly without it too (its colours are set in `theme.py`), but the file keeps Streamlit's own accents in the same colours.
4. At https://share.streamlit.io choose **Create app**, select the repository, branch `main` and file `app.py`. Under **Advanced settings** pick **Python 3.12**, then **Deploy**.
5. The first start downloads the NASA JPL file (32.7 MB), which takes about a minute.

## Run locally

Install the exact, checksum-verified versions the app was tested with (Python 3.12 or newer):

```
python -m venv .venv
.venv\Scripts\python -m pip install --require-hashes --only-binary ":all:" -r requirements.txt
.venv\Scripts\python -m streamlit run app.py --server.address 127.0.0.1
```

`requirements.in` lists the direct components; `requirements.txt` is the full lock with SHA-256
hashes (generated with `uv pip compile requirements.in --universal --python-version 3.12
--generate-hashes --only-binary :all:`). The same lock serves Streamlit Community Cloud.

## Dates, data and credits

Dates run from 1850 to 2149. Put de440.bsp in `ephem/` for the prayer times and the Moon to reach 1550–2650. The Mecca crescent table then needs rebuilding with `python tools/build_tables.py`.

The Americas coastline table and the transcription of Diyanet's calendar come from the libmuslim project (Apache-2.0); see `THIRD_PARTY.md`. The Arabic fonts are subsets of Noto Kufi Arabic and Noto Naskh Arabic, © The Noto Project Authors, under the SIL Open Font License (`assets/fonts/`).

## License

MIT License, copyright (c) 2026 Gerad Smith. See [LICENSE](LICENSE). Third-party data and fonts keep their own licences: see [THIRD_PARTY.md](THIRD_PARTY.md).

## Security and privacy

- The Windows desktop copy of Sky Taqwim listens on this computer only (127.0.0.1). "Share on this network.bat" can open it to the local network, protected by a new password each time; only the person at the computer sees the Quit button.
- The desktop copy keeps its data and logs in `%LOCALAPPDATA%\SkyTaqwim`, checks its program files against `MANIFEST.sha256` at every start, and each release publishes SHA-256 checksums of its zips in `SHA256SUMS.txt`.
- All components are pinned to exact versions and installed with `--require-hashes`.
- The desktop-only code (`desktop.py`) does nothing on a hosted copy: no Quit button is shown there.
- The app keeps no accounts, places or settings on the server; it uses the browser's location only to work out local times and the qibla.
