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
