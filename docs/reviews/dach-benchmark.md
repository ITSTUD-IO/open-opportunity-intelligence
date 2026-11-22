# DACH benchmark — source discovery and comparison

Targets: commercetools, Personio, n8n, Ehrhardt Partner Group (EPG).

## Method
Run `python -m packages.dach_benchmark --output out/dach-benchmark.json`. The CI integration workflow also publishes the `dach-benchmark` JSON artifact. Each target has an explicit `result` of `ok`, `error`, or `not_collected`. **Missing source data must never be interpreted as a zero technical-opportunity score.**

| Company | Proposed source | Current integration status |
|---|---|---|
| commercetools | Public Greenhouse board token `commercetools` | Candidate; live request and board identity must be verified in CI |
| Personio | Career-site/ATS discovery | Not yet connected |
| n8n | Career-site/ATS discovery | Not yet connected |
| Ehrhardt Partner Group | https://www.epg-jobs.com/ | Custom-source integration needed |

The existing Greenhouse and Lever adapters remain available. An Ashby public-board adapter was added to enable a later verified Ashby integration; **do not guess board tokens**.

## Benchmark criteria
- Number of active postings and postings with technical signals.
- Category counts, explainable contributions, capped and uncapped scores.
- Score saturation at 100 and company-size bias.
- Source coverage, missing description fields, and evidence quality.
- A technical hiring signal is **not** proof of consulting demand.

## Caveats
Until source discovery and live collection succeed, no cross-company ranking can be claimed. Stripe remains the reference case: 778 postings, 233 with signals, uncapped score 115, capped score 100 (live PR #6 validation). This DACH benchmark is an extension of PR #6; keep the PR unmerged.
