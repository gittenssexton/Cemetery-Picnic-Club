/* CPC cemetery visual iconography evidence registry + radial motif detector v1.
   Labels/translations sourced from user's nine-page illustrated historical
   symbolism guide (Scan Nov 8 2026, PDF pages 3-7). No image glyphs copied.
   Shape classification is conservative: image evidence is unverified.
 */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCIconography=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_ICONOGRAPHY_V1';
const SOURCE={title:'Scan Nov 8, 2026 at 7.00 PM.pdf',drive_file_id:'1TDwejroxzYUY2-C8hzGaoHa9FCxtMUMo',scope:'illustrated gravestone symbolism reference'};
const entries=[
['scythe','Scythe',3,'time_mortality','curved blade attached to a handle'],
['hourglass','Hourglass',3,'time_mortality','two opposed chambers joined at narrow waist'],
['winged_hourglass','Winged hourglass',3,'time_mortality','hourglass with a wing shape on each side'],
['inverted_torch','Inverted torch',3,'time_mortality','flame-bearing torch pointing down'],
['crown','Crown',3,'faith_afterlife','symmetrical tiered crown with pointed tips'],
['book','Book or Bible',3,'faith_afterlife','two opposed open page forms'],
['pointing_hand','Hand pointing upward',3,'faith_afterlife','hand and upright pointing finger'],
['clasped_hands','Clasped hands',3,'faith_afterlife','paired hands joining'],
['lamb','Lamb',3,'faith_afterlife','small animal with four legs and woolly body'],
['anchor','Anchor',6,'faith_afterlife','vertical shank, cross arm and curved flukes'],
['heart','Heart',6,'faith_afterlife','bilaterally symmetric two-lobed heart outline'],
['gate','Gate or door',6,'faith_afterlife','upright opening with lintel or arch'],
['flowers','Flowers',6,'plants_trees','blossoms on stems'],
['cut_flower','Flower cut by scythe',6,'plants_trees','cut or downward drooping blossom with cutting blade'],
['rose','Rose',6,'plants_trees','layered flower petals'],
['rosebud','Rosebud or broken bud',6,'plants_trees','small closed or broken flower bud'],
['fleur_de_lis','Fleur-de-lis',6,'plants_trees','symmetric three-petal stylized lily'],
['grapes','Grapes',6,'plants_trees','hanging bunch of rounded berries'],
['vines','Vines',5,'plants_trees','repeating curved stems with attached leaves'],
['ivy','Ivy',5,'plants_trees','climbing vine with ivy leaves'],
['leaves','Leaves',5,'plants_trees','leaf shapes along stems'],
['branches','Branches',5,'plants_trees','forked woody stems'],
['palm','Palm branches or palmettes',5,'plants_trees','long curved frond with tapered leaves'],
['wheat','Wheat',5,'plants_trees','vertical stem with repeated grain heads'],
['oak','Oak leaves and acorns',5,'plants_trees','lobed leaves and acorn shapes'],
['willow','Weeping willow',5,'plants_trees','downward drooping tree branches'],
['tree_of_life','Tree of Life',5,'plants_trees','upright branching tree form'],
['broken_tree','Broken or cut tree',5,'plants_trees','trunk with abruptly cut or broken top'],
['pinwheel','Pinwheel',7,'geometric_ornamental','circular border with rotating curved vanes or blades'],
['rosette','Rosette',7,'geometric_ornamental','circular flower of radial pointed petal forms'],
['scallops','Scallops',7,'geometric_ornamental','repeating rows of small concave or convex arcs'],
['diamonds','Diamonds',7,'geometric_ornamental','horizontal repetition of linked lozenge shapes'],
['stars','Stars',7,'geometric_ornamental','five-or-more radiating sharp points'],
['scrolls','Scrolls',7,'geometric_ornamental','symmetrical curled scroll ends'],
['urn','Urn',7,'monuments_architecture','symmetrical lidded vessel with curved sides and foot'],
['broken_column','Broken column',7,'monuments_architecture','upright cylindrical pedestal with fractured top'],
['obelisk','Obelisk',7,'monuments_architecture','slender tapering pillar ending in pointed tip']
].map(([id,label,pdf_page,group,visual_pattern])=>({id,label,pdf_page,group,visual_pattern,
 source_id:SOURCE.drive_file_id,verified_visual_template:false,interpretation_status:'source_text_context_not_shape_proof'}));
const byId=Object.fromEntries(entries.map(e=>[e.id,e]));
function classifyCircularRegion(rgba,w,h,box){
 if(!rgba||rgba.length<w*h*4||!box||box.w*w<12||box.h*h<12)return null;
 const cx=(box.x+box.w/2)*w,cy=(box.y+box.h/2)*h,rx=box.w*w/2,ry=box.h*h/2;
 if(Math.min(rx,ry)<7)return null;
 const K=24,R=[.28,.45,.64],profiles=R.map(()=>new Array(K).fill(0));
 const sample=(x,y)=>{x=Math.max(0,Math.min(w-1,Math.round(x)));y=Math.max(0,Math.min(h-1,Math.round(y)));const i=(y*w+x)*4;return .2126*rgba[i]+.7152*rgba[i+1]+.0722*rgba[i+2]};
 const vals=[];
 for(let ring=0;ring<R.length;ring++)for(let k=0;k<K;k++){
  const theta=k*2*Math.PI/K,r=R[ring],xx=cx+Math.cos(theta)*rx*r,yy=cy+Math.sin(theta)*ry*r;
  const v=(sample(xx,yy)+sample(xx+1,yy)+sample(xx,yy+1))/3;
  profiles[ring][k]=v;vals.push(v);
 }
 const avg=vals.reduce((a,b)=>a+b,0)/vals.length;
 const dispersion=Math.sqrt(vals.reduce((a,b)=>a+(b-avg)**2,0)/vals.length);
 if(dispersion<14)return null; // Blank disk, uniform stone, or insufficient texture.
 const rows=profiles.map(row=>{const m=row.reduce((a,b)=>a+b,0)/K;return row.map(v=>m-v)});
 const corr=(a,b,shift)=>{let num=0,aa=0,bb=0;for(let k=0;k<K;k++){const x=a[k],y=b[(k+shift+K)%K];num+=x*y;aa+=x*x;bb+=y*y}return num/Math.sqrt(Math.max(1e-6,aa*bb))};
 let best={score:-2,shift:0};
 for(let shift=-7;shift<=7;shift++){const score=corr(rows[0],rows[2],shift);if(score>best.score)best={score,shift}}
 const radialConsistency=corr(rows[0],rows[2],0);
 // A radial ring pattern with a stable angular shift may indicate curving
 // blades; aligned rings may indicate petals. Both are susceptible to stain,
 // cracks and lighting artifacts, therefore no exact symbol assignment here.
 const directionalShift=Math.abs(best.shift);
 const hasOrganizedPattern=best.score>.52&&dispersion>=16;
 if(!hasOrganizedPattern)return null;
 const candidates=directionalShift>=2&&best.score-radialConsistency>.19?
 ['pinwheel','rosette']:['rosette','pinwheel'];
 return {kind:'circular_radial_ornament_candidate_unverified',
   candidates:candidates.map(id=>({id,label:byId[id].label,pdf_page:byId[id].pdf_page})),
   evidence:{angular_correlation:+best.score.toFixed(3),shift_bins:best.shift,radial_consistency:+radialConsistency.toFixed(3),local_contrast:+dispersion.toFixed(1)},
   status:'shape_family_only_unverified',box:{...box},source_id:SOURCE.drive_file_id};
}
return{VERSION,SOURCE,entries,byId,classifyCircularRegion};
});
