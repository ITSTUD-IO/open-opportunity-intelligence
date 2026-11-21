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

## Live results — 2026-11-21

Source: successful Greenhouse integration workflow run [44934977904](https://github.com/ITSTUD-IO/open-opportunity-intelligence/actions/runs/44934977904), commit `d0d7a560`. Exact same snapshot, 778 postings with descriptions.

| Metric | v1 | v2 | Delta |
|---|---:|---:|---:|
| Postings with at least one signal | 236 | 233 | -3 |
| Architecture | 156 | 154 | -2 |
| Cloud | 57 | 56 | -1 |
| AI engineering | 50 | 50 | 0 |
| DevOps | 17 | 17 | 0 |
| Platform engineering | 31 | 31 | 0 |
| Modernization | 0 | 0 | 0 |

No added category signals. Exactly three removed (posting, category) pairs:

1. [Technical Recruiter, OpenRouter (Fixed Term)](https://stripe.com/jobs/search?gh_jid=8404144): `architecture`. **Previously human-confirmed false positive**; expected removal.
2. [Senior Brand Designer, Link](https://stripe.com/jobs/search?gh_jid=8172672): `cloud`. **Previously human-confirmed false positive**; expected removal.
3. [GTM Recruiter, OpenRouter (Fixed Term)](https://stripe.com/jobs/search?gh_jid=8404131): `architecture`. **Human-confirmed correct removal (2026-11-21)**; reviewer assessed no relevant technical architecture signal.

All other 775 postings retain the same category-level classification between versions. This is an exact algorithmic comparison, not a manual confirmation of relevance. All three removed signals were assessed by the human reviewer as false positives. No unintended category-level losses were observed in this 778-posting snapshot; this is not a guarantee for other boards or future snapshots.

**Status:** All three removals human-reviewed as correct; CI for the tested code passed. Merge-readiness assessment: technically ready for review/merge, subject to required branch checks and any repository approval policy. Documentation-only commit should still receive its normal checks. Do not merge without explicit user authorization.


## Limitations
The public job board is mutable. A single snapshot controls version-comparison drift, but results may not generalize across employers. Technical hiring signals do not prove external consulting buying intent.
