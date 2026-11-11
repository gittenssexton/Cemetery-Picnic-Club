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
let running=false,timer=null,latest=[],manual=false,annotations=[],lastDraw=0,reading=false,lockedTrackId=null,autoStoneId=null,autoStoneHits=0,liveFeatures=[],surfaceConditions=null,featureTracker=window.CPCSurfaceFeatures?.tracker?.(),visualTracker=window.CPCVisualLock?.createTracker?.(),scanTick=0,visualStone=null,lastGray=null,lastMapping=null,lastCandidateList=[],focusRegion=null,focusMetrics=null;let tracks=[],nextTrackId=1,latestAnalysis=null,latestMonuments=[],contourTracker=window.CPCPixelContours?.createTracker?.();
function fit(){const r=stage.getBoundingClientRect();const dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(r.width*dpr);canvas.height=Math.round(r.height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);return{w:r.width,h:r.height}}
function videoRect(w,h){const vw=video.videoWidth||1,vh=video.videoHeight||1;const sc=Math.max(w/vw,h/vh);return{w:vw*sc,h:vh*sc,x:(w-vw*sc)/2,y:(h-vh*sc)/2}}
function cycle(){if(!running||!stage.classList.contains('active')||stage.classList.contains('review')||video.readyState<2)return;
 const {w,h}=fit();const vr=videoRect(w,h);g.clearRect(0,0,160,200);const sc=Math.max(160/video.videoWidth,200/video.videoHeight);const scanX=(160-video.videoWidth*sc)/2,scanY=(200-video.videoHeight*sc)/2;g.drawImage(video,scanX,scanY,video.videoWidth*sc,video.videoHeight*sc);
 // Map scan pixels through source video into the center-cropped on-screen preview.
 // The scanning canvas and phone viewport rarely share an aspect ratio.
 const point=(p)=>[vr.x+((p[0]*160-scanX)/sc)*vr.w/video.videoWidth,vr.y+((p[1]*200-scanY)/sc)*vr.h/video.videoHeight];
 const p=g.getImageData(0,0,160,200).data,gray=new Uint8Array(160*200);for(let i=0;i<gray.length;i++)gray[i]=(p[4*i]*77+p[4*i+1]*150+p[4*i+2]*29)>>8;
 lastGray=gray;lastMapping={scanX,scanY,scale:sc,videoWidth:video.videoWidth,videoHeight:video.videoHeight,screenW:w,screenH:h,vr};
 const motionState=window.CPCMotionLock?.status?.()||{motion:'unknown',may_add_feature_evidence:true};
 const fullScan=(scanTick++%3===0)||!visualTracker?.current?.();
 if(fullScan){
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
   contourTracker.update(window.CPCPixelContours.analyzeScene(p,160,200).regions,motionState):[];
 }
 const candidates=fullScan?latestMonuments.filter(r=>r.classification==='possible_monument_shape'&&r.box.h>.15&&r.box.w>.06):[];
 if(fullScan)lastCandidateList=candidates;
 visualStone=fullScan?visualTracker?.confirm?.(candidates,gray,160,200):visualTracker?.advance?.(gray,160,200);
 // Publicly visible live detection is tentative and never automatically labeled as a named stone.
 if($('livePreviewEnhance')?.checked&&latestAnalysis?.preview){
   const brightness=latestAnalysis.preview.brightness,contrast=latestAnalysis.preview.contrast;
   video.style.filter='brightness('+brightness+') contrast('+contrast+')';
 }else video.style.filter='';
 // Persistent visual stone identity is corrected by full segmentation, but tracked
 // optically on intermediate frames. It is not switched to unrelated nearby objects.
 const candidate=visualStone;
 if(!candidate&&lockedTrackId!==null){lockedTrackId=null;$('liveLockTarget').textContent='Lock detected stone';focusRegion=null;}
 const roi=candidate?window.CPCFocusRegion?.resolve?.(candidate,focusRegion):null;
 if(focusRegion&&!roi){focusRegion=null;featureTracker?.reset?.();}
 focusMetrics=roi?.is_detail?roi:null;
 // Suppress new internal-stroke assertions during rapid turns; visual silhouettes
 // remain visible when a genuinely re-detected candidate exists.
 liveFeatures=candidate&&motionState.may_add_feature_evidence&&($('liveLettering')?.checked||$('liveDetails')?.checked)?
   featureTracker?.update?.(window.CPCSurfaceFeatures.scan(p,160,200,focusMetrics?{box:roi}:candidate))||[]:[];
 // Evaluate exposure/patchy light/chromatic deposits on the candidate stone surface only.
 // These flags describe appearance; they never identify lichen, algae, mildew or stains.
 surfaceConditions=window.CPCSurfaceConditions?.analyze?.(p,160,200,focusMetrics?{box:roi}:candidate||null)||null;
 // If the user enables preview enhancement, favor stone-face exposure over bright
 // sky and dark vegetation around it. Only change the displayed video CSS filter.
 if($('livePreviewEnhance')?.checked&&surfaceConditions?.preview&&!focusMetrics){
   video.style.filter='brightness('+surfaceConditions.preview.brightness+') contrast('+surfaceConditions.preview.contrast+')';
 }
 if(focusMetrics)video.style.filter='';
 ctx.clearRect(0,0,w,h);
 if(focusMetrics){
   // Only improve the tapped patch in the LIVE overlay. Draw full-resolution
   // video through a clipped window; the rest of the scene remains visible
   // and completely unchanged. Capture always saves the untouched source.
   const a=point([roi.x,roi.y]),b=point([roi.x+roi.w,roi.y+roi.h]);
   ctx.save();ctx.beginPath();ctx.rect(a[0],a[1],b[0]-a[0],b[1]-a[1]);ctx.clip();
   if($('livePreviewEnhance')?.checked){
     ctx.filter='contrast(1.21) brightness(1.045)';
     ctx.drawImage(video,vr.x,vr.y,vr.w,vr.h);
     ctx.filter='none';
   }
   ctx.restore();
   ctx.save();ctx.strokeStyle='rgba(255,219,69,.95)';ctx.lineWidth=2.1;
   ctx.setLineDash([5,3]);ctx.strokeRect(a[0],a[1],b[0]-a[0],b[1]-a[1]);ctx.restore();
 }
 if($('liveMonuments')?.checked){
   // Focus on one stable, upright stone; suppress unrelated floating rectangles.
   ctx.save();ctx.setLineDash([]);ctx.lineWidth=3;
   if(candidate?.points?.length){
     ctx.strokeStyle='#ffdb45';ctx.lineWidth=3.3;
     const first=point(candidate.points[0]);ctx.beginPath();ctx.moveTo(first[0],first[1]);
     for(let i=1;i<candidate.points.length;i++){const pt=point(candidate.points[i]);ctx.lineTo(pt[0],pt[1]);}
     ctx.closePath();ctx.stroke();
   }
   ctx.restore();
 }
 if(candidate&&liveFeatures.length){
   ctx.save();ctx.setLineDash([]);
   for(const f of liveFeatures){
     const isLetter=f.kind==='letter_like_stroke_unverified';
     if(isLetter&&!$('liveLettering')?.checked)continue;
     if(!isLetter&&!$('liveDetails')?.checked)continue;
     if(isLetter){
       // Highlight real connected stroke pixels (not the whole rectangular letter box).
       // These remain unverified high-contrast shapes, not deciphered characters.
       ctx.fillStyle='rgba(255,216,45,.53)';
       for(const [x,y,len] of f.strokes||[]){
         const a=point([x/160,y/200]),b=point([(x+len)/160,(y+1)/200]);
         ctx.fillRect(a[0],a[1],Math.max(1,b[0]-a[0]),Math.max(1,b[1]-a[1]));
       }
     }else{
       const a=point([f.x,f.y]),b=point([f.x+f.w,f.y+f.h]);
       ctx.strokeStyle='rgba(255,216,45,.8)';ctx.lineWidth=1.4;ctx.strokeRect(a[0],a[1],b[0]-a[0],b[1]-a[1]);
     }
   }
   ctx.restore();
 }
 if($('liveLettering')?.checked&&latestAnalysis&&!focusMetrics){
   ctx.save();ctx.setLineDash([3,5]);ctx.strokeStyle='rgba(255,219,69,.65)';ctx.lineWidth=1.4;
   for(const r of latestAnalysis.textRegions){const a=point([r.x,r.y+r.h]),b=point([r.x+r.w,r.y+r.h]);ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();}
   ctx.restore();
 }
 ctx.lineWidth=2;ctx.strokeStyle='#f4d48c';ctx.fillStyle='rgba(244,212,140,.12)';ctx.setLineDash([5,5]);
 // No floating circles: detail candidates remain in the status summary until real surface contours are available.
 ctx.setLineDash([]);for(const a of annotations){const x=a.x*w,y=a.y*h;ctx.strokeStyle='#7ce1b7';ctx.lineWidth=3;ctx.beginPath();ctx.arc(x,y,22,0,Math.PI*2);ctx.stroke();ctx.fillStyle='#082b20';ctx.fillRect(Math.min(w-145,x+18),Math.max(0,y-24),138,27);ctx.fillStyle='#def8e8';ctx.font='12px system-ui';ctx.fillText(a.label.slice(0,18),Math.min(w-141,x+22),Math.max(18,y-7))}
 const m=latestMonuments.length,letter=latestAnalysis?.textRegions.length||0;
 const potential=latestMonuments.filter(r=>r.classification==='possible_monument_shape').length;
 const letterFeatures=liveFeatures.filter(f=>f.kind==='letter_like_stroke_unverified').length;
 const carvings=liveFeatures.filter(f=>f.kind==='carving_or_surface_detail_unverified').length;
 status.textContent='LIVE: '+m+' outlines, '+potential+' monument-like shapes. '+(lockedTrackId!==null?'Target locked. ':'')+letterFeatures+' letter-like strokes, '+carvings+' surface details. Shapes are unverified; no name or symbol identified.';
 if($('liveTargetStatus'))$('liveTargetStatus').textContent=
  (focusMetrics?'Detail focus active: examining the tapped part of this stone. Other areas remain visible but are not analyzed for engraving. ':
   lockedTrackId!==null?'Stone manually locked. ':candidate?'Stone outline acquired. ':'Seeking stable upright stone. ')+
  (motionState.motion==='rapid'?'Phone turning quickly; hold steady to confirm details.':
   motionState.motion==='moving'?'Phone moving; outline updates require stronger visual agreement.':
   motionState.motion==='steady'?'Phone steady; refining inscription evidence.':
   'Motion unavailable; using image-only tracking.');
 if($('liveFocusStatus'))$('liveFocusStatus').textContent=focusMetrics?
   'Investigating selected area · '+liveFeatures.filter(f=>f.kind==='letter_like_stroke_unverified').length+
   ' possible letter strokes · '+liveFeatures.filter(f=>f.kind!=='letter_like_stroke_unverified').length+
   ' other details · no characters or symbols confirmed.':
   candidate?'Entire stone under observation. Tap any point on it to inspect that area.':
   'Searching for a stone. Tap a visible yellow outline when it appears.';
 if($('liveQuality'))$('liveQuality').textContent=surfaceConditions?.advice?.[0]||latestAnalysis?.advice[0]||'Live preview quality appears usable; check lettering at full resolution after capture.';
 if($('liveSurfaceStatus'))$('liveSurfaceStatus').textContent=surfaceConditions?.flags?.length?'Surface observation: '+surfaceConditions.flags.map(f=>f.replaceAll('_',' ')).join('; ')+'. Color and lighting estimates only; no growth or moisture identified.':'Surface observation: no strong lighting or colored-patch flags in this view.';
 lastDraw=Date.now();
}
function start(){if(running)return;running=true;scanTick=0;cycle();timer=setInterval(cycle,240);$('liveDiscovery').checked=true;}
function stop(){running=false;visualTracker?.reset?.();visualStone=null;lastGray=null;lastMapping=null;lastCandidateList=[];focusRegion=null;focusMetrics=null;scanTick=0;lockedTrackId=null;autoStoneId=null;autoStoneHits=0;featureTracker?.reset?.();liveFeatures=[];surfaceConditions=null;if(timer)clearInterval(timer);timer=null;tracks=[];latest=[];latestAnalysis=null;latestMonuments=[];contourTracker?.reset?.();video.style.filter='';canvas.classList.remove('enabled');ctx.clearRect(0,0,canvas.width,canvas.height);status.textContent='Live analysis paused.';}
function saveAnnotation(){const id=$('symbolChoice').value,record=catalog.find(c=>c[0]===id);if(!record){status.textContent='Choose a symbol from the reference first.';return}
 const x=Number($('markX').value),y=Number($('markY').value);annotations.push({x,y,symbol_id:id,label:record[1],interpretation:record[2],source:'User-supplied symbol identification',source_document:'Scan Nov 8, 2026 at 7.00 PM.pdf',source_page:record[3],review_status:'unreviewed',created_at:new Date().toISOString()});status.textContent=`Marked ${record[1]} based on your selection; not auto-identified.`;$('markPanel').hidden=true;manual=false;canvas.classList.remove('enabled');cycle()}
