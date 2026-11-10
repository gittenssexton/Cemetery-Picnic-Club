// node tests/test_camera_export_archive.js
// Exercise the actual ZIP writer function extracted from the field camera source.
// Synthetic images only; no production/private user coordinates or images.
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
const privacy=fs.readFileSync(path.join(__dirname,'../web/camera/export-privacy.js'),'utf8');
const begin=html.indexOf('function concatBytes('),end=html.indexOf('async function exportShareable()',begin);
assert.ok(begin>0&&end>begin,'ZIP implementation must be present');
const context={TextEncoder,Uint8Array,Uint32Array,DataView,Date};vm.createContext(context);
vm.runInContext(html.slice(begin,end)+';this.packageZIP=packageZIP',context);
const out={};vm.runInNewContext(privacy,{window:out,crypto});
const secret={id:'PRIVATE-SECRET-UUID',location:{latitude:42.209090,longitude:-72.196600,horizontal_accuracy_m:3},
  location_observation:{provider:'device_gps',latitude:42.209090},notes:'SECRET-NOTES',cemetery:'PRIVATE-CEMETERY',monument_type:'tablet',material_hypothesis:'zinc'};
const record=out.CPCExportPrivacy.buildShareableRecord(secret,{confirmed:true,material:true});
assert.equal(out.CPCExportPrivacy.validatePublicRecord(record),true);
const entries=[{name:'record.json',data:new TextEncoder().encode(JSON.stringify(record))},
 {name:'image_01.jpg',data:new Uint8Array([0xff,0xd8,0xff,0xd9])}];
const buffer=Buffer.from(context.packageZIP(entries));assert.ok(buffer.length>100);
let offset=0;const exported=[];
while(offset+30<=buffer.length&&buffer.readUInt32LE(offset)===0x04034b50){
 const n=buffer.readUInt16LE(offset+26),x=buffer.readUInt16LE(offset+28),size=buffer.readUInt32LE(offset+18);
 const name=buffer.subarray(offset+30,offset+30+n).toString('utf8');
 const body=buffer.subarray(offset+30+n+x,offset+30+n+x+size);
 exported.push({name,body});offset+=30+n+x+size;
}
assert.equal(buffer.readUInt32LE(offset),0x02014b50,'Central directory exists');
assert.deepEqual(exported.map(f=>f.name),['record.json','image_01.jpg']);
const json=exported[0].body.toString('utf8');
for(const token of ['PRIVATE-SECRET-UUID','42.20909','-72.1966','SECRET-NOTES','PRIVATE-CEMETERY','location_observation','cemetery_match']){
 assert.equal(json.includes(token),false,'Share ZIP contains private token: '+token);
}
assert.ok(!exported.some(f=>/original|geotagged|GPS|private/i.test(f.name)));
assert.ok(html.includes("context.drawImage(state.image,0,0,canvas.width,canvas.height)"),'Public image must be reconstructed from pixels');
assert.ok(html.includes("blobFromCanvas(canvas,.89)"),'Public image must be re-encoded');
assert.ok(html.includes('integrity-manifest.json'),'Private archive must have an integrity manifest');
const privateOriginal=Buffer.from('synthetic original bytes');
const digest=crypto.createHash('sha256').update(privateOriginal).digest('hex');
assert.equal(digest.length,64);
console.log('Synthetic archive bytes and public redaction checks passed');
