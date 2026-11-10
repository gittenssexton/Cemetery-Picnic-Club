# Warren vital records — extraction checkpoint 1 (2026-11-10)

## Actual work completed
- Read published full text of *Vital Records of Warren (Formerly Western)*, 1910, at https://www.loc.gov/item/10008543/ (OCR/text source; book itself public-domain).
- Inspected the publisher's legend: **G.S.2 = gravestone, Pine Grove Cemetery at Warren Centre**; **G.S.1 = South Warren Cemetery**, C.R. = church record.
- Extracted **25 structured birth-entry candidates** from **printed page 9** (ABBOT through ARNOLD, excluding the final ARNOLD Sophia Augusta entry as the next batch boundary).
- Registered name as printed, date with precision, parent or spouse context when stated, surname spelling, page number, original reference code and an explicit source class.
- **6 of 25 are G.S.2 Pine Grove-derived entries:** Eunice Ainsworth, Jabez Ainsworth, Nancy M. Stone Allen, Pardon P. Allen, Ruth Tyler Allen and Sally Stanford Allen.
- These six **MUST NOT** be used as independent corroboration of matching Pine Grove stones.
- **19 of 25** have no printed G.S.2 code and are *provisionally* classified town-book-origin; publisher states unmarked entries generally come from town books. This still requires original-page verification.
- Ambiguities: 'Betsy Arnold' year OCR reads `1S03` (tentatively interpreted 1803); 'Rodoulphus Arnold' spelling OCR differs across copies; one Anderson son is unnamed; 'Abbot/Abbott', 'Adams/Adoms' variants remain distinct as printed.

## Verification restriction
Attempted direct image inspection of the LOC/Wikimedia PDF page, but the image service returned a cache miss. No candidate is marked verified. The JSON contains structured working interpretations from OCR and **not** a diplomatic verbatim transcription or certified event record.
- Source page: 9
- Digital scan sequence: **not yet validated**, intentionally null in JSON.
- Do not import these rows into public-facing `vital_record_entries` as `record_level=original`.
- Do not link candidates to `persons`, `burials`, or `markers` without actual evidence review.

## Source
Franklin P. Rice (publisher), *Vital Records of Warren (Formerly Western), Massachusetts, to the End of the Year 1849* (Worcester, 1910), printed p. 9, births. Library of Congress LCCN 10008543.
LOC digitized edition: https://www.loc.gov/resource/gdcmassbookdig.vitalrecordsofwa00war/
OCR alternative: https://ldsgenealogy.com/MA/Vital-records-of-Warren-formerly-Western-Massachusetts-to-the-end-of-the-year-1849.htm (explicitly warns AI-based transcription may contain errors).

## Next required actions
1. Open scan and visually review printed p. 9. Resolve OCR uncertainties and distinguish exact printed spellings.
2. Save literal `entry_verbatim` spans and authoritative digital image sequence after review.
3. Then generate D1-ready inserts with reproducible IDs and source-code/participant links.
4. Expand next batch with remaining ARNOLD and p. 10; verify each.
5. Review 25 entries before any D1 population; protect living persons for later volumes.
