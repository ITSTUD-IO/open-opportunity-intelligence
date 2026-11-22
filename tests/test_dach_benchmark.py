from packages.dach_benchmark import benchmark
from packages.collectors.job_boards import ashby


def test_ashby_normalization():
    payload = {"jobs": [{"id": "123", "title": "Platform Engineer", "jobUrl": "https://jobs.ashbyhq.com/example/123", "location": "Berlin", "descriptionHtml": "Kubernetes"}]}
    jobs = ashby("example", payload)
    assert len(jobs) == 1
    assert jobs[0]["raw"]["content"] == "Kubernetes"
    assert jobs[0]["source"] == "ashby"


def test_dach_benchmark_does_not_invent_scores_for_missing_sources():
    result = benchmark(targets=[
        {"company": "example", "country": "DE", "source": "greenhouse", "board": "example", "status": "candidate"},
        {"company": "unknown", "country": "DE", "source": None, "board": None, "status": "discovery_required"},
    ], collector=lambda source, board: [{
        "id": "1", "source": source, "board": board, "title": "Cloud Engineer",
        "url": "https://example.com/1", "raw": {"content": "AWS"}
    }])
    assert result["results"][0]["profile"]["score"] == 15
    assert result["results"][1]["result"] == "not_collected"
    assert "profile" not in result["results"][1]
