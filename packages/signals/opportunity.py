"""Explainable company-level research prioritization from technical hiring signals.

Scores indicate *research priority*, never probability of purchasing consulting.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from .rules import detect
except ImportError:
    from rules import detect

SCORING_VERSION = "1"
WEIGHTS = {
    "architecture": 18,
    "cloud": 15,
    "platform_engineering": 20,
    "devops": 15,
    "ai_engineering": 17,
    "modernization": 20,
}
BREADTH_BONUS_PER_EXTRA_CATEGORY = 5
BREADTH_BONUS_CAP = 15
VOLUME_BONUS_PER_EXTRA_POSTING = 2
VOLUME_BONUS_CAP = 15


def aggregate(jobs: list[dict], *, weights: dict[str, int] | None = None) -> list[dict]:
    """Group by source/board; de-duplicate repeated posting IDs.

    No company identity resolution or buying intent inference is attempted.
    """
    weights = dict(WEIGHTS if weights is None else weights)
    if set(weights) != set(WEIGHTS) or any(type(v) is not int or not 0 <= v <= 100 for v in weights.values()):
        raise ValueError("weights must specify each known category with integer values 0..100")
    groups = defaultdict(dict)
    for job in jobs:
        if not all(job.get(k) for k in ("source", "board", "id", "url")):
            raise ValueError("job requires source, board, id, and url")
        key = (str(job["source"]), str(job["board"]))
        groups[key][str(job["id"])] = job  # same ID counted once

    output = []
    for (source, board), unique in sorted(groups.items()):
        by_category = defaultdict(list)
        for job_id, job in sorted(unique.items()):
            for signal in detect(job):
                by_category[signal["category"]].append({
                    "posting_id": job_id,
                    "title": job.get("title") or "",
                    "url": job["url"],
                    "matched_terms": signal["matched_terms"],
                    "confidence": signal["confidence"],
                })
        if not by_category:
            continue
        categories = sorted(by_category)
        matched_ids = {x["posting_id"] for items in by_category.values() for x in items}
        contributions = [{"reason": "category:" + category, "points": weights[category],
                          "posting_count": len(by_category[category])} for category in categories]
        breadth = min(BREADTH_BONUS_CAP, max(0, len(categories) - 1) * BREADTH_BONUS_PER_EXTRA_CATEGORY)
        volume = min(VOLUME_BONUS_CAP, max(0, len(matched_ids) - 1) * VOLUME_BONUS_PER_EXTRA_POSTING)
        contributions.extend([
            {"reason": "category_breadth", "points": breadth},
            {"reason": "distinct_posting_volume", "points": volume},
        ])
        raw_score = sum(x["points"] for x in contributions)
        output.append({
            "company_key": source + ":" + board,
            "identity_status": "unverified_source_board",
            "source": source, "board": board,
            "score": min(100, raw_score), "raw_score": raw_score,
            "scoring_version": SCORING_VERSION,
            "postings_analyzed": len(unique),
            "postings_with_signals": len(matched_ids),
            "category_counts": {category: len(by_category[category]) for category in categories},
            "contributions": contributions,
            "evidence": {category: by_category[category] for category in categories},
            "interpretation": "Research priority only; no verified consulting demand or purchase probability.",
        })
    return sorted(output, key=lambda x: (-x["score"], x["company_key"]))


def markdown_report(profiles: list[dict]) -> str:
    lines = ["# Opportunity Intelligence — research priorities", "",
             "Scores are deterministic research priorities (0–100), **not** probabilities of consulting demand.",
             "Company keys are unverified source/board identifiers.", "",
             "| Company key | Score | Postings with signals | Categories |",
             "|---|---:|---:|---|"]
    for p in profiles:
        lines.append("| " + " | ".join([p["company_key"], str(p["score"]),
                     str(p["postings_with_signals"]), ", ".join(p["category_counts"])]) + " |")
    for p in profiles:
        lines.extend(["", "## " + p["company_key"], "",
                      "**Score:** " + str(p["score"]) + "/100; **identity:** " + p["identity_status"], "",
                      "**Contributions:** " + "; ".join(c["reason"] + " +" + str(c["points"]) for c in p["contributions"]), ""])
        for category, evidence in p["evidence"].items():
            lines.append("### " + category)
            for e in evidence:
                terms = ", ".join(m["term"] for m in e["matched_terms"])
                lines.append("- [" + e["title"].replace("[", "").replace("]", "") + "](" + e["url"] + ") — " + terms)
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only explainable hiring signal research prioritization")
    parser.add_argument("--board", help="Optional Greenhouse board filter, e.g. stripe")
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.limit <= 100000:
        parser.error("--limit must be between 1 and 100000")
    import os
    import psycopg
    if not os.environ.get("DATABASE_URL"):
        parser.error("DATABASE_URL is required")
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id, source, board, title, url, raw
                           FROM job_postings WHERE active=TRUE
                           AND (%s IS NULL OR board=%s)
                           ORDER BY board, id LIMIT %s""",
                        (args.board, args.board, args.limit))
            jobs = [dict(zip(("id", "source", "board", "title", "url", "raw"), row))
                    for row in cur.fetchall()]
    profiles = aggregate(jobs)
    result = {"generated_at": datetime.now(timezone.utc).isoformat(),
              "scoring_version": SCORING_VERSION, "postings_analyzed": len(jobs),
              "profiles": profiles}
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_out.write_text(markdown_report(profiles), encoding="utf-8")
    print(json.dumps({"postings_analyzed": len(jobs), "profiles": len(profiles),
                      "scores": {p["company_key"]: p["score"] for p in profiles}}, sort_keys=True))


if __name__ == "__main__":
    main()
