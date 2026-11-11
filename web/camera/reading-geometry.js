/* CPC perspective-normalized inscription surface.
   Planar four-corner rectification from original image pixels.
   This is projective 2D geometry informed by an assumed stone plane, NOT
   a measured 3D mesh or groove depth. No generative content. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCReadingGeometry=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_READING_GEOMETRY_V1';
function quadMap(points,u,v){
 if(!Array.isArray(points)||points.length!==4)return null;
 // Source vertices: top-left, top-right, bottom-right, bottom-left.
 const [a,b,c,d]=points;const dx1=b[0]-c[0],dy1=b[1]-c[1],dx2=d[0]-c[0],dy2=d[1]-c[1],
 dx3=a[0]-b[0]+c[0]-d[0],dy3=a[1]-b[1]+c[1]-d[1];
 const determinant=dx1*dy2-dx2*dy1;
 let g=0,h=0;
 if(Math.abs(dx3)+Math.abs(dy3)>1e-8){
  if(Math.abs(determinant)<1e-8)return null;
  g=(dx3*dy2-dx2*dy3)/determinant;h=(dx1*dy3-dx3*dy1)/determinant;
 }
 const aa=b[0]-a[0]+g*b[0],bb=d[0]-a[0]+h*d[0],cc=a[0],
 dd=b[1]-a[1]+g*b[1],ee=d[1]-a[1]+h*d[1],ff=a[1],
 denom=g*u+h*v+1;if(!Number.isFinite(denom)||Math.abs(denom)<1e-9)return null;
 return{x:(aa*u+bb*v+cc)/denom,y:(dd*u+ee*v+ff)/denom};
}
function rectify(src,w,h,points,outW=360,outH=480){
 if(!src||src.length<w*h*4||!Number.isInteger(w)||!Number.isInteger(h)||points?.length!==4)throw Error('Invalid planar photo and corners');
 if(outW<12||outH<12||outW>1000||outH>1000)throw Error('Invalid rectified size');
 const out=new Uint8ClampedArray(outW*outH*4);
 const nearest=(x,y,chan)=>src[(Math.max(0,Math.min(h-1,y))*w+Math.max(0,Math.min(w-1,x)))*4+chan];
 for(let y=0;y<outH;y++)for(let x=0;x<outW;x++){
  const q=quadMap(points,(x+.5)/outW,(y+.5)/outH);
  if(!q||q.x<0||q.y<0||q.x>=w-1||q.y>=h-1)continue;
  const x0=Math.floor(q.x),y0=Math.floor(q.y),fx=q.x-x0,fy=q.y-y0;
  const k=(y*outW+x)*4;
  for(let c=0;c<3;c++)out[k+c]=nearest(x0,y0,c)*(1-fx)*(1-fy)+nearest(x0+1,y0,c)*fx*(1-fy)+nearest(x0,y0+1,c)*(1-fx)*fy+nearest(x0+1,y0+1,c)*fx*fy;
  out[k+3]=255;
 }
 return{version:VERSION,width:outW,height:outH,data:out,method:'planar_four_corner_projective_correction',limitations:'Assumes flat engraving face and correctly ordered four corners; not actual three-dimensional reconstruction.'};
}
return{VERSION,quadMap,rectify};
});
