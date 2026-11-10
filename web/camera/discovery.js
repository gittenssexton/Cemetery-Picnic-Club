/* CPC Live Discovery 0.7 - on-device edge-based visual regions and human annotation.
   NOT a trained object/symbol detector: highlighted regions are visual-interest proposals only. */
(()=>{'use strict';
const catalog=[
['scythe','Scythe','Death the reaper, cutting life down like grain at harvest; often held by Father Time or a skeletal figure.',3],
['hourglass','Hourglass','Time running out; an emptied upper chamber may indicate a life has ended.',3],
['winged_hourglass','Winged hourglass','Time flies; wings stress how quickly a life passes.',3],
['inverted_torch','Inverted torch','A life put out; a still-burning torch can suggest life continuing beyond death.',3],
['crown','Crown','Victory over death and the reward of the faithful.',3],
['bible','Book or Bible','Faith, scripture, devotion, or the Book of Life.',3],
['pointing_hand','Hand pointing upward','The soul gone to heaven; a direction to the living to look there, too.',3],
['clasped_hands','Clasped hands','Farewell and hope of reunion, often between husband and wife.',3],
['lamb','Lamb','Innocence, often on children’s graves; may also refer to Christ as Lamb of God.',3],
['anchor','Anchor','Hope and steadfast faith; sometimes a reference to seafaring life.',6],
['heart','Heart','Love, devotion, or in some uses the soul.',6],
['gate','Gate or door','Passage from this life into the next.',6],
['flowers','Flowers','Beauty and brevity of life; flowers bloom and fade.',6],
['cut_flower','Flower cut by scythe','A life cut short; seen in some Longmeadow-school carvings.',6],
['rose','Rose','Love and beauty; a rose in bloom can represent death in the prime of life.',6],
['rosebud','Rosebud or broken bud','A life ended before it could bloom, often found on children’s graves.',6],
['fleur_de_lis','Fleur-de-lis','Stylized lily associated with purity and the Trinity; sometimes simply ornament.',6],
['grapes','Grapes','Christ, communion, spiritual life, abundance, or harvest.',6],
['vines','Vines','Life and the bond between Christ and the faithful; often used as a border.',5],
['ivy','Ivy','Faithfulness and everlasting life.',5],
['leaves','Leaves','Growth and renewal, or mortality as leaves fall; sometimes purely decorative.',5],
['branches','Branches','Life and family lines.',5],
['palm','Palm branches or palmettes','Victory over death; sometimes simple ornament.',5],
['wheat','Wheat','A full life gathered like a harvest; often associated with old age.',5],
['oak','Oak leaves and acorns','Strength, endurance and long life.',5],
['willow','Weeping willow','Mourning; commonly paired with an urn on later gravestones.',5],
['tree_of_life','Tree of Life','Eternal life and paradise.',5],
['broken_tree','Broken or cut tree','A life cut short, or the end of a family line.',5],
['pinwheel','Pinwheel','Motion, eternity or the sun; can be only ornamental.',7],
['rosette','Rosette','Sun, life and renewal; often located in upper corners.',7],
['scallops','Scallops','Usually an ornamental border.',7],
['diamonds','Diamonds','Usually ornamental framing around inscriptions.',7],
['stars','Stars','Heaven, divine guidance, or the soul in glory.',7],
['scrolls','Scrolls','Ornament that frames and shapes sides or shoulders.',7],
['urn','Urn','Mourning and remembrance; often appears with willow imagery.',7],
['broken_column','Broken column','A life cut short, or loss of family support.',7],
['obelisk','Obelisk','Eternal life and reaching toward heaven; popular in nineteenth-century cemeteries.',7]
];
const $=id=>document.getElementById(id), video=$('video'),stage=$('cameraStage'),canvas=$('discoveryCanvas'),ctx=canvas.getContext('2d',{alpha:true}),status=$('discoveryStatus');
const scan=document.createElement('canvas');scan.width=160;scan.height=200;const g=scan.getContext('2d',{willReadFrequently:true});
let running=false,timer=null,latest=[],manual=false,annotations=[],lastDraw=0,reading=false;let tracks=[],nextTrackId=1,latestAnalysis=null,latestMonuments=[],contourTracker=window.CPCPixelContours?.createTracker?.();
function fit(){const r=stage.getBoundingClientRect();const dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);return{w:r.width,h:r.height}}
function videoRect(w,h){const vw=video.videoWidth||1,vh=video.videoHeight||1;const sc=Math.max(w/vw,h/vh);return{w:vw*sc,h:vh*sc,x:(w-vw*sc)/2,y:(h-vh*sc)/2}}
function cycle(){if(!running||!stage.classList.contains('active')||stage.classList.contains('review')||video.readyState<2)return;
 const {w,h}=fit();const vr=videoRect(w,h);g.clearRect(0,0,160,200);const sc=Math.max(160/video.videoWidth,200/video.videoHeight);const scanX=(160-video.videoWidth*sc)/2,scanY=(200-video.videoHeight*sc)/2;g.drawImage(video,scanX,scanY,video.videoWidth*sc,video.videoHeight*sc);
 // Map scan pixels through source video into the center-cropped on-screen preview.
 // The scanning canvas and phone viewport rarely share an aspect ratio.
 const point=(p)=>[vr.x+((p[0]*160-scanX)/sc)*vr.w/video.videoWidth,vr.y+((p[1]*200-scanY)/sc)*vr.h/video.videoHeight];
 const p=g.getImageData(0,0,160,200).data,gray=new Uint8Array(160*200);for(let i=0;i<gray.length;i++)gray[i]=(p[4*i]*77+p[4*i+1]*150+p[4*i+2]*29)>>8;
 // Conservative tiled edge density highlights candidate surface detail, not symbols.
 const tiles=[];const nx=8,ny=10,tw=20,th=20;
 for(let ty=1;ty<ny-1;ty++)for(let tx=1;tx<nx-1;tx++){
  let score=0,light=0;for(let y=ty*th+2;y<(ty+1)*th-2;y+=2)for(let x=tx*tw+2;x<(tx+1)*tw-2;x+=2){const i=y*160+x;const dx=gray[i+1]-gray[i-1],dy=gray[i+160]-gray[i-160];score+=Math.min(255,Math.abs(dx)+Math.abs(dy));light+=gray[i]}
  score/=64;light/=64;
  if(score>15&&light>23&&light<238)tiles.push({x:(tx+.5)/nx,y:(ty+.5)/ny,score});
 }
 tiles.sort((a,b)=>b.score-a.score);
 // Keep an individual region track across scans, rather than moving the circle
 // instantly to the strongest tile every 1.2 s. Stable tracks appear after two
 // observations; missed detections may persist briefly, then expire.
 const selected=[];for(const t of tiles){if(selected.every(o=>Math.hypot(t.x-o.x,t.y-o.y)>.17)){selected.push(t);if(selected.length===5)break}}
 const assigned=new Set();
 for(const old of tracks){
   let choice=-1,distance=.14;
   for(let k=0;k<selected.length;k++){
     if(assigned.has(k))continue;
     const d=Math.hypot(selected[k].x-old.x,selected[k].y-old.y);
     if(d<distance){distance=d;choice=k}
   }
   if(choice>=0){
     const t=selected[choice];assigned.add(choice);
     old.x=.72*old.x+.28*t.x;old.y=.72*old.y+.28*t.y;
     old.score=.65*old.score+.35*t.score;old.hits=Math.min(6,old.hits+1);old.missed=0;
   } else old.missed++;
 }
 tracks=tracks.filter(t=>t.missed<=2);
 for(let k=0;k<selected.length;k++){
   if(assigned.has(k)||tracks.length>=6)continue;
   const t=selected[k];tracks.push({...t,id:nextTrackId++,hits:1,missed:0});
 }
 const stable=tracks.filter(t=>t.hits>=2&&t.missed<=1).sort((a,b)=>b.score-a.score).slice(0,3);
 latest=stable;
 const live=window.CPCLiveAnalysis;
 latestAnalysis=live?.analyzeRGBA?.(p,160,200)||null;
 const mode=document.querySelector('[data-shot][aria-pressed="true"]')?.dataset.shot||'front';
 latestMonuments=$('liveMonuments')?.checked&&contourTracker?
   contourTracker.update(window.CPCPixelContours.analyzeScene(p,160,200).regions):[];
 // Publicly visible live detection is tentative and never automatically labeled as a named stone.
 if($('livePreviewEnhance')?.checked&&latestAnalysis?.preview){
   const brightness=latestAnalysis.preview.brightness,contrast=latestAnalysis.preview.contrast;
   video.style.filter='brightness('+brightness+') contrast('+contrast+')';
 }else video.style.filter='';
 ctx.clearRect(0,0,w,h);
 if($('liveMonuments')?.checked){
   ctx.save();ctx.lineWidth=2;
   for(const shape of latestMonuments){const points=shape.points;if(!points?.length)continue;
     const possible=shape.classification==='possible_monument_shape';
     ctx.strokeStyle=possible?'#7fe0bd':'rgba(192,205,220,.60)';
     ctx.lineWidth=possible?2.7:1.4;ctx.setLineDash(possible?[]:[3,6]);
     const first=point(points[0]);ctx.beginPath();ctx.moveTo(first[0],first[1]);
     for(let i=1;i<points.length;i++){const pt=point(points[i]);ctx.lineTo(pt[0],pt[1]);}
     ctx.closePath();ctx.stroke();
   }
   ctx.restore();
 }
 if($('liveLettering')?.checked&&latestAnalysis){
   ctx.save();ctx.setLineDash([3,5]);ctx.strokeStyle='#8bc4ff';ctx.lineWidth=2;
   for(const r of latestAnalysis.textRegions){const a=point([r.x,r.y+r.h]),b=point([r.x+r.w,r.y+r.h]);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
   ctx.restore();
 }
 ctx.lineWidth=2;ctx.strokeStyle='#f4d48c';ctx.fillStyle='rgba(244,212,140,.12)';ctx.setLineDash([5,5]);
 // No floating circles: detail candidates remain in the status summary until real surface contours are available.
 ctx.setLineDash([]);for(const a of annotations){const x=a.x*w,y=a.y*h;ctx.strokeStyle='#7ce1b7';ctx.lineWidth=3;ctx.beginPath();ctx.arc(x,y,22,0,Math.PI*2);ctx.stroke();ctx.fillStyle='#082b20';ctx.fillRect(Math.min(w-145,x+18),Math.max(0,y-24),138,27);ctx.fillStyle='#def8e8';ctx.font='12px system-ui';ctx.fillText(a.label.slice(0,18),Math.min(w-141,x+22),Math.max(18,y-7))}
 const m=latestMonuments.length,letter=latestAnalysis?.textRegions.length||0;
 const potential=latestMonuments.filter(r=>r.classification==='possible_monument_shape').length;
 status.textContent='LIVE regions: '+m+' outlines, '+potential+' shape candidates, '+letter+' text-like areas, '+stable.length+' surface details. No monument has been identified.';
 if($('liveQuality'))$('liveQuality').textContent=latestAnalysis?.advice[0]||'Live preview quality appears usable; check lettering at full resolution after capture.';
 lastDraw=Date.now();
}
function start(){if(running)return;running=true;cycle();timer=setInterval(cycle,1200);$('liveDiscovery').checked=true;}
function stop(){running=false;if(timer)clearInterval(timer);timer=null;tracks=[];latest=[];latestAnalysis=null;latestMonuments=[];contourTracker?.reset?.();video.style.filter='';canvas.classList.remove('enabled');ctx.clearRect(0,0,canvas.width,canvas.height);status.textContent='Live analysis paused.';}
function saveAnnotation(){const id=$('symbolChoice').value,record=catalog.find(c=>c[0]===id);if(!record){status.textContent='Choose a symbol from the reference first.';return}
 const x=Number($('markX').value),y=Number($('markY').value);annotations.push({x,y,symbol_id:id,label:record[1],interpretation:record[2],source:'User-supplied symbol identification',source_document:'Scan Nov 8, 2026 at 7.00 PM.pdf',source_page:record[3],review_status:'unreviewed',created_at:new Date().toISOString()});status.textContent=`Marked ${record[1]} based on your selection; not auto-identified.`;$('markPanel').hidden=true;manual=false;canvas.classList.remove('enabled');cycle()}
const chooser=$('symbolChoice');for(const c of catalog){let option=document.createElement('option');option.value=c[0];option.textContent=c[1];chooser.appendChild(option)}
chooser.addEventListener('change',()=>{const c=catalog.find(c=>c[0]===chooser.value);$('symbolDescription').textContent=c?`${c[2]} — reference PDF p. ${c[3]}`:''});
$('markSymbol').addEventListener('click',()=>{if(!running){status.textContent='Enable live analysis and camera first.';return}manual=true;canvas.classList.add('enabled');status.textContent='Tap the carving in the camera view to place a reference annotation.'});
canvas.addEventListener('click',e=>{if(!manual)return;const r=canvas.getBoundingClientRect();$('markX').value=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width));$('markY').value=Math.max(0,Math.min(1,(e.clientY-r.top)/r.height));$('markPanel').hidden=false;manual=false;canvas.classList.remove('enabled')});
$('saveSymbol').addEventListener('click',saveAnnotation);$('cancelSymbol').addEventListener('click',()=>{$('markPanel').hidden=true;manual=false;canvas.classList.remove('enabled')});
$('clearSymbols').addEventListener('click',()=>{annotations=[];cycle();status.textContent='Annotations cleared for next monument.'});
$('liveDiscovery').addEventListener('change',e=>e.target.checked?start():stop());
// No automatic label claims. Working visual-interest indicators and user-tagged references only.
window.CPCDiscovery={start,stop,getAnnotations:()=>annotations.map(a=>({...a})),
 snapshot:()=>({analysis_version:latestAnalysis?.version||null,contour_engine_version:window.CPCPixelContours?.VERSION||null,visual_region_count:latest.length,text_like_region_count:latestAnalysis?.textRegions.length||0,possible_outline_count:latestMonuments.length,quality:latestAnalysis?.quality||null,analysis_status:'heuristic_unverified',enhancement_applies_only_to_preview:true}),
 clear:()=>{annotations=[];manual=false;canvas.classList.remove('enabled');$('markPanel').hidden=true},
 catalog:catalog.map(c=>({id:c[0],name:c[1],meaning:c[2],source_page:c[3]}))};
})();
