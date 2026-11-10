/* Source-linked, explicitly point-only cemetery candidate registry.
 * Not a universal inventory. No polygon, lot coordinate, or ground merger is asserted.
 * Pine Grove coordinates are from docs/PINE_GROVE_DOSSIER.md and are a site centroid only.
 * St. Paul and South Warren are intentionally omitted pending separately verified coordinates.
 */
window.CPCCemeterySites=Object.freeze({
 version:'warren-pilot-point-only-2026-11-10',
 entities:[{
   id:'cem-pine-grove-warren',
   name:'Pine Grove Cemetery',
   entity_kind:'cemetery',
   geometry:{type:'Point',coordinates:[-72.19660,42.20909]},
   geometry_status:'approximate_centroid',
   source_id:'docs/PINE_GROVE_DOSSIER.md',
   source_url:'https://github.com/gittenssexton/Cemetery-Picnic-Club/blob/main/docs/PINE_GROVE_DOSSIER.md',
   note:'Site centroid; NOT a surveyed cemetery perimeter or individual grave location.'
 }]
});
