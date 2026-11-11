/* CPC cemetery stone surface diagnostics v1.
 * Lightweight deterministic analysis of IMAGE APPEARANCE only:
 * exposure, patchy illumination, texture, chromatic deposits, and sheen.
 * Does not establish lichen/moss/mold species, moisture, material, or damage causes.
 * No original image pixels are changed.
 */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCSurfaceConditions=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_SURFACE_CONDITIONS_V1';
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
const round=v=>Math.round(v*1000)/1000;
function analyze(rgba,w,h,region){
 if(!rgba||!Number.isInteger(w)||!Number.isInteger(h)||w<32||h<32||rgba.length<w*h*4)throw Error('Invalid surface frame');
 const b=region?.box||{x:0,y:0,w:1,h:1},x0=clamp(Math.floor(b.x*w),0,w-1),y0=clamp(Math.floor(b.y*h),0,h-1),
 x1=clamp(Math.ceil((b.x+b.w)*w),x0+1,w),y1=clamp(Math.ceil((b.y+b.h)*h),y0+1,h);
 const tw=4,th=4,tiles=new Array(tw*th).fill(null).map(()=>({sum:0,sumSq:0,count:0,edge:0,green:0,warm:0,black:0,white:0}));
 let n=0,low=0,high=0,greens=0,warms=0,neutrals=0,brightNeutral=0,deep=0,sum=0,texture=0,textureN=0;
 const lum=(i)=>Math.round(.2126*rgba[i]+.7152*rgba[i+1]+.0722*rgba[i+2]);
 const values=new Uint8Array(w*h);
 for(let y=y0;y<y1;y++)for(let x=x0;x<x1;x++){
  const i=(y*w+x)*4,r=rgba[i],g=rgba[i+1],bl=rgba[i+2],v=lum(i);
  values[y*w+x]=v;
  const tileX=Math.min(tw-1,Math.floor((x-x0)*tw/(x1-x0))),tileY=Math.min(th-1,Math.floor((y-y0)*th/(y1-y0))),t=tiles[tileY*tw+tileX];
  const chroma=Math.max(r,g,bl)-Math.min(r,g,bl);
  const green=(g>r*1.12&&g>bl*1.07&&g-r>11);
  const warm=(r>g*1.12&&r>bl*1.3&&r-g>20);
  const neutral=chroma<28;
  t.count++;t.sum+=v;t.sumSq+=v*v;
  if(green){greens++;t.green++}
  if(warm){warms++;t.warm++}
  if(neutral)neutrals++;
  if(v<=20){low++;deep++;t.black++}
  if(v>=245){high++;if(neutral){brightNeutral++;t.white++}}
  sum+=v;n++;
 }
 for(let y=y0+1;y<y1-1;y+=2)for(let x=x0+1;x<x1-1;x+=2){
  const i=y*w+x,v=values[i],edge=Math.abs(values[i-1]-values[i+1])+Math.abs(values[i-w]-values[i+w]);
  texture+=edge;textureN++;
  const tx=Math.min(tw-1,Math.floor((x-x0)*tw/(x1-x0))),ty=Math.min(th-1,Math.floor((y-y0)*th/(y1-y0)));
  tiles[ty*tw+tx].edge+=edge;
 }
 const avg=n?sum/n:0,spatial=tiles.filter(t=>t.count>0).map(t=>t.sum/t.count);
 const spread=spatial.length?Math.max(...spatial)-Math.min(...spatial):0;
 const tileStd=spatial.length?Math.sqrt(spatial.reduce((s,v)=>s+(v-avg)**2,0)/spatial.length):0;
 const clippedShadow=low/Math.max(1,n),clippedHighlight=high/Math.max(1,n),
 chromaticGreen=greens/Math.max(1,n),chromaticWarm=warms/Math.max(1,n),specular=brightNeutral/Math.max(1,n);
 const uneven=spread>66&&tileStd>20;
 const flags=[];
 if(clippedHighlight>.045||specular>.028)flags.push('bright_reflections_or_clipped_highlights');
 if(clippedShadow>.085)flags.push('deep_shadow_detail_loss');
 if(uneven)flags.push('patchy_illumination_candidate');
 if(chromaticGreen>.055)flags.push('green_surface_patches_unverified');
 if(chromaticWarm>.065)flags.push('warm_colored_surface_deposits_unverified');
 if(avg<75)flags.push('low_average_luminance');
 const advice=[];
 if(flags.includes('bright_reflections_or_clipped_highlights'))advice.push('Bright reflections: shift the camera angle and take another photo.');
 if(flags.includes('patchy_illumination_candidate'))advice.push('Uneven lighting: move out of dappled shade if possible; keep a second angle.');
 if(flags.includes('green_surface_patches_unverified'))advice.push('Green surface areas: may be growth, pigment, or reflected foliage; record them without assuming a species.');
 if(flags.includes('warm_colored_surface_deposits_unverified'))advice.push('Colored patches: may be staining, growth, paint, or stone color; preserve the original view.');
 if(flags.includes('deep_shadow_detail_loss')||flags.includes('low_average_luminance'))advice.push('Deep shade: hold steady and try a different angle for the lettering.');
 if(!advice.length)advice.push('Surface exposure is usable; take an oblique-angle photo if letters remain faint.');
 // Capped GLOBAL correction for display only. No manufactured strokes, inpainting, or wetness inference.
 const preview={brightness:round(clamp(avg<65?1.15:avg<108?1.07:avg>206?.94:1,.9,1.17)),
 contrast:round(clamp(uneven?.99:tileStd<18?1.09:1,.95,1.11))};
 return {version:VERSION,region:{x:x0/w,y:y0/h,w:(x1-x0)/w,h:(y1-y0)/h},
 metrics:{mean_luminance:round(avg),tile_luminance_range:round(spread),tile_luminance_std:round(tileStd),
 clipped_shadow_fraction:round(clippedShadow),clipped_highlight_fraction:round(clippedHighlight),
 specular_candidate_fraction:round(specular),green_chromatic_fraction:round(chromaticGreen),
 warm_chromatic_fraction:round(chromaticWarm),neutral_fraction:round(neutrals/Math.max(1,n)),
 edge_energy:round(texture/Math.max(1,textureN))},
 flags,advice,preview,
 caveat:'Color and lighting only; no biological species, moisture, stone type, etching or inscription verified.'};
}
return {VERSION,analyze};
});
