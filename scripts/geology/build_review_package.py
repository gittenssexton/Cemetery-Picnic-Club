#!/usr/bin/env python3
"""Build non-production source-stamped MassGIS geology QA review files."""
import csv, hashlib, json, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source=ROOT/'massgis_bedlith_unreviewed_qa.json'
obj=json.loads(source.read_text())
points=obj['qa_points']
headers=['point_id','place','latitude','longitude','map_symbol','rock_group_a','rock_group_b','lithology_code','lithology_modifier','geologic_province','distance_to_polygon_boundary_m','boundary_sensitive_within_1500m','review_status','source_id','caveat']
rows=[]
for p in points:
    a=p['matches'][0] if p['matches'] else {}
    boundary=min(p['boundary_distance_m']) if p['boundary_distance_m'] else None
    rows.append(dict(point_id=p['point_id'],place=p['place'],latitude=p['latitude'],longitude=p['longitude'],map_symbol=a.get('BEDROCK_1'),rock_group_a=a.get('ROCK_GPA'),rock_group_b=a.get('ROCK_GPB'),lithology_code=a.get('LITHO_CODE'),lithology_modifier=a.get('LITH_MOD'),geologic_province=a.get('G_PROVINCE'),distance_to_polygon_boundary_m=boundary,boundary_sensitive_within_1500m=boundary is not None and boundary < 1500,review_status='unreviewed',source_id=obj['source_id'],caveat=p['caveat']))
