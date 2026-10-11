const SW_VERSION='2.8.0';
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
// Intentionally no fetch handler: network requests and the existing refresh/version logic remain unchanged.
