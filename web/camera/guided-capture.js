/* CPC guided monument session and overview selection. Deterministic, no AI.
   Proposal rectangles are edge-density candidates only; never identified graves. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCGuidedCapture=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_GUIDED_CAPTURE_V1';
const ORDER=['overview','front','inscription','carving','side','back'];
const DIRECTIONS={
 overview:'Step back. Include several headstones and a landmark. Take a distance photograph, then tap the stone you will document.',
 front:'Photograph the selected monument straight on, showing its full top, shoulders and base.',
 inscription:'Photograph the inscription clearly, moving closer without touching the monument.',
 carving:'Take a close-up of carved symbols, ornaments, or distinctive lettering. Skip if none are present.',
 side:'Photograph one safe, accessible side to show thickness, seams or natural layers.',
 back:'If safely accessible, photograph the reverse for inscriptions, signatures and construction details.'
};
function nextStep(captured,skipped){
 const done=new Set(Array.isArray(captured)?captured:[]),skip=new Set(Array.isArray(skipped)?skipped:[]);
 return ORDER.find(s=>!done.has(s)&&!skip.has(s))||null;
}
function rectangle(cx,cy,width,height){
 for(const n of [cx,cy,width,height])if(!Number.isFinite(n))throw Error('Invalid overview geometry');
 width=Math.max(.04,Math.min(.9,width));height=Math.max(.04,Math.min(.95,height));
 const x=Math.max(0,Math.min(1-width,cx-width/2)),y=Math.max(0,Math.min(1-height,cy-height/2));
 return {x:+x.toFixed(5),y:+y.toFixed(5),w:+width.toFixed(5),h:+height.toFixed(5)};
}
function photoToView(rx,ry,rw,rh,photoW,photoH){
 // Image is rendered by object-fit:contain within review canvas.
 if(![rx,ry,rw,rh,photoW,photoH].every(Number.isFinite)||rw<=0||rh<=0||photoW<=0||photoH<=0)return null;
 const scale=Math.min(rw/photoW,rh/photoH),dx=(rw-photoW*scale)/2,dy=(rh-photoH*scale)/2;
 const x=(rx-dx)/(photoW*scale),y=(ry-dy)/(photoH*scale);
 return x>=0&&x<=1&&y>=0&&y<=1?{x,y}:null;
}
function propose(imageData,width,height){
 // High-contrast vertical edges, small bounded output. Deliberately unverified.
 // Never accept candidate as a semantic monument identification.
 if(!imageData||!Number.isInteger(width)||!Number.isInteger(height)||width<32||height<32)return [];
 const size=width*height*4;if(imageData.length<size)return [];
 const gridX=16,gridY=12,energy=new Float64Array(gridX*gridY),count=new Uint32Array(gridX*gridY);
 for(let y=2;y<height-2;y+=2)for(let x=2;x<width-2;x+=2){
   const p=(y*width+x)*4;
   const gray=(off)=>.2126*imageData[off]+.7152*imageData[off+1]+.0722*imageData[off+2];
   const dx=Math.abs(gray(p-4)-gray(p+4)),dy=Math.abs(gray(p-width*4)-gray(p+width*4));
   const gx=Math.min(gridX-1,Math.floor(x/width*gridX)),gy=Math.min(gridY-1,Math.floor(y/height*gridY)),i=gy*gridX+gx;
   energy[i]+=dx*.65+dy*.35;count[i]++;
 }
 const tiles=Array.from(energy,(e,i)=>count[i]?e/count[i]:0);
 const sorted=tiles.slice().sort((a,b)=>a-b),threshold=Math.max(16,sorted[Math.floor(sorted.length*.79)]||0);
 const cells=tiles.map(v=>v>=threshold),seen=new Uint8Array(cells.length),candidates=[];
 for(let index=0;index<cells.length;index++){
   if(!cells[index]||seen[index])continue;
   const queue=[index];seen[index]=1;let left=gridX,top=gridY,right=0,bottom=0,score=0;
   for(let qi=0;qi<queue.length;qi++){
     const i=queue[qi],x=i%gridX,y=Math.floor(i/gridX);
     left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);score+=tiles[i];
     for(const j of [i-1,i+1,i-gridX,i+gridX]){
       if(j<0||j>=cells.length)continue;
       const jx=j%gridX,jy=Math.floor(j/gridX);
       if(Math.abs(x-jx)+Math.abs(y-jy)!==1||!cells[j]||seen[j])continue;
       seen[j]=1;queue.push(j);
     }
   }
   const cols=right-left+1,rows=bottom-top+1;
   if(queue.length<2||cols>8||rows>10||cols>rows*1.6)continue;
   const rect={x:Math.max(0,(left-.4)/gridX),y:Math.max(0,(top-.7)/gridY),w:Math.min(1,(cols+.8)/gridX),h:Math.min(1,(rows+1.5)/gridY)};
   candidates.push({...rect,kind:'visual_edge_candidate_unverified',score:score/queue.length});
 }
 return candidates.sort((a,b)=>b.score-a.score).slice(0,4).map(({score,...rest})=>rest);
}
return {VERSION,ORDER,DIRECTIONS,nextStep,rectangle,photoToView,propose};
});
