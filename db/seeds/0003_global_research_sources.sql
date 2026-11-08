-- 0003: research leads independently of any cemetery; metadata only.
INSERT OR IGNORE INTO research_works
(id,title,authors,published_year,work_type,publisher,journal,volume,issue,pages,doi,url,full_text_status,rights_status,review_status)
VALUES
('work-forbes-1927','Gravestones of Early New England and the Men Who Made Them, 1653–1800','Harriette Merrifield Forbes',1927,'book','Houghton Mifflin',NULL,NULL,NULL,NULL,NULL,'https://books.google.com/books?id=ZawgAAAAMAAJ','available_external','check_edition_and_host','metadata_verified'),
('work-dethlefsen-deetz-1966','Death’s Heads, Cherubs, and Willow Trees: Experimental Archaeology in Colonial Cemeteries','Edwin Dethlefsen; James Deetz',1966,'article',NULL,'American Antiquity','31','4','502–510','10.2307/2694382','https://www.cambridge.org/core/journals/american-antiquity/article/abs/deaths-heads-cherubs-and-willow-trees-experimental-archaeology-in-colonial-cemeteries1/AD6C9694AB7BE0BB65A4B2614CAA26C2','abstract_only','copyrighted','metadata_verified'),
('work-ludwig-1966','Graven Images: New England Stonecarving and Its Symbols, 1650–1815','Allan I. Ludwig',1966,'book','Wesleyan University Press',NULL,NULL,NULL,NULL,NULL,'https://www.weslpress.org/9780819560407/graven-images/','not_acquired','copyrighted','metadata_verified'),
('work-kelly-williams-1982','And the Men Who Made Them: The Signed Gravestones of New England','Sue Kelly; Anne Williams',1982,'article',NULL,'Markers','2',NULL,NULL,NULL,'https://gravestonestudies.org/knowledge-center/archives','not_acquired','check_publisher_terms','bibliography_only'),
('work-sweeney-1985','Where the Bay Meets the River: Gravestones and Stonecutters in the River Towns of Western Massachusetts, 1690–1810','Kevin M. Sweeney',1985,'article',NULL,'Markers','3',NULL,NULL,NULL,'https://gravestonestudies.org/knowledge-center/archives','not_acquired','check_publisher_terms','bibliography_only'),
('work-boston-iconography','Iconography of Gravestones at Burying Grounds','City of Boston Parks and Recreation',NULL,'government','City of Boston',NULL,NULL,NULL,NULL,NULL,'https://www.boston.gov/departments/parks-and-recreation/iconography-gravestones-burying-grounds','available_external','check_publication_rights','partly_reviewed'),
('work-farber-intro-1997','Early American Gravestones: Introduction to the Farber Gravestone Collection','Jessie Lie Farber',1997,'report','American Antiquarian Society',NULL,NULL,NULL,NULL,NULL,'https://www.americanantiquarian.org/sites/default/files/2026-04/farber.pdf','available_external','check_publication_rights','partly_reviewed');

INSERT OR IGNORE INTO research_collections
(id,institution,name,catalog_url,scope_note,metadata_license,image_license,access_status)
VALUES
('collection-farber','American Antiquarian Society','Farber Gravestone Collection','https://www.americanantiquarian.org/farber-gravestone-collection','Northeastern United States focus with additional coverage; AAS catalog states >13,500 images of >9,000 stones. 1997 introduction gives different totals: do not conflate versions.','not_verified','not_verified','catalog_public'),
('collection-ags-markers','Association for Gravestone Studies / Project MUSE','Markers volumes 1–25','https://gravestonestudies.org/knowledge-center/archives','AGS reports nonmember access for volumes 1–25, but reuse is not automatically licensed.','not_verified','not_verified','online_read_access');

