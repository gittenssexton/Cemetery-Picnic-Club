-- New England vital sources: jurisdiction and bibliography metadata ONLY.
-- Does not create any vital events, people, burials, matches, images, or OCR-derived facts.
-- Source: data/vital-records/new-england-source-registry.json on vital core branch.
INSERT OR IGNORE INTO vital_jurisdictions
(id,jurisdiction_type,name,state_code,note) VALUES
('vit-state-ma','state','Massachusetts','MA','Research discovery scope; no unrestricted person-level API assumed'),
('vit-state-ct','state','Connecticut','CT','Historical town/register access varies'),
('vit-state-ri','state','Rhode Island','RI','Open historical archive records subject to item-level rights'),
('vit-state-nh','state','New Hampshire','NH','Historical records require per-collection access checks'),
('vit-state-vt','state','Vermont','VT','Partner scan licenses require separate review'),
('vit-state-me','state','Maine','ME','Pre-1892 locality records differ from statewide records');

INSERT OR IGNORE INTO vital_jurisdictions
(id,jurisdiction_type,name,state_code,parent_id,alternate_names_json,note)
VALUES ('vit-town-warren-ma','town','Warren','MA','vit-state-ma',
        '["Western"]','Historical Western name retained, not assumed to equal every historical locality entry');

INSERT OR IGNORE INTO vital_record_collections
(id,title,repository,record_start_year,record_end_year,state_code,
 jurisdiction_id,canonical_url,catalog_identifier,publication_year,
 original_record_type,rights_status,access_method,ingestion_authorization,
 citation_template,notes)
VALUES
('ma-warren-1849-rice1910',
 'Vital records of Warren (formerly Western), Massachusetts, to the end of the year 1849',
 'Library of Congress',NULL,1849,'MA','vit-town-warren-ma',
 'https://www.loc.gov/item/10008543/','LCCN 10008543',1910,
 'compiled_mixed_evidence','public_domain_claim_loc_review_before_reuse',
 'public_catalog','metadata_only',
 'Vital records of Warren (formerly Western), Massachusetts, to the end of the year 1849 (1910), printed p. [page], Library of Congress item 10008543.',
 'Historical printed volume blends town, church and gravestone evidence; G.S.2 denotes Pine Grove gravestones, not independent corroboration; page images require review');
