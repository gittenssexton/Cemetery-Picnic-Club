/* CPC Silhouette pilot v0.1: self-contained color-region proposal on a captured photo.
   Not trained AI or a verified segmentation model. Never modifies original image. */
(function(root){'use strict';
 function median(a){a.sort((x,y)=>x-y);return a[Math.floor(a.length/2)]||0}
 function propose(img){
  const W=180,H=Math.max(120,Math.round(img.height*180/img.width));
  const c=document.createElement('canvas');c.width=W;c.height=H;const ctx=c.getContext('2d',{willReadFrequently:true});ctx.drawImage(img,0,0,W,H);
  const data=ctx.getImageData(0,0,W,H).data;
  function pix(x,y){const i=(y*W+x)*4;return[data[i],data[i+1],data[i+2]]}
  function sample(x0,x1,y0,y1,step=3){const samples=[[],[],[]];for(let y=Math.round(H*y0);y<H*y1;y+=step)for(let x=Math.round(W*x0);x<W*x1;x+=step){const v=pix(x,y);for(let k=0;k<3;k++)samples[k].push(v[k])}return samples.map(median)}
  const center=sample(.42,.58,.28,.65),left=sample(.02,.12,.28,.72),right=sample(.88,.98,.28,.72);
  const dist=(a,b)=>Math.hypot((a[0]-b[0])*.8,(a[1]-b[1])*1.15,(a[2]-b[2])*.9);
  const contrast=Math.min(dist(center,left),dist(center,right));
  if(contrast<20)return{ok:false,reason:'Low foreground/background color separation',contrast:+contrast.toFixed(1)};
  const n=W*H,prob=new Uint8Array(n),seen=new Uint8Array(n),queue=new Int32Array(n);
  for(let y=0;y<H;y++)for(let x=0;x<W;x++){
   const v=pix(x,y),fg=dist(v,center),bg=Math.min(dist(v,left),dist(v,right));
   // Compare foreground vs background appearance; limit overly dark shadows and bright highlights.
   if(fg<Math.max(42,contrast*.93)&&fg<bg*.96)prob[y*W+x]=1;
  }
  // Morphologically close small holes in the stone caused by lettering / lichen.
  const dilated=new Uint8Array(n),closed=new Uint8Array(n);
  for(let y=1;y<H-1;y++)for(let x=1;x<W-1;x++){
   const i=y*W+x;for(let dy=-1;dy<=1;dy++){for(let dx=-1;dx<=1;dx++){if(prob[i+dy*W+dx]){dilated[i]=1;break}}if(dilated[i])break}
  }
  for(let y=2;y<H-2;y++)for(let x=2;x<W-2;x++){
   const i=y*W+x;let yes=1;for(let dy=-1;dy<=1&&yes;dy++)for(let dx=-1;dx<=1;dx++)if(!dilated[i+dy*W+dx]){yes=0;break}closed[i]=yes;
  }
  // Component seeded in the interior of the chosen stone, not the largest dark background object.
  let seed=-1;outer:for(let off=0;off<35;off+=3){for(const sy of [.52,.42,.62,.32,.72]){
   const yy=Math.min(H-1,Math.round(H*sy));for(const sign of [-1,1]){
    const xx=Math.round(W/2+sign*off),idx=yy*W+xx;if(xx>1&&xx<W-2&&closed[idx]){seed=idx;break outer}
   }
  }}
  if(seed<0)return{ok:false,reason:'No central stone-like region found',contrast:+contrast.toFixed(1)};
  let head=0,tail=0;queue[tail++]=seed;seen[seed]=1;let minX=W,maxX=0,minY=H,maxY=0;
  while(head<tail){const cur=queue[head++],x=cur%W,y=(cur/W)|0;
   if(x<minX)minX=x;if(x>maxX)maxX=x;if(y<minY)minY=y;if(y>maxY)maxY=y;
   for(const nb of [cur-W,cur+W,cur-1,cur+1]){
    if(nb<0||nb>=n)continue;const nx=nb%W,ny=(nb/W)|0;if(Math.abs(nx-x)+Math.abs(ny-y)!==1)continue;
    if(closed[nb]&&!seen[nb]){seen[nb]=1;queue[tail++]=nb}
   }
  }
  const fraction=tail/n;
  if(fraction<.07||fraction>.79||minX<=2||maxX>=W-3||minY<=1||maxY>=H-2){return{ok:false,reason:'Segmentation ambiguous or stone touches frame boundary',contrast:+contrast.toFixed(1),coverage:+fraction.toFixed(2)}}
  // Trace approximate left/right boundary per horizontal strip, retaining the top arc profile.
  const ptsLeft=[],ptsRight=[],stride=3;for(let y=minY;y<=maxY;y+=stride){let l=W,r=-1;
   for(let x=minX;x<=maxX;x++){if(seen[y*W+x]){l=Math.min(l,x);r=Math.max(r,x)}}
   if(r>=l+4){ptsLeft.push([l,y]);ptsRight.push([r,y])}
  }
  if(ptsLeft.length<12)return{ok:false,reason:'Too few contour segments',contrast:+contrast.toFixed(1)};
  const poly=[...ptsLeft,...ptsRight.reverse()].map(([x,y])=>[Math.round(x*img.width/W),Math.round(y*img.height/H)]);
  return{ok:true,polygon:poly,algorithm:'central_color_region_connected_component_v01',status:'unverified_candidate',contrast:+contrast.toFixed(1),coverage:+fraction.toFixed(2),resolution:[W,H]};
 }
 root.CPCSilhouette={propose};
})(typeof window!=='undefined'?window:globalThis);