const chooser=$('symbolChoice');for(const c of catalog){let option=document.createElement('option');option.value=c[0];option.textContent=c[1];chooser.appendChild(option)}
chooser.addEventListener('change',()=>{const c=catalog.find(c=>c[0]===chooser.value);$('symbolDescription').textContent=c?`${c[2]} — reference PDF p. ${c[3]}`:''});
function pointInPolygon(x,y,polygon){
 let inside=false;
 for(let i=0,j=polygon.length-1;i<polygon.length;j=i++){
  const a=polygon[i],b=polygon[j];
  if(((a[1]>y)!==(b[1]>y))&&x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0])inside=!inside;
 }
 return inside;
}
function tapTarget(event){
 if(!running||manual||!lastMapping||!lastGray)return false;
 const rect=canvas.getBoundingClientRect(),m=lastMapping;
 const x=event.clientX-rect.left,y=event.clientY-rect.top;
 const vx=(x-m.vr.x)/m.vr.w*m.videoWidth,vy=(y-m.vr.y)/m.vr.h*m.videoHeight;
 const nx=(m.scanX+vx*m.scale)/160,ny=(m.scanY+vy*m.scale)/200;
 if(nx<0||nx>1||ny<0||ny>1)return false;
 const possible=[...(visualStone?[visualStone]:[]),...lastCandidateList];
 const hits=possible.filter(c=>c?.points?.length&&
   (pointInPolygon(nx,ny,c.points)||
   (nx>=c.box.x-.013&&nx<=c.box.x+c.box.w+.013&&ny>=c.box.y-.013&&ny<=c.box.y+c.box.h+.013)));
 if(!hits.length)return false;
 // Choose the smallest overlapping detected region; this makes an explicitly tapped
 // neighboring stone win over an overlapping larger stone when both are candidates.
 hits.sort((a,b)=>a.box.w*a.box.h-b.box.w*b.box.h);
 const selected=hits[0];
 // Do not reset optical history when the operator taps a feature on the same
 // stone. The tap instead anchors a detail area relative to the moving stone.
 const same=visualStone&&(
   selected.persistent_lock_id===visualStone.persistent_lock_id||
   (Math.abs(selected.box.x-visualStone.box.x)<.035&&Math.abs(selected.box.y-visualStone.box.y)<.035&&Math.abs(selected.box.w-visualStone.box.w)<.045));
 const found=same?visualStone:visualTracker.select(selected,lastGray,160,200);
 if(!found)return false;
 visualStone=found;lockedTrackId=found.persistent_lock_id;
 focusRegion=window.CPCFocusRegion?.fromTap?.(found,nx,ny)||null;
 featureTracker?.reset?.();
 $('liveLockTarget').textContent='Unlock target';
 if($('liveTargetStatus'))$('liveTargetStatus').textContent='Investigating this part of the selected stone. Yellow area marks the live analysis region.';
 status.textContent='Focused on tapped feature. Attempting to refine local letter strokes and surface contrast; no inscription or symbol has been identified.';
 cycle();
 return true;
}
$('markSymbol').addEventListener('click',()=>{if(!running){status.textContent='Enable live analysis and camera first.';return}manual=true;canvas.classList.add('enabled');status.textContent='Tap the carving in the camera view to place a reference annotation.'});
canvas.addEventListener('click',e=>{if(!manual){tapTarget(e);return;}const r=canvas.getBoundingClientRect();$('markX').value=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width));$('markY').value=Math.max(0,Math.min(1,(e.clientY-r.top)/r.height));$('markPanel').hidden=false;manual=false;canvas.classList.remove('enabled')});
$('saveSymbol').addEventListener('click',saveAnnotation);$('cancelSymbol').addEventListener('click',()=>{$('markPanel').hidden=true;manual=false;canvas.classList.remove('enabled')});
$('clearSymbols').addEventListener('click',()=>{annotations=[];cycle();status.textContent='Annotations cleared for next monument.'});
$('liveDiscovery').addEventListener('change',e=>e.target.checked?start():stop());
$('liveFocusWhole')?.addEventListener('click',()=>{
 focusRegion=null;focusMetrics=null;featureTracker?.reset?.();
 if($('liveFocusStatus'))$('liveFocusStatus').textContent='Whole stone: engraving and surface analysis returned to the full detected monument.';
 if(running)cycle();
});
$('liveLockTarget')?.addEventListener('click',()=>{
 if(lockedTrackId!==null){lockedTrackId=null;focusRegion=null;focusMetrics=null;featureTracker?.reset?.();$('liveLockTarget').textContent='Lock detected stone';return}
 const candidate=visualTracker?.current?.();
 if(!candidate){status.textContent='No stable monument-like shape yet. Move closer or improve the angle.';return}
 lockedTrackId=candidate.persistent_lock_id;featureTracker?.reset?.();$('liveLockTarget').textContent='Unlock target';cycle();
});
// No automatic label claims. Working visual-interest indicators and user-tagged references only.
window.CPCDiscovery={start,stop,getAnnotations:()=>annotations.map(a=>({...a})),
 snapshot:()=>({analysis_version:latestAnalysis?.version||null,focus_region_engine:window.CPCFocusRegion?.VERSION||null,focus_target:focusMetrics?{...focusMetrics}:null,focus_command:focusRegion?{kind:focusRegion.kind,u:focusRegion.u,v:focusRegion.v,stone_id:focusRegion.stone_id}:null,visual_lock_engine:window.CPCVisualLock?.VERSION||null,visual_lock_state:visualStone?.tracking_state||'searching',motion_guidance:window.CPCMotionLock?.status?.()?.motion||'unknown',motion_assist_version:window.CPCMotionLock?.VERSION||null,surface_conditions:surfaceConditions?{...surfaceConditions,preview:undefined}:null,surface_feature_version:window.CPCSurfaceFeatures?.VERSION||null,live_feature_count:liveFeatures.length,locked_target_track_id:lockedTrackId,contour_engine_version:window.CPCPixelContours?.VERSION||null,visual_region_count:latest.length,text_like_region_count:latestAnalysis?.textRegions.length||0,possible_outline_count:latestMonuments.length,quality:latestAnalysis?.quality||null,analysis_status:'heuristic_unverified',enhancement_applies_only_to_preview:true}),
 clear:()=>{annotations=[];manual=false;canvas.classList.remove('enabled');$('markPanel').hidden=true},
 catalog:catalog.map(c=>({id:c[0],name:c[1],meaning:c[2],source_page:c[3]}))};
})();
