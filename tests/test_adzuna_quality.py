import pytest

from packages.collectors.adzuna_quality import audit_market, search_url


def job(job_id="1", **changes):
    row = {"id": job_id, "title": "Cloud Engineer",
           "company": {"display_name": "Example GmbH"},
           "location": {"display_name": "Berlin"},
           "redirect_url": "https://www.adzuna.de/details/1",
           "description": "Azure and Kubernetes. " * 15}
    row.update(changes)
    return row


def test_dach_search_url_is_bounded_and_encodes_credentials():
    url = search_url("de", "my app", "a&b", results_per_page=20)
    assert "/de/search/1?" in url
    assert "app_id=my+app" in url
    assert "app_key=a%26b" in url
    with pytest.raises(ValueError):
        search_url("us", "a", "b")
    with pytest.raises(ValueError):
        search_url("at", "a", "b", results_per_page=100)


def test_audit_counts_quality_and_does_not_claim_verified_country():
    report = audit_market("at", {"count": 500, "results": [job(), job("2", description="short", company={})]})
    assert report["sampled"] == 2
    assert report["api_market"] == "AT"
    assert report["coverage"]["description_200_chars"] == .5
    assert report["coverage"]["employer"] == .5
    assert report["quality_gate"] == "review_required"
    assert "unverified" in report["country_evidence"]


def test_audit_rejects_malformed_response():
    with pytest.raises(ValueError):
        audit_market("de", {})
    with pytest.raises(ValueError):
        audit_market("us", {"results": []})
