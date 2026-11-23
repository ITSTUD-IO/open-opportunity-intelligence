"""Bounded read-only Arbeitnow public feed quality audit.

This is not production ingestion: no pagination, persistence, or scoring.
Commercial reuse permission must be checked separately.
"""
import argparse
import json
from urllib.parse import urlparse

from packages.collectors.job_boards import fetch_json
from packages.signals.rules import detect, visible_text

FEED_URL = "https://www.arbeitnow.com/api/job-board-api"
COUNTRIES = {"DE", "AT", "CH"}
COUNTRY_NAMES = {"germany": "DE", "deutschland": "DE",
                 "austria": "AT", "österreich": "AT",
                 "switzerland": "CH", "schweiz": "CH", "suisse": "CH"}


def country_of(job):
    value = job.get("country") or job.get("country_code") or ""
    if isinstance(value, dict):
        value = value.get("code") or value.get("name") or ""
    if not isinstance(value, str):
        return None
    code = value.strip().upper()
    return code if code in COUNTRIES else COUNTRY_NAMES.get(value.strip().lower())


def valid_https(url):
    if not isinstance(url, str):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def audit(payload, limit=30):
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("Unexpected Arbeitnow feed schema")
    if not 1 <= limit <= 100:
        raise ValueError("Sample limit must be between 1 and 100")
    entries = payload["data"][:limit]
    if not entries:
        raise ValueError("Arbeitnow feed returned no postings")
    rows = []
    slugs = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        description = visible_text(item.get("description") or "") if isinstance(item.get("description"), str) else ""
        title = item.get("title") if isinstance(item.get("title"), str) else ""
        company = item.get("company_name") if isinstance(item.get("company_name"), str) else ""
        location = item.get("location") if isinstance(item.get("location"), str) else ""
        slug = item.get("slug") if isinstance(item.get("slug"), str) else ""
        url = item.get("url")
        slugs.append(slug)
        job = {"id": slug, "source": "arbeitnow", "board": "unresolved",
               "title": title, "url": url or "", "raw": {"content": description}}
        rows.append({
            "id_present": bool(slug.strip()),
            "description_present": len(description.strip()) >= 200,
            "description_length": len(description.strip()),
            "company_present": bool(company.strip()),
            "location_present": bool(location.strip()),
            "https_url": valid_https(url),
            "country": country_of(item) or "unknown",
            "signal_categories": sorted({s["category"] for s in detect(job)}) if valid_https(url) else [],
            "title": title[:100],
        })
    if not rows:
        raise ValueError("No usable Arbeitnow records")
    n = len(rows)
    def coverage(key):
        return round(sum(bool(row[key]) for row in rows) / n, 3)
    return {
        "source": "arbeitnow", "sample_size": n, "sample_limit": limit,
        "sample_scope": "first page only; not representative of DACH market",
        "quality": {"description_200_chars": coverage("description_present"),
                    "company": coverage("company_present"),
                    "location": coverage("location_present"),
                    "https_url": coverage("https_url"),
                    "stable_id": coverage("id_present"),
                    "unique_slugs": len(set(slugs)) == len(slugs) == n},
        "countries_explicit_only": {c: sum(r["country"] == c for r in rows)
                                    for c in ("DE", "AT", "CH", "unknown")},
        "signal_postings": sum(bool(r["signal_categories"]) for r in rows),
        "examples": [{"title": r["title"], "country": r["country"],
                      "description_length": r["description_length"],
                      "signals": r["signal_categories"]} for r in rows[:10]],
        "gate": "technical_quality_only; production use requires rights review",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be 1..100")
    print("ARBEITNOW_QUALITY_AUDIT " + json.dumps(audit(fetch_json(FEED_URL), args.limit), ensure_ascii=False))


if __name__ == "__main__":
    main()
