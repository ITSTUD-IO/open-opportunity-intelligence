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

    def test_greenhouse_content_field(self):
        posting = job("Engineer")
        posting["raw"] = {"content": "<p>We use Kubernetes and Terraform</p>"}
        self.assertEqual({s["category"] for s in rules.detect(posting)}, {"cloud", "devops"})

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


    def test_stripe_review_false_positive_design_cloud(self):
        # Synthetic description reproduces the reviewed ambiguous match.
        self.assertEqual(rules.detect(job("Senior Brand Designer, Link",
                                         "Collaborate with the Cloud brand team")), [])

    def test_stripe_review_false_positive_recruiter_architecture(self):
        self.assertEqual(rules.detect(job("Technical Recruiter, OpenRouter (Fixed Term)",
                                         "Recruit across Engineering and Architecture")), [])

    def test_context_guard_preserves_strong_technical_evidence(self):
        self.assertEqual({s["category"] for s in rules.detect(job(
            "Senior Brand Designer", "Design brand assets for an AWS campaign"))}, {"cloud"})
        self.assertEqual({s["category"] for s in rules.detect(job(
            "Technical Recruiter", "Hire enterprise architects for architecture teams"))},
            {"architecture"})

    def test_stripe_review_positive_category_fixtures(self):
        # Representative synthetic excerpts, not archived verbatim job postings.
        cases = [
            ("Software Engineer, Secure Devices", "Platform engineering using AWS and cloud", {"platform_engineering", "cloud"}),
            ("Staff Backend Engineer - CI Services", "Improve developer experience, DevOps CI/CD and architecture", {"platform_engineering", "devops", "architecture"}),
            ("Integration Engineer, Professional Services", "Cloud integration, CI/CD, architecture, and LLM", {"cloud", "devops", "architecture", "ai_engineering"}),
            ("Implementation Consultant, Professional Services", "Cloud architecture and LLM implementation", {"cloud", "architecture", "ai_engineering"}),
            ("Staff Engineer, Support Experiences", "Architecture for LLM and generative AI", {"architecture", "ai_engineering"}),
            ("Staff Product Manager, Sail Core", "Developer experience and architecture", {"platform_engineering", "architecture"}),
            ("Full Stack Engineer, Developer & End User Experience Platform", "Developer experience", {"platform_engineering"}),
            ("Security Engineer, Bridge", "Secure CI/CD pipelines", {"devops"}),
            ("Strategy & Transformation Advisor (Enterprise Commerce Architecture)", "Cloud architecture", {"architecture", "cloud"}),
        ]
        for title, description, expected in cases:
            with self.subTest(title=title):
                self.assertEqual({s["category"] for s in rules.detect(job(title, description))}, expected)

    def test_stripe_review_negative_category_fixtures(self):
        # Synthetic no-signal descriptions; these do not prove real postings lack signals.
        titles = [
            "Account Executive, Product Sales (Data)",
            "Account Executive, Startups - Grower (Italian Fluency)",
            "Third Party Risk Analyst",
            "Deal Pricing Strategist, APAC",
            "Partner Development Manager- Alliances & Channels",
        ]
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(rules.detect(job(title, "Commercial and stakeholder responsibilities")), [])


if __name__ == "__main__":
    unittest.main()
