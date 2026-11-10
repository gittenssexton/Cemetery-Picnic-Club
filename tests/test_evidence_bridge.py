"""Cited bridge links must be real, reversible and non-authoritative."""
import importlib.util
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bridge", ROOT / "scripts/domain_evidence_bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class EvidenceBridgeTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        for p in sorted((ROOT / "db/migrations").glob("*.sql")):
            self.db.executescript(p.read_text(encoding="utf-8"))
        self.db.execute("INSERT INTO cemeteries(id,name,town) VALUES ('c','Synthetic','Test')")
        self.db.execute("INSERT INTO markers(id,cemetery_id) VALUES ('m','c')")
        self.db.execute("""INSERT INTO images(id,marker_id,rights_basis,analysis_authorized,publish_authorized)
                           VALUES ('photo','m','unknown',0,0)""")
        self.db.execute("""INSERT INTO vital_record_collections
          (id,title,repository,state_code,canonical_url)
          VALUES ('collection','Test','Test','MA','https://example.invalid')""")
        self.db.execute("""INSERT INTO vital_source_documents
          (id,collection_id,source_url)
          VALUES ('doc','collection','https://example.invalid/one')""")
        self.db.execute("""INSERT INTO vital_record_entries
          (id,document_id,local_entry_key,event_type,primary_name_verbatim,entry_verbatim)
          VALUES ('event','doc','1','death','Example Person','Synthetic source reading')""")
        self.db.execute("""INSERT INTO sources(id,title,source_type,access_scope)
          VALUES ('citation','Synthetic source','test','internal')""")
        self.addCleanup(self.db.close)

    def register_two(self):
        bridge.register_reference(self.db, "IMG:photo_original:photo", "photo")
        bridge.register_reference(self.db, "VIT:event:record-001", "event")

    def link(self, **kw):
        args = dict(link_id="link-001",source_ref="IMG:photo_original:photo",
                    target_ref="VIT:event:record-001",relation="possible_subject",
                    evidence_source_id="citation",evidence_locator="synthetic p. 1")
        args.update(kw)
        return bridge.create_candidate_link(self.db, **args)

    def test_register_real_source_rows_and_safe_candidate(self):
        self.register_two()
        self.link()
        row = self.db.execute("""SELECT review_status, access_scope, publication_permission
                   FROM domain_evidence_links WHERE id='link-001'""").fetchone()
        self.assertEqual(row, ("candidate","restricted","unknown"))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM persons").fetchone()[0], 0)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0)
        self.assertEqual(self.db.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_source_cannot_be_fabricated(self):
        with self.assertRaises(ValueError):
            bridge.register_reference(self.db,"GEO:geologic_map:fake","nonexistent")
        with self.assertRaises(ValueError):
            bridge.register_reference(self.db,"VIT:event:fake","nonexistent")

    def test_idempotent_registration_cannot_remap_to_another_source(self):
        bridge.register_reference(self.db, "IMG:photo_original:photo", "photo")
        bridge.register_reference(self.db, "IMG:photo_original:photo", "photo")
        self.db.execute("""INSERT INTO images(id,rights_basis) VALUES ('different','unknown')""")
        with self.assertRaises(ValueError):
            bridge.register_reference(self.db, "IMG:photo_original:photo", "different")

    def test_citation_and_endpoint_must_exist(self):
        self.register_two()
        with self.assertRaises(ValueError):
            self.link(evidence_source_id="fabricated")
        self.db.execute("DELETE FROM images WHERE id='photo'")
        with self.assertRaises(ValueError):
            self.link()
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM domain_evidence_links").fetchone()[0], 0)

    def test_rejection_preserves_source_records_and_original(self):
        self.register_two()
        self.link()
        bridge.reject_candidate_link(self.db,"link-001","synthetic-reviewer","2026-11-10T15:00:00Z")
        self.assertEqual(self.db.execute(
            "SELECT review_status FROM domain_evidence_links WHERE id='link-001'"
        ).fetchone()[0],"rejected")
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0],1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM vital_record_entries").fetchone()[0],1)
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM domain_entity_refs").fetchone()[0],2)
        with self.assertRaises(ValueError):
            bridge.reject_candidate_link(self.db,"link-001","a","2026-11-10T15:00:00Z")


    def test_private_candidate_not_exposed_to_public_lookup(self):
        self.register_two()
        self.link(evidence_note="Private provisional field note")
        internal = bridge.list_links(self.db,"IMG:photo_original:photo")
        self.assertEqual(len(internal), 1)
        self.assertEqual(internal[0]["evidence_note"], "Private provisional field note")
        self.assertEqual(bridge.list_links(self.db,"IMG:photo_original:photo",public=True), [])

    def test_public_lookup_redacts_citation_and_requires_review(self):
        self.register_two()
        self.link(evidence_note="Restricted original transcript")
        self.db.execute("""UPDATE domain_evidence_links
           SET review_status='reviewed',reviewer='reviewer',
               reviewed_at='2026-11-10T15:00:00Z',
               access_scope='public',publication_permission='permitted'
           WHERE id='link-001'""")
        # A link's own permission alone is insufficient.
        self.assertEqual(bridge.list_links(self.db,"VIT:event:record-001",public=True), [])
        self.db.execute("UPDATE images SET rights_basis='own_photo',publish_authorized=1 WHERE id='photo'")
        self.db.execute("UPDATE vital_record_entries SET review_status='reviewed' WHERE id='event'")
        self.db.execute("UPDATE sources SET access_scope='public' WHERE id='citation'")
        rows = bridge.list_links(self.db,"VIT:event:record-001",public=True)
        self.assertEqual(len(rows),1)
        self.assertNotIn("evidence_note",rows[0])
        self.assertNotIn("evidence_locator",rows[0])
        self.assertNotIn("evidence_ref",rows[0])
        self.assertEqual(rows[0]["review_status"],"reviewed")


    def test_public_link_with_private_source_is_hidden(self):
        self.register_two()
        self.link()
        self.db.execute("""UPDATE domain_evidence_links
          SET review_status='reviewed', reviewer='r', reviewed_at='2026-11-10T15:00:00Z',
          access_scope='public', publication_permission='permitted'
          WHERE id='link-001'""")
        self.db.execute("UPDATE images SET rights_basis='own_photo', publish_authorized=1 WHERE id='photo'")
        self.db.execute("UPDATE vital_record_entries SET review_status='reviewed' WHERE id='event'")
        # A restricted evidence citation vetoes the public link.
        self.assertEqual(bridge.list_links(self.db,"IMG:photo_original:photo",public=True), [])
        self.db.execute("UPDATE sources SET access_scope='public' WHERE id='citation'")
        self.assertEqual(len(bridge.list_links(self.db,"IMG:photo_original:photo",public=True)), 1)
        self.db.execute("UPDATE vital_record_entries SET privacy_status='restricted' WHERE id='event'")
        self.assertEqual(bridge.list_links(self.db,"IMG:photo_original:photo",public=True), [])
        self.db.execute("UPDATE vital_record_entries SET privacy_status='public_historical' WHERE id='event'")
        self.db.execute("UPDATE images SET publish_authorized=0 WHERE id='photo'")
        self.assertEqual(bridge.list_links(self.db,"VIT:event:record-001",public=True), [])

    def test_field_draft_never_public_even_after_link_review(self):
        self.db.execute("INSERT INTO field_drafts(id,data_json) VALUES ('draft','{}')")
        bridge.register_reference(self.db,"IMG:field_draft:draft","draft")
        bridge.register_reference(self.db,"VIT:event:record-001","event")
        bridge.create_candidate_link(self.db,link_id="draft-link",
            source_ref="IMG:field_draft:draft",target_ref="VIT:event:record-001",
            relation="possible_subject",evidence_source_id="citation",
            evidence_locator="synthetic p. 1")
        self.db.execute("""UPDATE domain_evidence_links SET review_status='reviewed',
          reviewer='r', reviewed_at='2026-11-10T15:00:00Z',
          access_scope='public', publication_permission='permitted'""")
        self.db.execute("UPDATE sources SET access_scope='public' WHERE id='citation'")
        self.db.execute("UPDATE vital_record_entries SET review_status='reviewed' WHERE id='event'")
        self.assertEqual(bridge.list_links(self.db,"VIT:event:record-001",public=True), [])

    def test_invalid_domain_and_uncited_relation(self):
        with self.assertRaises(ValueError):
            bridge.parse_ref("OTHER:person:one")
        self.register_two()
        with self.assertRaises(ValueError):
            self.link(evidence_locator="")
        with self.assertRaises(ValueError):
            self.link(independently_observed=1)


if __name__ == "__main__":
    unittest.main()
