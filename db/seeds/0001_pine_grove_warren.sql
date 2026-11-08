-- Pine Grove, Warren, MA research seed; NO grave GPS positions or third-party photographs.
-- Draft carver claims below come from a user-supplied working document, not independent verification.
INSERT OR IGNORE INTO cemeteries
(id,name,alternate_name,address,town,state,country,latitude,longitude,centroid_accuracy_m,governance,contact_public,public_access_notes)
VALUES
('cem-pine-grove-warren','Pine Grove Cemetery','Pinegrove Cemetery','207 Maple Street, Warren, MA 01083',
'Warren','MA','US',42.20909,-72.19660,NULL,'Town of Warren Cemetery Commission',
'Cemetery@warren-ma.gov','Dawn to dusk (town rules effective 2026-03-23); obtain authorization for maintenance and gatherings');

INSERT OR IGNORE INTO sources (id,title,source_type,url,citation,access_scope) VALUES
('src-warren-2008','Warren Reconnaissance Report','municipal_heritage_report',
'https://www.mass.gov/doc/warren/download','MA DCR, Warren Reconnaissance Report (2008), Burial Grounds, p. 23','public'),
('src-warren-2024','Town of Warren 2024 Annual Report — Cemetery Department','municipal_report',
'https://www.warren-ma.gov/sites/g/files/vyhlif3996/f/news/s50981_warren_tr.pdf',
'Warren 2024 Annual Report, Cemetery Department, p. 66','public'),
('src-warren-rules-2026','Town of Warren Cemetery Rates and Regulations (2026-03-23)','municipal_rules',
'https://warren-ma.gov/425/Rates-and-Regulations','Town of Warren, March 23 2026 rules','public'),
('src-carvers-draft','Carvers_Section_Draft (2).pdf','user_supplied_research_draft',
NULL,'Unpublished working draft provided by project owner, Soule Family, pp. 6–7','internal');

INSERT OR IGNORE INTO persons(id,display_name,privacy_status)
VALUES ('person-jemima-lincoln','Jemima Lincoln','public'),
('person-martha-glezen','Martha Glezen','public');

INSERT OR IGNORE INTO markers(id,cemetery_id,marker_type,physical_description,verification_status)
VALUES
('marker-jemima-lincoln','cem-pine-grove-warren','headstone',
'Candidate attributed to a Soule-family workshop; exact appearance and plot must be field checked','research_candidate'),
('marker-martha-glezen','cem-pine-grove-warren','headstone',
'Candidate attributed by a reported inscription to Beza Soule Jr.; exact appearance and plot must be field checked','research_candidate');

INSERT OR IGNORE INTO marker_person_links(marker_id,person_id,relationship_type)
VALUES ('marker-jemima-lincoln','person-jemima-lincoln','commemorates'),
('marker-martha-glezen','person-martha-glezen','commemorates');

INSERT OR IGNORE INTO craftspeople(id,display_name,biography_note,home_region,date_range_text)
VALUES ('carver-beza-soule-jr','Beza Soule Jr.','Individual named in reported 1804 signature; attribution requires field comparison','Worcester County, MA','Late 1700s–early 1800s'),
('carver-soule-workshop','Soule family / unidentified carver','Attribution to the family, not a specific maker; do not collapse into Beza Soule Jr.','Massachusetts','1740s–1800s');

INSERT OR IGNORE INTO inscriptions(id,marker_id,kind,transcription,review_status,source_id)
VALUES ('inscr-jemima-signature','marker-jemima-lincoln','signature_excerpt','by Soule','unreviewed','src-carvers-draft'),
('inscr-martha-signature','marker-martha-glezen','signature_excerpt','Engraved by Beza Soule, Jr. of Western','unreviewed','src-carvers-draft');

INSERT OR IGNORE INTO claims(id,subject_type,subject_id,predicate,value_text,confidence,review_status,method)
VALUES
('claim-pg-earliest','cemetery','cem-pine-grove-warren','earliest_reported_inscription_year','1746','supported','unreviewed','municipal heritage report'),
('claim-jemima-year','marker','marker-jemima-lincoln','reported_signature_year','1786','tentative','unreviewed','user-supplied draft'),
('claim-martha-year','marker','marker-martha-glezen','reported_signature_year','1804','tentative','unreviewed','user-supplied draft'),
('claim-jemima-maker','marker','marker-jemima-lincoln','attributed_carver',NULL,'tentative','unreviewed','draft signature excerpt + stylistic attribution'),
('claim-martha-maker','marker','marker-martha-glezen','attributed_carver',NULL,'supported','unreviewed','draft report of inscription');
UPDATE claims SET object_type='craftsperson',object_id='carver-soule-workshop' WHERE id='claim-jemima-maker';
UPDATE claims SET object_type='craftsperson',object_id='carver-beza-soule-jr' WHERE id='claim-martha-maker';

INSERT OR IGNORE INTO claim_evidence(claim_id,source_id,page_or_locator,excerpt_or_note) VALUES
('claim-pg-earliest','src-warren-2008','p. 23','Report identifies earliest stone as 1746'),
('claim-jemima-year','src-carvers-draft','p. 7','Draft lists Jemima Lincoln signature at Pine Grove, 1786'),
('claim-martha-year','src-carvers-draft','p. 7','Draft lists Martha Glezen and Beza Soule Jr. attribution at Pine Grove, 1804'),
('claim-jemima-maker','src-carvers-draft','p. 7','Only by Soule; cannot assign one individual carver'),
('claim-martha-maker','src-carvers-draft','p. 7','Reported Engraved by Beza Soule, Jr. of Western');

-- No exact stone positions, birth/death dates, or original image assets were inferred.
