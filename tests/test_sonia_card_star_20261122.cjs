'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('web/app.js', 'utf8');
const helper = source.match(/^function cosmosCardStarArt\(row\)\{[^\n]*\}/m);
assert(helper, 'card star helper exists');
const check = vm.runInNewContext(helper[0] + ';cosmosCardStarArt');
assert.equal(check({group:8,id:758001}), true, 'Lyr Sonia borrows purple Cosmos star');
assert.equal(check({group:7,id:12345}), true, 'existing Cosmos girls unchanged');
assert.equal(check({group:8,id:12345}), false, 'unrelated Chaos girls unaffected');
assert.equal(check({group:1,id:12345}), false, 'other factions unaffected');
assert.equal((source.match(/cosmosCardStarArt\(row\)\?'_group_7'/g)||[]).length, 2,
  'both 10-star and 11+ star card emblems use targeted style');
for (const file of ['star_orange_group_7.png','potentiality_card_star_group_7.png','potentiality_card_star_group_7_max.png']) {
 assert(fs.existsSync('web/assets/girl-ui/'+file), file+' exists');
}
const catalog=JSON.parse(fs.readFileSync('web/assets/girls-catalog.json','utf8'));
const sonia=catalog.find(row=>row.id===758001);
assert.equal(sonia.group,8,'Lyr Sonia remains in Chaos faction');
const html=fs.readFileSync('web/index.html','utf8');
assert(html.includes('/app.js?v=20261122-battle-ep-sonia-r6'));
console.log('PASS: Lyr Sonia borrows purple Cosmos card-star art, factions and others unchanged');
