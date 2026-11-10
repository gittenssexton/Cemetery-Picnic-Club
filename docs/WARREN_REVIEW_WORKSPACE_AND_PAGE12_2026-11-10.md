# Warren vital-records pilot — offline review workspace, 140 provisional records
**Date:** 2026-11-10. **Environment:** isolated CPC staging, not production.

## What is actually finished

The provisional source pilot now includes **four page-complete candidate sets** from the 1910 *Vital records of Warren (formerly Western)* printed birth section. Initial 75 selected OCR samples, 26 omissions from pages 9–11, and 39 scan-derived entries on printed p. 12 are preserved as **140 source candidates**. The attached original Cornell scan's PDF indices 12–15 correspond to printed pages 9–12.

| Printed page | Candidates | G.S.2 derived |
|--:|--:|--:|
| 9 | 26 | 6 |
| 10 | 35 | 10 |
| 11 | 40 | 1 |
| 12 | 39 | 7 |
| **Total** | **140** | **24** |

**0 named human page-review attestations; 0 accepted vital-record events; 0 persons; 0 burials; 0 identity matches.** The 24 G.S.2 records originate from Pine Grove gravestones and are not independent confirmation of the same original markers.

### Actual isolated Cloudflare D1 result

- Migrated through **0010**; five provenance-linked candidate batches, 140 records.
- Page 12 source batch: `data/vital-records/warren-1910-births-p012-assistant-provisional.json`; batch SHA-256 `568b15d0b7f0944ddb4f15dc19261527828908fecdf0bd3b012341fcab04b358`.
- Source PDF SHA-256 `59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6`.
- No foreign-key violations. All entries remain `requires_page_image_check`, and no human signoff has been fabricated.
- The API Worker has NOT been deployed. Its private internal read-only route supports page `9|10|11|12` and a bounded `after` keyset cursor, so it no longer truncates pages with over 25 entries.

## Faster setup: build directly from the audited source PDF

Use the original Cornell PDF from the connected Drive; the tool checks it against SHA-256 `59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6`. It renders printed pages 9–12 directly and embeds them into a **private local HTML review workspace**:

```bash
python3 -m pip install pymupdf
python3 -m scripts.build_warren_review_workspace --pdf "/path/to/Vital_records_of_Warren_Cornell.pdf" --output warren-review-private.html
```

Open the resulting HTML locally. This option requires no separate PNG extraction, no authentication and no server. It refuses mismatched PDFs rather than making assumptions about printed-page offsets. **Do not upload the generated scan-embedded HTML to public GitHub**. It exports only unsigned review drafts, not approved events.

## Run a private local review workspace

From the integration branch root, with Python 3:

```bash
python3 -m scripts.build_warren_review_workspace --output warren-review-private.html
```

This creates one **offline** HTML file containing all 140 provisional candidate names, per-record SHA-256, source class, and original OCR or scan-line readings. Open it locally in a modern browser. No server, token, online login, geolocation access, or database connection is needed.

To show the actual scanned pages side by side, privately place rendered PNGs into a directory named `warren-scans`, using exact filenames `warren_scan_p09.png`, `warren_scan_p10.png`, `warren_scan_p11.png`, `warren_scan_p12.png`. The first three already exist in this work session; page 12 was rendered from the same owner-held PDF. Then run:

```bash
python3 -m scripts.build_warren_review_workspace --output warren-review-with-scans.html --scan-dir warren-scans
```

**Important:** this second HTML embeds the full historical page images as base64. Keep it local/private, do not add generated HTML to the public GitHub repository or publish its URL. The script refuses to overwrite existing HTML.

Reviewers can select printed page and source candidate, compare the scan on the left with the OCR/readings on the right, write a proposed exact line and corrected name/date, mark **draft only** (consistent, needs correction, hold), and click **Export review drafts as JSON**. The result is a separate unsigned JSON draft file, not a valid signed approval, not a source import, and not a person or cemetery identification. Browser session changes are not auto-synced. Export drafts before closing.

To generate a tabular offline worksheet:

```bash
python3 -m scripts.export_warren_review_sheet --output warren-140-review.csv
```

The worksheet has 140 rows and deliberately blank attestation fields. It does not create an accepted source record.

## What remains intentionally blocked

1. Have a named reviewer inspect source-line fidelity, including the uncertain ABBOT `Jemima` glyph, p. 10 BAKER `I.` initial, BARNES Charles 1849 date and p. 12 names/dates. Preserve exact printed wording and any ambiguous readings, not merely normalized names.
2. Resolve source reuse and provenance for each record; preserve G.S.2 as gravestone-derived. A matching photo is circular corroboration, not independent support.
3. Use the explicit, source-rights-gated `scripts/review_warren_vitals.py` and append-only review tables **only after** someone actually signs the page review. The offline export file does not bypass that process.
4. Field-test the camera GPS and exported ZIP on a real iPhone/Safari device; conduct staging Worker Access/authentication testing and final privacy checks separately.
5. Continue later printed pages incrementally; this pilot does not cover the entire Warren volume, all of Massachusetts, or all of New England.

CI reference: https://github.com/gittenssexton/Cemetery-Picnic-Club/actions/runs/42871544876 — **131 Python tests passing**, Node staging auth and camera EXIF checks passing.

**Do not merge or deploy PR #5 to production based on this pilot alone.**
