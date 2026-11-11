/* CPC phone motion helper for outdoor stone tracking.
   DeviceOrientation and DeviceMotion are measured in the phone frame.
   Rotational steadiness only: not depth, scale, 3D, calibrated projection or proof of an object.
   Sensor events never leave the device or become raw archived motion trails. */
(function(root,factory){const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCMotionLock=api;})(typeof window!=='undefined'?window:null,function(root){'use strict';
const VERSION='CPC_MOTION_LOCK_V1';
let enabled=false,lastOrientation=null,lastMotionAt=0,lastOrientationAt=0,rate=null,history=[],permission='not_requested',active=false;
const finite=x=>typeof x==='number'&&Number.isFinite(x);
const difference=(a,b)=>Math.abs(((a-b+540)%360)-180);
function observeOrientation(evt,now=Date.now()){
 const angles=[evt.alpha,evt.beta,evt.gamma];
 if(!angles.every(finite))return;
 if(lastOrientation&&now>lastOrientationAt){
   const seconds=(now-lastOrientationAt)/1000;
   if(seconds>.025&&seconds<1.5){
     const components=angles.map((angle,i)=>difference(angle,lastOrientation[i]));
     const degreesPerSecond=Math.hypot(...components)/seconds;
     if(degreesPerSecond<350)history.push({at:now,rate:degreesPerSecond});
   }
 }
 lastOrientation=angles;lastOrientationAt=now;prune(now);
}
function observeMotion(evt,now=Date.now()){
 const r=evt?.rotationRate;
 if(!r)return;
 const values=[r.alpha,r.beta,r.gamma].filter(finite);
 if(!values.length)return;
 const mag=Math.hypot(...values);
 if(mag<350){rate=mag;lastMotionAt=now;history.push({at:now,rate:mag});prune(now)}
}
function prune(now){while(history.length&&(history[0].at<now-1500||history.length>90))history.shift()}
function status(now=Date.now()){
 prune(now);
 // A brief sensor gap must not cause a false steady lock.
 const fresh=(now-lastMotionAt<1400&&rate!==null)||(now-lastOrientationAt<1400&&lastOrientation!==null&&history.length);
 const readings=history.filter(v=>v.at>=now-850);
 const mean=readings.length?readings.reduce((a,v)=>a+v.rate,0)/readings.length:null;
 const motion=!!fresh&&mean!==null?mean<3.5?'steady':mean<16?'moving':'rapid':'unknown';
 return {version:VERSION,available:typeof root?.DeviceOrientationEvent!=='undefined'||typeof root?.DeviceMotionEvent!=='undefined',
  permission,active:enabled&&active,sensor_fresh:!!fresh,rotation_deg_per_s:mean===null?null:Math.round(mean*10)/10,motion,
  may_refine_outline:motion!=='rapid',may_add_feature_evidence:motion==='steady'||motion==='unknown',
  // Thresholds guide visual persistence, not physical georeferencing.
  evidence_frames:motion==='steady'?2:motion==='moving'?3:motion==='rapid'?4:2};
}
function start(){
 if(!root?.addEventListener)return false;
 if(!active){root.addEventListener('deviceorientation',onOrientation);root.addEventListener('devicemotion',onMotion);active=true;}
 enabled=true;if(permission==='not_requested')permission='available_without_explicit_prompt';
 return true;
}
function onOrientation(evt){observeOrientation(evt)}
function onMotion(evt){observeMotion(evt)}
async function requestFromGesture(){
 if(!root?.isSecureContext){permission='requires_https';return status()}
 const orientation=root.DeviceOrientationEvent,motion=root.DeviceMotionEvent;
 if(!orientation&&!motion){permission='unsupported';return status()}
 try{
  // Call all permission methods synchronously before awaiting: iOS requires the user gesture.
  const pending=[];
  if(typeof orientation?.requestPermission==='function')pending.push(orientation.requestPermission());
  if(typeof motion?.requestPermission==='function')pending.push(motion.requestPermission());
  const results=await Promise.all(pending);
  if(results.some(r=>r!=='granted')){permission='denied';return status()}
  permission='granted';start();return status();
 }catch(err){permission='denied';return {...status(),error:String(err?.message||err)}}
}
function reset(){lastOrientation=null;lastMotionAt=0;lastOrientationAt=0;rate=null;history=[]}
function stop(){if(active&&root?.removeEventListener){root.removeEventListener('deviceorientation',onOrientation);root.removeEventListener('devicemotion',onMotion)}active=false;enabled=false;reset()}
return {VERSION,status,start,stop,requestFromGesture,observeOrientation,observeMotion,reset,difference};
});
