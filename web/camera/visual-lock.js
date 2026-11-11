/* CPC optical gravestone lock v1.
   Sparse visual-gradient block matching moves a VERIFIED-AGAIN silhouette between slower
   full image segmentations. No object recognition/AR dimensions. Original photos unchanged. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCVisualLock=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_VISUAL_LOCK_V1',clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function copyGray(frame,w,h){if(!frame||frame.length<w*h)return null;return Uint8Array.from(frame.subarray(0,w*h))}
function shifted(region,dx,dy,w,h){
 if(!region?.points?.length)return null;
 const sx=dx/w,sy=dy/h,b=region.box;
 if(b.x+sx<0||b.y+sy<0||b.x+b.w+sx>1||b.y+b.h+sy>1)return null;
 return {...region,points:region.points.map(p=>[p[0]+sx,p[1]+sy]),box:{...b,x:b.x+sx,y:b.y+sy}};
}
function gradient(g,w,x,y){const i=y*w+x;return [g[i+1]-g[i-1],g[i+w]-g[i-w]]}
function motionEstimate(prev,next,w,h,region){
 if(!prev||!next||!region?.box||prev.length<w*h||next.length<w*h)return null;
 const b=region.box,x0=Math.max(3,Math.floor(b.x*w)+3),x1=Math.min(w-4,Math.ceil((b.x+b.w)*w)-3),
 y0=Math.max(3,Math.floor(b.y*h)+3),y1=Math.min(h-4,Math.ceil((b.y+b.h)*h)-3);
 if(x1-x0<14||y1-y0<15)return null;
 const samples=[];
 const xStep=Math.max(3,Math.floor((x1-x0)/13)),yStep=Math.max(3,Math.floor((y1-y0)/14));
 for(let y=y0;y<=y1;y+=yStep)for(let x=x0;x<=x1;x+=xStep){
  const grad=gradient(prev,w,x,y),edge=Math.abs(grad[0])+Math.abs(grad[1]);
  if(edge>=13)samples.push([x,y,grad[0],grad[1]]);
 }
 // A featureless surface cannot be optical-tracked safely. Use latest confirmed contour.
 if(samples.length<18)return null;
 const maxShift=8,cmp=(dx,dy)=>{
  let sum=0,n=0;
  for(const [x,y,gx,gy] of samples){
   const xx=x+dx,yy=y+dy;if(xx<2||xx>=w-2||yy<2||yy>=h-2)continue;
   const g=gradient(next,w,xx,yy);sum+=Math.abs(g[0]-gx)+Math.abs(g[1]-gy);n++;
  }
  return n>=samples.length*.7?sum/n:Infinity;
 };
 let best={dx:0,dy:0,error:cmp(0,0)};
 // Examine integer shifts; carved grooves and thin lettering are high-frequency
 // features, so skipping alternate pixels can miss the correct displacement.
 for(let dy=-maxShift;dy<=maxShift;dy++)for(let dx=-maxShift;dx<=maxShift;dx++){
  const error=cmp(dx,dy);if(error<best.error)best={dx,dy,error};
 }
 if(best.error>36)return null;
 return {...best,samples:samples.length,confidence:clamp(1-best.error/36,0,1)};
}
function createTracker(){
 let region=null,previous=null,lastObserved=0,lastConfirmed=0,state='searching',pending=null,serial=0;
 const MAX_UNCONFIRMED_MS=1500;
 function reset(){region=null;previous=null;lastObserved=0;lastConfirmed=0;state='searching';pending=null;serial=0;}
 function advance(gray,w,h,now=Date.now()){
  if(!region){previous=copyGray(gray,w,h);return null}
  if(previous&&lastObserved&&now-lastObserved<850){
   const estimate=motionEstimate(previous,gray,w,h,region);
   if(estimate){
    const translated=shifted(region,estimate.dx,estimate.dy,w,h);
    if(translated){region=translated;state='tracking';}
    else state='holding';
   }else state='holding';
  }
  previous=copyGray(gray,w,h);lastObserved=now;
  if(now-lastConfirmed>MAX_UNCONFIRMED_MS){reset();return null}
  return current(now);
 }
 function confirm(candidates,gray,w,h,now=Date.now()){
  // Predict where the existing stone should be in the latest frame.
  if(region)advance(gray,w,h,now);
  const good=(candidates||[]).filter(c=>c.classification==='possible_monument_shape'&&c.points?.length);
  const overlap=(a,b)=>{const x=Math.max(a.x,b.x),y=Math.max(a.y,b.y),r=Math.min(a.x+a.w,b.x+b.w),bot=Math.min(a.y+a.h,b.y+b.h);const v=Math.max(0,r-x)*Math.max(0,bot-y);return v/Math.max(.000001,a.w*a.h+b.w*b.h-v)};
  let found=null;
  if(region){
   let best=.22;
   for(const c of good){const score=overlap(region.box,c.box);if(score>best){best=score;found=c}}
   // Do not jump to a different monument because it is now the largest shape.
   if(!found)return current(now);
  }else{
   const sorted=good.sort((a,b)=>(b.shape_score||0)+(b.pixels||0)/10000-(a.shape_score||0)-(a.pixels||0)/10000);
   const first=sorted[0];
   if(first){
    if(pending&&overlap(pending.box,first.box)>.45){pending={box:first.box,hits:pending.hits+1};}
    else pending={box:first.box,hits:1};
    if(pending.hits>=1)found=first; // Upstream contour tracker already required multiple matching segmentation frames.
   }
  }
  if(found){
   const wasLocked=!!region,old=region;
   if(!wasLocked)serial++;
   // Damp small contour boundary shifts from segmentation while letting silhouette
   // follow moving stones; only blend when point ordering/length is identical.
   let points=found.points;
   if(old&&old.points?.length===points.length){
    points=points.map((p,i)=>[old.points[i][0]*.38+p[0]*.62,old.points[i][1]*.38+p[1]*.62]);
   }
   region={...found,points,persistent_lock_id:serial};
   lastConfirmed=now;lastObserved=now;state='confirmed';pending=null;previous=copyGray(gray,w,h);
  }
  return current(now);
 }
 function current(now=Date.now()){
  if(!region||now-lastConfirmed>MAX_UNCONFIRMED_MS)return null;
  return {...region,tracking_state:state,last_confirmed_ms_ago:Math.max(0,now-lastConfirmed)};
 }
 return {advance,confirm,current,reset,VERSION};
}
return{VERSION,createTracker,motionEstimate,shifted};
});
