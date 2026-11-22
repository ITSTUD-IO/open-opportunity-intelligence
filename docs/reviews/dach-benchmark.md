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

## Personio and EPG source adapter progress (2026-11-22)

- Added `personio_xml` parser and collector for the documented **public Personio tenant XML** shape (`<workzag-jobs><position>…`). This is a reusable adapter for companies using Personio Recruiting, **not** evidence that Personio SE's own careers run on that feed. Do not activate the Personio SE benchmark target until its actual tenant and official vacancy URL scheme are verified.
- Added a strict employer-host allowlisted `epg_job_links` extractor to discover `https://jobs-ads.epg.com/jobposting/…` links from employer-owned listing HTML. This is a discovery primitive, **not** a complete EPG collector: pagination, rendering requirements, posting content extraction, job IDs and live end-to-end verification remain open.
- Unit tests cover the XML structure and external-link rejection. There is currently **no verified Personio SE or EPG score**.
- Source-validation gate: confirm public employer source, inspect a live response, verify description extraction and vacancy URL, then enable benchmark collection and compare evidence against the original page. Never interpret blocked or absent data as score zero.

## EPG implementation focus (2026-11-22)

Personio SE is **deferred** and excluded from active benchmark targets at the user's request. The reusable generic Personio XML parser remains in the codebase but is not run.

The EPG collector now:
1. Reads the employer-owned public listing page `https://www.epg-jobs.com/stellenangebote/berufserfahrene`.
2. Extracts only HTTPS links to `jobs-ads.epg.com/jobposting/<id>`.
3. Retrieves each posting, extracts visible text and a page title, and normalizes records as `epg:ehrhardt-partner-group`.
4. Fails explicitly when a listing is JavaScript-rendered or posting content is incomplete. Such a failure is **not** scored as zero.

**Live caveat:** This initial collector assumes static HTML and one listing page. It may need an official API or browser-rendering discovery and pagination. CI result must be inspected before calling EPG connected or assigning any score.

## Verified EPG source discovery — GitHub Actions run 45026855858

The live HTML response from `https://www.epg-jobs.com/stellenangebote/berufserfahrene` identifies the recruiting provider **BITE**:
- `https://static.b-ite.com/jobs-api/004/api-v4.js`
- `https://cs-assets.b-ite.com/epg/jobs-api/v2/epg.min.js`
- `https://static.b-ite.com/jobs-api/loader-v1/api-loader-v1.min.js`
- Listing configuration: `data-bite-jobs-api-listing="epg:direkteinstieg-listing-de"`
- An employer-hosted application URL occurs in the initial HTML: `https://jobs-ads.epg.com/de/jobposting/69a6ecc20c71848aa118e77ebc730957bf34fbb81/apply`.

**Conclusion:** The initial static-link collector does not match the provider's dynamic listing. Inspect the public BITE JavaScript/configuration to identify its documented/read-only list endpoint and response schema, then implement a targeted adapter. No verified listing API URL, pagination contract or successful EPG score yet. Source: integration run https://github.com/ITSTUD-IO/open-opportunity-intelligence/actions/runs/45026855858 .
