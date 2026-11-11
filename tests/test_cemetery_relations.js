/* Run: node tests/test_cemetery_relations.js */
const assert=require('node:assert/strict');
const {validate,hierarchy,active}=require('../web/camera/cemetery-relations.js');
let n=0;function eq(a,b){n++;assert.deepEqual(a,b);}
const entities=[{id:'complex'},{id:'modern'},{id:'old'},{id:'independent'}];
const link=(subject_id,predicate,object_id,more={})=>({
 subject_id,predicate,object_id,source_id:'synthetic-document',
 review_status:'reviewed',...more
});
const edges=[
 link('modern','part_of_complex','complex'),
 link('complex','contains_historical_ground','old',{valid_from:'1900-01-01'}),
 link('old','adjacent_to','independent'),
 link('old','possible_duplicate_of','independent',{review_status:'unreviewed'})
];
eq(validate(entities,edges).ok,true);
eq(hierarchy('modern',entities,edges,'2026-11-10').ancestors.map(x=>x.entity_id),['complex']);
eq(hierarchy('old',entities,edges,'2026-11-10').ancestors.map(x=>x.entity_id),['complex']);
eq(hierarchy('old',entities,edges,'1800-01-01').ancestors,[]);
eq(hierarchy('independent',entities,edges,'2026-11-10').ancestors,[]);
eq(hierarchy('missing',entities,edges).status,'unknown_entity');
eq(validate(entities,[link('modern','part_of_complex','complex'),link('complex','part_of_complex','modern')]).ok,false);
eq(validate(entities,[link('modern','part_of_complex','modern')]).ok,false);
eq(validate(entities,[link('modern','part_of_complex','missing')]).ok,false);
eq(validate(entities,[link('modern','same_as','complex')]).ok,false);
eq(validate(entities,[link('modern','part_of_complex','complex',{source_id:null})]).ok,false);
eq(validate(entities,[link('modern','part_of_complex','complex',{review_status:'unreviewed'})]).ok,true);
eq(hierarchy('modern',entities,[link('modern','part_of_complex','complex',{review_status:'unreviewed'})]).ancestors,[]);
eq(validate(entities,[link('modern','part_of_complex','complex',{valid_from:'2026-12-01',valid_to:'2026-01-01'})]).ok,false);
eq(active(link('a','part_of_complex','b',{valid_from:'2000-01-01',valid_to:'2010-12-31'}),'2026-11-10'),false);
eq(active(link('a','part_of_complex','b',{valid_from:'2000-01-01',valid_to:'2010-12-31'}),'2007-01-01'),true);
eq(validate(entities,[link('modern','part_of_complex','complex',{valid_from:'2026-02-31'})]).ok,false);
console.log('CPC cemetery relation graph: '+n+' assertions passed');
