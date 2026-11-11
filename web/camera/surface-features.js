/* CPC rules-based live surface feature proposals v1.
   No OCR, object recognition or confirmed iconography. All evidence remains provisional. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCSurfaceFeatures=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_SURFACE_FEATURES_V2';
function scan(rgba,w,h,region){
 if(!rgba||rgba.length<w*h*4||!region?.box)return {letters:[],details:[],motifs:[],version:VERSION};
 const b=region.box, x0=Math.max(2,Math.floor(b.x*w+4)),x1=Math.min(w-3,Math.ceil((b.x+b.w)*w-4)),
 y0=Math.max(2,Math.floor(b.y*h+5)),y1=Math.min(h-3,Math.ceil((b.y+b.h)*h-5));
 if(x1-x0<15||y1-y0<16)return {letters:[],details:[],motifs:[],version:VERSION};
 const gray=new Uint8Array(w*h),edges=new Uint8Array(w*h),seen=new Uint8Array(w*h),queue=new Int32Array(w*h);
 let sum=0,count=0;for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){const i=y*w+x,j=i*4;gray[i]=(rgba[j]*54+rgba[j+1]*183+rgba[j+2]*19)>>8;sum+=gray[i];count++;}
 // Local edge responses; only contiguous stroke groups can become feature regions.
 let energy=0;for(let y=y0+1;y<y1-1;y++)for(let x=x0+1;x<x1-1;x++){const i=y*w+x;const v=Math.abs(gray[i+1]-gray[i-1])+Math.abs(gray[i+w]-gray[i-w]);energy+=v;}
 const threshold=Math.max(32,Math.min(95,energy/Math.max(1,count)*1.35));
 for(let y=y0+1;y<y1-1;y++)for(let x=x0+1;x<x1-1;x++){
 const i=y*w+x;const dx=Math.abs(gray[i+1]-gray[i-1]),dy=Math.abs(gray[i+w]-gray[i-w]);
 if(dx+dy>threshold)edges[i]=1;
 }
 // Group compact stroke clusters. This detects candidate glyphs or carving fragments,
 // not recognized letters, words or symbols.
 const found=[];
 for(let y=y0+1;y<y1-1;y++)for(let x=x0+1;x<x1-1;x++){
 const start=y*w+x;if(!edges[start]||seen[start])continue;
 let head=0,tail=1,minX=x,maxX=x,minY=y,maxY=y;queue[0]=start;seen[start]=1;
 while(head<tail){
  const p=queue[head++],px=p%w,py=(p/w)|0;
  minX=Math.min(minX,px);maxX=Math.max(maxX,px);minY=Math.min(minY,py);maxY=Math.max(maxY,py);
  for(const d of [-w-1,-w,-w+1,-1,1,w-1,w,w+1]){
   const k=p+d;if(k<0||k>=w*h||seen[k]||!edges[k])continue;
   const kx=k%w,ky=(k/w)|0;
   if(Math.abs(kx-px)>1||Math.abs(ky-py)>1)continue;
   seen[k]=1;queue[tail++]=k;
  }
 }
 const bw=maxX-minX+1,bh=maxY-minY+1;
 if(tail<4||tail>count*.21||bw<2||bh<2||bw>x1-x0-2||bh>y1-y0-2)continue;
 // Keep the exact edge pixels for a transparent overlay, never a rectangle-shaped fill.
 // RLE rows are small and serializable; no camera pixels are modified.
 const byRow=new Map();
 for(let z=0;z<tail;z++){const v=queue[z],py=(v/w)|0,px=v%w;if(!byRow.has(py))byRow.set(py,[]);byRow.get(py).push(px);}
 const strokes=[];
 for(const [py,xs] of [...byRow].sort((a,b)=>a[0]-b[0])){
   xs.sort((a,b)=>a-b);let startX=xs[0],last=xs[0];
   for(let k=1;k<=xs.length;k++){
     if(k<xs.length&&xs[k]<=last+1){last=xs[k];continue;}
     strokes.push([startX,py,last-startX+1]);
     if(k<xs.length){startX=xs[k];last=xs[k];}
   }
 }
 found.push({strokes,x:minX/w,y:minY/h,w:bw/w,h:bh/h,pixels:tail,aspect:bw/bh,
  centerX:(minX+maxX)/2/w,centerY:(minY+maxY)/2/h});
 }
 // Glyph-like candidates are compact and repeated at compatible heights in a row.
 const glyphs=found.filter(o=>o.aspect>.13&&o.aspect<3.6&&o.h*h>=3&&o.h*h<=25&&o.w*w<=25);
 const letters=[];
 for(const f of glyphs){
  const near=glyphs.filter(o=>o!==f&&Math.abs(o.centerY-f.centerY)*h<Math.max(4,f.h*h*.9)&&
   Math.abs(o.h-f.h)*h<Math.max(6,f.h*h*.75)&&Math.abs(o.centerX-f.centerX)*w<32);
  if(near.length>=1)letters.push({...f,kind:'letter_like_stroke_unverified'});
 }
 // Other groups are preserved as carving/structural texture details.
 const details=found.filter(f=>!letters.includes(f)&&f.pixels>=9)
 .sort((a,b)=>b.pixels-a.pixels).slice(0,12).map(f=>({...f,kind:'carving_or_surface_detail_unverified'}));
 // Circular bounds with directional strokes: shape only. Never identify a pinwheel
 // from circularity; a radial motif label requires independent confirmation.
 const motifs=details.filter(o=>o.aspect>.75&&o.aspect<1.3&&o.w*w>=9&&o.h*h>=9)
 .slice(0,3).map(o=>({...o,kind:'circular_motif_candidate_unverified',suggestion:'possible circular ornament; check for radial blades'}));
 return{version:VERSION,letters:letters.slice(0,40),details,motifs,mean_luminance:Math.round(sum/count)};
}
function tracker(){
 let tracks=[],serial=1;
 return {update(features){
  const incoming=[...(features?.letters||[]),...(features?.details||[]),...(features?.motifs||[])],next=[],used=new Set();
  for(const old of tracks){
   let pick=-1,best=.065;
   for(let j=0;j<incoming.length;j++){
    if(used.has(j)||incoming[j].kind!==old.region.kind)continue;
    const o=incoming[j],dx=(o.centerX-old.region.centerX),dy=(o.centerY-old.region.centerY);
    const distance=Math.hypot(dx,dy);
    const sizeRatio=Math.max(o.w/old.region.w,old.region.w/o.w,o.h/old.region.h,old.region.h/o.h);
    if(sizeRatio>1.8)continue;
    if(distance<best){best=distance;pick=j;}
   }
   if(pick>=0){used.add(pick);next.push({id:old.id,region:incoming[pick],hits:Math.min(10,old.hits+1),misses:0});}
  }
  for(let i=0;i<incoming.length;i++)if(!used.has(i))next.push({id:serial++,region:incoming[i],hits:1,misses:0});
  tracks=next.slice(0,70);
  return tracks.filter(t=>t.hits>=2).map(t=>({...t.region,track_id:t.id}));
 },reset(){tracks=[];serial=1;}};
}
return {VERSION,scan,tracker};
});
