"""Deterministic review sample for assessing keyword signal precision.

This is a review queue, not a precision estimate until humans label results.
"""
from __future__ import annotations

import hashlib
from collections import defaultdict

CATEGORIES = ("architecture", "cloud", "ai_engineering", "platform_engineering",
              "devops", "modernization")


def review_sample(jobs: list[dict], detect, *, per_category: int = 3, negatives: int = 5) -> dict:
    if per_category < 0 or negatives < 0:
        raise ValueError("Sample sizes must be nonnegative")
    positives = defaultdict(list)
    no_signals = []
    for job in jobs:
        signals = detect(job)
        entry = {
            "source": job["source"], "board": job["board"], "evidence_id": job["id"],
            "url": job["url"], "title": job.get("title", ""),
            "categories": [s["category"] for s in signals],
            "matched_terms": {s["category"]: s["matched_terms"] for s in signals},
            "review_label": None,  # reviewer: relevant / irrelevant / uncertain
            "review_notes": None,
        }
        if signals:
            for signal in signals:
                positives[signal["category"]].append(entry)
        else:
            no_signals.append(entry)

    def select(entries, n):
        # Stable selection independent of API ordering; avoid first-N sampling bias.
        return sorted(entries, key=lambda e: hashlib.sha256(e["evidence_id"].encode()).hexdigest())[:n]

    return {
        "method": "stable_hash_sample_v1",
        "positive_samples": {category: select(positives[category], per_category)
                             for category in CATEGORIES},
        "negative_samples": select(no_signals, negatives),
        "review_instructions": (
            "Check original posting URL and context. Label each category-specific match "
            "relevant/irrelevant/uncertain. For negatives, note any missed category. "
            "Report precision only after human labels; this sample is not ground truth."
        ),
    }
