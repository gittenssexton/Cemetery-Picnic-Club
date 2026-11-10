/* CPC export privacy profiles v1. No raw/private record may be serialized through buildShareableRecord. */
(()=>{'use strict';
 const PUBLIC_SCHEMA='CPC_SHAREABLE_RECORD_V1';
 function scalar(s,max=500){return typeof s==='string'?s.normalize('NFC').slice(0,max):''}
 function buildShareableRecord(record,review){
   if(!record||!review||review.confirmed!==true)throw Error('Explicit sharing review is required');
   const opts={image:review.image===true,inscription:review.inscription===true,site:review.site===true,material:review.material===true};
   const output={schema_version:PUBLIC_SCHEMA,public_export_id:'PUB-'+crypto.randomUUID(),
     privacy:{profile:'public_redacted',precise_location_included:false,reviewed_by_user:true,visible_content_may_reveal_site:true},
     monument:{form:opts.material?scalar(record.monument_type,90)||'unknown':'unknown',
       inscription_status:'unverified'},
     observations:{motifs:[],material_candidates:opts.material&&record.material_hypothesis&&record.material_hypothesis!=='unknown'?[{label:scalar(record.material_hypothesis,100),status:'unverified'}]:[]},
     site_display:opts.site?(scalar(review.approvedSiteName,160)||null):null,
     inscription:opts.inscription?(scalar(review.approvedInscription,1500)||null):null,
     assets:opts.image?[{file:'image_01.jpg',kind:'reencoded_visual_preview',rights_reviewed_by_user:true}]:[],
     notices:['No precise coordinates exported','Photographic content and inscriptions can reveal a location','All interpretations remain provisional']};
   return output;
 }
 function validatePublicRecord(record){
   if(!record||record.schema_version!==PUBLIC_SCHEMA||record.privacy?.precise_location_included!==false)throw Error('Public schema invalid');
   const json=JSON.stringify(record);
   const banned=/(?:latitude|longitude|accuracy_m|horizontal_accuracy|location_observation|cemetery_match|cemetery_assignment|private_archive|gps_exif|geotagged|source_files|originalBlob|monument_group_id|candidate_catalog|provider)/i;
   if(banned.test(json))throw Error('Sensitive key or metadata in public record');
   return true;
 }
 window.CPCExportPrivacy={buildShareableRecord,validatePublicRecord};
})();
