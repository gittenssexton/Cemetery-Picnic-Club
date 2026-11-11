const CACHE='cpc-field-camera-0.9.7';
const ASSETS=['./','./index.html','./cemetery-resolver.js','./cemetery-sites.js','./cemetery-relations.js','./exif.js','./export-privacy.js','./discovery.js','./silhouette.js','./guided-capture.js','./live-analysis.js','./pixel-contours.js','./surface-features.js','./surface-conditions.js','./motion-lock.js','./visual-lock.js','./focus-region.js','./drive-sync.js','./manifest.webmanifest','./icon.svg'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(ASSETS)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{if(event.request.method!=='GET')return;event.respondWith(caches.match(event.request).then(x=>x||fetch(event.request)));});
