"""Inspect publicly served BITE frontend assets for job-list API integration.

Diagnostic only: does not make speculative requests to backend endpoints.
"""
import json
import re
from urllib.parse import urlparse
from packages.collectors.job_boards import fetch_text

ASSETS = (
    "https://static.b-ite.com/jobs-api/004/api-v4.js",
    "https://cs-assets.b-ite.com/epg/jobs-api/v2/epg.min.js",
    "https://static.b-ite.com/jobs-api/loader-v1/api-loader-v1.min.js",
)
KEYWORDS = ("postings/search", "jobposting", "api/v1", "listing", "fetch(", "XMLHttpRequest", "axios", "https://")


def inspect_asset(url, fetcher=fetch_text):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ("static.b-ite.com", "cs-assets.b-ite.com"):
        raise ValueError("Unexpected asset host")
    script = fetcher(url)
    matches = []
    lower = script.lower()
    for keyword in KEYWORDS:
        offset = 0
        while len(matches) < 45:
            pos = lower.find(keyword.lower(), offset)
            if pos < 0:
                break
            snippet = " ".join(script[max(0, pos - 130):pos + 180].split())
            if snippet not in matches:
                matches.append(snippet[:310])
            offset = pos + len(keyword)
    return {"asset": url, "bytes": len(script.encode("utf-8")), "snippets": matches, "prefix": script[:180]}


def main():
    for url in ASSETS:
        try:
            result = inspect_asset(url)
        except Exception as exc:
            result = {"asset": url, "error": f"{type(exc).__name__}: {exc}"}
        print("EPG_BITE_ASSET " + json.dumps(result, ensure_ascii=False)[:16000])


if __name__ == "__main__":
    main()
