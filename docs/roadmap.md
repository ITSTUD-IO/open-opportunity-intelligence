# Four-week proof-of-concept roadmap

This is a planning target, not a delivery guarantee.

## Week 1 — Foundations
- Repository scaffolding, Docker Compose, PostgreSQL migrations and configuration
- Select two legally usable data sources; document licensing and collection limits
- Build first collector and persist raw provenance

## Week 2 — Normalization and signals
- Add second source, company resolution, deduplication and snapshots
- Implement deterministic signal taxonomy and test fixtures
- Establish ingestion metrics and failure reporting

## Week 3 — Intelligence
- Add provider-neutral LLM interface and structured opportunity extraction
- Ground hypotheses in evidence and add confidence/priority scoring
- Manually review an initial sample for false positives and hallucinations

## Week 4 — Validation and review
- Expose FastAPI endpoints and a minimal review interface or CLI
- Process a target sample of 500–1,000 companies where source coverage allows
- Review the top 20 opportunities, capture feedback and summarize quality/costs

## Success criteria
- At least two functioning, permitted source connectors
- Reproducible incremental runs with source provenance and deduplication
- Every surfaced opportunity has evidence and explicit uncertainty
- Manual precision-at-20 reported, with reviewer agreement and failure examples
- Inference and data acquisition costs measured; no promise of fixed precision

## Decision gate
Continue only if reviewers find the ranked opportunities actionable and collection costs, licensing and maintenance are sustainable.
