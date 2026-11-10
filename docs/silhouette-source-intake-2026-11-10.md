# Silhouette source intake — 2026-11-10

## First-party source catalog
- **Farber (2003)**: [AAS free PDF](https://www.americanantiquarian.org/sites/default/files/2026-04/farber.pdf). 57-page study; extensive section on early New England sizes and shapes, tripartite markers, transitions in shoulder styles, and carver attribution. **Free access does not grant general commercial image/model training rights**; use paraphrased typology and seek permission before bulk harvesting.
- **Forbes (1927)**: [Google Books full view with PDF and EPUB download links](https://books.google.com/books?id=ZawgAAAAMAAJ). Foundational Massachusetts/New England stonecarvers and gravestone forms. Original 1927 US edition is expected to be in the public domain in the US; verify each scan/edition and any separately reproduced photographs.
- **NPS Preservation Brief 48 (2016)**: [download government PDF](https://www.nps.gov/subjects/ncptt/upload/Preserving-Grave-Markers-in-Historic-Cemeteries.pdf). Formal classification of single-element/multiple-element/structures and practical material-condition context. Identify third-party photo rights independently.
- **NPS rapid cemetery survey form**: [download PDF](https://www.nps.gov/subjects/ncptt/upload/NCPTT-CEMETERY-SURVEY-FORM.pdf). Useful field terminologies and materials checklist.
- **AAS Farber image collection**: [collection](https://www.americanantiquarian.org/farber-gravestone-collection). More than 13,500 images documenting 9,000+ grave markers. Individual item rights/licensing and acceptable bulk reuse must be checked before downloading or training; do **not** assume a freely accessible collection is open licensed.
- **Project Gutenberg Perkins (1902)**: [Handbook of Old Burial Hill, Plymouth, Massachusetts](https://www.gutenberg.org/ebooks/70098), explicitly public domain in USA and downloadable. Strong local-site/inscription reference, weaker for silhouette taxonomy.
- **Ludwig, Graven Images (1966)**: [publisher information](https://www.weslpress.org/9780819560407/graven-images/). Valuable contextual scholarship, **not open source**. Library/loan access does not authorize redistribution or training; licensed consultation only.
- **User's own scan**: `Scan Nov 8, 2026 at 7.00 PM.pdf` in Cemetery Picnic Club Drive. Illustrated motifs and explanations (scan pages 3–7). This is for symbol semantics, not a comprehensive silhouette manual. Publishing illustrated elements requires a separate rights check.

## Research extraction completed
`data/gravestone_silhouette_vocabulary_v01.json` contains original normalized taxonomy for marker form, top profile, shoulders, finials, borders, relative geometry, condition and capture protocol. Terms were derived from source descriptions, not copied illustrations.

## Next verified work
1. Map current `0004_monument_analysis.sql` fields to the new controlled vocabulary; add discriminators as reversible candidate classifications rather than overwriting source descriptions.
2. Assemble a rights-checked labeled *photograph* set. A silhouette classifier needs images of complete stones and segmentation masks, not text alone. Prioritize user's owned Pine Grove images with verified permissions.
3. Label **full contours** plus tympanum, shoulder, base and border landmarks. Record the visible above-ground shape and any obscured/broken segments separately.
4. Annotate source, location, dated inscription, whether the stone may have been reset, maker attribution confidence and material type.
5. Quantitatively test segmentation with held-out stones and diverse lighting; track IoU and boundary F-score. Avoid conflating regional stylistic tradition with a specific carver.

## Restrictions
Source-linked facts are not machine-learning ground truth without independent image annotation. A book's PDF accessibility is not an automatic license to republish its images. First iteration should remain New England-focused but keep a global-friendly generic form vocabulary.