INSERT OR IGNORE INTO geographic_scopes(id,name,scope_type,modern_country_code,description) VALUES
('scope-global','Global','global',NULL,'No implied geographic exclusion'),
('scope-new-england','New England','region','US','Regional scholarly coverage; not a filter on the core'),
('scope-boston','Boston, Massachusetts','locality','US','City-specific interpretive guidance');

INSERT OR IGNORE INTO cultural_traditions(id,name,description) VALUES
('trad-new-england-colonial','Colonial New England funerary carving','Research framework for regional iconography, not a universal explanation');

INSERT OR IGNORE INTO research_work_geography(work_id,scope_id,coverage_note) VALUES
('work-forbes-1927','scope-new-england','New England stonecarvers'),
('work-dethlefsen-deetz-1966','scope-new-england','Massachusetts colonial burial grounds'),
('work-boston-iconography','scope-boston','City of Boston burial grounds');

-- Distinct readings, deliberately not definitive meanings.
INSERT OR IGNORE INTO motif_interpretations
(id,motif_id,interpretation_text,interpretation_type,tradition_id,scope_id,review_status)
VALUES
('interp-deaths-head-mortality','motif-deaths-head','The death’s-head is discussed in Boston material as a reminder of bodily death and mortality; the precise meaning of an individual stone requires context.','scholarly_hypothesis','trad-new-england-colonial','scope-boston','source_reviewed'),
('interp-cherub-heaven','motif-winged-cherub','A winged cherub has been interpreted as an image of the soul’s flight to heaven, but Boston sources caution against treating this as a universal chronological or theological replacement.','scholarly_hypothesis','trad-new-england-colonial','scope-boston','source_reviewed'),
('interp-willow-mourning','motif-willow','Boston historical interpretation describes the willow as a longstanding mourning symbol in a neoclassical funerary context.','scholarly_hypothesis','trad-new-england-colonial','scope-boston','source_reviewed'),
('interp-urn-antiquity','motif-urn','Boston interpretation connects the funerary urn with ancient Roman imagery revived in neoclassical commemoration.','scholarly_hypothesis','trad-new-england-colonial','scope-boston','source_reviewed');

INSERT OR IGNORE INTO research_citations(id,work_id,locator,note) VALUES
('cite-boston-17c','work-boston-iconography','Seventeenth-century iconography','Description and variations of death’s-head'),
('cite-boston-18c','work-boston-iconography','Eighteenth-century iconography','Overlap of death’s-heads and cherubs; reported interpretations'),
('cite-boston-19c','work-boston-iconography','Nineteenth-century iconography','Urn and willow design descriptions'),
('cite-deetz-abstract','work-dethlefsen-deetz-1966','Publisher abstract','Author-proposed evolution model, not full-text reading');

INSERT OR IGNORE INTO interpretation_citations(interpretation_id,citation_id,evidence_role) VALUES
('interp-deaths-head-mortality','cite-boston-17c','supports'),
('interp-cherub-heaven','cite-boston-18c','supports'),
('interp-willow-mourning','cite-boston-19c','supports'),
('interp-urn-antiquity','cite-boston-19c','supports');

INSERT OR IGNORE INTO review_tasks(id,entity_type,entity_id,task_type,description,priority,state) VALUES
('task-farber-terms','collection','collection-farber','license_request','Determine collection metadata access and image-analysis/reuse permissions.',1,'open'),
('task-markers-access','collection','collection-ags-markers','source_access','Retrieve Kelly/Williams and Sweeney full articles via authorized open-access or library routes.',1,'open'),
('task-pine-jemima','marker','marker-jemima-lincoln','field_validation','Confirm inscription, location, dated marker and actual signature with original photographs.',1,'open'),
('task-pine-martha','marker','marker-martha-glezen','field_validation','Verify reported Beza Soule Jr. signature in situ.',1,'open'),
('task-symbol-compare','motif','motif-winged-cherub','scholarship_comparison','Compare Deetz/Dethlefsen and Ludwig from full texts before firm generalizations.',2,'blocked');
