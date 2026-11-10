-- NONPRODUCTION / REVIEW-GATED DATA SEED.
-- Requires schema migration 0004 and source inventory seed 0005.
-- Populates publisher-supported symbol *definitions*, not site geology or geometry.
-- No cemetery/gravestone unit, material, or quarry assignment is made.
INSERT OR IGNORE INTO geology_units
 (id,map_id,original_symbol,formal_name,lithology,geologic_age,description,legend_locator,interpretation_status,reviewer,reviewed_at)
 VALUES
 ('zen1983-Ops','usgs-ma-bedrock-zen-1983','Ops','Partridge Formation',
 'sulfidic mica schist','Middle Ordovician',
 'USGS Bulletin 1605-A describes the Ops facies as typical sulfidic mica schist within Partridge Formation; compare Zen 1983 map. Publisher symbol cross-reference only.',
 'https://ngmdb.usgs.gov/Geolex/resources/docs/USGS_B-1605-A_t.pdf; https://pubs.usgs.gov/of/2006/1272/documents/MAmetadata.htm',
 'transcribed',NULL,NULL),
 ('zen1983-Dl','usgs-ma-bedrock-zen-1983','Dl','Littleton Formation',
 'pelitic metamorphic rocks','Early Devonian',
 'Mapped Dl symbol corresponds to Littleton Formation in USGS MA database metadata and Bulletin 1605-A; publisher cross-reference only.',
 'https://pubs.usgs.gov/of/2006/1272/documents/MAmetadata.htm; https://ngmdb.usgs.gov/Geolex/resources/docs/USGS_B-1605-A_t.pdf',
 'transcribed',NULL,NULL);