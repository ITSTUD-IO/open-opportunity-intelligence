import importlib.util
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "signals"))
from opportunity import aggregate, markdown_report


def job(id, title, content, board="stripe"):
    return {"id": id, "source": "greenhouse", "board": board, "title": title,
            "url": "https://stripe.com/jobs/search?gh_jid=" + id,
            "raw": {"content": content}}


class OpportunityTests(unittest.TestCase):
    def test_stripe_representative_signals_and_explanations(self):
        jobs = [
            job("7982720", "Software Engineer, Secure Devices", "Platform engineering using AWS and cloud"),
            job("8203973", "Integration Engineer, Professional Services", "Cloud CI/CD architecture LLM"),
            job("8172672", "Senior Brand Designer, Link", "Cloud branding"),
            job("8404144", "Technical Recruiter, OpenRouter", "Architecture hiring"),
            job("8190059", "Account Executive, Product Sales (Data)", "Commercial sales"),
        ]
        profiles = aggregate(jobs)
        self.assertEqual(len(profiles), 1)
        p = profiles[0]
        self.assertEqual(p["company_key"], "greenhouse:stripe")
        self.assertEqual(p["identity_status"], "unverified_source_board")
        self.assertEqual(p["postings_with_signals"], 2)
        self.assertEqual(p["category_counts"], {
            "ai_engineering": 1, "architecture": 1, "cloud": 2,
            "devops": 1, "platform_engineering": 1})
        self.assertEqual(p["score"], 100)
        self.assertEqual(p["raw_score"], 102)
        self.assertEqual(sum(c["points"] for c in p["contributions"]), p["raw_score"])
        self.assertIn("https://stripe.com/jobs/search?gh_jid=8203973", markdown_report(profiles))

    def test_duplicate_posting_not_double_counted(self):
        jobs = [job("a", "Cloud Engineer", "AWS"), job("a", "Cloud Engineer", "AWS")]
        self.assertEqual(aggregate(jobs)[0]["postings_with_signals"], 1)
        self.assertEqual(aggregate(jobs)[0]["category_counts"]["cloud"], 1)

    def test_separate_boards_and_sort(self):
        jobs = [job("a", "Cloud Engineer", "", "beta"),
                job("b", "Platform Engineer", "Terraform", "alpha")]
        profiles = aggregate(jobs)
        self.assertEqual([p["board"] for p in profiles], ["alpha", "beta"])
        self.assertGreater(profiles[0]["score"], profiles[1]["score"])

    def test_empty_and_only_negative(self):
        self.assertEqual(aggregate([]), [])
        self.assertEqual(aggregate([job("a", "Account Executive", "Sales")]), [])
        self.assertIn("research priorities", markdown_report([]))

    def test_configurable_weights(self):
        weights = {k: 0 for k in ("architecture", "cloud", "platform_engineering",
                                   "devops", "ai_engineering", "modernization")}
        weights["cloud"] = 7
        self.assertEqual(aggregate([job("a", "Cloud Engineer", "")], weights=weights)[0]["score"], 7)
        with self.assertRaises(ValueError):
            aggregate([job("a", "Cloud Engineer", "")], weights={"cloud": 10})

    def test_stable_order_and_bounded_score(self):
        jobs = [job(str(i), "Cloud Engineer", "AWS") for i in range(20)]
        a = aggregate(jobs)
        self.assertEqual(a, aggregate(list(reversed(jobs))))
        self.assertLessEqual(a[0]["score"], 100)
        self.assertEqual(a[0]["score"], 30)


if __name__ == "__main__":
    unittest.main()
