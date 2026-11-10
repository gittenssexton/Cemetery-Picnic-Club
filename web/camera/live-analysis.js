/* Continuous on-device visual evidence cues. Deterministic, no OCR or semantic recognition.
 * Photo/monument suggestions require human verification; do not use as maker/material ID.
 */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCLiveAnalysis=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
 const VERSION='CPC_LIVE_ANALYSIS_V1';
 function analyzeRGBA(p,w,h){
   if(!p||!Number.isInteger(w)||!Number.isInteger(h)||w<32||h<32||p.length<w*h*4)throw Error('Invalid analysis frame');
   const gray=new Uint8Array(w*h),rowEdges=new Float64Array(h),rowCounts=new Uint32Array(h);
   let sum=0,sq=0,clippedLow=0,clippedHigh=0,edgeEnergy=0,edgeCount=0;
   for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x,j=i*4;
     const v=Math.round(.2126*p[j]+.7152*p[j+1]+.0722*p[j+2]);gray[i]=v;sum+=v;sq+=v*v;
     if(v<=14)clippedLow++;if(v>=248)clippedHigh++;
   }
   // Check for repeated horizontal strokes: a text-like texture candidate only.
   for(let y=2;y<h-2;y+=2)for(let x=3;x<w-3;x+=2){
     const i=y*w+x,dx=Math.abs(gray[i+1]-gray[i-1]),dy=Math.abs(gray[i+w]-gray[i-w]);
     rowEdges[y]+=Math.min(255,dy);rowCounts[y]++;edgeEnergy+=dx+dy;edgeCount++;
   }
   const mean=sum/(w*h),std=Math.sqrt(Math.max(0,sq/(w*h)-mean*mean));
   const stripe=new Float64Array(h);
   for(let y=2;y<h-2;y+=2)stripe[y]=rowCounts[y]?rowEdges[y]/rowCounts[y]:0;
   const candidates=[];
   for(let y=Math.round(h*.13);y<Math.round(h*.85)-12;y+=4){
     const end=Math.min(h-3,y+18);let hits=0,energy=0;
     for(let row=y;row<end;row+=2){const e=stripe[row];if(e>22)hits++;energy+=e;}
     if(hits>=3&&energy>140){
       let l=w,r=0,marked=0;
       for(let x=Math.round(w*.1);x<Math.round(w*.9);x+=3){
         let score=0;
         for(let yy=y;yy<end;yy+=3){const i=yy*w+x;score+=Math.abs(gray[i-1]-gray[i+1]);}
         if(score>95){l=Math.min(l,x);r=Math.max(r,x);marked++;}
       }
       if(marked>=5&&r-l>=w*.16){
         const box={x:Math.max(0,(l-5)/w),y:y/h,w:Math.min(1,(r-l+10)/w),h:(end-y)/h,kind:'text_like_edges_unverified',score:energy};
         if(!candidates.some(c=>Math.abs(c.y-box.y)<.105))candidates.push(box);
       }
     }
   }
   const bands=candidates.sort((a,b)=>b.score-a.score).slice(0,3).map(({score,...c})=>c);
   const glare=clippedHigh/(w*h),shadow=clippedLow/(w*h);
   const quality={mean_luminance:+mean.toFixed(1),contrast_std:+std.toFixed(1),glare_fraction:+glare.toFixed(3),shadow_fraction:+shadow.toFixed(3),edge_strength:+(edgeEnergy/Math.max(1,edgeCount)).toFixed(1)};
   const advice=[];
   if(mean<57||shadow>.42)advice.push('Low light: try a clearer angle or brighter natural light.');
   if(glare>.11)advice.push('Possible glare: change angle to avoid bright reflections.');
   if(std<27)advice.push('Low contrast: try gentle side lighting for carvings or text.');
   // Display-only preview filter; never alter original camera-frame pixels.
   const targetBrightness=mean<70?1.17:mean<110?1.09:mean>205?.92:1;
   const targetContrast=std<32?1.14:std<50?1.07:1;
   return {version:VERSION,textRegions:bands,quality,advice,preview:{brightness:targetBrightness,contrast:targetContrast}};
 }
 return {VERSION,analyzeRGBA};
});
