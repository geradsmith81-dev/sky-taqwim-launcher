# Sky Taqwim launcher · تقويم السماء

Home-screen page for **Sky Taqwim**, the Islamic calendar (Sunni and Shia) from NASA JPL astronomy. Add this page to a
phone's home screen; opening the icon goes straight to the app.

While `APP_URL` in `index.html` is still `REPLACE-WITH-STREAMLIT-APP-URL`, the page says so and does **not** redirect.

## What is in this folder

| File | What it does |
|---|---|
| `index.html` | The page. It holds the app's address (`APP_URL`, one line near the bottom). |
| `manifest.webmanifest` | Name, colours and icons for Android and desktop "Install app". Starts at `./?source=homescreen`. |
| `sw.js` | A small service worker that keeps this page (not the app) available offline. |
| `icons/` | `apple-touch-icon.png` (180, iPhone/iPad), `favicon-32.png`, `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` (Android; the art sits inside the central safe circle). |

## Publish it on GitHub Pages (once)

1. Sign in to GitHub and press **New repository**. Name it `sky-taqwim-launcher`, choose **Public**, and press **Create repository**.
2. On the new repository's page, press **Add file**, then **Upload files**. Drag in everything from this folder:
   `index.html`, `manifest.webmanifest`, `sw.js`, `README.md` and the whole `icons` folder (drag the folder itself so
   the files land in `icons/`). Press **Commit changes**.
3. Open **Settings**, then **Pages** (left column). Under **Build and deployment**, set **Source** to
   **Deploy from a branch**, **Branch** to `main` and the folder to `/ (root)`. Press **Save**.
4. Wait a minute or two, then reload the Pages settings. GitHub shows the address, for example
   `https://YOUR-GITHUB-NAME.github.io/sky-taqwim-launcher/`. Open it: the page should say the app address is not set yet.

## Add the app's address (when the Streamlit app is live)

1. Deploy the Sky Taqwim app on Streamlit Community Cloud and copy its address (it ends in `.streamlit.app/`).
2. In the launcher repository, open `index.html` and press the pencil (**Edit**).
3. Near the bottom, change the line
   `var APP_URL = "REPLACE-WITH-STREAMLIT-APP-URL";`
   to your address, for example `var APP_URL = "https://sky-taqwim-example.streamlit.app/";`
   (keep the quotation marks and the semicolon).
4. Open `sw.js`, change `sky-taqwim-launcher-v1` to `sky-taqwim-launcher-v2`, and commit. This makes phones that
   already have the page fetch the new copy. Do the same (v3, v4 ...) after any later change.
5. Wait a minute and open the Pages address again. The button now reads **Open Sky Taqwim** and opens the app.

If Streamlit ever gives the app a new address, repeat steps 2-5.

## Put it on a phone's home screen

* **iPhone or iPad (Safari):** open the Pages address, tap the Share button (square with an arrow), then
  **Add to Home Screen**, then **Add**.
* **Android (Chrome, Samsung Internet, Edge):** open the Pages address, tap the three dots, then
  **Add to home screen** or **Install app**.

The page also offers this itself: on Android it shows an **Add Sky Taqwim to this device** button (the browser's own
install prompt), and on iPhone/iPad it shows where the Share > **Add to Home Screen** command is.

Then open it from the icon **Sky Taqwim** (a gold arch under the new crescent): it goes straight to the app. This works
for both kinds of home-screen icon: an installed app (it opens in its own window) and an Android shortcut (it opens in
the browser with `?source=homescreen`). The page replaces itself with the app, so the Back button does not return to
it and cannot loop; every launch from the icon opens the app. The first time you tap **Use my location** in the app,
allow location for the site.

**If an icon made before November 2026 still stops at this page:** open the Pages address once in the browser and
reload it (this fetches the new copy), or delete the icon and add it again.

## Notes

* Adapted from the public template `geradsmith81-dev/afterglow-launcher` (same files; renamed, recoloured, given the placeholder
  check and an offline fallback that ignores `?source=homescreen`; the redirect and install prompt follow
  `geradsmith81-dev/sky-luach-launcher`).
* The app itself is never cached by the service worker: calendar and sky data always come fresh from the app.
* Colours follow the app's theme: night lapis `#0b1430`, gold `#ebc25f`, ivory `#f6efdc`, lapis button `#2a4d9b`
  (white text 8.0:1).
