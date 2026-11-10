// Run: node tests/test_camera_export_privacy.js
// Tests the actual browser privacy helper in a minimal Node VM.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const source=fs.readFileSync(path.join(__dirname,'../web/camera/export-privacy.js'),'utf8');
const window={};vm.runInNewContext(source,{window,crypto:webcrypto});
const {buildShareableRecord,validatePublicRecord}=window.CPCExportPrivacy;
const restricted={id:'CPC-private-key',location:{latitude:42.20909,longitude:-72.19660,accuracy_m:3},location_observation:{latitude:42.20909,longitude:-72.19660,provider:'gps'},cemetery:'Hidden Site',cemetery_match:{candidates:[{distance_m:1}]},notes:'SECRET-NOTE',monument:'Private Record',monument_type:'tablet',material_hypothesis:'slate',originalBlob:'SECRET-ORIGINAL'};
assert.throws(()=>buildShareableRecord(restricted,{confirmed:false}),/review/i);
const deny=buildShareableRecord(restricted,{confirmed:true});
validatePublicRecord(deny);
const denyStr=JSON.stringify(deny);
for(const bad of ['CPC-private-key','SECRET-NOTE','SECRET-ORIGINAL','42.20909','-72.19660','Hidden Site','location_observation','cemetery_match'])assert.ok(!denyStr.includes(bad),bad);
assert.equal(deny.assets.length,0);
assert.equal(deny.site_display,null);
assert.equal(deny.inscription,null);
assert.match(deny.public_export_id,/^PUB-/);
const approved=buildShareableRecord(restricted,{confirmed:true,site:true,approvedSiteName:'Public Cemetery',material:true,inscription:true,approvedInscription:'A visible epitaph',image:true});
validatePublicRecord(approved);assert.equal(approved.site_display,'Public Cemetery');
assert.equal(approved.assets.length,1);assert.equal(approved.inscription,'A visible epitaph');
assert.throws(()=>validatePublicRecord({...approved,location_observation:{latitude:42.20909}}),/Sensitive/);
assert.throws(()=>validatePublicRecord({...approved,inscription:'42.209090, -72.196600'}),/coordinates/);
console.log('Camera public export privacy helper: 16+ checks passed');
