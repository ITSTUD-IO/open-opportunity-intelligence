"""Adzuna DACH evaluation adapter; no persistence or production ingestion.

Live requests require explicit evaluation approval and developer credentials.
Country attribution is the requested API market, not verified job location.
"""
import argparse
import json
import os
import urllib.parse

from packages.collectors.job_boards import fetch_json
from packages.collectors.arbeitnow_quality import valid_https
from packages.signals.rules import visible_text, detect

MARKETS = ("de", "at", "ch")
API_ROOT = "https://api.adzuna.com/v1/api/jobs"


def search_url(market, app_id, app_key, *, page=1, results_per_page=20, what="software engineer"):
    if market not in MARKETS:
        raise ValueError("Only DE, AT, CH markets are supported")
    if not 1 <= page <= 2 or not 1 <= results_per_page <= 50:
        raise ValueError("Evaluation limited to two pages and 50 results per page")
    if not app_id or not app_key:
        raise ValueError("Adzuna API credentials required")
    query = urllib.parse.urlencode({
        "app_id": app_id, "app_key": app_key, "results_per_page": results_per_page,
        "what": what, "content-type": "application/json",
    })
    return f"{API_ROOT}/{market}/search/{page}?{query}"


def audit_market(market, payload):
    if market not in MARKETS:
        raise ValueError("Unsupported Adzuna market")
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise ValueError("Unexpected Adzuna results schema")
    rows = payload["results"]
    n = len(rows)
    counts = {"description_200_chars": 0, "employer": 0, "location": 0,
              "https_url": 0, "id": 0, "signal_postings": 0}
    ids = []
    lengths = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        description = visible_text(item.get("description") or "") if isinstance(item.get("description"), str) else ""
        lengths.append(len(description.strip()))
        counts["description_200_chars"] += len(description.strip()) >= 200
        employer = item.get("company")
        counts["employer"] += isinstance(employer, dict) and bool(str(employer.get("display_name") or "").strip())
        location = item.get("location")
        counts["location"] += isinstance(location, dict) and bool(str(location.get("display_name") or "").strip())
        url = item.get("redirect_url")
        counts["https_url"] += valid_https(url)
        job_id = str(item.get("id") or "").strip()
        counts["id"] += bool(job_id)
        if job_id:
            ids.append(job_id)
        if valid_https(url):
            normalized = {"id": job_id, "source": "adzuna", "board": market,
                          "title": str(item.get("title") or ""), "url": url,
                          "raw": {"content": description}}
            counts["signal_postings"] += bool(detect(normalized))
    coverage = {k: round(v / n, 3) if n else 0 for k, v in counts.items()}
    return {
        "source": "adzuna", "api_market": market.upper(),
        "country_evidence": "API search market only; individual posting country unverified",
        "sampled": n, "reported_total": payload.get("count"),
        "coverage": coverage, "unique_nonempty_ids": len(set(ids)),
        "description_length_min": min(lengths) if lengths else None,
        "description_length_max": max(lengths) if lengths else None,
        "description_quality_warning": "API descriptions may be snippets, not full postings",
        "quality_gate": "review_required" if not n or coverage["description_200_chars"] < .8
                        or coverage["employer"] < .9 or coverage["location"] < .9
                        or coverage["https_url"] < .95 or len(set(ids)) != n else "technical_pass_only",
        "commercial_reuse_permission": "unverified",
    }


def main():
    parser = argparse.ArgumentParser(description="Bounded Adzuna API evaluation; requires approval")
    parser.add_argument("--market", choices=MARKETS, required=True)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if os.getenv("ADZUNA_EVALUATION_APPROVED") != "1":
        parser.error("ADZUNA_EVALUATION_APPROVED=1 required after terms review")
    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        parser.error("ADZUNA_APP_ID and ADZUNA_APP_KEY are required")
    # Never print the request URL: it contains credentials.
    result = audit_market(args.market, fetch_json(search_url(args.market, app_id, app_key,
                                                             results_per_page=args.limit)))
    print("ADZUNA_QUALITY_AUDIT " + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
