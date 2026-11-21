"""Compare v1 keyword-only and v2 guarded signals on the exact same jobs.

v1 is reconstructed by disabling the only v2 behavioral change: role-context
suppression. Both versions share the unchanged keyword patterns and parser.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from contextlib import contextmanager

try:
    from . import rules
except ImportError:
    import rules


@contextmanager
def baseline_v1():
    original_guard, original_version = rules.suppress_weak_match, rules.RULE_VERSION
    try:
        rules.suppress_weak_match = lambda category, title, matches, fields: False
        rules.RULE_VERSION = "1"
        yield
    finally:
        rules.suppress_weak_match, rules.RULE_VERSION = original_guard, original_version


def compare(jobs: list[dict]) -> dict:
    with baseline_v1():
        before = {str(j["id"]): {s["category"] for s in rules.detect(j)} for j in jobs}
    after = {str(j["id"]): {s["category"] for s in rules.detect(j)} for j in jobs}
    by_id = {str(j["id"]): j for j in jobs}
    removed = []
    added = []
    for job_id in sorted(before):
        job = by_id[job_id]
        for category in sorted(before[job_id] - after[job_id]):
            removed.append({"id": job_id, "title": job.get("title"), "url": job.get("url"), "category": category})
        for category in sorted(after[job_id] - before[job_id]):
            added.append({"id": job_id, "title": job.get("title"), "url": job.get("url"), "category": category})
    return {
        "method": "same_snapshot_v1_keyword_baseline_vs_v2_context_guards",
        "postings_analyzed": len(jobs),
        "postings_with_signals_v1": sum(bool(v) for v in before.values()),
        "postings_with_signals_v2": sum(bool(v) for v in after.values()),
        "category_counts_v1": dict(sorted(Counter(c for cats in before.values() for c in cats).items())),
        "category_counts_v2": dict(sorted(Counter(c for cats in after.values() for c in cats).items())),
        "removed_signals": removed,
        "added_signals": added,
        "review_required": "Inspect every removed signal for unintended loss; no population-wide accuracy claim.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, help="JSON file containing a list of normalized jobs")
    args = parser.parse_args()
    with open(args.json, encoding="utf-8") as f:
        jobs = json.load(f)
    print(json.dumps(compare(jobs), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
