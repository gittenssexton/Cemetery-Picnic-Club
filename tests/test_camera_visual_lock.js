// node tests/test_camera_visual_lock.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../web/camera/visual-lock.js'),'utf8'),context={module:{exports:{}}};
vm.runInNewContext(source,context);const {VERSION,motionEstimate,createTracker}=context.module.exports;
assert.equal(VERSION,'CPC_VISUAL_LOCK_V1');
const w=160,h=200;
function image(dx=0,dy=0){const p=new Uint8Array(w*h);for(let y=30;y<172;y++)for(let x=38;x<128;x++){const xx=x+dx,yy=y+dy;if(xx>=0&&xx<w&&yy>=0&&yy<h)p[yy*w+xx]=Math.floor((x*13+y*17+(x*y)%71)%190)+45}return p;}
const shape={box:{x:38/w,y:30/h,w:90/w,h:142/h},points:[[38/w,30/h],[128/w,30/h],[128/w,172/h],[38/w,172/h]],classification:'possible_monument_shape',shape_score:8,pixels:9000};
const estimate=motionEstimate(image(),image(4,3),w,h,shape);
assert.equal(estimate.dx,4);assert.equal(estimate.dy,3);assert.ok(estimate.confidence>.95);
assert.equal(motionEstimate(new Uint8Array(w*h),new Uint8Array(w*h),w,h,shape),null,'Featureless stone cannot be confidently tracked');
const t=createTracker(),now=Date.now(),first=t.confirm([shape],image(),w,h,now);
assert.ok(first&&first.points.length===4,'Accept a silhouette already stabilized by contour tracker');
const moved=t.advance(image(4,3),w,h,now+240);
assert.ok(Math.abs(moved.box.x-(42/w))<.001,'Follow the same stone between full scans');
assert.ok(Math.abs(moved.box.y-(33/h))<.001);
assert.equal(moved.tracking_state,'tracking');
const unrelated={...shape,box:{x:.01,y:.01,w:.25,h:.3},points:[[.01,.01],[.26,.01],[.26,.31],[.01,.31]]};
const keep=t.confirm([unrelated],image(4,3),w,h,now+720);
assert.ok(keep,'Unrelated object should not replace recently tracked monument');
assert.ok(keep.box.x>.2,'Unrelated proposal must not steal the lock');
const held=t.advance(new Uint8Array(w*h),w,h,now+960);
assert.equal(held.tracking_state,'holding');
assert.equal(t.advance(new Uint8Array(w*h),w,h,now+1800),null,'Release the lock after an evidence timeout');
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8'),discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(html.includes('visual-lock.js'));assert.ok(discovery.includes('timer=setInterval(cycle,240)'));
assert.ok(discovery.includes('visualTracker?.confirm'));assert.ok(discovery.includes('visualTracker?.advance'));
new Function(discovery);new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
console.log('Persistent visual stone lock: acquisition, optical shift, unrelated target rejection, temporary hold, expiry passed');
