// Basic Service Worker for Forkast
self.addEventListener('install', (event) => {
    console.log('Service Worker installed');
});

self.addEventListener('fetch', (event) => {
    // Basic pass-through
    event.respondWith(fetch(event.request));
});
