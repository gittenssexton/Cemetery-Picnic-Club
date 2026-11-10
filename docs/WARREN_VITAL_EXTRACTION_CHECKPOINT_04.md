# Warren vital records — extraction checkpoint 4
**2026-11-10 | `feature/new-england-vital-records-core`**

## Results
- Retained **75 provisional birth-entry candidates** across printed pp. **9, 10 and 11** in the 1910 Warren volume.
- **14 of 75 have source code G.S.2**, meaning Pine Grove Cemetery gravestone-derived additions. Never count them as independent evidence confirming photographed gravestones.
- Cross-checked the text against a *second, independent digitization* (Cornell University PDF, Internet Archive `cu31924028839573`), accessible via:
  https://upload.wikimedia.org/wikipedia/commons/6/69/...Vital_records_of_Warren_%28formerly_Western%29%2C_Massachusetts%2C_to_the_end_of_the_year_1849_%28IA_cu31924028839573%29.pdf
- **Corrected four `BARWUM` surname candidates to `BARNUM`**, with an embedded correction audit trail.
- Corrected earlier unjustified normalization: the p. 9 ABBOT George mother-name text layer appears `Jemama` rather than the prior `Jemima`; pending original-image review.
- Flagged p. 10 BAKER Marion initial `L` / `I` as unresolved; both digitizations need image comparison.
- Flagged that these **25-entry batches are selected extraction samples and NOT complete, consecutive pages**. In particular p. 10 includes BALLARD, BARDWELL and others between staged names, so page coverage was previously overstated.
- Added `scripts/test_warren_vitals.py` with six local regression tests: counts, G.S.2 lineage, scan-verification states, surname correction audit, SQLite isolated staging, and no-overwrite safety.
- Connector-based validation in previous checkpoint confirmed 75 structurally valid candidates, 75 unique IDs, 14 G.S.2 and no source-lineage invariant violations. No GitHub Actions / Python runner test has been executed in this session.

## Source limitation
The remote PDF **text layer** was accessible, and its glossary confirms G.S.2 is Pine Grove, but `web` page screenshots at PDF page indexes 16–18 failed with a cache miss. The image-level QA remains blocked, hence **none of the 75 entries is visually verified**. Do not promote to `vital_record_entries` as a reviewed fact and do not import to production D1.

## Execute locally, once repository checkout is available

```bash
python -m unittest discover -s scripts -p 'test_warren_vitals.py' -v
python scripts/stage_warren_vitals.py --output /tmp/cpc-warren-stage-2026-11-10.sqlite
```

The staging importer refuses overwrite and only creates `ocr_vital_candidates`, not `persons`, `burials` or canonical vital records. Staging database file is not uploaded yet.

## Next QA tasks
1. Obtain full PDF locally (Cornell/Library of Congress, public domain), resolve pp. 9–11 page-image review for date/initial/parent-name ambiguities; verify exact printed page-to-image offsets.
2. Correct the remaining OCR candidates and create verbatim-entry transcription (not just reconstructed names and dates).
3. Inventory **all omitted entries** per page and document page completeness; only then scale bulk parsing.
4. Execute six regression tests from a full repository checkout and inspect SQLite integrity.
5. Pilot a small **reviewed** batch in a development D1, linking source documents and participant roles; keep all person/marker merges manually reviewed.
