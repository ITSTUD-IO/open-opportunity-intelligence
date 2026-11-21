# Stripe signal rules v1 → v2: same-snapshot validation

## Method
- Source: live public Greenhouse board token `stripe`.
- `tests/greenhouse_live_e2e.py` fetches jobs once, validates and persists the same snapshot, and prints `SIGNAL_VERSION_COMPARISON`.
- `packages/signals/compare_versions.py` evaluates v1 keyword-only behavior and v2 context guards on **identical normalized jobs**, without a second fetch.
- v1 is reconstructed by disabling v2's context suppression, keeping keyword rules and HTML parsing identical. This is valid because context suppression is the only intended behavioral change.
- The JSON contains category counts, postings with signals, and every removed or added (posting, category) pair.
- All removed pairs must be manually checked against the original posting text; a removal is **not automatically a true-positive correction**.
- Historical 778-posting counts from earlier runs cannot be directly compared with a newer live snapshot because the board may change.

## Known human-reviewed cases
- Expected false positives to remove: `8172672/cloud` (Senior Brand Designer, Link); `8404144/architecture` (Technical Recruiter, OpenRouter).
- Expected relevant signals to preserve: 20 reviewed category matches across nine postings (see `docs/reviews/stripe-signal-review-2026-11-20.md`).
- Five reviewed correct negatives should remain without signals.
- Regression tests use **synthetic excerpts**, not archived verbatim posting content.

## Live results
The PR-triggered integration workflow runs the Stripe snapshot comparison. Retrieve the `SIGNAL_VERSION_COMPARISON` line from its job logs, inspect every `removed_signals` entry and record measured counts here before approving merge.

**Status:** live results pending; no claim of zero unintended losses until all removed matches are inspected.

## Limitations
The public job board is mutable. A single snapshot controls version-comparison drift, but results may not generalize across employers. Technical hiring signals do not prove external consulting buying intent.
