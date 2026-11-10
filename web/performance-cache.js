/* GXB3 online client cache/snapshot layer.
 * Static resources and a sanitized visual shell are cached locally.
 * Only idempotent profile updates may be queued after a network failure.
 */
(function () {
  'use strict';
  var SNAPSHOT_KEY = 'gxb3.home-shell.snapshot.v2';
  var PROFILE_QUEUE_KEY = 'gxb3.profile.queue.v1';
  var MAX_SNAPSHOT_BYTES = 180000;
  var MAX_PROFILE_QUEUE = 8;
  var PROFILE_TTL_MS = 24 * 60 * 60 * 1000;

  function registerServiceWorker() {
    if (!('serviceWorker' in navigator) || !window.isSecureContext) return;
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
  }
  function restoreShell() {
    var home = document.getElementById('home-view');
    if (!home) return;
    try {
      var raw = localStorage.getItem(SNAPSHOT_KEY);
      if (!raw) return;
      var snapshot = JSON.parse(raw);
      if (!snapshot || snapshot.version !== 1 || typeof snapshot.html !== 'string') return;
      if (Date.now() - Number(snapshot.savedAt || 0) > 7 * 24 * 60 * 60 * 1000) return;
      if (snapshot.html.length > MAX_SNAPSHOT_BYTES) return;
      home.innerHTML = snapshot.html;
      home.setAttribute('data-cached-shell', 'true');
    } catch (_) {
      try { localStorage.removeItem(SNAPSHOT_KEY); } catch (__) {}
    }
  }
  function saveShell() {
    var home = document.getElementById('home-view');
    if (!home) return;
    try {
      var clone = home.cloneNode(true);
      clone.removeAttribute('data-cached-shell');
      ['home-level', 'home-gold', 'home-gems'].forEach(function (id) {
        var node = clone.querySelector('#' + id);
        if (node) node.textContent = '—';
      });
      clone.querySelectorAll('[data-user-data], input, textarea').forEach(function (node) {
        if (node.matches('input, textarea')) node.value = '';
        node.textContent = '';
      });
      var html = clone.innerHTML;
      if (html.length > MAX_SNAPSHOT_BYTES) return;
      localStorage.setItem(SNAPSHOT_KEY, JSON.stringify({ version: 1, savedAt: Date.now(), html: html }));
    } catch (_) {}
  }
  function readProfileQueue() {
    try {
      var q = JSON.parse(localStorage.getItem(PROFILE_QUEUE_KEY) || '[]');
      if (!Array.isArray(q)) return [];
      return q.filter(function (item) {
        return item && item.body && Date.now() - Number(item.createdAt || 0) < PROFILE_TTL_MS;
      }).slice(-MAX_PROFILE_QUEUE);
    } catch (_) { return []; }
  }
  function writeProfileQueue(q) {
    try {
      if (q.length) localStorage.setItem(PROFILE_QUEUE_KEY, JSON.stringify(q.slice(-MAX_PROFILE_QUEUE)));
      else localStorage.removeItem(PROFILE_QUEUE_KEY);
    } catch (_) {}
  }
  function enqueueProfile(body) {
    if (!body || typeof body !== 'object') return;
    var q = readProfileQueue();
    q.push({ createdAt: Date.now(), body: body });
    writeProfileQueue(q);
  }
  function installProfileQueue() {
    if (!window.fetch) return;
    var nativeFetch = window.fetch.bind(window);
    window.fetch = function (input, init) {
      var requestUrl = typeof input === 'string' ? input : (input && input.url) || '';
      var method = (init && init.method) || (input && input.method) || 'GET';
      var isProfilePost = /\/api\/profile(?:\?|$)/.test(requestUrl) && String(method).toUpperCase() === 'POST';
      return nativeFetch(input, init).then(function (response) {
        if (isProfilePost && response.ok) flushProfileQueue();
        return response;
      }).catch(function (error) {
        if (isProfilePost && init && typeof init.body === 'string') {
          try { enqueueProfile(JSON.parse(init.body)); } catch (_) {}
        }
        throw error;
      });
    };
    window.addEventListener('online', flushProfileQueue);
    setTimeout(flushProfileQueue, 1500);
  }
  function flushProfileQueue() {
    if (!navigator.onLine || !window.fetch || flushProfileQueue.running) return;
    var q = readProfileQueue();
    if (!q.length) return;
    flushProfileQueue.running = true;
    var nativeFetch = window.fetch;
    var index = 0;
    function next() {
      if (index >= q.length) { writeProfileQueue([]); flushProfileQueue.running = false; return; }
      var item = q[index++];
      nativeFetch('/api/profile', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', body: JSON.stringify(item.body) })
        .then(function (response) {
          if (!response.ok) throw new Error('profile queue response');
          return next();
        })
        .catch(function () {
          writeProfileQueue(q.slice(index - 1));
          flushProfileQueue.running = false;
        });
    }
    next();
  }
  function wrapStartGame() {
    var current;
    try {
      Object.defineProperty(window, 'GxbStartGame', {
        configurable: true,
        get: function () { return current; },
        set: function (fn) {
          if (typeof fn !== 'function') { current = fn; return; }
          current = function () {
            return Promise.resolve(fn.apply(this, arguments)).then(function (result) {
              setTimeout(saveShell, 0);
              flushProfileQueue();
              return result;
            });
          };
        }
      });
    } catch (_) {}
  }
  registerServiceWorker();
  installProfileQueue();
  restoreShell();
  wrapStartGame();
})();
