"""Public job-board adapters. Explicit company board IDs only; no discovery crawling."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime, timezone
from pathlib import Path


def fetch_json(url: str, *, timeout: int = 15) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenOpportunityIntelligence/0.1 (research prototype)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def normalize(source: str, board: str, job_id: str, title: str, url: str, location: str, raw: dict) -> dict:
    key = hashlib.sha256(f"{source}:{board}:{job_id}".encode()).hexdigest()
    return {"id": key, "source": source, "board": board, "source_job_id": str(job_id),
            "title": title, "url": url, "location": location,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "raw": raw}


def greenhouse(board: str, payload: dict) -> list[dict]:
    jobs = []
    for job in payload.get("jobs", []):
        jobs.append(normalize("greenhouse", board, str(job["id"]), job.get("title", ""),
                              job.get("absolute_url", ""), (job.get("location") or {}).get("name", ""), job))
    return jobs


def lever(board: str, payload: list[dict]) -> list[dict]:
    jobs = []
    for job in payload:
        categories = job.get("categories") or {}
        jobs.append(normalize("lever", board, str(job["id"]), job.get("text", ""),
                              job.get("hostedUrl", ""), categories.get("location", ""), job))
    return jobs


def ashby(board: str, payload: dict) -> list[dict]:
    """Normalize public Ashby job board postings; reject incomplete entries."""
    jobs = []
    for job in payload.get("jobs", []):
        job_id = job.get("id") or job.get("jobId")
        url = job.get("jobUrl") or job.get("applyUrl")
        if not job_id or not url:
            continue
        description = job.get("descriptionHtml") or job.get("descriptionPlain") or ""
        raw = dict(job, content=description)
        location = job.get("location") or ""
        if isinstance(location, dict):
            location = location.get("name", "")
        jobs.append(normalize("ashby", board, str(job_id), job.get("title", ""),
                              url, str(location), raw))
    return jobs



def personio_xml(board: str, xml_text: str) -> list[dict]:
    """Normalize a public Personio tenant XML feed (not necessarily Personio SE)."""
    root = ET.fromstring(xml_text)
    if root.tag != "workzag-jobs":
        raise ValueError("Unexpected Personio XML root")
    jobs = []
    for position in root.findall("position"):
        job_id = (position.findtext("id") or "").strip()
        title = (position.findtext("name") or "").strip()
        if not job_id or not title:
            continue
        sections = []
        for section in position.findall(".//jobDescriptions/*"):
            sections.extend((node.text or "") for node in section.iter() if node.text)
        description = " ".join(sections)
        raw = {"content": description, "department": position.findtext("department") or "",
               "createdAt": position.findtext("createdAt") or ""}
        url = f"https://{board}.jobs.personio.de/job/{urllib.parse.quote(job_id, safe='')}"
        jobs.append(normalize("personio_xml", board, job_id, title, url,
                              position.findtext("office") or "", raw))
    return jobs


class _EPGJobLinks(HTMLParser):
    """Extract only employer-hosted jobposting URLs from an employer index."""
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        href = dict(attrs).get("href", "")
        parsed = urllib.parse.urlparse(urllib.parse.urljoin("https://www.epg-jobs.com/", href))
        if parsed.scheme == "https" and parsed.netloc == "jobs-ads.epg.com" and parsed.path.startswith("/jobposting/"):
            self.urls.add(urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", "")))


def epg_job_links(index_html: str) -> list[str]:
    parser = _EPGJobLinks()
    parser.feed(index_html)
    return sorted(parser.urls)


def fetch_text(url: str, *, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenOpportunityIntelligence/0.1 (research prototype)"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8")



class _EPGJobPage(HTMLParser):
    """Read page title and visible job text without external HTML dependencies."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts = []
        self.parts = []
        self.in_title = False
        self.hidden = 0
        self.meta_title = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag in ("script", "style", "noscript"):
            self.hidden += 1
        if tag == "meta" and attrs.get("property") == "og:title":
            self.meta_title = attrs.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag in ("script", "style", "noscript"):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)
        if not self.hidden:
            self.parts.append(data)


