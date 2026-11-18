// Cache the public app shell. Private drafts and photographs live in IndexedDB.
const CACHE_PREFIX = "cpc-pine-grove-field-shell-";
const CACHE = CACHE_PREFIX + "v3";
const APP = ["./", "./index.html", "./stone-id.html", "./manifest.webmanifest", "./icon.svg"]
 .map(path => new URL(path, self.registration.scope).href);

self.addEventListener("install", event => {
 event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
 event.waitUntil(caches.keys().then(keys => Promise.all(keys
  .filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE)
  .map(key => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener("fetch", event => {
 const {request} = event;
 const url = new URL(request.url);
 url.search = "";
 if (request.method !== "GET" || !APP.includes(url.href)) return;

 event.respondWith((async () => {
  try {
   const response = await fetch(request);
   if (response.ok && !request.url.includes("?")) {
    try {
     const cache = await caches.open(CACHE);
     await cache.put(url.href, response.clone());
    } catch {
     // A cache write failure should not prevent the page from loading.
    }
   }
   return response;
  } catch {
   return await caches.match(url.href, {cacheName: CACHE}) || Response.error();
  }
 })());
});
