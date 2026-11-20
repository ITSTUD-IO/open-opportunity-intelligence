# Open Opportunity Intelligence

Open-source, evidence-first market intelligence for identifying potential software engineering consulting opportunities from publicly accessible company signals.

**Status:** Planning / proof of concept. **Initial use:** internal business development. This repository contains software and documentation, not internal lead data.

## What it does
1. Collect permitted job postings and company announcements.
2. Resolve company identities and track changes over time.
3. Detect engineering investment signals (platform engineering, cloud, DevOps, modernization, architecture, AI).
4. Generate evidence-linked opportunity hypotheses with explicit uncertainty.
5. Prioritize findings and collect reviewer feedback.

Hiring activity is **not** proof of purchase intent. All hypotheses require human validation.

## Documentation
- [Product vision](docs/product-vision.md)
- [Architecture](docs/architecture.md)
- [High-level epics](docs/epics.md)
- [Four-week PoC roadmap](docs/roadmap.md)

## Proposed stack
Python, FastAPI, PostgreSQL, scheduled workers and an optional React dashboard. Hosted LLMs initially, with a replaceable adapter for local models.

## First milestone
A reproducible end-to-end run from two permitted sources to a ranked, evidence-backed opportunity list. Evaluate the top 20 with human reviewers before investing in a richer dashboard.

## Data and security
Respect source licenses, collection restrictions, privacy and retention requirements. Never commit API keys, private sales assessments or restricted source datasets.

## License
Intended license: Apache-2.0. Verify the repository contains a LICENSE file before relying on this declaration.
