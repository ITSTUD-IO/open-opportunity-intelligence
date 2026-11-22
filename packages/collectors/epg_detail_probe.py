"""Bounded, read-only verification of employer-hosted EPG detail pages.

Samples ten records; does not change benchmark scores or crawl the entire board.
"""
import json
import re
from html import unescape

from packages.collectors.job_boards import epg, epg_job_page, fetch_text


def probe(jobs, fetcher=fetch_text, limit=10):
    missing = [j for j in jobs if not str(j["raw"].get("content") or "").strip()]
    # Include a known technical title when available; otherwise deterministic sample.
    technical = [j for j in missing if "devops" in j["title"].lower()]
    sample = (technical[:1] + [j for j in missing if j not in technical])[:limit]
    results = []
    for job in sample:
        row = {"id": job["source_job_id"], "title": job["title"], "url": job["url"]}
        try:
            detail = epg_job_page(job["url"], fetcher(job["url"]))
            body = detail["raw"]["content"]
            # Reject generic redirect shells and content that does not mention the role.
            title_words = [w.lower() for w in re.findall(r"[A-Za-zÄÖÜäöüß]{4,}", job["title"])
                           if w.lower() not in {"mwd", "eine", "einen"}]
            if not title_words or not any(w in body.lower() for w in title_words):
                raise ValueError("detail text does not match advertised role")
            if "DIE AUFGABEN" not in body and "DIE POSITION" not in body and "DIE ANFORDERUNGEN" not in body:
                raise ValueError("detail page lacks role-specific section markers")
            row.update({"status": "complete", "description_length": len(body),
                        "signals": sorted({s["category"] for s in __import__(
                            "packages.signals.rules", fromlist=["detect"]).detect(detail)})})
        except Exception as exc:
            row.update({"status": "incomplete", "reason": type(exc).__name__ + ": " + str(exc)[:140]})
        results.append(row)
    return {"sampled": len(results), "complete": sum(r["status"] == "complete" for r in results),
            "results": results}


def main():
    print("EPG_DETAIL_PROBE " + json.dumps(probe(epg("ehrhardt-partner-group")), ensure_ascii=False))


if __name__ == "__main__":
    main()
