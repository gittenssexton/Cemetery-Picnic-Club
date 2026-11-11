// node tests/test_camera_iconography.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/iconography.js'),'utf8');
const c={module:{exports:{}}};vm.runInNewContext(src,c);const api=c.module.exports;
assert.equal(api.VERSION,'CPC_ICONOGRAPHY_V1');
assert.equal(api.entries.length,37);
for(const id of ['pinwheel','rosette','scallops','diamonds','stars','scrolls','urn','broken_column','obelisk','winged_hourglass','clasped_hands','willow'])assert.ok(api.byId[id]&&api.byId[id].source_id,'Guide entry missing '+id);
assert.equal(api.byId.pinwheel.pdf_page,7);assert.equal(api.byId.urn.pdf_page,7);
const w=160,h=200,box={x:.3,y:.3,w:.4,h:.35};
function image(kind){
const a=new Uint8Array(w*h*4);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){
 const i=(y*w+x)*4,dx=(x-w*.5)/(box.w*w*.5),dy=(y-(box.y+box.h/2)*h)/(box.h*h*.5);
 const rr=Math.hypot(dx,dy),theta=Math.atan2(dy,dx);
 const phi=kind==='pinwheel'?theta-rr*2:theta;
 const dark=rr<.75&&rr>.2&&Math.abs(Math.sin(5*phi))<.24;
 const v=dark?45:202;a[i]=a[i+1]=a[i+2]=v;a[i+3]=255;
}return a}
assert.equal(api.classifyCircularRegion(new Uint8Array(w*h*4).fill(130),w,h,box),null);
const pin=api.classifyCircularRegion(image('pinwheel'),w,h,box),rose=api.classifyCircularRegion(image('rosette'),w,h,box);
assert.ok(pin&&pin.candidates[0].id==='pinwheel','Synthetic winding should prioritize pinwheel possibility');
assert.ok(rose&&rose.candidates[0].id==='rosette','Synthetic radial petals should prioritize rosette possibility');
assert.equal(pin.status,'shape_family_only_unverified');
assert.equal(pin.source_id,api.SOURCE.drive_file_id);
assert.ok(api.entries.every(e=>!e.verified_visual_template));
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(html.includes('iconography.js'));assert.ok(html.includes('id="liveIconographyStatus"'));
assert.ok(discovery.includes('CPCIconography?.classifyCircularRegion'));new Function(discovery);
console.log('Guide taxonomy and conservative pinwheel/rosette radial geometry tests passed');
