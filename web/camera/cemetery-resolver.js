/* CPC cemetery candidate resolver v0.1.
 * Pure JavaScript, no GPS acquisition, network calls or database writes.
 * GeoJSON coordinates are [longitude, latitude]. Source quality is required.
 * Outcomes are hypotheses, never burial/plot identifications.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object' && module.exports) module.exports=api;
  else root.CPCCemeteryResolver=api;
})(typeof globalThis==='object'?globalThis:this,function(){
  'use strict';
  const R=6371008.8;
  const rad=d=>d*Math.PI/180;
  function validFix(f){
    if(!f || !Number.isFinite(f.lat) || !Number.isFinite(f.lon) ||
       Math.abs(f.lat)>90 || Math.abs(f.lon)>180 ||
       !Number.isFinite(f.horizontal_accuracy_m) || f.horizontal_accuracy_m<0)
      return false;
    if(f.fix_age_s!=null && (!Number.isFinite(f.fix_age_s)||f.fix_age_s<0)) return false;
    return true;
  }
  function distance(a,b){
    const p1=rad(a[1]),p2=rad(b[1]),dp=p2-p1,dl=rad(b[0]-a[0]);
    const h=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
    return 2*R*Math.asin(Math.min(1,Math.sqrt(h)));
  }
  // Local equirectangular projection about test point, for small cemetery extents.
  function xy(point,anchor){
    return [R*rad(point[0]-anchor[0])*Math.cos(rad(anchor[1])),R*rad(point[1]-anchor[1])];
  }
  function ringContains(point,ring){
    let inside=false;const p=xy(point,point);
    for(let i=0,j=ring.length-1;i<ring.length;j=i++){
      const a=xy(ring[i],point),b=xy(ring[j],point);
      if((a[1]>p[1])!==(b[1]>p[1]) && p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]) inside=!inside;
    }
    return inside;
  }
  function polygonContains(point,rings){
    return !!rings.length && ringContains(point,rings[0]) && !rings.slice(1).some(r=>ringContains(point,r));
  }
  function segmentDistance(point,a,b){
    const p=xy(point,point),x=xy(a,point),y=xy(b,point),dx=y[0]-x[0],dy=y[1]-x[1];
    const t=Math.max(0,Math.min(1,-(x[0]*dx+x[1]*dy)/(dx*dx+dy*dy||1)));
    return Math.hypot(x[0]+t*dx,x[1]+t*dy);
  }
  function boundaryDistance(point,rings){
    let best=Infinity;
    for(const ring of rings)for(let i=0;i<ring.length;i++){
      best=Math.min(best,segmentDistance(point,ring[i],ring[(i+1)%ring.length]));
    }
    return best;
  }
  function isCoordinate(p){
    return Array.isArray(p) && p.length>=2 && Number.isFinite(p[0]) &&
      Number.isFinite(p[1]) && Math.abs(p[0])<=180 && Math.abs(p[1])<=90;
  }
  function validPolygon(rings){
    return Array.isArray(rings) && rings.length>0 && rings.every(ring=>
      Array.isArray(ring) && ring.length>=4 && ring.every(isCoordinate) &&
      ring[0][0]===ring[ring.length-1][0] &&
      ring[0][1]===ring[ring.length-1][1]
    );
  }
  function geometryResult(point,geometry){
    if(!geometry) return null;
    if(geometry.type==='Point'){
      if(!isCoordinate(geometry.coordinates))return null;
      return {inside:false,distance_m:distance(point,geometry.coordinates),kind:'point'};
    }
    if(!['Polygon','MultiPolygon'].includes(geometry.type)) return null;
    const polys=geometry.type==='Polygon'?[geometry.coordinates]:geometry.coordinates;
    if(!Array.isArray(polys)||!polys.length||!polys.every(validPolygon))return null;
    let inside=false,min=Infinity;
    for(const rings of polys){
      if(polygonContains(point,rings)) inside=true;
      min=Math.min(min,boundaryDistance(point,rings));
    }
    return {inside,distance_m:inside?0:min,boundary_distance_m:min,kind:'polygon'};
  }
  function resolve(fix,entities,opts={}){
    if(!validFix(fix)) return {status:'invalid_fix',candidates:[],reason:'Invalid GPS coordinate or accuracy'};
    const stale=fix.fix_age_s!=null && fix.fix_age_s>(opts.max_fix_age_s??120);
    const point=[fix.lon,fix.lat],radius=fix.horizontal_accuracy_m;
    const nearby=opts.nearby_m??250;
    const matches=[];
    for(const entity of entities||[]){
      if(!entity||!entity.id)continue;
      const geo=geometryResult(point,entity.geometry);
      if(!geo)continue;
      const intersects=geo.kind==='polygon' && (geo.inside||geo.distance_m<=radius);
      if(!intersects && geo.distance_m>radius+nearby)continue;
      const verified=entity.geometry_status==='verified_boundary' && geo.kind==='polygon' && !!entity.source_id;
      const safelyInside=verified && geo.inside && geo.boundary_distance_m>radius && !stale;
      matches.push({
        entity_id:entity.id,name:entity.name||entity.id,
        entity_kind:entity.entity_kind||'cemetery',
        parent_id:entity.parent_id||null,
        geometry_status:entity.geometry_status||'unknown',
        source_id:entity.source_id||null,
        inside_geometry:geo.inside,
        intersects_accuracy_circle:intersects,
        distance_m:Math.round(geo.distance_m),
        boundary_clearance_m:geo.kind==='polygon'&&geo.inside?Math.round(geo.boundary_distance_m):null,
        status:safelyInside?'within_verified_boundary':intersects?'possible_within':'nearby_only',
        reasons:[geo.kind==='point'?'point_only_discovery':verified?'verified_polygon':'unverified_polygon',
                 stale?'stale_fix':null].filter(Boolean)
      });
    }
    // Never mark any independently named child verified if another plausible child overlaps.
    const plausible=matches.filter(m=>m.intersects_accuracy_circle);
    // Point-only names close enough to lie within the accuracy circle can
    // compete as discovery hypotheses, but can never establish containment.
    const overlappingPoints=matches.filter(m=>
      m.geometry_status!=='verified_boundary' &&
      m.reasons.includes('point_only_discovery') && m.distance_m<=radius);
    const siteCandidates=plausible.filter(m=>m.entity_kind!=='cemetery_complex');
    const competingNames=[...siteCandidates,...overlappingPoints.filter(m=>m.entity_kind!=='cemetery_complex')];
    // Any two separately identified possible child grounds remain ambiguous, even if
    // they share a parent. A complex itself is not a competing child cemetery.
    const multiple=new Set(competingNames.map(m=>m.entity_id)).size>1;
    if(multiple) for(const m of competingNames){
      if(m.intersects_accuracy_circle)m.status='possible_within';
      m.reasons.push('competing_site');
    }
    // A parent boundary never establishes the child ground identity.
    const parentOnly=plausible.length>0 && siteCandidates.length===0 &&
      plausible.some(m=>m.entity_kind==='cemetery_complex');
    const unresolvedChild=parentOnly || (plausible.some(m=>m.entity_kind==='cemetery_complex') &&
      siteCandidates.length!==1);
    const status=stale?'stale_fix':multiple?'multiple_candidates':
      unresolvedChild?'complex_child_unresolved':
      plausible.length?'possible_within':matches.length?'nearby_only':'unknown';
    const definitive=(!stale && !multiple && !unresolvedChild &&
      siteCandidates.length===1 && siteCandidates[0].status==='within_verified_boundary');
    matches.sort((a,b)=>Number(b.intersects_accuracy_circle)-Number(a.intersects_accuracy_circle)||a.distance_m-b.distance_m);
    return {status:definitive?'within_verified_boundary':status,fix_accuracy_m:radius,
      candidates:matches,selected_entity_id:null,
      parent_complex_ids:plausible.filter(m=>m.entity_kind==='cemetery_complex').map(m=>m.entity_id),
      unresolved_child:unresolvedChild,
      notice:'Location matching is provisional; this does not identify a monument, person or plot.'};
  }
  return {validFix,distance,geometryResult,resolve};
});
