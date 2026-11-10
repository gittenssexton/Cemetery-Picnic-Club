// node tests/test_camera_live_analysis.js
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const src=fs.readFileSync(path.join(__dirname,'../web/camera/live-analysis.js'),'utf8');
const context={module:{exports:{}}};vm.runInNewContext(src,context);const a=context.module.exports;
assert.equal(a.VERSION,'CPC_LIVE_ANALYSIS_V1');
function frame(v){const p=new Uint8Array(160*200*4);for(let i=0;i<p.length;i+=4){p[i]=p[i+1]=p[i+2]=v;p[i+3]=255}return p}
const dark=a.analyzeRGBA(frame(0),160,200);
assert.ok(dark.advice.some(x=>x.includes('Low light')));
assert.ok(dark.preview.brightness>1);
const bright=a.analyzeRGBA(frame(220),160,200);
assert.equal(bright.quality.mean_luminance,220);
assert.equal(bright.preview.brightness,.92);
assert.equal(bright.textRegions.length,0);
assert.throws(()=>a.analyzeRGBA(new Uint8Array(8),160,200));
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
for(const term of ['id="liveDiscovery" checked','id="liveMonuments" checked','id="liveLettering" checked','id="liveDetails" checked','id="livePreviewEnhance" checked','live_visual_evidence:window.CPCDiscovery','live-analysis.js','guided-capture.js']){
  assert.ok(html.includes(term),'Missing camera UI hook: '+term);
}
const discovery=fs.readFileSync(path.join(__dirname,'../web/camera/discovery.js'),'utf8');
for(const term of ["window.CPCLiveAnalysis","window.CPCGuidedCapture?.propose?.","video.style.filter=","canvas.classList.add('enabled')","canvas.classList.remove('enabled')","snapshot:"]){
  assert.ok(discovery.includes(term),'Missing live analysis hook: '+term);
}
new Function(html.slice(html.lastIndexOf('<script>\n')+9,html.lastIndexOf('</script>')));
new Function(discovery);
console.log('Live camera analysis and UI integration tests passed');
