// node tests/test_camera_surface_features.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/surface-features.js'),'utf8');
const ctx={module:{exports:{}}};vm.runInNewContext(src,ctx);const {VERSION,scan,tracker}=ctx.module.exports;
assert.equal(VERSION,'CPC_SURFACE_FEATURES_V1');
const w=160,h=200,img=new Uint8Array(w*h*4);
for(let i=0;i<w*h;i++){img[i*4]=130;img[i*4+1]=133;img[i*4+2]=128;img[i*4+3]=255}
function black(x,y){const i=(y*w+x)*4;img[i]=img[i+1]=img[i+2]=20}
for(let c=0;c<4;c++){const start=35+c*14;for(let y=70;y<83;y++)for(let x=start;x<start+7;x++){if(x===start||x===start+6||y===70||y===82)black(x,y)}}
for(let y=108;y<145;y++){black(55,y);black(75,y)}for(let x=55;x<76;x++){black(x,108);black(x,144)}
const target={box:{x:.1,y:.2,w:.8,h:.65}};
const found=scan(img,w,h,target);
assert.ok(found.letters.length>=2,'Expected repeated stroke groups to yield letter-like candidates');
assert.ok(found.details.length>=1,'Expected distinct larger carving structure');
assert.ok(found.letters.every(f=>f.kind==='letter_like_stroke_unverified'));
assert.ok(found.details.every(f=>f.kind==='carving_or_surface_detail_unverified'));
const t=tracker();assert.equal(t.update(found).length,0);assert.ok(t.update(found).length>=2);assert.equal(t.update({letters:[],details:[],motifs:[]}).length,0);
assert.equal(scan(img,w,h,null).letters.length,0);
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
assert.ok(discovery.includes('CPCSurfaceFeatures.scan'));assert.ok(html.includes('surface-features.js'));assert.ok(html.includes('id="liveLockTarget"'));
new Function(discovery);new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
console.log('Rule-based live surface feature proposals and stabilization passed');
