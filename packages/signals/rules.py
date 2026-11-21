"""Deterministic, evidence-linked engineering hiring signals (not buying intent)."""
from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from html import unescape
from collections import defaultdict
from datetime import datetime, timezone

# Keep rules small, inspectable and versioned. Patterns use word boundaries to
# avoid e.g. 'ai' matching 'maintain' or 'cloud' matching 'cloudy'.
RULE_VERSION = "2"
RULES = {
    "platform_engineering": (r"platform engineer(?:ing)?", r"internal developer platform", r"developer experience", r"\bbackstage\b"),
    "cloud": (r"\bcloud\b", r"\baws\b", r"\bazure\b", r"\bgcp\b", r"google cloud", r"\bkubernetes\b"),
    "devops": (r"\bdevops\b", r"\bsre\b", r"site reliability", r"\bterraform\b", r"\bci/cd\b", r"\bgitops\b"),
    "modernization": (r"moderni[sz]", r"legacy migration", r"replatform", r"mainframe", r"application migration"),
    "architecture": (r"solution architect", r"software architect", r"enterprise architect", r"\barchitecture\b"),
    "ai_engineering": (r"machine learning engineer", r"\bmlops\b", r"\bllm\b", r"generative ai", r"\bai engineer(?:ing)?\b"),
}
COMPILED = {category: tuple(re.compile(r"(?<!\w)" + p + r"(?!\w)", re.I) for p in patterns)
            for category, patterns in RULES.items()}

# Conservative context guards: weak generic keywords in non-engineering roles
# are insufficient on their own. Strong category-specific terms still count.
DESIGN_ROLE = re.compile(r"\b(?:brand|graphic|visual|creative|product|marketing)\s+design(?:er)?\b|\bdesigner\b", re.I)
RECRUITING_ROLE = re.compile(r"\b(?:recruit(?:er|ing|ment)?|talent acquisition|sourcer)\b", re.I)
CLOUD_STRONG = re.compile(r"\b(?:aws|azure|gcp|kubernetes)\b|google cloud", re.I)
ARCHITECTURE_STRONG = re.compile(r"\b(?:solution|software|enterprise)\s+architects?\b", re.I)


def suppress_weak_match(category: str, title: str, matches: list[dict], fields: dict) -> bool:
    """Suppress only ambiguous matches in roles known to cause false positives.

    Strong technical evidence survives the guard; title is used for role
    context, not an exact-job blacklist. This is a heuristic, not a verdict.
    """
    if category == "cloud" and DESIGN_ROLE.search(title):
        return not CLOUD_STRONG.search(fields["title"] + " " + fields["description"])
    if category == "architecture" and RECRUITING_ROLE.search(title):
        return not ARCHITECTURE_STRONG.search(fields["title"] + " " + fields["description"])
    return False


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden += 1
        elif tag in ("p", "div", "li", "br", "h1", "h2", "h3"):
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
        elif tag in ("p", "div", "li", "h1", "h2", "h3"):
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def visible_text(value: str) -> str:
    parser = _VisibleText()
    parser.feed(value)
    return unescape(" ".join(parser.parts))


def detect(job: dict) -> list[dict]:
    """Return signals based on title and explicit description only.

    Greenhouse's default jobs endpoint may omit descriptions. Do not search
    arbitrary raw JSON: metadata can contain unrelated terms.
    """
    title = job.get("title") or ""
    raw = job.get("raw") or {}
    description = job.get("description") or ((raw.get("content") or raw.get("description")) if isinstance(raw, dict) else "") or ""
    fields = {"title": title, "description": visible_text(description) if isinstance(description, str) else ""}
    results = []
    for category, patterns in COMPILED.items():
        matches = []
        for field, value in fields.items():
            if not isinstance(value, str):
                continue
            for pattern in patterns:
                match = pattern.search(value)
                if match:
                    matches.append({"field": field, "term": match.group(0)})
        if matches and not suppress_weak_match(category, title, matches, fields):
            results.append({
                "rule_version": RULE_VERSION,
                "category": category,
                "source": job["source"],
                "board": job["board"],
                "evidence_id": job["id"],
                "evidence_url": job["url"],
                "matched_terms": matches,
                "confidence": "medium" if any(m["field"] == "title" for m in matches) else "low",
                "explanation": "Keyword evidence in job posting; hiring is not confirmed consulting demand.",
            })
    return results


def summarize(jobs: list[dict]) -> list[dict]:
    """Group signals by source/board (a provisional company key)."""
    grouped = defaultdict(lambda: {"posting_ids": set(), "categories": defaultdict(set), "signals": []})
    for job in jobs:
        key = (job["source"], job["board"])
        for signal in detect(job):
            group = grouped[key]
            group["posting_ids"].add(job["id"])
            group["categories"][signal["category"]].add(job["id"])
            group["signals"].append(signal)
    return [{
        "source": source, "board": board,
        "company_key_type": "source_board_unresolved",
        "postings_with_signals": len(group["posting_ids"]),
        "categories": {category: len(ids) for category, ids in sorted(group["categories"].items())},
        "signals": group["signals"],
        "caveat": "Board is not a verified canonical company identity; signals are not confirmed buying intent.",
    } for (source, board), group in sorted(grouped.items())]


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only signal analysis of stored active postings")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum postings to inspect (1..10000)")
    parser.add_argument("--board", help="Optional board filter")
    args = parser.parse_args()
    if not 1 <= args.limit <= 10000:
        parser.error("--limit must be between 1 and 10000")
    import os
    import psycopg
    if not os.environ.get("DATABASE_URL"):
        parser.error("DATABASE_URL is required")
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, source, board, title, url, raw
                   FROM job_postings WHERE active=TRUE AND (%s IS NULL OR board=%s)
                   ORDER BY board, id LIMIT %s""",
                (args.board, args.board, args.limit))
            jobs = [dict(zip(("id", "source", "board", "title", "url", "raw"), row))
                    for row in cur.fetchall()]
    print(json.dumps({"analyzed_at": datetime.now(timezone.utc).isoformat(),
                      "rule_version": RULE_VERSION, "postings_analyzed": len(jobs),
                      "groups": summarize(jobs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
