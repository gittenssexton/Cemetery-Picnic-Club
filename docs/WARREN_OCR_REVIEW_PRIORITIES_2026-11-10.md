# Warren 1910 births — provisional OCR review priorities
**Prepared 2026-11-10 | CPC integration staging | Original printed pp. 9–11**

## Verified engineering status

- Isolated D1: `cemetery-picnic-club-integration-staging`; migration `0009_vital_ocr_review_queue.sql` added and recorded in staging migration ledger.
- Copied the **original three JSON research batches** from `feature/new-england-vital-records-core` to the integration branch without changing their candidate text. The source files are **selected 25-record samples**, not all entries on those pages.
- Staged all **75 unique OCR candidates** into `vital_ocr_review_candidates`, never into accepted `vital_record_entries`. Exactly **25 each** from printed pages 9, 10, and 11; **14** have G.S.2 Pine Grove gravestone provenance. All **75 remain unverified**, digital image sequence unknown.
- Three batch SHA-256 values recorded, and individual source records have SHA-256 of the complete candidate JSON. `PRAGMA foreign_key_check` returned no violations.
- Accepted vital events: **0**; persons: **0**; burials: **0**; identity matches: **0**. Source images were not downloaded, modified, or published.
- Do not infer that independently scanned Cornell/LOC text layers equal manual inspection of original page images.

## Page-by-page review inventory

| Printed page | Selected candidates | G.S.2 gravestone-derived | Missing ISO-normalized date | Non-day precision | Candidates with OCR notes |
| --- | ---: | ---: | ---: | ---: | ---: |
| 9 | 25 | 6 | 5 | 5 | 4 |
| 10 | 25 | 7 | 5 | 5 | 4 |
| 11 | 25 | 1 | 1 | 1 | 5 |
| **Total** | **75** | **14** | **11** | **11** | **13** |

The lack of an ISO date can be historically correct (year-only or ambiguous original date). Do not fill in missing day/month.

## Highest-priority image-level checks

- **p. 9, ABBOT George** `MA-WARREN-RICE1910-BIRTH-P009-001`: mother's spelling `Jemama` in a text layer versus earlier normalization `Jemima`; verify printed image, retain exact source spelling.
- **p. 9, ARNOLD Betsy** `...P009-019`: apparent `1S03` OCR year, provisionally rendered 1803; inspect original digits.
- **p. 9, ARNOLD Rodoulphus** `...P009-024`: name variant `Rodbulphus` in OCR, unresolved; confirm letterforms.
- **p. 9, ANDERSON unnamed son** `...P009-017`: unnamed child is not a verified given name; preserve relationship context.
- **p. 10, ASHLEY Anna** `...P010-001`: provisional dual-year `1748-9` and `174S-9` OCR text; review date precision before normalization.
- **p. 10, BACON Jeptha Jr.** `...P010-012`: G.S.2 gravestone-derived; confirm age/year wording but do not count photo and printed G.S.2 as two independent sources.
- **p. 10, BAKER Marion** `...P010-024`: uncertain middle initial L versus I. This is also G.S.2.
- **p. 10, BAKER unnamed child** `...P010-025`: do not invent a child name.
- **p. 11, BARNES Charles** `...P011-001`: OCR parent name `Alarsha` versus staged `Marsha`; inspect printed entry.
- **p. 11, four BARNUM entries** `...P011-022` through `...P011-025`: cross-text correction of OCR `BARWUM` to `BARNUM`; still requires printed image review.

There are **13 records with explicit notes** in the batch files. The priority examples above organize the same notes; they do not claim additional independently verified errors.

## Review protocol

1. Obtain and retain a rights-cleared original page-image reference for each printed page; determine the corresponding digital-image number **from the image**, not by guessing the offset.
2. For each candidate, compare the full line on the page and preserve source text verbatim, printed page, spelling, typography and source abbreviation.
3. Explicitly mark uncertain names/dates and differentiate OCR text, corrected reading and original source wording. Include reviewer, date and scan locator in subsequent approval events.
4. Check **page completeness**: the batches are intentionally incomplete samples. Capture omitted lines separately with stable identifiers.
5. Classify G.S.2 as Pine Grove gravestone-derived dependent evidence. Matching the same marker image is not independent support.
6. Only after visual QA, add reviewed **source events** through an explicit acceptance workflow. Never automatically create people, cemetery burials, or family relationships from these candidate names.

## Operator entry point

```bash
python3 -m scripts.stage_warren_ocr_review
python3 -m scripts.stage_warren_ocr_review --apply --database /path/to/prepared-local.sqlite
```

The first command validates and performs **no write**. The second requires a previously migrated local SQLite DB and the `0006` vital bibliography seed. It stages provisional candidates only. Production remains unchanged.


## Additional public-source access check

- The separate Cornell/Wikimedia PDF text layer was accessible through a public search result. It displays the publisher's statement that sources include supplements to town records; the abbreviations confirm `G.S.2` is Pine Grove gravestone material. Pages labeled 9–11 include the flagged ABBOT `Jemama` / `Jemima`, ASHLEY dual-year notation, BAKER middle initial and BARNUM surnames in machine-extracted text.
- **Not scan-verified:** attempts to obtain rendered PDF page screenshots (page indexes 16–18) returned a cache-miss error; a separate Internet Archive PDF request was inaccessible. Consequently **no candidate was promoted**, and `source_image_verified` remains false for all 75.
- Public reference: https://upload.wikimedia.org/wikipedia/commons/6/69/...Vital_records_of_Warren_%28formerly_Western%29%2C_Massachusetts%2C_to_the_end_of_the_year_1849_%28IA_cu31924028839573%29.pdf
- Reading the OCR/text layer is useful for prioritization but must not be called visual confirmation of print or independent corroboration.
