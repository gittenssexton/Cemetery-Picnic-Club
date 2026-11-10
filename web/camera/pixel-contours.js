/* CPC live pixel-contour candidate engine. A contour follows segmented pixels; it is not a
   trained gravestone recognizer and must never be used as a verified monument identification. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCPixelContours=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_PIXEL_CONTOURS_V1';
function analyze(rgba,w,h){
 if(!rgba||!Number.isInteger(w)||!Number.isInteger(h)||w<40||h<40||rgba.length<w*h*4)return[];
 const n=w*h,mask=new Uint8Array(n),seen=new Uint8Array(n),queue=new Int32Array(n);
 // Prefer dark-to-mid, unsaturated monument surfaces; reject bright grass and green foliage.
 // This remains a narrow heuristic, not a general classifier.
 for(let y=3;y<h-3;y++)for(let x=3;x<w-3;x++){
  const i=y*w+x,j=i*4,r=rgba[j],g=rgba[j+1],b=rgba[j+2];
  const lum=.2126*r+.7152*g+.0722*b,chrom=Math.max(r,g,b)-Math.min(r,g,b);
  const green=(g>r*1.11&&g>b*1.08&&g-r>12),veryDark=lum<24;
  if(lum>26&&lum<215&&chrom<70&&!green&&!veryDark)mask[i]=1;
 }
 // Require at least three of five neighboring sample points to reject single-pixel texture.
 const clean=new Uint8Array(n);
 for(let y=4;y<h-4;y++)for(let x=4;x<w-4;x++){const i=y*w+x;
  if(mask[i]&&mask[i-1]+mask[i+1]+mask[i-w]+mask[i+w]>=2)clean[i]=1;
 }
 const components=[];
 for(let y=8;y<h-8;y++)for(let x=8;x<w-8;x++){
  const start=y*w+x;if(!clean[start]||seen[start])continue;
  let head=0,tail=1;queue[0]=start;seen[start]=1;
  let minX=x,maxX=x,minY=y,maxY=y,touches=false;
  while(head<tail){
   const p=queue[head++],px=p%w,py=(p/w)|0;
   minX=Math.min(minX,px);maxX=Math.max(maxX,px);minY=Math.min(minY,py);maxY=Math.max(maxY,py);
   if(px<=5||px>=w-6||py<=5||py>=h-6)touches=true;
   for(const k of [p-1,p+1,p-w,p+w]){
    if(k<0||k>=n||seen[k]||!clean[k])continue;
    const kx=k%w,ky=(k/w)|0;
    if(Math.abs(kx-px)+Math.abs(ky-py)!==1)continue;
    seen[k]=1;queue[tail++]=k;
   }
  }
  const bw=maxX-minX+1,bh=maxY-minY+1,fill=tail/(bw*bh);
  if(touches||tail<Math.max(65,n*.006)||tail>n*.43||bh<h*.13||bw<w*.045||
    bh<bw*.85||fill<.26||fill>.97||maxY<h*.24)continue;
  // Recover a true boundary from connected component pixels, not a rectangle or circle.
  // Row intersections preserve a curved crown and variable-width shoulders.
  const left=[],right=[],stride=Math.max(1,Math.round(h/110));
  for(let yy=minY;yy<=maxY;yy+=stride){
    let l=w,rr=-1;
    for(let xx=minX;xx<=maxX;xx++)if(seen[yy*w+xx]){
      l=Math.min(l,xx);rr=Math.max(rr,xx);
    }
    if(rr-l>=3){left.push([l/w,yy/h]);right.push([rr/w,yy/h]);}
  }
  if(left.length<8)continue;
  const points=left.concat(right.reverse());
  components.push({points,box:{x:minX/w,y:minY/h,w:bw/w,h:bh/h},
   kind:'pixel_contour_unverified',fill:+fill.toFixed(2),pixels:tail});
 }
 components.sort((a,b)=>b.pixels-a.pixels);
 // Suppress near-overlapping duplicate proposals.
 const accepted=[];for(const c of components){
  const cx=c.box.x+c.box.w/2,cy=c.box.y+c.box.h/2;
  if(accepted.some(t=>Math.hypot(cx-(t.box.x+t.box.w/2),cy-(t.box.y+t.box.h/2))<.12))continue;
  accepted.push(c);if(accepted.length>=3)break;
 }
 return accepted;
}
function overlap(a,b){
 const x=Math.max(a.x,b.x),y=Math.max(a.y,b.y),right=Math.min(a.x+a.w,b.x+b.w),bottom=Math.min(a.y+a.h,b.y+b.h);
 const intersection=Math.max(0,right-x)*Math.max(0,bottom-y),union=a.w*a.h+b.w*b.h-intersection;
 return union>0?intersection/union:0;
}
function createTracker(){
 let tracks=[],nextId=1;
 return {update(candidates){
  const used=new Set(),next=[];
  for(const old of tracks){
   let hit=-1,score=.46;
   for(let i=0;i<candidates.length;i++){
    if(used.has(i))continue;
    const iou=overlap(old.contour.box,candidates[i].box);
    if(iou>score){score=iou;hit=i}
   }
   if(hit>=0){
    used.add(hit);next.push({id:old.id,contour:candidates[hit],hits:old.hits+1,misses:0});
   }else if(old.misses<1)next.push({...old,misses:old.misses+1});
  }
  for(let i=0;i<candidates.length;i++)if(!used.has(i))next.push({id:nextId++,contour:candidates[i],hits:1,misses:0});
  tracks=next.slice(0,5);
  // Hide outlines until two consecutive stable matches, and hide on missed frame.
  return tracks.filter(t=>t.hits>=2&&t.misses===0).slice(0,3).map(t=>({...t.contour,track_id:t.id}));
 },reset(){tracks=[];nextId=1;}};
}
return {VERSION,analyze,overlap,createTracker};
});
