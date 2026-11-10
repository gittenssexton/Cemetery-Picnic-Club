/* CPC evidence-aware cemetery relationship graph.
 * Pure browser/Node module. Relationships do NOT merge cemetery identities.
 * Only documented, directionally valid current relations are used for hierarchy.
 */
(function(root,factory){
 const api=factory();
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.CPCCemeteryRelations=api;
})(typeof globalThis==='object'?globalThis:this,function(){
 'use strict';
 const PARENTS=new Set(['part_of_complex','contains_historical_ground']);
 const ALLOWED=new Set([...PARENTS,'adjacent_to','shares_entrance_with',
   'administratively_managed_with','renamed_to','merged_into_at_date',
   'overlaps_disputed_boundary','separate_from','possible_duplicate_of']);
 const parseDate=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&
   !Number.isNaN(Date.parse(s))&&new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;
 function active(edge,date){
   if(!date)return true;
   if(!parseDate(date))return false;
   return (!edge.valid_from||edge.valid_from<=date)&&(!edge.valid_to||date<=edge.valid_to);
 }
 function validate(entities,relationships){
   const errors=[],ids=new Set(),edges=[];
   for(const e of entities||[]){
     if(!e||typeof e.id!=='string'||!e.id.trim())errors.push('missing_entity_id');
     else if(ids.has(e.id))errors.push('duplicate_entity:'+e.id);
     else ids.add(e.id);
   }
   for(const r of relationships||[]){
     if(!r||!ALLOWED.has(r.predicate)){errors.push('invalid_predicate');continue;}
     if(!ids.has(r.subject_id)||!ids.has(r.object_id))errors.push('missing_entity_reference');
     if(r.subject_id===r.object_id)errors.push('self_relationship');
     if(!r.source_id||!String(r.source_id).trim())errors.push('missing_relationship_source');
     if(r.valid_from&&!parseDate(r.valid_from))errors.push('invalid_from_date');
     if(r.valid_to&&!parseDate(r.valid_to))errors.push('invalid_to_date');
     if(r.valid_from&&r.valid_to&&r.valid_from>r.valid_to)errors.push('reversed_date_range');
     if(!r.review_status||!['reviewed','unreviewed','disputed','rejected'].includes(r.review_status))
       errors.push('invalid_review_status');
     edges.push(r);
   }
   // Reject potential cycles of containment, including different effective periods.
   const graph=new Map([...ids].map(id=>[id,[]]));
   for(const r of edges){
     if(!PARENTS.has(r.predicate)||!ids.has(r.subject_id)||!ids.has(r.object_id))continue;
     const child=r.predicate==='part_of_complex'?r.subject_id:r.object_id;
     const parent=r.predicate==='part_of_complex'?r.object_id:r.subject_id;
     graph.get(child).push(parent);
   }
   const visiting=new Set(),seen=new Set();
   function dfs(id){
     if(visiting.has(id)){errors.push('containment_cycle:'+id);return;}
     if(seen.has(id))return;
     visiting.add(id);
     for(const parent of graph.get(id)||[])dfs(parent);
     visiting.delete(id);seen.add(id);
   }
   for(const id of ids)dfs(id);
   return {ok:errors.length===0,errors:[...new Set(errors)]};
 }
 function hierarchy(entityId,entities,relationships,atDate){
   const validated=validate(entities,relationships);
   if(!validated.ok)return {status:'invalid_graph',errors:validated.errors,ancestors:[]};
   if(!(entities||[]).some(e=>e.id===entityId))return {status:'unknown_entity',ancestors:[]};
   const parents=new Map();
   for(const r of relationships||[]){
     if(!PARENTS.has(r.predicate)||r.review_status!=='reviewed'||!active(r,atDate))continue;
     const child=r.predicate==='part_of_complex'?r.subject_id:r.object_id;
     const parent=r.predicate==='part_of_complex'?r.object_id:r.subject_id;
     if(!parents.has(child))parents.set(child,[]);
     parents.get(child).push({entity_id:parent,source_id:r.source_id,
       predicate:r.predicate,valid_from:r.valid_from||null,valid_to:r.valid_to||null});
   }
   const ancestors=[],queue=[entityId],visited=new Set([entityId]);
   while(queue.length){
     const id=queue.shift();
     for(const parent of parents.get(id)||[]){
       if(visited.has(parent.entity_id))continue;
       visited.add(parent.entity_id);ancestors.push(parent);queue.push(parent.entity_id);
     }
   }
   return {status:'ok',ancestors,unreviewed_links_excluded:true};
 }
 return {validate,hierarchy,active};
});
