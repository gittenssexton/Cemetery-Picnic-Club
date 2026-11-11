// node tests/test_camera_pixel_contours.js
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/pixel-contours.js'),'utf8'),ctx={module:{exports:{}}};
vm.runInNewContext(src,ctx);
const {analyze,analyzeScene,createTracker,overlap,VERSION}=ctx.module.exports;
assert.equal(VERSION,'CPC_PIXEL_CONTOURS_V2');
const w=160,h=200,rgba=new Uint8Array(w*h*4);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){
 const k=(y*w+x)*4;rgba[k]=34;rgba[k+1]=143;rgba[k+2]=54;rgba[k+3]=255;
 const stone=(y>=55&&y<169&&x>=46&&x<112)||(y>=30&&y<55&&Math.pow((x-79)/33,2)+Math.pow((y-55)/25,2)<=1);
 const redSurface=(x>=9&&x<=35&&y>=100&&y<=125);
 const darkSurface=(x>=118&&x<=145&&y>=47&&y<=85);
 if(stone){rgba[k]=125;rgba[k+1]=127;rgba[k+2]=122}
 if(redSurface){rgba[k]=204;rgba[k+1]=70;rgba[k+2]=65}
 if(darkSurface){rgba[k]=53;rgba[k+1]=49;rgba[k+2]=52}
}
const scene=analyzeScene(rgba,w,h);
assert.ok(scene.regions.length>=3,'Must include more than gray monument regions');
assert.ok(scene.monumentCandidates.length>=1,'Must evaluate monument-like regions');
assert.ok(scene.regions.some(r=>r.box.x<.1),'Must preserve red left object, not only neutral stones');
assert.ok(scene.regions.some(r=>r.box.x>.7),'Must preserve dark right object');
assert.ok(scene.regions.some(r=>r.points.length>60),'Should trace actual boundaries');
assert.ok(scene.regions.every(r=>r.kind==='visual_region_unverified'),'Never assert semantic identification');
assert.ok(scene.regions.some(r=>new Set(r.points.map(p=>p[0])).size>5),'Contours cannot be perfect box proxies');
assert.ok(scene.regions.some(r=>r.classification==='possible_monument_shape'));
const tracker=createTracker();
assert.equal(tracker.update(scene.regions).length,0,'No display on first frame');
assert.ok(tracker.update(scene.regions).length>=3,'Stable multi-object frame should display several regions');
assert.equal(tracker.update([]).length,0,'Missing frames must hide regions');
tracker.reset();assert.equal(tracker.update(scene.regions).length,0);
assert.ok(overlap({x:0,y:0,w:1,h:1},{x:.5,y:.5,w:1,h:1})>.1);
assert.deepEqual([...analyze(new Uint8Array(w*h*4),w,h)],[]);
assert.deepEqual([...analyze(new Uint8Array(7),w,h)],[]);
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
assert.ok(html.includes('pixel-contours.js'));
assert.ok(html.includes('CPCPixelContours.analyzeScene'));
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(discovery.includes('contourTracker.update(window.CPCPixelContours.analyzeScene'));
assert.ok(discovery.includes('const point=(p)=>'));
assert.ok(!discovery.includes('ctx.ellipse(x,y,r,r*.9'));
new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
new Function(discovery);
console.log('Broad live region segmentation, candidate assessment, and multi-object stable tracking checks passed');
