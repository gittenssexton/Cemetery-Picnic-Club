# Data Core — Ten-step execution handoff
Date: 2026-11-08

## Implementation milestones
1. **Global research model** — Completed in `db/migrations/0002_global_research_core.sql`. Sources, archives, motifs and makers stand alone without a cemetery.
2. **Bibliographic metadata** — Completed starter dataset of seven linked works in `db/seeds/0003_global_research_sources.sql`. Full texts not imported.
3. **Memento mori interpretations** — Four provisional, linked interpretations backed by pinpointed citations; these do not automatically establish universal meanings.
4. **Institutional archive registry** — Farber and Association for Gravestone Studies collections are represented as metadata, with rights explicitly unverified.
5. **Evidence review queue** — Five initial research/permission/field validation tasks populated.
6. **Repeatable import format** — `data/templates/research_works_example.csv` plus `scripts/import_bibliography.py`. CSV metadata only; validation and dry-run default. `--apply` writes to an existing local SQLite database, never directly to D1 production.
7. **Validation and duplicate protection** — Validates required fields, stable IDs, DOI syntax, status vocabulary, publication year, HTTPS links, duplicates inside CSV; DB rejects duplicate primary keys. No destructive UPSERT is performed.
8. **Cross-cemetery graph invariants** — Tests show global sources and scopes do not depend on cemetery records, interpretations can compete, and shared motifs do not assign maker identities.
9. **Automated tests and export** — GitHub Actions runs all Python unittest cases on migrations and seeds. `scripts/export_research_catalog.py` creates a read-only, rights-conscious JSON catalog from local SQLite metadata; it does not export copyrighted photo objects.
10. **Drive source-handoff and coordination** — Research catalog and acquisition checklist are mirrored in Cemetery Picnic Club research folders. GitHub retains executable source of truth; Drive retains scholarly evidence, notes, and permission documents.

## Reproducible local test
```bash
python3 -m unittest discover -s tests -v
```

## Build a local database for demonstration
```bash
python3 - <<'PY'
from pathlib import Path
import sqlite3
db=sqlite3.connect('cemetery-demo.db')
db.execute('PRAGMA foreign_keys=ON')
for f in ('db/migrations/0001_initial.sql','db/migrations/0002_global_research_core.sql',
          'db/seeds/0001_pine_grove_warren.sql','db/seeds/0002_carver_motifs.sql',
          'db/seeds/0003_global_research_sources.sql'):
    db.executescript(Path(f).read_text(encoding='utf-8'))
db.close()
PY
python3 scripts/import_bibliography.py data/templates/research_works_example.csv --check
python3 scripts/export_research_catalog.py --database cemetery-demo.db --output research-catalog.json
```

## Essential trust and data design
- A person, burial, marker and memorial remain separate entities.
- Biography metadata is not equivalent to reviewed full text or permission to reproduce text.
- The Farber archive's image permissions are not assumed.
- One global culture/symbol classification may link to many cemeteries, with distinct traditions and time frames.
- Source claims, predictions, iconographic observations and scholarly interpretations must remain distinguishable.
- Pine Grove is an identification pilot, not a filter on research.
- No production D1 database, photo bucket, online import endpoint or public research search service has been provisioned or deployed by this milestone.

## Next production prerequisites
- Verify data rights and institution-specific metadata reuse permissions before large-scale imports.
- Review research source texts and resolve citation locations for the catalog.
- Add login, privacy, abuse controls and authorization before accepting member uploads.
- Provision staging D1/R2 and implement a Worker API; secure it before production deployment.
- Conduct physical iPhone field tests of photo capture, storage limits, GPS accuracy and permissions.
