// node tests/test_camera_pixel_contours.js
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/pixel-contours.js'),'utf8'),ctx={module:{exports:{}}};
vm.runInNewContext(src,ctx);const {analyze,createTracker,overlap,VERSION}=ctx.module.exports;
assert.equal(VERSION,'CPC_PIXEL_CONTOURS_V1');
const w=160,h=200,rgba=new Uint8Array(w*h*4);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){
 const k=(y*w+x)*4;rgba[k]=34;rgba[k+1]=143;rgba[k+2]=54;rgba[k+3]=255;
 const on=(y>=55&&y<169&&x>=46&&x<112)||
  (y>=30&&y<55&&Math.pow((x-79)/33,2)+Math.pow((y-55)/25,2)<=1);
 if(on){rgba[k]=125;rgba[k+1]=127;rgba[k+2]=122}
}
const contours=analyze(rgba,w,h);
assert.ok(contours.length>0,'Expected a gray curved monument against green background');
assert.ok(contours[0].points.length>40,'Expected multi-point pixel outline');
assert.ok(new Set(contours[0].points.map(v=>v[0])).size>5,'Outline must not be a rectangle');
assert.equal(contours[0].kind,'pixel_contour_unverified');
const tracker=createTracker();
assert.equal(tracker.update(contours).length,0,'No display on first frame');
assert.equal(tracker.update(contours).length,1,'Second stable frame appears');
assert.equal(tracker.update([]).length,0,'Missing frame hides outline');
tracker.reset();assert.equal(tracker.update(contours).length,0);
assert.ok(overlap({x:0,y:0,w:1,h:1},{x:.5,y:.5,w:1,h:1})>.1);
assert.deepEqual([...analyze(new Uint8Array(w*h*4),w,h)],[]);
assert.deepEqual([...analyze(new Uint8Array(7),w,h)],[]);
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
assert.ok(html.includes('pixel-contours.js'));
assert.ok(html.includes('CPCPixelContours.analyze'));
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(discovery.includes('contourTracker.update(window.CPCPixelContours.analyze'));
assert.ok(!discovery.includes('ctx.ellipse(x,y,r,r*.9'));
assert.ok(!discovery.includes("ctx.strokeRect(r.x*w,r.y*h,r.w*w,r.h*h)"));
new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
new Function(discovery);
console.log('Pixel contours: synthetic curved-outline and stability tests passed');
