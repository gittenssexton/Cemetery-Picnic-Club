-- Local authoritative references; METADATA ONLY, no spatial geometry ingested.
-- Run after 0004_geological_map_core.sql. Do not treat these sources as reviewed.
INSERT OR IGNORE INTO geology_map_sources
(id,title,authors,year,publisher,scale_denominator,region,source_url,provider,
 rights_note,citation_text,geometry_status,validation_status,notes)
VALUES
('usgs-gq1358-warren-bedrock-1977',
 'Bedrock geologic map of the Warren quadrangle, Worcester, Hampden, and Hampshire counties, south-central Massachusetts',
 'John S. Pomeroy',1977,'USGS',24000,'Warren quadrangle, MA',
 'https://doi.org/10.3133/gq1358','USGS',
 'USGS publication; verify individual scans before republication',
 'Pomeroy, J.S. (1977), Bedrock geologic map of the Warren quadrangle, USGS Geologic Quadrangle GQ-1358, scale 1:24,000.',
 'raster_only','inventory_only',
 'Higher-detail independent bedrock map for cemetery vicinity. Catalog verified; plate/legend and precise Pine Grove location NOT yet reviewed; do not assign units.'),
('usgs-gq1357-warren-surficial-1977',
 'Surficial geologic map of the Warren quadrangle, Massachusetts',
 'John S. Pomeroy',1977,'USGS',24000,'Warren quadrangle, MA',
 'https://doi.org/10.3133/gq1357','USGS',
 'USGS publication; verify individual scans before republication',
 'Pomeroy, J.S. (1977), Surficial geologic map of the Warren quadrangle, USGS Geologic Quadrangle GQ-1357, scale 1:24,000.',
 'raster_only','inventory_only',
 'Surficial geology, NOT local bedrock formation identity. Context for glacial sediment, outcrop and soil conditions only.'),
('usgs-mf541d-warren-depth-bedrock-1974',
 'Map showing depth to bedrock, Warren Quadrangle, Massachusetts',
 'C.J. Londquist and John S. Pomeroy',1974,'USGS',24000,'Warren quadrangle, MA',
 'https://doi.org/10.3133/mf541D','USGS',
 'USGS publication; verify individual scans before republication',
 'Londquist, C.J. and Pomeroy, J.S. (1974), Map showing depth to bedrock, Warren Quadrangle, USGS MF-541-D.',
 'raster_only','inventory_only',
 'Depth to bedrock data, NOT source for assigning schist, other lithology, gravestone stone, or quarry.');
