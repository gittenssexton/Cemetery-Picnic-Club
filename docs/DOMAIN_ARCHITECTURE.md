# CPC Domain Architecture and Nomenclature — RFC 001
Status: implemented **as a registry and validation contract on a feature branch**; application/data migration integration remains pending.

## One core, independent disciplines

Cemetery Picnic Club is one global evidence graph with **bounded disciplinary modules**. Each domain may ingest, validate, review and search data independently. Shared entity references, rather than copied records, connect them. A blocked geology import must not prevent vital-record processing or a camera capture.

```text
                         CPC shared identity / evidence core
                 (sources, claims, rights, review, provenance)
                                      |
        +-------------+---------------+--------------+-------------+
        |             |               |              |             |
     GEO geology   VIT vital        ICO motifs     IMG camera    CAR carvers
        |             |               |              |             |
        +-------------+---------------+--------------+-------------+
                                      |
                           typed, cited relationships
                           to CEM / KIN / LOC / HIS / CON
```

## Rules every field follows

1. Each field owns a three-letter namespace: `GEO`, `VIT`, `ICO`, `CAR`, `IMG`, `HIS`, `KIN`, `CEM`, `LOC`, `CON`. The machine-readable [domain registry](../architecture/domain-registry.json) is the canonical inventory.
2. Field names and term definitions belong to their owning domain. Example: `GEO.geologic_unit` (mapped rock in a region) is **not** `GEO.material_candidate` (what the monument may be made from). `VIT.event` is **not** `CEM.burial`.
3. Canonical cross-module references use `<domain>:<entity-type>:<stable-id>`. Existing SQLite IDs are grandfathered in and can be wrapped, not rewritten. Do not merge records by display text.
4. Every assertion must carry a source or explicit evidence-missing state, citation locator when available, confidence, review status, valid/event time vs recording time, and rights. Existing tables don't all have the same columns: adapt through a versioned API/contract, not a destructive blanket schema rewrite.
5. Every module has an **ingest → normalize → validate → stage → human review → publish** pipeline. No unknown-licensed content is silently published or used for training. A data source may be visible in a research inventory without ingestion permission.
6. Producers publish facts or *candidate hypotheses* with explicit status. Consumers must not silently promote a candidate into a fact. Cross-domain links are independently justified claims.
7. Field-specific transformations are independent: a GIS raster conversion cannot block inscription transcription, but any shared claim must cite its geologic or archival source.
8. All source changes go through repeatable tests, migration dry-runs, and provenance checks. Database schema and API changes are versioned; breaking changes require migration and a compatibility plan.
9. Historical place names, international script/terms, calendar systems, uncertain dates and local terminology stay intact alongside normalized search fields. No geographic limit is imposed by Pine Grove.
10. Publication/analysis permissions, living-person privacy, sensitive cemetery locations, and heritage restrictions are enforced **at each module boundary**, not just at a UI screen.

## Exemplary cross-domain question

Photo IMG:capture:p1 shows a slate-like texture. `GEO.material_candidate` may suggest slate; `LOC.coordinate_observation` may place the photographer near mapped bedrock; `CAR.attribution_candidate` may note a historic workshop used slate; `VIT.event` may contain a possible death date. **None proves the others.** The unified interface can present candidate results together with their respective evidence and uncertainty.

## Directory convention (target for new work)

```
architecture/domain-registry.json      machine-readable domain ownership/terms
docs/DOMAIN_ARCHITECTURE.md             this policy
db/migrations/                          globally sequential, immutable deployment migrations
db/seeds/                               provenance-aware source-specific seed data
domains/<code>/README.md                terminology and responsibilities
domains/<code>/contracts/v1/            versioned input/output JSON schemas
domains/<code>/ingest/                   source adapters; no cloud publication by default
domains/<code>/tests/                    fixtures and domain-specific test data
tests/                                   integration tests across domain boundaries
```

We do **not** need separate deployed databases for each discipline now. Cloudflare D1 is suitable for initial relational joins and independent, bounded modules; R2 can hold authorized media and tiled geology when enabled. Later service splits should be a scaling decision, not an assumption.

## The migration conflict found in the November 10 audit

`main` already contains `0001`, `0002`, `0003`.

- Geology branch contains `0004_geological_map_core.sql`
- Camera PR #3 contains `0004_monument_analysis.sql` (duplicate!)
- Vital records branch contains `0005_new_england_vital_records.sql`

**Integration sequence planned:** keep geology at 0004; rename the camera migration to 0005; rename vital-records to 0006. Validate dependencies and all seeds together **in an integration branch**, then stage against a fresh database. This is a proposal, not yet a committed merge. Never rename a migration that has already been executed on production; append reconciliation migrations instead.

Branch owners should not merge over one another's migration number. CI must reject duplicate numeric prefixes, missing table dependencies and regressive changes. Avoid changing unrelated Worker deployments.

## Immediately usable development convention

For a new dataset, create a domain entry, name its entities/terms and allowed statuses, provide source/rights/review rules, run a validator on a small sample, stage and review; *then* propose shared links. This enables parallel work without duplicated definitions or circular evidence.

## Current state

A declarative domain registry and validation tests can enforce **terminology, namespace and migration-plan consistency**. Full branch integration, secure D1 deployment, live query services and research ingestion remain separate tasks. Existing legacy SQL tables are left untouched by this RFC.
