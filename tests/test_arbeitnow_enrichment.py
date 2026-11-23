from packages.collectors.arbeitnow_enrichment import (
    country_evidence, canonical_url, deduplication_keys, audit_enrichment,
)


def test_country_evidence_is_conservative():
    assert country_evidence({"location": "Berlin"}) == (None, "unverified")
    assert country_evidence({"location": "Berlin, Germany"}) == ("DE", "location_country_suffix")
    assert country_evidence({"location": "Vienna, Austria"}) == ("AT", "location_country_suffix")
    assert country_evidence({"location": "Zürich, Schweiz"}) == ("CH", "location_country_suffix")
    assert country_evidence({"location": "Remote, EU"}) == (None, "unverified")
    assert country_evidence({"country": "DE", "location": "Vienna, Austria"}) == ("DE", "explicit_field")


def test_url_canonicalization_does_not_drop_distinguishing_query():
    assert canonical_url("https://EXAMPLE.com/job/1?ref=abc#apply") == "https://example.com/job/1?ref=abc"
    assert canonical_url("http://example.com/job/1") is None
    assert canonical_url("https://user:pass@example.com/job") is None


def test_deduplication_only_produces_candidate_keys():
    item = {"slug": "a", "url": "https://example.com/job/a",
            "company_name": "Example GmbH", "title": "Cloud Engineer", "location": "Berlin"}
    keys = deduplication_keys(item)
    assert len(keys) == 3
    report = audit_enrichment([item, dict(item, slug="b")])
    assert report["duplicate_candidate_key_collisions"] == 2
    assert report["deduplication_status"] == "candidates_only_no_automatic_merging"
