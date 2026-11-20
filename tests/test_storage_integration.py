"""PostgreSQL integration tests. Run manually with TEST_DATABASE_URL set."""
import importlib.util
import os
import unittest
import uuid
from pathlib import Path

try:
    import psycopg
except ImportError:
    psycopg = None

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("storage", ROOT / "packages/collectors/storage.py")
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)


@unittest.skipUnless(psycopg and os.environ.get("TEST_DATABASE_URL"), "Requires psycopg and TEST_DATABASE_URL")
class StorageIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg.connect(os.environ["TEST_DATABASE_URL"])
        storage.initialize(cls.conn)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_lifecycle_and_idempotency(self):
        board = "test_" + uuid.uuid4().hex[:16]
        job = {"id": uuid.uuid4().hex, "source": "greenhouse", "board": board,
               "source_job_id": "1", "title": "Platform Engineer",
               "url": "https://example.org/jobs/1", "location": "Remote",
               "raw": {"id": 1, "title": "Platform Engineer"}}
        self.assertEqual(storage.upsert_snapshot(self.conn, "greenhouse", board, [job])["created"], 1)
        self.assertEqual(storage.upsert_snapshot(self.conn, "greenhouse", board, [job])["unchanged"], 1)
        changed = {**job, "title": "Senior Platform Engineer", "raw": {"id": 1, "title": "Senior Platform Engineer"}}
        self.assertEqual(storage.upsert_snapshot(self.conn, "greenhouse", board, [changed])["changed"], 1)
        self.assertEqual(storage.upsert_snapshot(self.conn, "greenhouse", board, [])["closed"], 1)
        self.assertEqual(storage.upsert_snapshot(self.conn, "greenhouse", board, [changed])["reopened"], 1)
        with self.conn.cursor() as cur:
            cur.execute("SELECT event_type FROM job_events WHERE posting_id=%s ORDER BY id", (job["id"],))
            self.assertEqual([row[0] for row in cur.fetchall()], ["created", "changed", "closed", "reopened"])

    def test_failed_snapshot_rolls_back(self):
        board = "test_" + uuid.uuid4().hex[:16]
        job = {"id": uuid.uuid4().hex, "source": "greenhouse", "board": board,
               "source_job_id": "1", "title": "Engineer", "url": "https://example.org/1",
               "location": "Remote", "raw": {}}
        with self.assertRaises(ValueError):
            storage.upsert_snapshot(self.conn, "greenhouse", board, [job, job])
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM job_postings WHERE id=%s", (job["id"],))
            self.assertEqual(cur.fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
