const CACHE_NAME = 'cache-v1';
const urlsToCache = [
    '/home',
    
    
    
];
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

