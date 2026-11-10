# Warren vital-record extraction checkpoint 3 — 2026-11-10

## Completed in this work session

- **Third 25-entry OCR-assisted candidate batch** from the births section, printed **page 11**, covering Barnes/Barns and early Barwum entries.
- Combined staging **75 candidates** across printed pages **9, 10, 11**, with **14 entries explicitly marked G.S.2** (6 + 7 + 1), which refers to Pine Grove Cemetery.
- Rechecked and improved the earlier two batches' provenance: an unmarked entry is not automatically independent evidence, so `independent_from_pine_grove_photo` is **null** for provisional town-book entries and **false** for G.S.2 entries.
- Added `source_image_verified=false` to all 75 records and retained `requires_page_image_check` status.
- Flagged the 1784/1801 Arnold name OCR ambiguity (`Rodbulphus` in text layer vs staged `Rodoulphus`) and Ashley Anna's partial `Feb. 20, 1748-9` OCR date. These need image review; neither should be confidently normalized.
- Created `scripts/stage_warren_vitals.py`, a **local, isolated SQLite staging importer**. It validates duplicate IDs, counts, page citations, status, and G.S.2 independence; the staging table is deliberately NOT the production `vital_record_entries` table.
- Ran a connector-side validation against the three committed JSON files: **75 rows, 75 unique IDs, 14 G.S.2, 0 validation-rule errors**.

## Source evidence

1910 Warren volume, public-domain scan and text layer:
https://upload.wikimedia.org/wikipedia/commons/2/2c/Vital_records_of_Warren_%28formerly_Western%29%2C_Massachusetts%2C_to_the_end_of_the_year_1849_%28IA_vitalrecordsofwa00war%29.pdf

Publisher preface: entries from town books with separately coded additions, `G.S.2.` for Pine Grove; `G.S.1.` for South Warren.

## Blocker: original page imagery

A PDF textual layer was accessible via the web reader, but screenshots failed with remote cache-miss errors. An attempted external PDF download also failed. Therefore **none of the 75 rows can be reported as visually verified against page scans**.

## Explicitly not done

- Did not run the new Python staging importer in a writable full-repo environment. It is committed and ready to run, but its SQLite output has **not** been independently verified.
- Did not run D1 migrations, create D1 event entries, merge persons, determine burials, or publish records.
- Did not assume unmarked town-book additions are independently corroborated.

## Next steps

1. Retrieve a usable original PDF copy and visually review pp. 9–11, preserving exactly printed entry text and image sequence.
2. Correct OCR uncertainty and transcribe the exact entries before trusted database import.
3. Run `python scripts/stage_warren_vitals.py --output /tmp/cpc_warren_staging.sqlite` from the repository checkout and inspect row counts/integrity.
4. Only then transform reviewed entries into schema `0005` with verified source/page references; do not imply imported OCR candidates have become facts.
5. Extend extraction to later Warren pages, then independent marriages and deaths, retaining separate lineage and review queues.
