// Keeps the launcher page itself available offline (the app needs the internet anyway).
// Change the version (v1 -> v2 ...) whenever a file here changes, so phones fetch the new copy.
const CACHE = "sky-taqwim-launcher-v3";
const FILES = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png",
               "icons/icon-maskable-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if (new URL(e.request.url).origin !== location.origin) return;     // the app itself is never cached
  e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put(e.request, c)); return r; })
                .catch(() => caches.match(e.request, { ignoreSearch: true })));   // "./?source=homescreen" -> "./"
});
