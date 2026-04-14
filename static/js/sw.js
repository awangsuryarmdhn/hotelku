/**
 * MantaHotel — Service Worker (PWA)
 * ==================================
 * Caches static assets for offline shell loading.
 */

var CACHE_NAME = 'mantahotel-v1';
var STATIC_ASSETS = [
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/manifest.json',
];

/* Install — cache static assets */
self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

/* Activate — clean old caches */
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames.filter(function (cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function (cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
    self.clients.claim();
});

/* Fetch — network first, fall back to cache for static assets */
self.addEventListener('fetch', function (event) {
    /* Skip non-GET requests */
    if (event.request.method !== 'GET') return;

    /* For static assets, try cache first */
    if (event.request.url.includes('/static/')) {
        event.respondWith(
            caches.match(event.request).then(function (response) {
                return response || fetch(event.request).then(function (fetchResponse) {
                    return caches.open(CACHE_NAME).then(function (cache) {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                });
            })
        );
        return;
    }

    /* For everything else, network first */
    event.respondWith(
        fetch(event.request).catch(function () {
            return caches.match(event.request);
        })
    );
});
