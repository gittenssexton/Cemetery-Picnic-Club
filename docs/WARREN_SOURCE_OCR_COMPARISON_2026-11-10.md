# Warren 1910 birth records — source-to-source OCR comparison (not scan verification)

**Current state:** 75 candidate OCR readings from three selected 25-record samples, 0 scan-verified or accepted records. Source rights: LOC lists the digitized book as public domain. Do not treat two OCR text layers of the same 1910 printed book as independently corroborating historical evidence.

## Newly grounded page-image locators

The Library of Congress public gallery index identifies **digital Image 13 = printed p. 9**, **Image 14 = printed p. 10**, and **Image 15 = printed p. 11** of the Warren births section. These are catalog/image-sequence locators **only**, not proof that the corresponding page pixels were examined.

- Gallery: https://www.loc.gov/resource/gdcmassbookdig.vitalrecordsofwa00war/?st=gallery
- Canonical book: https://www.loc.gov/item/10008543/
- Structured mapping: `data/vital-records/warren-1910-loc-page-locators.json`

**Do not** use these index numbers as `image_sha256` values, do not mark `source_image_verified=true`, and do not set `scan_checked` or accept any event. Scan retrieval/visual inspection remains outstanding.

## Contradictions between the public extracted text layers

| Candidate | Printed page | Cornell/Wikimedia extracted text | LOC indexed OCR description | Disposition |
|---|---:|---|---|---|
| `MA-WARREN-RICE1910-BIRTH-P009-001` ABBOT George | 9 | Mother's name appears `Jemama` | Mother's name rendered `Jemima` | **Conflict**: compare printed Image 13; neither reading is scan-confirmed |
| `MA-WARREN-RICE1910-BIRTH-P011-001` BARNES Charles | 11 | Date rendered `July i, 1849` | Gallery describes `July 1 1840` | **Conflict**: urgently compare printed Image 15; structured 1849 date remains provisional |
| `MA-WARREN-RICE1910-BIRTH-P010-001` ASHLEY Anna | 10 | `Feb. 20, 1748-9` | OCR renders `Feb 20 17489` | Dual-year notation needs visual inspection; do not force one modern ISO year |
| `MA-WARREN-RICE1910-BIRTH-P010-024` BAKER Marion | 10 | `Marion L Fairbank` | Indexed gallery lists BAKER entries but does not resolve initial | **Still unresolved**: L/I |
| `MA-WARREN-RICE1910-BIRTH-P011-022` through `-025` BARNUM group | 11 | `BARNUM` | Gallery excerpt does not resolve individual surname glyphs | Correction from `BARWUM` remains text-layer-only |

## Other source-text checks

- Cornell text layer renders p. 9 ARNOLD Betsy's date as `Dec. 7, 1803` and ARNOLD Rodoulphus by that spelling; this reduces OCR ambiguity but is **not** scan verification.
- Cornell layer displays an unnamed ANDERSON son and unnamed BAKER child; these must remain unnamed, never be silently assigned artificial legal names.
- The publisher's glossary describes `G.S.2` as Pine Grove gravestones; the 14 G.S.2 entries cannot be independent proof of the same original grave marker.

## Explicit review actions

1. Retrieve page-image pixels for LOC Image 13, Image 14, Image 15; record stable image URLs and compute actual SHA-256 of each downloaded image.
2. Compare both conflicting ABBOT spelling and BARNES Charles year first, then the remaining 11 OCR-annotated entries; inspect all 75 before accepting anything as page-verified.
3. Record verified exact print lines using named human scan-review evidence; preserve the original OCR candidate bytes/hashes and publish no private notes or original photos.
4. Inventory omitted rows on p. 9, 10, 11; these three batches are not page-complete.

**Engineering gate:** No action above has been logged as complete. The staging D1 remains 75 unverified candidates, zero review attestations, zero accepted events.

## Update: original Cornell page pixels recovered from connected Drive

**Supersedes the earlier scan-access blocker above.** The owner-held original Cornell digitization was located and fetched from Google Drive at https://drive.google.com/file/d/1Wn4XG9cI59RfkhTuevKwu4xoBHIBkaZI/view. The 204-page PDF has SHA-256 `59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6`. Its **PDF pages 13–15 (zero-index 12–14)** display printed pages 9–11.

The assistant rendered and inspected the actual page images at 2.4x. The exact rendered image SHA-256 fingerprints are printed p. 9 `86a4367f3425a5b24ab4f85ea120dda8fb825380477b774e6faffb94adf9f848`; p. 10 `8dda636648e75444ecd1fa63fbdc71c2ad2c0315dd10e78a71b40c84739ca18d`; p. 11 `775780404ee21ec22635ed5d64679b8db1a3e6012fc35567272fcd8a0e7cdbe2`. The images are render derivatives, not a checksum for a separately downloaded original image.

**Image-informed findings on 13 previously flagged OCR candidates:**
- Printed p. 9 **ABBOT George:** mother reads **Jemima**, not Cornell OCR `Jemama`. **ARNOLD Betsy:** year **1803**. **ARNOLD Rodoulphus:** the printed spelling is **Rodoulphus**. The unnamed ANDERSON son has a blank name line; do not assign a given name.
- Printed p. 10 **ASHLEY Anna:** **February 20, 1748–9**, preserving dual-year notation. **BACON Jeptha Jr.:** apparent bracketed uncertain parentage; **G.S.2** source remains dependent on a gravestone. **BAKER Marion I. Fairbank:** middle initial looks like printed **I.**, not L.; **G.S.2** remains gravestone-derived. Another BAKER child is unnamed in the printed line.
- Printed p. 11 **BARNES Charles:** date is **July 1, 1849** (not LOC indexed OCR 1840); mother's name **Marsha**. **Four BARNUM candidates:** the heading on the printed page is **BARNUM**, not OCR `BARWUM`.

These are **assistant-assisted visual readings**. The machine-readable proposed corrections, original file fingerprint and candidate IDs are stored at `data/vital-records/warren-1910-assisted-visual-review-2026-11-10.json`. A named human reviewer has NOT signed off on these images: **do not populate `vital_ocr_page_reviews`, change canonical OCR source JSON, set `source_image_verified`, or promote `vital_record_entries` without that separate attestation and rights workflow**.

The scanned page images still need person-level review before final catalog acceptance. Scans show more lines than the selected 25-record sample lists; page completeness and omissions must also be audited.
