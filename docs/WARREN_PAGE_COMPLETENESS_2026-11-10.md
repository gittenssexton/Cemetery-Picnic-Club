# Warren 1910 source pages 9–11 — complete pilot candidate reconciliation
Prepared 2026-11-10. **The 101 records are OCR/assistant-assisted source candidates, not approved historical events.**

## Scope and audit

Cornell University scan of *Vital records of Warren (formerly Western), Massachusetts, to the end of the year 1849* (Franklin P. Rice, 1910): printed pages **9, 10, 11**, PDF indexes **12, 13, 14** (zero-based).

Original scan available from the owner-held Drive file `1Wn4XG9cI59RfkhTuevKwu4xoBHIBkaZI`. Original PDF SHA-256:
`59c84a3f62810733555d7631c02ad7fd9f5cebd8dce6891f57f69192f4f830b6`.

| Page | Initial selected candidates | Previously omitted | Full line-candidate count | G.S.2 |
|---|---:|---:|---:|---:|
| 9 | 25 | 1 | 26 | 6 |
| 10 | 25 | 10 | 35 | 10 |
| 11 | 25 | 15 | 40 | 1 |
| **Total** | **75** | **26** | **101** | **17** |

These counts describe the **individual printed entries visible on the three pages** (including unnamed children and entries with dates derived from gravestones). They are not 101 uniquely identified people and not 101 independent original-town-register records. The 17 `G.S.2` entries derive from Pine Grove gravestones; the corresponding gravestone photographs do not independently corroborate the same information.

## Omitted-entry names and line sources

- **p. 9 (1):** ARNOLD Sophia Augusta.
- **p. 10 (10):** BALLARD Jacob Hamilton; BANISTER Eli, Levi and Timothy; BARDWELL Francis M. and Lucy B. Tyler (**G.S.2**); BARLOW Asael and Huldah; BARNES Aaron and Asa (**Asa = G.S.2**).
- **p. 11 (15):** BARNUM Nathan Gardner, Read Cutler and Warren Rice; BARRUS Achsah, Ame, Amos, Anne, Betsey, Charlottee, Clarise, Deborah, Esther (two distinct entries, 1748 and 1770), Jason and Joel.

All 26 entries have stable `...-OM###` candidate IDs, page index, original PDF SHA fingerprint, visually transcribed source line, date as printed, parents when present, and G.S.2 lineage where marked. Source:
`data/vital-records/warren-1910-page-omissions-2026-11-10.json`.

Original 75 records and their IDs/hashes were **not rewritten**. Supplemental source batches contain the additional 26.

## Actual isolated staging D1 results

- Applied supplementary candidate batch `warren-1910-page-omissions-2026-11-10.json` (26 rows), SHA-256:
`4a5cda37feae52279d3f0d3482e3c652a57abd5636ac0301705a4bc15e5a6c5c`.
- Total provisional candidates: **101**. Four source batches. Scan-approved: **0**. Human page reviews: **0**. Accepted vital events: **0**. People: **0**. Burials: **0**. Identity matches: **0**.
- `PRAGMA foreign_key_check` returned **zero violations**.
- No edits to Cartoveyra's database or production Workers.

## Software

- `scripts/stage_warren_page_omissions.py` validates and stages the 26 supplements; dry-run by default and local-only on the CLI. It detects changed records and refuses repeated imports with conflicting hashes.
- `tests/test_warren_page_omissions.py` verifies exact per-page totals, 17 dependent G.S.2 source entries, no identities or events, exact duplicate replay and rejection of altered provenance.
- `scripts/export_warren_review_sheet.py` now generates a **101-row** human review CSV worksheet, still with all human attestation/approval fields blank.
- `server/cpc-integration-staging.mjs` adds bounded keyset pagination to the **undeployed**, authenticated review-only Worker. Pages containing 26, 35 and 40 candidates can be paged through without losing rows to the old `LIMIT 25` behavior.

## Interpretation and outstanding work

This is **page-coverage reconciliation**, not a claim that all text is historically verified. Source-page checks, transcription ambiguity audit (including names/dates), named human approvals, independent source checks, omitted-record regression tests, and rights review are still necessary before accepting a single event into the canonical vital entry table. The first 75 and 26 new lines need review as one page-complete set. Do not infer identity, citizenship, burial, gravestone location or living descendants.

The LOC source code glossary identifies `G.S.2` as Pine Grove Cemetery gravestone evidence. Other sources in the compiled book require source-level attribution, not automatic labeling as independently obtained town registers.
