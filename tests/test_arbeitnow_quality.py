import pytest
from packages.collectors.arbeitnow_quality import audit, country_of, valid_https


def posting(slug, **changes):
    row = {"slug": slug, "title": "Platform Engineer", "company_name": "Example GmbH",
           "location": "Berlin", "url": "https://example.org/job/" + slug,
           "description": "<p>" + "Kubernetes and Terraform. " * 15 + "</p>"}
    row.update(changes)
    return row


def test_quality_counts_and_country_remains_unknown_without_explicit_evidence():
    report = audit({"data": [posting("a"), posting("b", country="DE"),
                             posting("c", description="short", url="http://invalid.example")]})
    assert report["sample_size"] == 3
    assert report["quality"]["description_200_chars"] == pytest.approx(2 / 3, abs=.001)
    assert report["quality"]["https_url"] == pytest.approx(2 / 3, abs=.001)
    assert report["countries_explicit_only"] == {"DE": 1, "AT": 0, "CH": 0, "unknown": 2}


def test_country_must_be_explicit():
    assert country_of(posting("a", location="Berlin, Germany")) is None
    assert country_of(posting("b", country="Austria")) == "AT"
    assert country_of(posting("c", country_code="CH")) == "CH"


def test_url_validation_rejects_unsafe_forms():
    assert valid_https("https://example.org/jobs/1")
    assert not valid_https("http://example.org/jobs/1")
    assert not valid_https("https://user:pass@example.org/jobs/1")
    assert not valid_https("javascript:alert(1)")


def test_malformed_feed_and_limit_rejected():
    with pytest.raises(ValueError):
        audit({"wrong": []})
    with pytest.raises(ValueError):
        audit({"data": []})
    with pytest.raises(ValueError):
        audit({"data": [posting("a")]}, limit=101)
