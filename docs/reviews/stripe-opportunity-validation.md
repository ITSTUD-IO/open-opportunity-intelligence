# Stripe live opportunity scoring validation

## Reproducible evidence

GitHub Actions [Greenhouse integration run 44936303719](https://github.com/ITSTUD-IO/open-opportunity-intelligence/actions/runs/44936303719) runs against the public Stripe Greenhouse board. The test fetches the board **once**, validates the snapshot, and applies `aggregate(jobs)` from `packages/signals/opportunity.py` to that exact snapshot.

The workflow writes `out/stripe-opportunities.json` and `out/stripe-opportunities.md` and uploads both as the `stripe-opportunity-report` artifact (14-day retention). The CI log prints a machine-readable `OPPORTUNITY_EVIDENCE` line with category counts, score, uncapped raw score, and individual contributions.

## Review checklist

1. Record the actual postings analyzed and postings with signals from `OPPORTUNITY_EVIDENCE`.
2. Record each category's contribution, breadth bonus, volume bonus, raw score and capped 0–100 score.
3. Assess saturation: `raw_score > 100` means the cap hides distinctions; if many boards reach 100, recalibrate scoring before comparative rankings.
4. Verify the report includes original job URLs and category evidence, and that suppressed designer/recruiter false positives do not contribute.
5. Explicitly distinguish technical hiring activity from verified sales opportunity.

## Status

**Awaiting completion and inspection of the current live CI run.** Do not treat the previous 778-posting signal snapshot as a newly measured opportunity score; the current job population can change. No live score is asserted in this document until the workflow output is verified.

**Merge:** PR #6 remains a draft; do not merge without authorization.