def epg_job_page(url: str, html: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "jobs-ads.epg.com" or not parsed.path.startswith("/jobposting/"):
        raise ValueError("Not an EPG employer-hosted job URL")
    job_id = parsed.path.removeprefix("/jobposting/").strip("/")
    if not job_id or "/" in job_id or not job_id.isalnum():
        raise ValueError("Invalid EPG job identifier")
    page = _EPGJobPage()
    page.feed(html)
    title = (page.meta_title or " ".join(page.title_parts)).split("|")[0].strip()
    description = " ".join(" ".join(page.parts).split())
    if not title or len(description) < 100:
        raise ValueError("Incomplete EPG job page; refusing misleading score")
    return normalize("epg", "ehrhardt-partner-group", job_id, title, url, "",
                     {"content": description})


EPG_BITE_API = "https://jobs.b-ite.com/adsapi/jobads"
EPG_BITE_CONFIG = "https://cs-assets.b-ite.com/epg/jobs-api/v2/epg.min.js"
EPG_LISTING_PAGE = "https://www.epg-jobs.com/stellenangebote/berufserfahrene"


def epg_bite_client_key(config_js: str) -> str:
    """Read the public listing key from the employer's published JS configuration."""
    import re
    match = re.search(r'\\bkey\\s*:\\s*["\\']([a-f0-9]{32})["\\']', config_js)
    if not match:
        raise ValueError("EPG BITE public client key not found in published configuration")
    return match.group(1)


def epg_bite_jobs(payload: dict, board: str = "ehrhardt-partner-group") -> list[dict]:
    """Normalize BITE ads; reject malformed or empty API responses."""
    if not isinstance(payload, dict) or not isinstance(payload.get("advertisements"), list):
        raise ValueError("EPG BITE response has no advertisements list")
    jobs = []
    for ad in payload["advertisements"]:
        if not isinstance(ad, dict):
            continue
        job_id = str(ad.get("hash") or "")
        title = ad.get("title") or ""
        if not job_id.isalnum() or not title:
            continue
        url = f"https://jobs-ads.epg.com/de/jobposting/{job_id}"
        raw = dict(ad, content=ad.get("description") or "")
        jobs.append(normalize("epg", board, job_id, title, url,
                              str(ad.get("job_site") or ""), raw))
    if not jobs:
        raise ValueError("EPG BITE returned no valid job advertisements")
    return jobs


def epg(board: str, *, fetcher=fetch_text, json_fetcher=None) -> list[dict]:
    """Collect public EPG listings from the BITE job ads API."""
    if board != "ehrhardt-partner-group":
        raise ValueError("Unknown EPG board")
    key = epg_bite_client_key(fetcher(EPG_BITE_CONFIG))
    params = urllib.parse.urlencode({"apikey": key})
    url = f"{EPG_BITE_API}?{params}"
    if json_fetcher is None:
        def json_fetcher(request_url):
            req = urllib.request.Request(request_url, headers={
                "User-Agent": "OpenOpportunityIntelligence/0.1 (research prototype)",
                "Accept": "application/json",
                "X-BITE-Origin": EPG_LISTING_PAGE,
            })
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.load(response)
    return epg_bite_jobs(json_fetcher(url), board)


def collect(source: str, board: str) -> list[dict]:
    safe_board = urllib.parse.quote(board, safe="")
    if source == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{safe_board}/jobs?content=true"
        return greenhouse(board, fetch_json(url))
    if source == "lever":
        url = f"https://api.lever.co/v0/postings/{safe_board}?mode=json"
        return lever(board, fetch_json(url))
    if source == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{safe_board}"
        return ashby(board, fetch_json(url))
    if source == "epg":
        return epg(board)
    if source == "personio_xml":
        return personio_xml(board, fetch_text(f"https://{safe_board}.jobs.personio.de/xml?language=en"))
    raise ValueError(f"Unsupported source: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public job postings for explicitly configured boards")
    parser.add_argument("--source", choices=("greenhouse", "lever", "ashby", "personio_xml", "epg"), required=True)
    parser.add_argument("--board", required=True, help="Company's public board identifier")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.board.replace("-", "").replace("_", "").isalnum():
        parser.error("Board must contain only letters, numbers, dashes or underscores")
    jobs = collect(args.source, args.board)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement makes repeated runs safe for this single-board snapshot.
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=False) + "\n")
    temp.replace(args.output)
    print(f"Saved {len(jobs)} postings from {args.source}/{args.board} to {args.output}")


if __name__ == "__main__":
    main()
