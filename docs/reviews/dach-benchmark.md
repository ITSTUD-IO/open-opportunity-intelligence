# DACH benchmark — source discovery and comparison

Targets: commercetools, Personio, n8n, Ehrhardt Partner Group (EPG).

## Method
Run `python -m packages.dach_benchmark --output out/dach-benchmark.json`. The CI integration workflow also publishes the `dach-benchmark` JSON artifact. Each target has an explicit `result` of `ok`, `error`, or `not_collected`. **Missing source data must never be interpreted as a zero technical-opportunity score.**

| Company | Proposed source | Current integration status |
|---|---|---|
| commercetools | Public Greenhouse board token `commercetools` | Candidate; live request and board identity must be verified in CI |
| Personio | Career-site/ATS discovery | Not yet connected |
| n8n | Public Ashby board `n8n` | Connected in benchmark; CI live validation pending |
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

## Source discovery (2026-11-22)

- **n8n:** Public Ashby careers board identified. The benchmark now collects `ashby:n8n`; live result and scoring still require successful CI verification.
- **Personio:** The employer's own careers page is https://www.personio.com/about-personio/careers/ . Do **not** confuse the Personio ATS XML API (for Personio's *customers*) with the employer's own recruiting backend. Its actual board/API identifier remains to be verified.
- **EPG:** Employer-owned careers at https://www.epg-jobs.com/stellenangebote and individual job descriptions at https://jobs-ads.epg.com/jobposting/… . A reliable index of current vacancy URLs and deduplication is still needed before adding an adapter. Avoid using third-party job board estimates as authoritative employer postings.
