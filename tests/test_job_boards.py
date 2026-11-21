import importlib.util
import unittest
from unittest.mock import patch
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "packages" / "collectors" / "job_boards.py"
spec = importlib.util.spec_from_file_location("job_boards", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class JobBoardTests(unittest.TestCase):
    def test_greenhouse(self):
        payload = {"jobs": [{"id": 123, "title": "Platform Engineer", "absolute_url": "https://example.org/job/123", "location": {"name": "Berlin"}}]}
        first = module.greenhouse("sample", payload)[0]
        second = module.greenhouse("sample", payload)[0]
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(first["location"], "Berlin")
        self.assertEqual(first["source"], "greenhouse")

    def test_greenhouse_requests_descriptions(self):
        payload = {"jobs": [{"id": 123, "title": "Engineer", "absolute_url": "https://example.org/123",
                            "content": "<p>Terraform and AWS</p>"}]}
        with patch.object(module, "fetch_json", return_value=payload) as fetch:
            jobs = module.collect("greenhouse", "sample")
        self.assertEqual(jobs[0]["raw"]["content"], "<p>Terraform and AWS</p>")
        self.assertEqual(fetch.call_args.args[0],
                         "https://boards-api.greenhouse.io/v1/boards/sample/jobs?content=true")

    def test_lever(self):
        payload = [{"id": "abc", "text": "DevOps Engineer", "hostedUrl": "https://example.org/abc", "categories": {"location": "Remote"}}]
        job = module.lever("sample", payload)[0]
        self.assertEqual(job["title"], "DevOps Engineer")
        self.assertEqual(job["location"], "Remote")

    def test_empty(self):
        self.assertEqual(module.greenhouse("x", {"jobs": []}), [])
        self.assertEqual(module.lever("x", []), [])


if __name__ == "__main__":
    unittest.main()
