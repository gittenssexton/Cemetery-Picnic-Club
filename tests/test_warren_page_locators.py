"""LOC image-index crosswalk is a locator, never evidence of visual scan approval."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class WarrenPageLocatorTests(unittest.TestCase):
    def test_loc_page_crosswalk_and_unverified_status(self):
        source=ROOT/"data/vital-records/warren-1910-loc-page-locators.json"
        item=json.loads(source.read_text(encoding="utf-8"))
        self.assertFalse(item["scan_content_verified"])
        self.assertEqual(item["collection_id"],"ma-warren-1849-rice1910")
        pages=item["mappings"]
        self.assertEqual(
            [(r["printed_page"],r["loc_image_sequence"]) for r in pages],
            [(9,13),(10,14),(11,15)])
        self.assertTrue(all(r["scan_content_verified"] is False for r in pages))
        for record in pages:
            self.assertNotIn("image_sha256",record)
            self.assertNotIn("reviewer_id",record)

    def test_original_source_batches_not_falsely_updated(self):
        for page in (9,10,11):
            pattern=f"warren-1910-births-p{page:03d}-batch{page-8:02d}.json"
            file=ROOT/"data/vital-records"/pattern
            data=json.loads(file.read_text(encoding="utf-8"))
            self.assertEqual(len(data["records"]),25)
            self.assertTrue(all(r["source_image_verified"] is False
                                and r["review_status"]=="requires_page_image_check"
                                and r["source"]["digital_page_sequence"] is None
                                for r in data["records"]))


if __name__=="__main__":
    unittest.main()
