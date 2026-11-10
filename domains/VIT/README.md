# VIT domain — CPC evidence contract v1

**Scope:** Historical source collections, verbatim vital-record entries, participants and reviewable identity leads.

Use `contracts/v1/record.schema.json` for cross-domain exchange. Canonical references use `VIT:<entity_type>:<stable_id>`. The schema is an interchange contract; it does not replace the existing SQL table primary keys.

## Intake and review
1. Obtain permitted source; retain original and its checksum where applicable.
2. Preserve the original spelling/observation alongside normalizations.
3. Record observed timestamp separately from historic event date, geography accuracy and coordinate datum as applicable.
4. Track access, analysis and publication permissions separately.
5. Stage hypotheses at `candidate` or `unreviewed` status; do not promote based on name, proximity, appearance or AI output alone.
6. Save reversible typed links with explicit evidence and reviewer state. Withdrawal of a candidate cannot delete its underlying source.

**Domain boundary:** A source statement is not a verified historical event or an identity match.

The first contract and tests use synthetic data only. No production ingestion or licensing authorization is implied.
