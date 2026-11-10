# Warren vital records — extraction checkpoint 2
Date: 2026-11-10
Branch: `feature/new-england-vital-records-core`

## Batch manifest
- `data/vital-records/warren-1910-births-p009-batch01.json`: 25 OCR-assisted candidate entries, birth section, **printed page 9**, 6 explicitly marked `G.S.2.` (Pine Grove Cemetery).
- `data/vital-records/warren-1910-births-p010-batch02.json`: 25 OCR-assisted candidate entries, birth section, **printed page 10**, 7 explicitly marked `G.S.2.`.

**Total 50 candidate entries**, **13 Pine Grove gravestone-derived**, **37 other entries provisionally assigned town-book source**. These counts are drawn from the JSON files, not inferred from total book coverage.

## Machine validation results
- 25 unique IDs in each batch (50 total); no missing printed page or normalized name; no invalid ISO date format.
- All 50 candidates correctly have `review_status: requires_page_image_check`; none were promoted to verified.
- Dates such as Ashley's 1748–49 and bracketed/uncertain pedigree for Jeptha Bacon intentionally retain uncertainty.
- Page 10 contains an unnamed child and a period race descriptor; the normalized name omits the descriptor and retains a review note. Do not silently publish historic descriptors without context.
- A direct scan-page screenshot attempt failed due a remote PDF cache miss. The OCR/text text is **not a literal verified transcription**. Some surname spelling and dates may need correction from page images.

## Anti-circularity
Publisher's `G.S.2.` indicates Pine Grove Cemetery gravestones. Thus all 13 such entries are **dependent on gravestone evidence**; they cannot independently verify photographed markers or a gravestone transcription.
Publisher `G.S.1.` indicates South Warren gravestones; other sources may be marked C.R. or P.R. See the book's preface before automated parsing.

## Links and source
- Canonical public-domain book: https://www.loc.gov/item/10008543/
- LOC reader: https://www.loc.gov/resource/gdcmassbookdig.vitalrecordsofwa00war/
- Secondary OCR comparison: https://ldsgenealogy.com/MA/Vital-records-of-Warren-formerly-Western-Massachusetts-to-the-end-of-the-year-1849.htm (warns AI text can contain errors)
- Franklin P. Rice, ed./publisher, *Vital Records of Warren (Formerly Western), Massachusetts, to the End of the Year 1849* (Worcester, MA, 1910), pp. 9–10.

## Integration gate
**Do not yet insert as final `vital_record_entries`**: that table requires a verbatim source entry, but these extracted records are normalized OCR candidates and the scans have not been visually compared. Avoid fabricating `entry_verbatim` or LOC image sequence. Keep staging as JSON until reviewed.

## Next
1. Obtain accessible page images of print pages 9 and 10 and review all 50 candidate readings.
2. Record exact printed entry segments and scan sequence to populate `vital_source_page_refs` reliably.
3. Produce audited SQLite seed with `vital_record_entries`, participant roles and `G.S.2.` source-code classification; test using `PRAGMA foreign_key_check`.
4. Begin marriages and deaths as independent collections after pilot QA.
5. Make provisional matches against Pine Grove stones while keeping them **candidates only**.
