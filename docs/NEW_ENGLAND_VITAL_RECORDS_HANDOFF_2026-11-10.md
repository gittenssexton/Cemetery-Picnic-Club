# Cemetery Picnic Club — New England vital records ingestion handoff
**Prepared:** 2026-11-10  
**Repository:** `gittenssexton/Cemetery-Picnic-Club`  
**Branch:** `feature/new-england-vital-records-core`  
**Status:** Source research, six-state registry and schema committed. **No vital-event entries have been ingested, no production D1 migration has been run, and no automatic person matches have been accepted.**

## Mission

Create a single **CPC-owned, searchable, citation-first vital-record database** covering **Massachusetts, Connecticut, Rhode Island, New Hampshire, Vermont and Maine**. Begin with **Warren, Massachusetts**, especially older Pine Grove Cemetery markers. Expand by municipality and collection, not by unverified bulk name scraping.

Differentiate:
1. An **event** (birth, baptism, marriage, intention, death, burial);
2. A **printed transcription** or archival original that reports the event;
3. A **person identity** in CPC;
4. A **grave marker** or actual burial;
5. A proposed **relationship or identity match**.

These are separate records. The same person may have multiple events and name forms; a person is not necessarily buried where a book records death; a gravestone may commemorate several people.

## The key Warren discovery: source-dependent citations

Start with *Vital records of Warren (formerly Western), Massachusetts, to the end of the year 1849* (Worcester: Franklin P. Rice, 1910), 196 printed pages, Library of Congress LCCN 10008543.

- Canonical item: https://www.loc.gov/item/10008543/
- Page images / OCR: https://www.loc.gov/resource/gdcmassbookdig.vitalrecordsofwa00war/
- Rights: Library of Congress identifies this book as public-domain.
- It includes town-book entries **and** additions from other sources, so publication does not make every entry an independent town record.
- **Source code `GS2` explicitly refers to gravestones in Pine Grove Cemetery** (see the frontmatter abbreviations, image 8 in the LOC online viewer). `GS1` refers to South Warren Cemetery. Other abbreviations include `CR` (church record); copy and verify the complete glossary before parsing.
- **Crucial anti-circularity rule:** A `GS2` entry and a photo of the same Pine Grove gravestone are **one evidentiary lineage**, not two independent corroborating sources. A published index derived from that same gravestone also does not increase independent-source count. The original town register, separate church record, probate, or independently sourced census evidence may corroborate.
- Preserve historical spellings, qualifiers, uncertain dates, maiden names, parents, spouse and source codes as printed. Never fill missing dates from visual inference.

**MA records timeline:** statewide birth/marriage/death records began in 1841; Massachusetts Archives holds 1841–1935, with 1841–1930 largely linked to FamilySearch digitization, and later records still being transferred; RVRS handles 1936–present. Pre-1841 primarily requires town records. Official: https://www.sec.state.ma.us/divisions/archives/collections/vital-records.htm

## Six-state intake strategy

| State | Early/historical research channel | Caution |
|---|---|---|
| **MA** | Town vital-record volumes (often to 1850); Archives 1841–1935 | Citation codes can mix cemetery, town and church evidence |
| **CT** | Town registers and Connecticut State Library before 1897; statewide from July 1, 1897 | Modern records have access controls |
| **RI** | State Archives digitized *open* records; earlier town collections | Birth and marriage records more than **101 years** old; deaths more than **51 years** old available as open Archives records per official source |
| **NH** | Genealogical vault and local records beginning around 1640 | Access, indexing and reuse must be checked individually |
| **VT** | Town records from the eighteenth century; VSARA partners with FamilySearch / Ancestry | Legal access to public vital records is separate from commercial site image licenses |
| **ME** | Town and Maine State Archives before 1892; statewide from January 1, 1892 | Do not assume statewide records exist before 1892 |

Official sources:
- CT https://portal.ct.gov/dph/resources-and-records/vital-records
- RI https://www.sos.ri.gov/divisions/state-archives/VitalRecords
- NH https://www.sos.nh.gov/vital-records/
- VT https://sos.vermont.gov/vsara/explore/people/vital-records
- ME https://www3.maine.gov/dhhs/mecdc/vital-records

No state office is assumed to provide an unrestricted person-level vital-record API. Where an API is lacking, source public-domain compilations and permissible public archival metadata, not restricted vital certificates.

## Database files

- `db/migrations/0005_new_england_vital_records.sql`: SQLite/Cloudflare D1 extension. **Stage/test only.**
- `data/vital-records/new-england-source-registry.json`: six-state source registry and the Warren pilot.
- This handoff: `docs/NEW_ENGLAND_VITAL_RECORDS_HANDOFF_2026-11-10.md`.
- Existing CPC structures `persons`, `markers`, `burials`, `sources`, `claims`, `claim_evidence`, `research_works` and `external_references` must remain intact.

