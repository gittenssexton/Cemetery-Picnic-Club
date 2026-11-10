# CPC metadata import auditing — integration staging

This is a **local-only** importer and Cloudflare staging database schema, not a public ingestion endpoint.

## What is implemented

- `db/migrations/0008_metadata_import_audit.sql`: records the import-batch SHA-256, canonical reference, source citation locator, rights status, record checksum, and review status without changing legacy domain table IDs.
- `scripts/ingest_audited_metadata.py`: validates the GEO map metadata, VIT collection metadata, and IMG local-draft record contracts before writing into an **existing local SQLite** database.
- Exact replay returns a duplicate count and does not insert another source row. A changed payload, changed source row, or previously untracked primary key is an explicit conflict. The batch is rolled back if any record fails.
- `tests/test_audited_metadata.py` exercises repeatability, rights conflicts, source drift, transaction rollback, untracked legacy rows, and the no-fabricated-identity boundary.
- All import records default to controlled review; no automatic linkage, public photos, monument stone assignment, person identification, or burial claim is generated.

## Local operator workflow

Start from a locally initialized database with all current migrations applied and a JSON array of **GEO geologic_map**, **VIT collection**, and/or **IMG field_draft** v1 records.

Dry run:

```bash
python3 -m scripts.ingest_audited_metadata /path/to/records.json
```

Apply to an existing LOCAL test SQLite database only:

```bash
python3 -m scripts.ingest_audited_metadata /path/to/records.json --apply --database /path/to/cpc-local.sqlite
```

No command here uploads to D1. Remote staging migration was applied separately via Cloudflare API; a staging-only ledger tracks SHA and deployment order.

## Source catalog status

- Geology seed `0005_geology_map_sources.sql`: six bibliographic/geologic map sources and three archive asset references, with **zero** accepted geologic units or gravestone provenance claims.
- Vital seed `0006_new_england_vital_catalog.sql`: six state jurisdiction records, Warren's historical alias Western, and one LOC Warren 1910 bibliography collection. **No** vital events, people, matches, or burial records were accepted.
- The Warren birth OCR candidates on the separate vital-record feature branch have not completed original-image QA. Do not place them in accepted `vital_record_entries` until reviewed.

These SQL seeds are **not themselves imported through the v8 audited JSON adapter**. Their seed filenames, GitHub SHA and import scope are instead recorded in the isolated staging seed ledger. Do not misrepresent the audited import table as having handled those seeds.

## Release gates

Before enabling a remote importer: add authenticated caller identity, authorized domain-level permissions, privacy redaction, rate limits, record-level rights checks, durable source-asset checksums, and safe idempotent D1 transactions. Before accepting Warren entries: verify the scanned page, text, source-code lineage (especially G.S.2) and completeness; never infer identity from a matching name alone.

Production, existing Cloudflare Workers, and original photographs remain unchanged.
