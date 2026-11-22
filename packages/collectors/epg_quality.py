"""Read-only quality audit of public EPG BITE postings."""
import json
from collections import Counter
from urllib.parse import urlparse

from packages.collectors.job_boards import epg
from packages.signals.rules import detect


def audit(jobs):
    ids = [job["source_job_id"] for job in jobs]
    missing_description = [j["source_job_id"] for j in jobs if not str(j["raw"].get("content") or "").strip()]
    missing_location = [j["source_job_id"] for j in jobs if not str(j.get("location") or "").strip()]
    api_urls = [(j["source_job_id"], (j["raw"].get("url") or {})) for j in jobs]
    mismatches = []
    for job_id, api_url in api_urls:
        href = api_url.get("href") if isinstance(api_url, dict) else api_url
        if href and href != next(j["url"] for j in jobs if j["source_job_id"] == job_id):
            mismatches.append({"id": job_id, "api_url": href})
    categories = Counter()
    signal_jobs = []
    for j in jobs:
        signals = detect(j)
        if signals:
            signal_jobs.append({"id": j["source_job_id"], "title": j["title"],
                                "categories": [s["category"] for s in signals],
                                "description_length": len(str(j["raw"].get("content") or ""))})
            categories.update(s["category"] for s in signals)
    return {"postings": len(jobs), "unique_source_ids": len(set(ids)),
            "missing_descriptions": len(missing_description),
            "missing_locations": len(missing_location),
            "api_url_mismatches": len(mismatches),
            "api_url_samples": mismatches[:5],
            "signal_postings": len(signal_jobs),
            "category_counts": dict(categories),
            "signal_samples": signal_jobs[:12],
            "missing_description_samples": missing_description[:10]}


def main():
    print("EPG_QUALITY_AUDIT " + json.dumps(audit(epg("ehrhardt-partner-group")), ensure_ascii=False))


if __name__ == "__main__":
    main()