New tables:
- `vital_jurisdictions`: municipalities/states and historical name changes (e.g., Western → Warren).
- `vital_record_collections`: archive, coverage, rights, availability and source.
- `vital_source_documents`: edition, physical volume, stable URL, checksum, OCR/transcription rights.
- `vital_source_page_refs`: **printed page AND digital image sequence** (they differ).
- `vital_record_entries`: event, verbatim line, date/name/place as printed, original evidence type, review.
- `vital_entry_participants`: subject, spouse, parents and others as textual roles; person link only after review.
- `vital_entry_source_codes`: document-specific glossary; `GS2` mapped to gravestone provenance, not town book.
- `vital_entity_match_candidates`: tentative person/marker/burial connections, supporting & contradictory features, independent source count, reviewer.
- `vital_ingestion_runs`: batch provenance, software version, records and errors.

## ETL workflow — Warren pilot

**A. Rights and catalog (once per volume)**
1. Retrieve canonical LOC metadata, stable item ID, page-image references, full title/edition and public-domain rights note.
2. Preserve the complete original scan or immutable download URL; record SHA-256 if downloaded.
3. Read **frontmatter abbreviation glossary** and publishers' note before any automated entry parsing.
4. Record historical town alias 'Western', current municipality 'Warren', MA; preserve event's contemporary place spelling.

**B. Parse (repeat in small, reviewable batches)**
5. Process **births, marriages, deaths separately**; target 10–25 printed pages per reviewed batch. Keep section headings and surname carryovers. Record LOC digital-image number and original printed page.
6. Save one literal entry per distinct printed entry with stable ID e.g. `MA-WARREN-1910:p018:line04` when line anchors verified. Do not invent source lines from noisy OCR. Use deterministic source+page+ordinal hash for ingestion deduplication.
7. OCR can suggest transcriptions, but retain `entry_verbatim`, original code and `extraction_confidence=unreviewed` until the page image is checked. Do not silently normalize ambiguous dates or names.
8. Split participants into role records. A marriage has at least two spouses where named; parents/witnesses are additional participants. Marriage intentions and marriages are distinct event types.
9. Store exact source abbreviations and use document-specific `vital_entry_source_codes` to classify evidence (gravestone, church, town book, etc.).
10. Reviewer spot-checks every initial extracted entry; automate after demonstrating acceptable accuracy and retain review queue for uncertainty.

**C. Connect to existing cemetery data**
11. Produce candidate links using name variants, temporal consistency, town and cemetery context. Do not automatically merge; rank *possible matches*.
12. For a `GS2` record linked to Pine Grove photo, tag **dependent evidence** and keep independent-source count unchanged.
13. Accept a person/marker connection only after a reviewer cites original pages and considers contradicting ages, generations and locations.
14. Link **death** events to a person, not an assumed burial. Link **burial** only when supported by distinct evidence.

**D. QA gate before publication**
15. Validate no broken foreign keys, duplicate compound source keys, invalid state codes, missing source/page locator or dates inconsistent with date precision.
16. Sample across surnames, event sections, pages and `GS1/GS2` entries. Document accuracy, OCR error types, unresolved ambiguities and privacy concerns.
17. Publish only indexed, reviewed historical entries to the CPC user-facing search; show exact citation, limitations and correction route.

## Suggested test acceptance criteria (initial Warren batch)
- One verified Warren volume registered with stable LOC URL, rights note, and correct 1910 attribution.
- All six states present as **jurisdiction/source registry**, not fabricated vital records.
- 25 consecutive Warren entries transcribed and **manually compared with scan**, each with printed page, digital image sequence, source codes and participant roles where present.
- Demonstrate at least one `GS2` case so a marker-derived entry does **not** count as independent corroboration.
- 0 automatically approved person merges, 0 assumed burials, 0 entries without traceable source locator.
- SQL migration passes an empty SQLite test followed by foreign-key check. Stage D1 only after checks and a migration backup plan.

## Licensing and safeguards

- Warren 1910 LOC digitization is public domain per LOC item record; always provide proper citation.
- APIs can discover metadata; do not assume they authorize full-text harvesting, derivative publication or images. LOC has loc.gov JSON, image and selected text services (https://www.loc.gov/apis/). FamilySearch access and copying require separate authorization.
- Use historical records first. Current personal vital records and sensitive adoption or medical details must not be bulk imported. Apply source/state-specific access rules and avoid publishing living persons' personal details.
- Separate OCR text copyright/conditions (if from another provider) from rights in the underlying 1910 book.
- Never replace verified original inscriptions with compiled record spellings.
- Keep corrections and contradictory historical sources instead of overwriting.

## Expansion order

1. Massachusetts: Warren + Pine Grove, then adjacent towns and other Massachusetts 'to 1850' books; build reusable ingestion pipeline.
2. Connecticut and Rhode Island: town and open archives sources, prioritizing historical overlap along state lines.
3. New Hampshire and Vermont: historic town registers and public/repository collections.
4. Maine: pre-1892 town registers and published historical volumes.
5. Expand all six states by source priority and available rights, not by forcing coverage where records are missing.

## Deployment status and next work

**Completed in this handoff:** documentary research, verified Warren source and `GS2` significance, six-state registry, schema design and committed source instructions.

**Not completed:** downloading or extracting the whole Warren text, loading any event rows, setting up a D1 production database, reviewing match candidates, integrating the UI or deploying an API.

**Next executable work:** write a reproducible Warren-volume extractor, parse a small review batch, create a QA report, test SQL locally and only then stage the first data upload. The first end-user view should be **Historical records / Unverified matches**, with full citations and provenance.
