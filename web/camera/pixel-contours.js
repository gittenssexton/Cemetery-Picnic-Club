/* CPC live visual-region segmentation v2.
 * Outline many high-contrast color/luminance regions BEFORE evaluating monument likelihood.
 * This is deterministic visual segmentation, not object/gravestone recognition.
 * Original images are unchanged. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCPixelContours=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_PIXEL_CONTOURS_V2';
function category(r,g,b){
 const min=Math.min(r,g,b),max=Math.max(r,g,b),d=max-min,light=(r+g+b)/3;
 if(light<24)return 0;
 if(d<Math.max(20,light*.15))return 1+Math.min(3,Math.floor(light/64));
 // Quantized hue groups let a gray stone, green grass, blue sky, and colored markers
 // become independent candidate surfaces. Not semantic object labels.
 let hue;
 if(max===r)hue=((g-b)/d+6)%6;
 else if(max===g)hue=(b-r)/d+2;
 else hue=(r-g)/d+4;
 const sector=Math.min(7,Math.floor(hue*8/6));
 const brightness=light<85?0:light<175?1:2;
 return 5+sector*3+brightness;
}
function outline(mask,w,h,minX,maxX,minY,maxY){
 // Trace boundary pixel edges into an ordered loop. Unlike row extremities,
 // this preserves concave shoulders and locally irregular stone silhouettes.
 const segs=new Map();
 const key=(x,y)=>y*(w+1)+x;
 const add=(a,b)=>{const k=key(a[0],a[1]);if(!segs.has(k))segs.set(k,[]);segs.get(k).push(b)};
 for(let y=minY;y<=maxY;y++)for(let x=minX;x<=maxX;x++){
  if(!mask[y*w+x])continue;
  if(y===0||!mask[(y-1)*w+x])add([x,y],[x+1,y]);
  if(x===w-1||!mask[y*w+x+1])add([x+1,y],[x+1,y+1]);
  if(y===h-1||!mask[(y+1)*w+x])add([x+1,y+1],[x,y+1]);
  if(x===0||!mask[y*w+x-1])add([x,y+1],[x,y]);
 }
 let longest=[];
 // A single coherent component may have holes. Keep its longest exterior loop.
 const limit=2*(w+h)+4*w*h;
 while(segs.size){
  const first=segs.keys().next().value,xy=[first%(w+1),Math.floor(first/(w+1))],loop=[xy];
  let current=first,steps=0;
  while(steps++<limit){
   const options=segs.get(current);if(!options?.length)break;
   const next=options.pop();if(options.length===0)segs.delete(current);
   current=key(next[0],next[1]);if(current===first)break;loop.push(next);
  }
  if(current===first&&loop.length>longest.length)longest=loop;
 }
 if(longest.length<16)return[];
 // Smooth out pixel stair steps by sampling every few pixels, never by drawing a box.
 const step=Math.max(1,Math.floor(longest.length/240));
 const result=[];for(let i=0;i<longest.length;i+=step)result.push([longest[i][0]/w,longest[i][1]/h]);
 return result;
}
function analyzeScene(rgba,w,h,options={}){
 if(!rgba||!Number.isInteger(w)||!Number.isInteger(h)||w<40||h<40||rgba.length<w*h*4)return{regions:[],monumentCandidates:[]};
 const n=w*h,bins=new Uint8Array(n),seen=new Uint8Array(n),queue=new Int32Array(n),maxRegions=Math.max(1,Math.min(40,Number(options.maxRegions)||18));
 for(let i=0;i<n;i++)bins[i]=category(rgba[i*4],rgba[i*4+1],rgba[i*4+2]);
 const raw=[];
 for(let y=1;y<h-1;y++)for(let x=1;x<w-1;x++){
  const seed=y*w+x,bin=bins[seed];if(seen[seed])continue;
  seen[seed]=1;let head=0,tail=1;queue[0]=seed;
  let minX=x,maxX=x,minY=y,maxY=y,sumL=0,sumSat=0,sumGreen=0,touches=false;
  while(head<tail){
   const p=queue[head++],px=p%w,py=Math.floor(p/w);
   minX=Math.min(minX,px);maxX=Math.max(maxX,px);minY=Math.min(minY,py);maxY=Math.max(maxY,py);
   const j=p*4,r=rgba[j],g=rgba[j+1],b=rgba[j+2];
   sumL+=(r+g+b)/3;sumSat+=Math.max(r,g,b)-Math.min(r,g,b);
   if(g>r*1.08&&g>b*1.06)sumGreen++;
   if(px<=1||py<=1||px>=w-2||py>=h-2)touches=true;
   for(const k of [p-1,p+1,p-w,p+w]){
    if(k<0||k>=n||seen[k]||bins[k]!==bin)continue;
    const kx=k%w,ky=Math.floor(k/w);
    if(Math.abs(kx-px)+Math.abs(ky-py)!==1)continue;
    seen[k]=1;queue[tail++]=k;
   }
  }
  const bw=maxX-minX+1,bh=maxY-minY+1,fill=tail/(bw*bh);
  // Ignore large background washes and tiny single-pixel texture fragments,
  // but otherwise preserve shapes of ANY color or aspect ratio.
  if(tail<Math.max(34,n*.0012)||tail>n*.58||bw<5||bh<5||fill<.13||touches&&tail>n*.33)continue;
  const mask=new Uint8Array(n);
  for(let j=0;j<tail;j++)mask[queue[j]]=1;
  const pts=outline(mask,w,h,minX,maxX,minY,maxY);
  if(pts.length<8)continue;
  const box={x:minX/w,y:minY/h,w:bw/w,h:bh/h};
  const neutral=sumSat/tail<41,green=sumGreen/tail>.4;
  const upright=bh/bw>.87,adequate=bh/h>.09&&bw/w>.025;
  const shapeScore=(upright?2:0)+(adequate?1:0)+(neutral?2:0)+(!green?1:0)+(maxY>h*.3?1:0)+(fill>.39?1:0);
  const stoneCandidate=upright&&adequate&&!green&&(neutral||bh/bw>1.55)&&shapeScore>=5&&tail<n*.36;
  raw.push({points:pts,box,pixels:tail,fill:+fill.toFixed(2),
   kind:'visual_region_unverified',classification:stoneCandidate?'possible_monument_shape':'unclassified_region',
   shape_score:shapeScore,neutral,green,touches_frame:touches});
 }
 // Prioritize potentially substantial regions while retaining different shape categories.
 raw.sort((a,b)=>b.pixels-a.pixels);
 const accepted=[];
 for(const region of raw){
  if(accepted.some(old=>overlap(old.box,region.box)>.7))continue;
  accepted.push(region);
  if(accepted.length>=maxRegions)break;
 }
 return{regions:accepted,monumentCandidates:accepted.filter(r=>r.classification==='possible_monument_shape')};
}
function analyze(rgba,w,h){return analyzeScene(rgba,w,h).regions;}
function overlap(a,b){
 const x=Math.max(a.x,b.x),y=Math.max(a.y,b.y),r=Math.min(a.x+a.w,b.x+b.w),bot=Math.min(a.y+a.h,b.y+b.h);
 const inter=Math.max(0,r-x)*Math.max(0,bot-y),union=a.w*a.h+b.w*b.h-inter;
 return union>0?inter/union:0;
}
function createTracker(){
 let tracks=[],nextId=1;
 return{update(candidates,motionState){
  // Motion alters persistence confidence; it does not fabricate a contour.
  const motion=motionState?.motion||'unknown',requiredHits=motion==='rapid'?4:motion==='moving'?3:2;
  const used=new Set(),next=[];
  for(const old of tracks){
   let hit=-1,score=motion==='rapid'?.48:.35;
   for(let i=0;i<candidates.length;i++){
    if(used.has(i))continue;
    const c=candidates[i],ratio=Math.max(c.box.w/old.contour.box.w,old.contour.box.w/c.box.w,c.box.h/old.contour.box.h,old.contour.box.h/c.box.h);
    if(ratio>1.75)continue;
    const iou=overlap(old.contour.box,c.box);
    if(iou>score){score=iou;hit=i}
   }
   if(hit>=0){used.add(hit);next.push({id:old.id,contour:candidates[hit],hits:Math.min(12,old.hits+1),misses:0});}
   else if(old.misses<1)next.push({...old,misses:old.misses+1});
  }
  for(let i=0;i<candidates.length;i++)if(!used.has(i))next.push({id:nextId++,contour:candidates[i],hits:1,misses:0});
  tracks=next.slice(0,25);
  return tracks.filter(t=>t.hits>=requiredHits&&t.misses===0).slice(0,18).map(t=>({...t.contour,track_id:t.id}));
 },reset(){tracks=[];nextId=1;}};
}
return{VERSION,analyze,analyzeScene,overlap,createTracker};
});
