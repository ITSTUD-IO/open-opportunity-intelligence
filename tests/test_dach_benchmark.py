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


def test_personio_xml_parses_public_tenant_feed():
    from packages.collectors.job_boards import personio_xml
    xml = """<workzag-jobs><position><id>123</id><name>Cloud Architect</name>
    <office>Munich</office><jobDescriptions><jobDescription><name>Tasks</name>
    <value>Azure architecture</value></jobDescription></jobDescriptions>
    </position></workzag-jobs>"""
    jobs = personio_xml("example", xml)
    assert len(jobs) == 1
    assert jobs[0]["raw"]["content"].find("Azure") >= 0
    assert jobs[0]["source"] == "personio_xml"


def test_epg_job_link_extraction_rejects_external_hosts():
    from packages.collectors.job_boards import epg_job_links
    html = """<a href="https://jobs-ads.epg.com/jobposting/abc">A</a>
    <a href="https://evil.example/jobposting/abc">B</a>
    <a href="https://jobs-ads.epg.com.evil.example/jobposting/abc">C</a>"""
    assert epg_job_links(html) == ["https://jobs-ads.epg.com/jobposting/abc"]


def test_epg_collector_extracts_employer_postings():
    from packages.collectors.job_boards import epg
    url = "https://jobs-ads.epg.com/jobposting/abc123"
    pages = {
        "https://www.epg-jobs.com/stellenangebote/berufserfahrene": f'<a href="{url}">Job</a>',
        url: "<html><head><title>Software Architect | EPG</title></head><body>" +
             "<main>Cloud architecture and software development. " * 8 + "</main></body></html>",
    }
    jobs = epg("ehrhardt-partner-group", fetcher=lambda u: pages[u])
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Software Architect"
    assert jobs[0]["source"] == "epg"
    assert "Cloud architecture" in jobs[0]["raw"]["content"]


def test_epg_collector_rejects_empty_static_listing():
    import pytest
    from packages.collectors.job_boards import epg
    with pytest.raises(ValueError, match="no job links"):
        epg("ehrhardt-partner-group", fetcher=lambda u: "<div id='app'></div>")
