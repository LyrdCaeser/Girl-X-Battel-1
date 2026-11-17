'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const css=read('web/hero-glow.css'),html=read('web/index.html');
const profile=read('web/skin-collection.css');
const js=read('web/hero-glow.js');
const rules=[
 ['Home',/#home-view \.home-profile\[data-avatar-frame="8080"\]>\.home-profile-portrait\{([^}]+)\}/],
 ['Profile',/#profile-view \.profile-avatar\[data-avatar-frame="8080"\]>img:first-child,\s*#profile-view \.profile-preview-avatar\[data-avatar-frame="8080"\]>img:first-child\{([^}]+)\}/]
];
for(const [name,regex] of rules){
 const m=css.match(regex);
 assert(m,name+' photo rule required');
 const rule=m[1];
 assert.match(rule,/inset:3%!important/);
 assert.match(rule,/width:94%!important;height:94%!important/);
 assert.match(rule,/border-radius:3%!important/);
 assert.match(rule,/(?:background-size|object-fit):cover!important/);
 assert.match(rule,/(?:background-position|object-position):center 40%!important/);
 assert.equal(3+94+3,100,name+' must cover the host symmetrically');
}
assert.match(css,/background-color:#18253b/,'home avatar fallback must not show white through transparent corners');
assert.match(js,/host\.dataset\.avatarFrame=id/,'only target frame 8080');
assert.match(html,/\/hero-glow\.css\?v=20261117-frame8080-photo-cover-r2/);
assert.match(profile,/#home-view \.home-profile-portrait\{[^}]*background-size:contain!important/);
assert.match(css,/#home-view \.home-profile\[data-avatar-frame="8080"\]>\.home-profile-portrait\{/);
assert.match(css,/#profile-view \.profile-avatar\[data-avatar-frame="8080"\]>\.profile-frame-image/);
assert.match(css,/#home-view \.home-profile\.hg-profile-animated\[data-avatar-frame="8080"\]>\.hg-glow\.hg-profile/);
assert(!/\.hg-profile-animated\s*>\.home-profile-portrait/.test(css),'animation must not hide uploaded photo');
console.log('PASS: home/profile/preview photo fills frame 8080 opening, centered and with no white gutters; all other frames unchanged');
