/* GXB3 Online asset routing.
 * The VPS remains authoritative for /api/*, auth, saves and gameplay.
 * Only immutable static assets may be redirected to a configured CDN prefix.
 */
(function () {
  'use strict';

  var rawBase = String(window.GXB_ASSET_BASE_URL || '').trim();
  var base = rawBase.replace(/\/+$/, '');
  var enabled = /^https:\/\/[^/?#]+(?:\/[^?#]*)?$/.test(base);
  var staticRoot = /^(\/assets\/|\/localization\/)/;
  var rootStatic = /^\/(?:[^/]+\.(?:js|css))(?:[?#].*)?$/i;

  function toAssetUrl(value) {
    if (!enabled || typeof value !== 'string' || !value) return value;
    if (/^(?:data:|blob:|mailto:|javascript:|https?:|\/\/)/i.test(value)) return value;
    var parsed;
    try { parsed = new URL(value, window.location.href); } catch (_) { return value; }
    if (parsed.origin !== window.location.origin) return value;
    var path = parsed.pathname;
    if (!staticRoot.test(path) && !rootStatic.test(path)) return value;
    return base + path + parsed.search + parsed.hash;
  }

  window.GXBAssetUrl = toAssetUrl;
  window.GXBAssetRouting = Object.freeze({ enabled: enabled, base: enabled ? base : '' });

  var nativeFetch = window.fetch;
  if (typeof nativeFetch === 'function') {
    window.fetch = function (input, init) {
      if (typeof input === 'string') return nativeFetch.call(this, toAssetUrl(input), init);
      if (input && typeof Request !== 'undefined' && input instanceof Request) {
        var next = toAssetUrl(input.url);
        if (next !== input.url) return nativeFetch.call(this, new Request(next, input), init);
      }
      return nativeFetch.call(this, input, init);
    };
  }

  if (typeof XMLHttpRequest !== 'undefined') {
    var nativeOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
      var args = Array.prototype.slice.call(arguments);
      args[1] = toAssetUrl(url);
      return nativeOpen.apply(this, args);
    };
  }

  function patchProperty(proto, property) {
    if (!proto) return;
    var descriptor = Object.getOwnPropertyDescriptor(proto, property);
    if (!descriptor || !descriptor.set || !descriptor.get) return;
    try {
      Object.defineProperty(proto, property, {
        configurable: descriptor.configurable,
        enumerable: descriptor.enumerable,
        get: descriptor.get,
        set: function (value) { descriptor.set.call(this, toAssetUrl(value)); }
      });
    } catch (_) { /* Older WebViews may reject redefining a native property. */ }
  }

  patchProperty(window.HTMLImageElement && HTMLImageElement.prototype, 'src');
  patchProperty(window.HTMLScriptElement && HTMLScriptElement.prototype, 'src');
  patchProperty(window.HTMLMediaElement && HTMLMediaElement.prototype, 'src');
  patchProperty(window.HTMLLinkElement && HTMLLinkElement.prototype, 'href');

  function rewriteNode(node) {
    if (!node || node.nodeType !== 1) return;
    ['src', 'href', 'poster'].forEach(function (name) {
      if (node.hasAttribute && node.hasAttribute(name)) {
        var value = node.getAttribute(name), next = toAssetUrl(value);
        if (next !== value) node.setAttribute(name, next);
      }
    });
    if (node.hasAttribute && node.hasAttribute('style')) {
      var style = node.getAttribute('style');
      var nextStyle = style.replace(/url\((['"]?)(\/[^)'"\s]+)\1\)/gi, function (_, q, url) {
        return 'url(' + q + toAssetUrl(url) + q + ')';
      });
      if (nextStyle !== style) node.setAttribute('style', nextStyle);
    }
    if (node.querySelectorAll) node.querySelectorAll('[src],[href],[poster],[style]').forEach(rewriteNode);
  }

  if (document.documentElement) rewriteNode(document.documentElement);
  if (typeof MutationObserver !== 'undefined' && document.documentElement) {
    new MutationObserver(function (records) {
      records.forEach(function (record) {
        if (record.type === 'attributes') rewriteNode(record.target);
        record.addedNodes.forEach(rewriteNode);
      });
    }).observe(document.documentElement, { subtree: true, childList: true, attributes: true,
      attributeFilter: ['src', 'href', 'poster', 'style'] });
  }
})();
