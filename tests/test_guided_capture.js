// Run with node tests/test_guided_capture.js
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'../web/camera/guided-capture.js'),'utf8');
const context={module:{exports:{}}};vm.runInNewContext(code,context);
const g=context.module.exports;
assert.equal(g.VERSION,'CPC_GUIDED_CAPTURE_V1');
assert.equal(g.nextStep([],[]),'overview');
assert.equal(g.nextStep(['overview'],[]),'front');
assert.equal(g.nextStep(['overview','front'],[]),'inscription');
assert.equal(g.nextStep(['overview','front','inscription'],['carving']),'side');
assert.equal(g.nextStep(['overview','front','inscription','carving','side'],[]),'back');
assert.equal(g.nextStep(g.ORDER,[]),null);
const rect=g.rectangle(.5,.5,.3,.6);
assert.equal(rect.x,.35);assert.equal(rect.y,.2);
const edge=g.rectangle(.99,.01,.5,.9);
assert.ok(edge.x+edge.w<=1&&edge.y===0);
assert.throws(()=>g.rectangle(NaN,.5,.4,.6));
assert.equal(g.photoToView(50,50,100,100,100,200).x,.5);
assert.equal(g.photoToView(5,50,100,100,100,200),null);
assert.deepEqual([...g.propose(new Uint8Array(3),2,3)],[]);
const empty=new Uint8Array(160*200*4);
assert.ok(Array.isArray(g.propose(empty,160,200)));
assert.ok(g.DIRECTIONS.overview.includes('Step back'));
const html=fs.readFileSync(path.join(__dirname,'../web/camera/index.html'),'utf8');
for(const item of ['data-shot="overview"','overviewPickerPanel','overviewSelectionStatus','continueMonumentBtn','guidedProgress','guided_skip_reasons','selectedTarget','function selectOverviewTarget','function updateGuidedProgress','CPCGuidedCapture.propose']){
  assert.ok(html.includes(item),'Missing '+item);
}
assert.ok(html.includes("state.shotType==='overview'?[[0,0],[w,0],[w,h],[0,h]]"));
assert.ok(html.includes('id="screenTestMode"'));
assert.ok(html.includes("const g=(unlocated||screenTest)?null:getLocation()"));
assert.ok(html.includes("r.shot_type==='overview'?'Original overview':'Processed reference'"));
assert.ok(html.includes('reference_image_no_site_attribution'));
assert.ok(g.propose(new Uint8Array(160*200*4),160,200).length<=3);
console.log('Guided capture rules and camera wiring checks passed');
