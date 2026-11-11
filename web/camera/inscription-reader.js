/* CPC deterministic inscription reader, proof-of-concept.
   Pixel-font prototype matching, NOT neural OCR / not an AI, no external network.
   Character candidates MUST remain unverified. Preserve original source photographs. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;if(root)root.CPCInscriptionReader=api;})(typeof window!=='undefined'?window:null,function(){'use strict';
const VERSION='CPC_INSCRIPTION_READER_2D_V1';
const FONT={
A:['01110','10001','10001','11111','10001','10001','10001'],
B:['11110','10001','10001','11110','10001','10001','11110'],
C:['01111','10000','10000','10000','10000','10000','01111'],
D:['11110','10001','10001','10001','10001','10001','11110'],
E:['11111','10000','10000','11110','10000','10000','11111'],
F:['11111','10000','10000','11110','10000','10000','10000'],
G:['01111','10000','10000','10111','10001','10001','01111'],
H:['10001','10001','10001','11111','10001','10001','10001'],
I:['11111','00100','00100','00100','00100','00100','11111'],
J:['00111','00010','00010','00010','10010','10010','01100'],
K:['10001','10010','10100','11000','10100','10010','10001'],
L:['10000','10000','10000','10000','10000','10000','11111'],
M:['10001','11011','10101','10101','10001','10001','10001'],
N:['10001','11001','10101','10011','10001','10001','10001'],
O:['01110','10001','10001','10001','10001','10001','01110'],
P:['11110','10001','10001','11110','10000','10000','10000'],
Q:['01110','10001','10001','10001','10101','10010','01101'],
R:['11110','10001','10001','11110','10100','10010','10001'],
S:['01111','10000','10000','01110','00001','00001','11110'],
T:['11111','00100','00100','00100','00100','00100','00100'],
U:['10001','10001','10001','10001','10001','10001','01110'],
V:['10001','10001','10001','10001','10001','01010','00100'],
W:['10001','10001','10001','10101','10101','10101','01010'],
X:['10001','10001','01010','00100','01010','10001','10001'],
Y:['10001','10001','01010','00100','00100','00100','00100'],
Z:['11111','00001','00010','00100','01000','10000','11111'],
0:['01110','10011','10101','10101','11001','10001','01110'],
1:['00100','01100','00100','00100','00100','00100','01110'],
2:['01110','10001','00001','00010','00100','01000','11111'],
3:['11110','00001','00001','01110','00001','00001','11110'],
4:['00010','00110','01010','10010','11111','00010','00010'],
5:['11111','10000','10000','11110','00001','00001','11110'],
6:['01110','10000','10000','11110','10001','10001','01110'],
7:['11111','00001','00010','00100','01000','01000','01000'],
8:['01110','10001','10001','01110','10001','10001','01110'],
9:['01110','10001','10001','01111','00001','00001','01110']
};
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
function glyphScore(mask,w,h,box,pattern){
 const rows=pattern, cols=rows[0].length;
 let error=0,total=0;
 for(let y=0;y<7;y++)for(let x=0;x<5;x++){
 const x0=box.x+Math.floor(x*box.w/cols),x1=box.x+Math.max(1,Math.ceil((x+1)*box.w/cols));
 const y0=box.y+Math.floor(y*box.h/7),y1=box.y+Math.max(1,Math.ceil((y+1)*box.h/7));
 let ink=0,n=0;
 for(let yy=y0;yy<Math.min(h,y1);yy++)for(let xx=x0;xx<Math.min(w,x1);xx++){ink+=mask[yy*w+xx];n++}
 const observed=n?ink/n:0,expected=rows[y][x]==='1'?1:0;
 error+=Math.abs(expected-observed);total++;
 }
 return clamp(1-error/total,0,1);
}
function segment(mask,w,h){
 const lines=[],rows=new Uint16Array(h);
 for(let y=0;y<h;y++)for(let x=0;x<w;x++)rows[y]+=mask[y*w+x];
 let start=-1;
 for(let y=0;y<=h;y++){
 const present=y<h&&rows[y]>0;
 if(present&&start<0)start=y;
 if(!present&&start>=0){if(y-start>=4)lines.push({y:start,h:y-start});start=-1}
 }
 const out=[];
 for(const line of lines){
 const columns=new Uint16Array(w);
 for(let x=0;x<w;x++)for(let y=line.y;y<line.y+line.h;y++)columns[x]+=mask[y*w+x];
 let col=-1,items=[];
 for(let x=0;x<=w;x++){const present=x<w&&columns[x]>0;if(present&&col<0)col=x;
 if(!present&&col>=0){const width=x-col;if(width>=2){let top=h,bottom=0;
 for(let yy=line.y;yy<line.y+line.h;yy++)for(let xx=col;xx<x;xx++)if(mask[yy*w+xx]){top=Math.min(top,yy);bottom=Math.max(bottom,yy)}
 if(top<=bottom)items.push({x:col,y:top,w:width,h:bottom-top+1})}col=-1}}
 if(items.length)out.push(items);
 }
 return out;
}
function recognize(rgba,w,h,box=null){
 if(!rgba||!Number.isInteger(w)||!Number.isInteger(h)||w<12||h<12||rgba.length<w*h*4)throw Error('Invalid inscription image');
 const b=box||{x:0,y:0,w:1,h:1},left=clamp(Math.floor(b.x*w),0,w-1),top=clamp(Math.floor(b.y*h),0,h-1),
 right=clamp(Math.ceil((b.x+b.w)*w),left+1,w),bottom=clamp(Math.ceil((b.y+b.h)*h),top+1,h);
 const sw=right-left,sh=bottom-top;if(sw>1100||sh>1100)return{version:VERSION,status:'region_too_large',candidates:[],text:''};
 const gray=new Uint8Array(sw*sh),hist=new Uint32Array(256);
 for(let y=0;y<sh;y++)for(let x=0;x<sw;x++){const k=((y+top)*w+x+left)*4,v=Math.round(.2126*rgba[k]+.7152*rgba[k+1]+.0722*rgba[k+2]);gray[y*sw+x]=v;hist[v]++}
 const n=sw*sh,mean=gray.reduce((a,b)=>a+b,0)/n;
 let sum=0;for(let i=0;i<256;i++)sum+=i*hist[i];
 let sB=0,wB=0,varianceMax=-1,threshold=127;
 for(let i=0;i<256;i++){wB+=hist[i];if(!wB)continue;const wF=n-wB;if(!wF)break;sB+=i*hist[i];
 const diff=sB/wB-(sum-sB)/wF,variance=wB*wF*diff*diff;if(variance>varianceMax){varianceMax=variance;threshold=i}}
 const contrast=Math.sqrt(gray.reduce((a,v)=>a+(v-mean)*(v-mean),0)/n);
 if(contrast<16)return{version:VERSION,status:'insufficient_contrast',candidates:[],text:'',contrast:Math.round(contrast)};
 const attempts=[];
 for(const dark of [true,false]){
 const mask=new Uint8Array(sw*sh);let ink=0;
 for(let i=0;i<mask.length;i++){mask[i]=dark?(gray[i]<threshold?1:0):(gray[i]>threshold?1:0);ink+=mask[i]}
 const fraction=ink/mask.length;
 if(fraction<.012||fraction>.55)continue;
 const lines=segment(mask,sw,sh),candidates=[];
 for(const line of lines.slice(0,8)){
  const letters=[];
  for(const r of line.slice(0,35)){
   if(r.h<5||r.h>sh*.55||r.w>r.h*1.5||r.w<r.h*.11)continue;
   const scored=Object.entries(FONT).map(([symbol,pattern])=>({symbol,score:glyphScore(mask,sw,sh,r,pattern)})).sort((a,b)=>b.score-a.score);
   const best=scored[0],second=scored[1];
   // Reject low fit and ambiguous letters rather than fabricating a transcription.
   const accepted=best.score>=.86&&(best.score-second.score)>=.035;
   letters.push({character:accepted?best.symbol:'?',score:+best.score.toFixed(3),ambiguous:!accepted,
    bounding_box:{x:(r.x+left)/w,y:(r.y+top)/h,w:r.w/w,h:r.h/h}});
  }
  if(letters.length>=2)candidates.push({characters:letters,text:letters.map(x=>x.character).join('')});
 }
 const good=candidates.reduce((a,l)=>a+l.characters.filter(c=>!c.ambiguous).length,0);
 attempts.push({candidates,good,dark});
 }
 attempts.sort((a,b)=>b.good-a.good);
 const best=attempts[0];
 return{version:VERSION,status:best?.good?'unverified_template_reading':'no_reliable_character_candidates',
  text:best?.good?best.candidates.map(c=>c.text).join(' / '):'',
  candidates:best?.candidates||[],recognized_character_count:best?.good||0,
  polarity:best?.dark?'dark_strokes':'light_strokes',threshold,contrast:Math.round(contrast),
  method:'deterministic_5x7_character_templates',
  limitations:'Not validated for engraved stone fonts; connected glyphs, damage, shading or perspective can cause errors. Never auto-assign a person or cemetery record.'};
}
return{VERSION,FONT,recognize,segment,glyphScore};
});
