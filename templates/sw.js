/**
 * Grand Nirwana Hotel — Service Worker (PWA)
 * Served from Root for Full Scope Coverage
 */

var CACHE_NAME = 'nirwana-v3';
var STATIC_ASSETS = [
    '/static/css/app.css',
    '/static/js/app.js',
    '/static/css/fonts.css',
    '/static/css/daisyui.min.css',
    '/static/js/tailwind.min.js',
    '/static/js/htmx.min.js',
    '/static/js/alpine.min.js',
    '/static/js/lucide.min.js',
    '/manifest.json'
];

/* Install — cache static assets */
self.addEventListener('install', function (event) {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(STATIC_ASSETS);
        })
    );
});

/* Activate — clean old caches */
self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames.map(function (cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

/* Fetch Strategy */
self.addEventListener('fetch', function (event) {
    if (event.request.method !== 'GET') return;

    // 1. For static files, try Cache First, then Network
    if (event.request.url.includes('/static/') || event.request.url.includes('manifest.json')) {
        event.respondWith(
            caches.match(event.request).then(function (response) {
                return response || fetch(event.request).then(function (fetchRes) {
                    return caches.open(CACHE_NAME).then(function (cache) {
                        cache.put(event.request, fetchRes.clone());
                        return fetchRes;
                    });
                });
            })
        );
        return;
    }

    // 2. For everything else (HTML, API, HTMX), always use Network Only
    // This prevents "stuck" state and logout bugs.
    event.respondWith(fetch(event.request));
});
