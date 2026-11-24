# DACH job-board source prioritization — 2026-11-22

## Decision

Pivot primary discovery from individual employer pages to DACH-relevant job boards. Employer pages remain enrichment and validation sources. **Do not treat public access as a redistribution or commercial analytics licence.** No source in this document is authorized for production lead generation without reviewing its terms and obtaining necessary permission.

| Priority | Source | DACH coverage | Access and constraints | MVP decision |
|---|---|---|---|---|
| P0 | Arbeitnow | Strong Germany/Europe technical-job focus; AT/CH coverage to measure | Public unauthenticated JSON feed; verify current terms, attribution and commercial analytics permission | First read-only technical quality spike |
| P0 | Adzuna | Country-specific DE/AT/CH search | Official documented REST API; registration for app_id/app_key. Commercial analysis, prospecting and lead generation require written agreement; trial only for evaluation | Parallel access/licensing and sample quality evaluation |
| P1 | Bundesagentur für Arbeit Jobsuche | DE breadth | Community-documented endpoints, **not an officially offered public API**; permission and stability uncertain | Research/validation only until authorized |
| P1 | arbeit.swiss Job-Room | CH breadth | No verified public read API; third-party API products exist, but rights and provenance require review | Research/validation or licensed provider |
| P1 | AMS alle jobs | AT breadth | AMS terms restrict reuse for purposes outside statutory remit, especially advertising; HR-API is for submitting employer vacancies, not a public read API | No bulk collection without permission |
| P2 | JOIN | European SMB coverage | Official API requires an employer token; not an open cross-company search API | Employer enrichment only or licensed aggregator |
| P2 | StepStone / Indeed / LinkedIn | Broad | No verified permission for automated bulk reuse in this project | Defer until official agreement |

## Evidence and links

- Arbeitnow: https://www.arbeitnow.com/api/job-board-api ; https://documenter.getpostman.com/view/18545278/UVJbJdKh
- Adzuna official API: https://developer.adzuna.com/overview ; terms: https://developer.adzuna.com/docs/terms_of_service
- BA community documentation (not official): https://github.com/bundesAPI/jobsuche-api
- AMS official terms: https://www.ams.at/arbeitsuchende/arbeitslos-was-tun/jobsuche-online-und-mobil/ams-jobsuche-hilfe
- JOIN employer-token API: https://docs.join.com/reference/quickstart

## First bounded spike: Arbeitnow

Read a small, capped sample of the published feed; **no persistent bulk import** until terms review. Produce a machine-readable audit: sample count, unique IDs, descriptions of substantive length, company/location completeness, DE/AT/CH country evidence, valid HTTPS job URLs, technical-signal hit rate, and sample role classifications. Log only aggregates and a few representative public job titles; preserve provenance. Fail closed if source access or schema changes. Do not infer country from vague city strings alone.

## Adzuna parallel track

Obtain developer credentials and written clarification/licence for the intended commercial opportunity-intelligence use. During the permitted evaluation window, compare description length, coverage of DE/AT/CH, employer identity, posting dates, pagination and canonical employer URLs. Do not treat short search snippets as complete descriptions.

## Acceptance gate

- >=80% of sampled postings with substantive description text; >=95% valid HTTPS URLs; >=90% employer name and location; stable unique IDs.
- DACH country attribution must be demonstrable, not guessed; separately report unknown.
- Sample at least 10 technical and 10 nontechnical postings to check false positives (e.g. visual design with generative AI is not automatically AI engineering).
- Deduplicate across sources and employer URLs; distinguish source observations from verified employer facts.
- If source quality fails, record a no-go and evaluate the next licensed source. Never invent a research-priority score from incomplete data.

## Scope

No change to scoring weights or existing employer collectors in this decision. PR #6 stays open and unmerged.

## Adzuna evaluation implementation (2026-11-23)

`packages/collectors/adzuna_quality.py` provides a **bounded, read-only** market-specific adapter for DE, AT and CH. It does not run in CI against the live API because credentials and explicit approval are required. Its fixture-based tests run in the repository test suite.

To run a permitted evaluation locally, first register an Adzuna developer application and confirm the intended use is covered by the terms or written agreement. Set `ADZUNA_EVALUATION_APPROVED=1`, `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` as environment variables (never commit them). Then run `python -m packages.collectors.adzuna_quality --market de --limit 20`; repeat for `at` and `ch`. The script does not print credentials, store job records or crawl pages. It reports aggregate field coverage, stable identifiers, description lengths and technical signal counts. API market is **not** treated as proof of an individual job's country.

**Current status:** Implementation and offline fixtures only; no real Adzuna response, licensing approval, or DACH coverage measurements yet. Full-text coverage is a critical go/no-go criterion because search APIs often return snippets.

## Live Adzuna checkpoint — 2026-11-24

Run: https://github.com/ITSTUD-IO/open-opportunity-intelligence/actions/runs/45486609676

Three successful requests for software engineer, 20 results per market. Reported totals DE 3659, AT 191, CH 715. All 60 samples had employer, location, HTTPS URL and unique IDs within each market. Signal hits DE 0/20, AT 3/20, CH 5/20. Every extracted description was exactly 500 characters (min=max in all markets), strongly suggesting truncation. Market is not independently verified posting country; reported totals are not deduplicated or market-wide estimates. HTTPS redirect URLs are not verified canonical employer URLs.

Decision: discovery candidate only; no-go for standalone full-text opportunity scoring pending richer licensed data or permitted employer enrichment. Existing technical gate does not establish completeness. Commercial permission remains unverified. Three successful calls observed; nominal remaining trial budget 22 if no other usage. No further calls made in this checkpoint.
