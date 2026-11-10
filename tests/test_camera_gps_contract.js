/* Run: node tests/test_camera_gps_contract.js
 * Static integration checks to prevent regression of the provenance safeguards.
 * Does not substitute for browser / iPhone capture and ZIP inspection.
 */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.join(__dirname,'..');
const html=fs.readFileSync(path.join(root,'web/camera/index.html'),'utf8');
const sw=fs.readFileSync(path.join(root,'web/camera/sw.js'),'utf8');
const registry=fs.readFileSync(path.join(root,'web/camera/cemetery-sites.js'),'utf8');
let checks=0;
function has(needle){checks++;assert.ok(html.includes(needle),'Missing camera integration: '+needle)}
function absent(needle){checks++;assert.ok(!html.includes(needle),'Unsafe camera default: '+needle)}
has('<script src="cemetery-resolver.js"></script>');
has('<script src="cemetery-sites.js"></script>');
has('updateSiteMatch(g);');
has('cemetery_match:g&&g.source');
has('location_observation_id:');
has('location_observation:g?');
has("visibility:'restricted_by_default'");
has("observation_type:'photographer_device_position_not_grave_survey'");
has('horizontal_accuracy_m:g.accuracy_m??null');
has('cemetery_assignment:{');
has("verification_state:'unverified'");
has("assignment_method:state.siteSelection?'user_selected_unverified'");
has('site_name_entry:');
has('cemetery_candidate_catalog_version:');
has("function resetToCapture(){state.siteSelection=null;state.siteMatch=null;");
has("mask_type:r.polygon_provenance?.method");
has("location_status:g?(g.source==='manual'?'manual_unverified'");
has('device_gps_stale');
has('<script src="cemetery-relations.js"></script>');
has('cemetery_relationships_at_capture:state.siteSelection?');
has('savedSiteEvidence');
has('r.cemetery_assignment?.cemetery_entity_id');
has('No site ID assigned');
has('id="exportGpsExif"');
has("if($('exportGpsExif').checked&&r.location?.latitude!=null");
has("strip.export_privacy={gps_exif_copy_included:false");
has('strip.export_privacy.gps_exif_copy_included=true');
has("async function openReview(r){$('exportGpsExif').checked=false;");
has('record_json_contains_coordinates:!!r.location');
absent('<span>GPS embedded in JPEG</span><strong>When available</strong>');


absent('id="cemetery" value="Pine Grove Cemetery"');
checks++;assert.ok(sw.includes("'./cemetery-resolver.js'")&&sw.includes("'./cemetery-sites.js'"));
checks++;assert.ok(registry.includes("geometry:{type:'Point'")&&!registry.includes("type:'Polygon'"));
console.log('CPC camera GPS contract: '+checks+' assertions passed');
