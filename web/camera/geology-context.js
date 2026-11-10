/* Cemetery Picnic Club · site-level geology context, pilot v1.
 * Static, user-reviewed RESEARCH REFERENCE, not a coordinate-to-bedrock lookup.
 * No network requests, no raw image access, no GPS access, no quarry inference.
 * Never copy into publicly shareable records without a separate review.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports) module.exports=api;
 else root.CPCGeologyContext=api;
})(typeof globalThis==='object'?globalThis:this,function(){
 'use strict';
 const PINE_GROVE_ID='cem-pine-grove-warren';
 const CONTEXT=Object.freeze({
  schema_version:'cpc-site-geology-context-v1',
  source_dataset:'MassGIS BEDROCKLITHOLOGY_POLY / USGS OFR 03-225',
  source_url:'https://www.mass.gov/info-details/massgis-data-bedrock-lithology',
  review_document:'docs/PINE_GROVE_BOUNDARY_REVIEW_2026-11-10.md',
  location_basis:'approximate cemetery centroid, not surveyed ground or any monument',
  mapped_point_symbol:'Ops',
  mapped_point_formation:'Partridge Formation',
  nearby_map_symbol:'Dl',
  nearby_map_formation:'Littleton Formation',
  boundary_distance_at_reference_m:43.58,
  published_map_positional_accuracy_approx_m:1500,
  interpretation:'Site-level background context ONLY. Neither formation is confirmed at any gravestone.',
  site_geology_status:'boundary_sensitive_unverified',
  monument_material_status:'not_inferred',
  quarry_origin_status:'unknown'
 });
 function contextForSite(siteId){
  return siteId===PINE_GROVE_ID?{...CONTEXT}:null;
 }
 function attachPrivate(record,siteId,explicitOptIn){
  if(!record || typeof record!=='object')throw Error('Private record required');
  const result={...record};
  delete result.geology_context;
  // Explicit opt-in ensures tentative geology is not silently attached to GPS.
  if(explicitOptIn===true){
   const c=contextForSite(siteId);
   if(c)result.geology_context=c;
  }
  return result;
 }
 function visibleSummary(siteId){
  const ctx=contextForSite(siteId);
  if(!ctx)return 'No reviewed site-level geology reference for this cemetery. This does not identify the monument stone.';
  return 'Pine Grove research only: MassGIS maps the approximate reference point as Ops (Partridge Formation), near Dl (Littleton Formation), ~44 m from a mapped contact. Published map positional uncertainty ~1.5 km; actual cemetery bedrock and the monument material/quarry remain unverified.';
 }
 return Object.freeze({PINE_GROVE_ID,contextForSite,attachPrivate,visibleSummary});
});
