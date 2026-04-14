/**
 * MantaHotel — Service Worker (PWA)
 * Served from Root for Full Scope Coverage
 */

var CACHE_NAME = 'mantahotel-v2';
var STATIC_ASSETS = [
    '/static/css/app.css',
    '/static/js/app.js',
    '/manifest.json'
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

/* Fetch — Network First, Cache Fallback */
self.addEventListener('fetch', function (event) {
    /* Skip non-GET requests */
    if (event.request.method !== 'GET') return;

    /* Network First Strategy for all requests */
    event.respondWith(
        fetch(event.request)
            .then(function (response) {
                // If response is valid, clone it and cache it for future offline use
                if (response && response.status === 200 && response.type === 'basic') {
                    var responseToCache = response.clone();
                    caches.open(CACHE_NAME).then(function(cache) {
                        cache.put(event.request, responseToCache);
                    });
                }
                return response;
            })
            .catch(function () {
                // Network failed (offline), try the cache
                return caches.match(event.request).then(function (response) {
                    if (response) {
                        return response;
                    }
                    // Optional: return a custom offline.html page here if neither network nor cache works
                    console.log("Offline mode, resource not in cache:", event.request.url);
                });
            })
    );
});
