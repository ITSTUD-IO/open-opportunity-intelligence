import importlib.util
import unittest
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1] / "packages" / "signals"
sys.path.insert(0, str(root))
import rules
import compare_versions


def posting(job_id, title, description):
    return {"id": job_id, "source": "greenhouse", "board": "stripe",
            "url": "https://stripe.com/jobs/search?gh_jid=" + job_id,
            "title": title, "raw": {"content": description}}


class ComparisonTests(unittest.TestCase):
    def test_guard_removes_only_ambiguous_signals(self):
        jobs = [
            posting("8172672", "Senior Brand Designer, Link", "Cloud branding"),
            posting("8404144", "Technical Recruiter, OpenRouter (Fixed Term)", "Architecture hiring"),
            posting("7982720", "Software Engineer, Secure Devices", "Platform engineering with AWS"),
            posting("8203973", "Integration Engineer, Professional Services", "Cloud CI/CD architecture LLM"),
        ]
        result = compare_versions.compare(jobs)
        self.assertEqual({(x["id"], x["category"]) for x in result["removed_signals"]},
                         {("8172672", "cloud"), ("8404144", "architecture")})
        self.assertEqual(result["added_signals"], [])
        self.assertEqual(result["postings_with_signals_v1"], 4)
        self.assertEqual(result["postings_with_signals_v2"], 2)
        self.assertEqual(rules.RULE_VERSION, "2")

    def test_empty_snapshot(self):
        result = compare_versions.compare([])
        self.assertEqual(result["postings_analyzed"], 0)
        self.assertEqual(result["removed_signals"], [])


if __name__ == "__main__":
    unittest.main()
