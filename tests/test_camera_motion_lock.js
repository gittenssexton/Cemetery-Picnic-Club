// node tests/test_camera_motion_lock.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/motion-lock.js'),'utf8');
const root={isSecureContext:true,DeviceOrientationEvent:{requestPermission:()=>Promise.resolve('granted')},DeviceMotionEvent:{requestPermission:()=>Promise.resolve('granted')},listeners:new Map(),addEventListener(k,fn){this.listeners.set(k,fn)},removeEventListener(k){this.listeners.delete(k)}};
const ctx={module:{exports:{}},window:root};vm.runInNewContext(src,ctx);const m=ctx.module.exports;
(async()=>{assert.equal(m.VERSION,'CPC_MOTION_LOCK_V1');assert.equal(m.difference(359,1),2);
const permission=await m.requestFromGesture();assert.equal(permission.permission,'granted');assert.equal(permission.active,true);
const now=Date.now();for(let i=0;i<8;i++)m.observeMotion({rotationRate:{alpha:.5,beta:1,gamma:0}},now-300+i*40);
assert.equal(m.status(now).motion,'steady');assert.equal(m.status(now).evidence_frames,2);
m.reset();for(let i=0;i<8;i++)m.observeMotion({rotationRate:{alpha:7,beta:9,gamma:0}},now-300+i*40);
assert.equal(m.status(now).motion,'moving');assert.equal(m.status(now).evidence_frames,3);
m.reset();for(let i=0;i<8;i++)m.observeMotion({rotationRate:{alpha:39,beta:4,gamma:0}},now-300+i*40);
assert.equal(m.status(now).motion,'rapid');assert.equal(m.status(now).may_add_feature_evidence,false);
m.stop();assert.equal(m.status(now).active,false);
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8'),discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(html.includes('motion-lock.js'));assert.ok(html.includes('id="liveMotionEnable"'));
assert.ok(discovery.includes('CPCMotionLock?.status'));assert.ok(discovery.includes('motionState.may_add_feature_evidence'));
console.log('Motion permission, wraparound, steadiness and rotation suppression checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});