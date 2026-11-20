/* GXB3 online client profile retry layer.
 * Failed profile POSTs are queued locally and retried when connectivity returns.
 * No service worker, static resource cache, or cached home-screen snapshot is used.
 */
(function () {
  'use strict';
  var PROFILE_QUEUE_KEY = 'gxb3.profile.queue.v1';
  var MAX_PROFILE_QUEUE = 8;
  var PROFILE_TTL_MS = 24 * 60 * 60 * 1000;

  function removeServiceWorkers() {
    try {
      for (var i = localStorage.length - 1; i >= 0; i--) {
        var key = localStorage.key(i);
        if (key && key.indexOf('gxb3.home-shell.snapshot.') === 0) {
          localStorage.removeItem(key);
        }
      }
    } catch (_) {}
    var controlled = !!(navigator.serviceWorker && navigator.serviceWorker.controller);
    var jobs = navigator.serviceWorker
      ? navigator.serviceWorker.getRegistrations().then(function(regs) {
          return Promise.all(regs.map(function(reg) { return reg.unregister(); }));
        })
      : Promise.resolve();
    Promise.resolve(jobs).catch(function() {}).then(function() {
      if (!('caches' in window)) return;
      return caches.keys().then(function(keys) {
        return Promise.all(keys.filter(function(k) {
          return k.indexOf('gxb3-online-static-') === 0;
        }).map(function(k) { return caches.delete(k); }));
      });
    }).then(function() {
      if (!controlled) return;
      try {
        if (sessionStorage.getItem('gxb3.sw.removed.v1') === '1') return;
        sessionStorage.setItem('gxb3.sw.removed.v1', '1');
        location.reload();
      } catch (_) {}
    }).catch(function(e) { console.warn('GXB3 SW cleanup:', e); });
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
              flushProfileQueue();
              return result;
            });
          };
        }
      });
    } catch (_) {}
  }
  removeServiceWorkers();
  installProfileQueue();
  wrapStartGame();
})();
