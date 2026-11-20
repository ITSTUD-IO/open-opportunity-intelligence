import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "packages/signals/rules.py"
spec = importlib.util.spec_from_file_location("signal_rules", path)
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


def job(title, description="", job_id="a"):
    return {"id": job_id, "source": "greenhouse", "board": "example",
            "title": title, "url": "https://example.org/jobs/" + job_id,
            "raw": {"description": description}}


class SignalRulesTests(unittest.TestCase):
    def test_platform_and_devops(self):
        signals = rules.detect(job("Platform Engineering Lead", "Terraform and GitOps"))
        self.assertEqual({s["category"] for s in signals}, {"platform_engineering", "devops"})
        self.assertTrue(all(s["evidence_id"] == "a" for s in signals))
        self.assertTrue(any(s["confidence"] == "medium" for s in signals))

    def test_cloud_and_modernization(self):
        signals = rules.detect(job("Cloud Migration Architect", "Legacy migration to AWS"))
        self.assertEqual({s["category"] for s in signals}, {"cloud", "modernization"})

    def test_ai_not_substring(self):
        self.assertEqual(rules.detect(job("Maintain retail systems")), [])
        self.assertEqual([s["category"] for s in rules.detect(job("LLM Engineer"))], ["ai_engineering"])

    def test_unrelated_raw_metadata_ignored(self):
        self.assertEqual(rules.detect({"**": "ignored", **job("Accountant"), "raw": {"tags": "AWS"}}), [])

    def test_html_description_and_entities(self):
        signals = rules.detect(job("Engineer", "<p>Build an internal developer platform &amp; GitOps</p>"))
        self.assertEqual({s["category"] for s in signals}, {"platform_engineering", "devops"})

    def test_html_attributes_and_scripts_are_not_evidence(self):
        signals = rules.detect(job("Engineer", '<a href="/cloud">General role</a><script>Terraform</script>'))
        self.assertEqual(signals, [])

    def test_group_deduplicates_postings_per_category(self):
        summary = rules.summarize([job("Cloud Engineer", "AWS and Azure"), job("DevOps Engineer", job_id="b")])
        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["categories"]["cloud"], 1)
        self.assertEqual(summary[0]["postings_with_signals"], 2)
        self.assertEqual(summary[0]["company_key_type"], "source_board_unresolved")


if __name__ == "__main__":
    unittest.main()
