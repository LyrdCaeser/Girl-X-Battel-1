/* GXB3 online static cache. API/auth/save requests are deliberately never cached. */
'use strict';

const CACHE_NAME = 'gxb3-online-static-v3';
const STATIC_EXT = /\.(?:js|css|json|png|webp|jpe?g|gif|svg|woff2?)(?:\?.*)?$/i;

function isStaticRequest(request) {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return false;
  if (/\.(?:mp3|ogg)$/i.test(url.pathname)) return false;
  if (url.pathname.startsWith('/api/') || url.pathname === '/asset-config.js') return false;
  return url.pathname.startsWith('/assets/') ||
    url.pathname.startsWith('/vendor/') ||
    url.pathname.startsWith('/localization/') ||
    STATIC_EXT.test(url.pathname);
}

self.addEventListener('install', event => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(key => key.startsWith('gxb3-online-static-') && key !== CACHE_NAME)
      .map(key => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  if (!isStaticRequest(event.request)) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const refresh = /\.(?:js|css|json)$/i.test(new URL(event.request.url).pathname);
    const cached = await cache.match(event.request);
    if (cached && !refresh) return cached;
    try {
      const response = await fetch(refresh ? new Request(event.request, {cache: 'no-store'}) : event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    } catch (error) {
      const fallback = await cache.match(event.request);
      if (fallback) return fallback;
      throw error;
    }
  })());
});