with (ROOT/'massgis_18_location_review.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=headers);w.writeheader();w.writerows(rows)
unit_rows=obj['unit_symbol_candidates']
with (ROOT/'massgis_unit_symbols_unreviewed.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['symbol','polygon_count','status','legend_locator']);w.writeheader();w.writerows(unit_rows)
# Actual input is a multi-file shapefile; hash each to preserve provenance.
files=sorted(Path('/mnt/data/bedlith_input').glob('BEDROCKLITHOLOGY_POLY.*'))
sha={p.name:hashlib.file_digest(p.open('rb'),'sha256').hexdigest() for p in files}
(ROOT/'massgis_source_manifest.json').write_text(json.dumps({'source_id':obj['source_id'],'source_url':obj['source_url'],'origin_drive_folder':'https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw','files_sha256':sha,'observed_crs':obj['crs_input'],'feature_count':obj['feature_count'],'sample_point_count':obj['point_count'],'distinct_symbol_candidates':len(unit_rows),'metadata_publisher':'USGS OFR 03-225 (Robinson & Kapo 2003)','position_uncertainty':'Approximately 1.5 km, per source metadata','validation_status':'real_shapefile_processed_unit_labels_unreviewed','production_ready':False},indent=2)+'\n')
db=sqlite3.connect(ROOT/'massgis_research_review.sqlite')
db.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE source (id TEXT PRIMARY KEY, source_url TEXT NOT NULL, observed_crs TEXT NOT NULL, feature_count INTEGER NOT NULL, review_status TEXT NOT NULL CHECK(review_status='unreviewed'));
CREATE TABLE unit_symbol_candidate (source_id TEXT NOT NULL REFERENCES source(id),symbol TEXT NOT NULL,polygon_count INTEGER NOT NULL,legend_locator TEXT,review_status TEXT NOT NULL CHECK(review_status='unreviewed'),PRIMARY KEY(source_id,symbol));
CREATE TABLE point_qa (point_id TEXT PRIMARY KEY,place TEXT NOT NULL,latitude REAL NOT NULL,longitude REAL NOT NULL,map_symbol TEXT,rock_group_a TEXT,rock_group_b TEXT,boundary_distance_m REAL,boundary_sensitive INTEGER NOT NULL,review_status TEXT NOT NULL CHECK(review_status='unreviewed'),source_id TEXT NOT NULL REFERENCES source(id),caveat TEXT NOT NULL);
''')
db.execute('INSERT INTO source VALUES (?,?,?,?,?)',(obj['source_id'],obj['source_url'],obj['crs_input'],obj['feature_count'],'unreviewed'))
db.executemany('INSERT INTO unit_symbol_candidate VALUES (?,?,?,?,?)',[(obj['source_id'],u['symbol'],u['polygon_count'],None,'unreviewed') for u in unit_rows])
db.executemany('INSERT INTO point_qa VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',[(r['point_id'],r['place'],r['latitude'],r['longitude'],r['map_symbol'],r['rock_group_a'],r['rock_group_b'],r['distance_to_polygon_boundary_m'],int(r['boundary_sensitive_within_1500m']),'unreviewed',r['source_id'],r['caveat']) for r in rows])
db.commit(); assert db.execute('select count(*) from point_qa').fetchone()[0]==18
assert db.execute('select count(*) from unit_symbol_candidate').fetchone()[0]==322
db.close()
p01=rows[0]
near=sum(r['boundary_sensitive_within_1500m'] for r in rows)
text=f'''# Massachusetts bedrock geology — real dataset processing checkpoint\n\nDate: 2026-11-10\nSource: MassGIS Bedrock Lithology, original USGS Open-File Report 03-225 (Robinson and Kapo, 2003).\n\n## Newly located input\nThe user-supplied complete shapefile is in the [Cemetery Picnic Club / bedlith folder](https://drive.google.com/drive/folders/1FidVq3NzOMb2bbrNAKR9IPHjhrL9uOuw). Original ".shp", ".dbf", ".shx", ".prj" and publisher metadata ".shp.xml" were read without modifying originals. Local materialization appended ".bin" to some binary names; local copies were renamed back to native shapefile extensions before processing.\n\n## Actual processing results\n- Real geometries loaded: **{obj['feature_count']:,} polygons**.\n- Source coordinate system: **{obj['crs_input']}**.\n- Distinct original map symbol candidates: **{len(unit_rows)}**. These are not 322 scientifically reviewed unit definitions.\n- QA locations matched: **{sum(bool(p['matches']) for p in points)} / {len(points)}**. All point assignments are provisional; several are towns' approximate centres.\n- Location tests within 1,500 m of a mapped polygon boundary: **{near} / {len(points)}**. This is a cautionary heuristic, not a statistical probability of wrong classification.\n- **P01 Pine Grove Cemetery approximate centre:** original unit symbol **{p01['map_symbol']}**; **{p01['rock_group_b']}** (source classification; broader class {p01['rock_group_a']}); map-geologic province **{p01['geologic_province']}**; nominal point-to-polygon-edge distance **{p01['distance_to_polygon_boundary_m']:.2f} m**.\n\n## Critical limitations\nThe source metadata estimates ~1.5 km spatial accuracy, much worse than P01's ~44 m polygon-edge proximity. **The specific bedrock under Pine Grove cannot be asserted confidently from this coordinate.** The \'Ops\' symbol and rock-group attribute are a reproducible map query, *not* an independently verified formation assignment, observed outcrop, gravestone material or quarry origin. Bedrock map unit legend crosswalk to Zen et al. 1983 still requires human review.\n\n## Deliverables\n- \'massgis_bedlith_unreviewed_qa.json\': full original values for 18 sample-point matches.\n- \'massgis_18_location_review.csv\': compact QA table with boundary flags.\n- \'massgis_unit_symbols_unreviewed.csv\': 322 source symbols and counts.\n- \'massgis_source_manifest.json\': file-level checksums and provenance.\n- \'massgis_research_review.sqlite\': temporary **unreviewed research database** (not production D1).\n- \'build_review_package.py\': deterministic packaging of the actual results.\n\n## Next verification gates\nReview P01 against original Zen 1983 legend, verify the cemetery centroid against authoritative surveyed coordinates, perform independent spatial alignment checks, review source license conditions, and test the D1 staging import. Do not deploy reviewed unit labels or assert stone provenance based on local geology. No additional GIS download or account connector is required for this Massachusetts step.\n'''
(ROOT/'MASSGIS_REAL_DATA_IMPORT_REPORT_2026-11-10.md').write_text(text)
print('Created package:',len(rows),'sample locations;',len(unit_rows),'source symbols;',near,'boundary-sensitive; P01=',p01['map_symbol'])