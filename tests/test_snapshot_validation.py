import importlib.util
import sys
import types
import unittest
from pathlib import Path

# Validation has no database dependency; the import does not connect to a DB.
root = Path(__file__).resolve().parents[1] / "packages" / "collectors"
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location("collect_to_db", root / "collect_to_db.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SnapshotValidationTests(unittest.TestCase):
    def setUp(self):
        self.job = {"id": "1", "source_job_id": "1", "title": "Engineer",
                    "url": "https://example.org/1", "source": "greenhouse", "board": "demo"}

    def test_valid(self):
        module.validate_snapshot([self.job], "greenhouse", "demo")

    def test_empty_rejected_by_default(self):
        with self.assertRaises(ValueError):
            module.validate_snapshot([], "greenhouse", "demo")

    def test_empty_explicit_override(self):
        module.validate_snapshot([], "greenhouse", "demo", allow_empty=True)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            module.validate_snapshot([self.job, self.job], "greenhouse", "demo")

    def test_wrong_board_rejected(self):
        with self.assertRaises(ValueError):
            module.validate_snapshot([self.job], "greenhouse", "another")

    def test_missing_title_rejected(self):
        with self.assertRaises(ValueError):
            module.validate_snapshot([{**self.job, "title": ""}], "greenhouse", "demo")


if __name__ == "__main__":
    unittest.main()
