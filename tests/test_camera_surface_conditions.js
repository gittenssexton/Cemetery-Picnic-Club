// node tests/test_camera_surface_conditions.js
'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const s=fs.readFileSync(path.join(__dirname,'../web/camera/surface-conditions.js'),'utf8');
const ctx={module:{exports:{}}};vm.runInNewContext(s,ctx);
const {VERSION,analyze}=ctx.module.exports;assert.equal(VERSION,'CPC_SURFACE_CONDITIONS_V1');
const w=160,h=200;function make(color){const b=new Uint8Array(w*h*4);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const p=(y*w+x)*4,c=color(x,y);b[p]=c[0];b[p+1]=c[1];b[p+2]=c[2];b[p+3]=255;}return b}
const even=analyze(make(()=>[132,132,132]),w,h),patch=analyze(make((x)=>x<80?[48,50,49]:[197,197,197]),w,h);
const green=analyze(make(x=>x<70?[45,133,58]:[130,130,130]),w,h);
const glare=analyze(make(x=>x<65?[255,255,255]:[130,130,130]),w,h);
assert.ok(!even.flags.includes('patchy_illumination_candidate'));
assert.ok(patch.flags.includes('patchy_illumination_candidate'));
assert.ok(green.flags.includes('green_surface_patches_unverified'));
assert.ok(glare.flags.includes('bright_reflections_or_clipped_highlights'));
assert.equal(even.metrics.green_chromatic_fraction,0);
assert.ok(patch.metrics.tile_luminance_range>100);
assert.ok(!('correctedPixels' in glare),'Original photographs must not be replaced');
assert.equal(green.caveat.includes('biological species'),true);
assert.throws(()=>analyze(new Uint8Array(12),w,h),/Invalid/);
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
assert.ok(html.includes('surface-conditions.js'));
assert.ok(html.includes('id="liveSurfaceStatus"'));
assert.ok(discovery.includes('CPCSurfaceConditions?.analyze'));
assert.ok(discovery.includes('surface_conditions:surfaceConditions?'));
new Function(discovery);new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
console.log('Cemetery surface diagnostics: illumination, colored patch, glare and non-destructive record tests passed');
