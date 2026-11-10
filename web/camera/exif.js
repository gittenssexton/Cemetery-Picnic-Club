/* Cemetery Picnic Club — dependency-free EXIF GPS appender for browser-encoded JPEG frames.
   Adds metadata to an exported copy only. Original full-frame JPEG bytes are retained. */
(function(root){'use strict';
  const asc=(a,s,offset)=>{for(let i=0;i<s.length;i++)a[offset+i]=s.charCodeAt(i)};
  function makeExif(lat,lon){
    const size=159,tiff=new Uint8Array(size),v=new DataView(tiff.buffer);
    asc(tiff,'II',0);v.setUint16(2,42,true);v.setUint32(4,8,true);
    v.setUint16(8,1,true);v.setUint16(10,0x8825,true);v.setUint16(12,4,true);v.setUint32(14,1,true);v.setUint32(18,26,true);v.setUint32(22,0,true);
    const gps=26;v.setUint16(gps,6,true);
    function entry(i,tag,type,count,val){let x=gps+2+i*12;v.setUint16(x,tag,true);v.setUint16(x+2,type,true);v.setUint32(x+4,count,true);v.setUint32(x+8,val,true);return x+8}
    let j=entry(0,0,1,4,0);tiff.set([2,3,0,0],j);
    j=entry(1,1,2,2,0);tiff[j]=lat<0?83:78;
    entry(2,2,5,3,104);
    j=entry(3,3,2,2,0);tiff[j]=lon<0?87:69;
    entry(4,4,5,3,128);
    entry(5,18,2,7,152);
    v.setUint32(gps+2+72,0,true);
    function writeDMS(value,offset){const n=Math.abs(value),deg=Math.floor(n),mins=Math.floor((n-deg)*60),sec=(n-deg-mins/60)*3600,vals=[[deg,1],[mins,1],[Math.round(sec*100000),100000]];vals.forEach(([num,den],i)=>{v.setUint32(offset+i*8,num,true);v.setUint32(offset+i*8+4,den,true)})}
    writeDMS(lat,104);writeDMS(lon,128);asc(tiff,'WGS-84\0',152);
    const exif=new Uint8Array(2+2+6+tiff.length),len=exif.length-2;exif.set([0xff,0xe1,(len>>>8)&255,len&255],0);asc(exif,'Exif\0\0',4);exif.set(tiff,10);return exif;
  }
  function addGPS(jpeg,lat,lon){
    if(!(jpeg instanceof Uint8Array))jpeg=new Uint8Array(jpeg);
    if(jpeg[0]!==0xff||jpeg[1]!==0xd8)throw new Error('Expected JPEG capture');
    if(!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)throw new Error('Invalid GPS coordinates');
    const exif=makeExif(lat,lon),res=new Uint8Array(jpeg.length+exif.length);res.set(jpeg.subarray(0,2));res.set(exif,2);res.set(jpeg.subarray(2),2+exif.length);return res;
  }
  root.CPCGeoTag={addGPS};
})(typeof window!=='undefined'?window:globalThis);
