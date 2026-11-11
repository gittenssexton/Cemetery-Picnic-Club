// node tests/test_camera_inscription_reading.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
function load(file){const ctx={module:{exports:{}}};vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../web/camera',file),'utf8'),ctx);return ctx.module.exports}
const reading=load('inscription-reader.js'),geometry=load('reading-geometry.js');
assert.equal(reading.VERSION,'CPC_INSCRIPTION_READER_2D_V1');
assert.equal(geometry.VERSION,'CPC_READING_GEOMETRY_V1');
const w=250,h=100,rgba=new Uint8Array(w*h*4);
for(let i=0;i<w*h;i++){rgba[i*4]=rgba[i*4+1]=rgba[i*4+2]=230;rgba[i*4+3]=255}
let column=10;for(const symbol of 'STONE'){const glyph=reading.FONT[symbol];for(let y=0;y<7;y++)for(let x=0;x<5;x++)if(glyph[y][x]==='1')for(let yy=0;yy<4;yy++)for(let xx=0;xx<4;xx++){const k=((20+y*4+yy)*w+column+x*4+xx)*4;rgba[k]=rgba[k+1]=rgba[k+2]=10}column+=26}
const result=reading.recognize(rgba,w,h);
assert.equal(result.text,'STONE','Controlled synthetic engraving-like letters should be transcribed');
assert.equal(result.status,'unverified_template_reading');
assert.equal(result.recognized_character_count,5);
assert.equal(reading.recognize(new Uint8Array(w*h*4).fill(120),w,h).status,'insufficient_contrast');
const quad=[[0,0],[w-1,0],[w-1,h-1],[0,h-1]],center=geometry.quadMap(quad,.5,.5);
assert.ok(Math.abs(center.x-124.5)<.001);
assert.ok(Math.abs(center.y-49.5)<.001);
const straight=geometry.rectify(rgba,w,h,quad,120,80);
assert.equal(straight.data.length,120*80*4);
assert.match(straight.method,/planar/);
assert.throws(()=>geometry.rectify(rgba,w,h,[[0,0]],120,80),/Invalid/);
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
assert.ok(html.includes('inscription-reader.js'));
assert.ok(html.includes('reading-geometry.js'));
assert.ok(html.includes('id="readInscription2d"'));
assert.ok(html.includes('id="readInscriptionPlane"'));
assert.ok(html.includes('reading_attempts'));
assert.ok(!html.includes('machine_verified_inscription'));
new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
console.log('2D character candidates and perspective-normalized reading paths passed');
