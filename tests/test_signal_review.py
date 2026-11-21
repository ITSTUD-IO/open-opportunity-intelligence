import importlib.util
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "packages" / "signals"


def load(name):
    spec = importlib.util.spec_from_file_location(name, root / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rules = load("rules")
review = load("review")


def posting(identifier, title):
    return {"id": identifier, "source": "greenhouse", "board": "sample",
            "url": "https://example.org/" + identifier, "title": title, "raw": {}}


class ReviewSampleTests(unittest.TestCase):
    def test_reproducible_and_bounded(self):
        jobs = [posting("a", "Cloud Engineer"), posting("b", "Cloud Architect"),
                posting("c", "Accountant"), posting("d", "Finance Manager")]
        first = review.review_sample(jobs, rules.detect, per_category=1, negatives=1)
        second = review.review_sample(list(reversed(jobs)), rules.detect, per_category=1, negatives=1)
        self.assertEqual(first, second)
        self.assertEqual(len(first["positive_samples"]["cloud"]), 1)
        self.assertEqual(len(first["negative_samples"]), 1)
        self.assertIsNone(first["negative_samples"][0]["review_label"])

    def test_missing_category_is_empty(self):
        result = review.review_sample([posting("x", "Accountant")], rules.detect)
        self.assertEqual(result["positive_samples"]["modernization"], [])

    def test_invalid_sample_size(self):
        with self.assertRaises(ValueError):
            review.review_sample([], rules.detect, per_category=-1)


if __name__ == "__main__":
    unittest.main()
