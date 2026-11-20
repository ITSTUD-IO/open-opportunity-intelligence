# High-level epics

## Immediate execution order
**Next milestone: Greenhouse live end-to-end validation (E1/E2/E6), followed by a minimal explainable signal engine (E3).** The initial run is manual; scheduling and dashboards are not prerequisites.

## E1 — Source ingestion
**Outcome:** Retrieve permitted Greenhouse and Lever job postings with provenance.
**Next task — Greenhouse dry run:** choose a permitted public board, run the collector against live data, store results in PostgreSQL and document invocation, source policy, counts, failures and timestamps.
**Acceptance:** source metadata and canonical URLs preserved; errors observable; repeat run does not create duplicate source records. Broader source coverage and scheduling remain later tasks.

## E2 — Company resolution and history
**Outcome:** Group records under a canonical company and detect new or changed postings.
**Next task — repeat-run validation:** run the same Greenhouse collection twice and verify a no-op second run; exercise changed/new/unavailable postings with controlled fixtures or observed live changes.
**Acceptance:** historical snapshots and first/last-seen timestamps; deterministic fingerprints; ambiguous company matches flagged; transient API failures never silently classified as deletions.

## E3 — Engineering signal detection
**Outcome:** Convert job postings into explainable consulting-relevant engineering investment signals.
**Next task — vertical slice:** implement deterministic rules for platform engineering, cloud, DevOps, modernization, architecture and AI engineering, with evidence IDs, matching terms, time window and confidence.
**Acceptance:** positive and negative fixtures; traceable evidence for each signal; grouped company-level view; explicit uncertainty and no claim of confirmed purchasing intent.

## E4 — AI opportunity analysis
**Outcome:** Generate structured, falsifiable consulting opportunity hypotheses from validated signals.
**Acceptance:** source IDs, evidence summary, counterevidence, confidence, caveats, analysis timestamp and model version; schema validation; no unsupported assertions. Defer LLM enrichment until E3 baseline is measured.

## E5 — Prioritization and review
**Outcome:** Rank companies by potential relevance and collect human feedback.
**Acceptance:** configurable scoring with separate evidence confidence, consulting relevance and commercial priority; review statuses relevant, irrelevant, known and needs-review; top 20 assessed by humans before dashboard investment.

## E6 — Delivery and quality
**Outcome:** Reproducible development and evaluation workflow.
**Next task:** document manual Greenhouse end-to-end commands, prerequisites, database checks, first/second-run observations, test fixtures and failure cases.
**Acceptance:** repeatable Docker Compose setup, tests, secret-safe configuration, concise dry-run report and a clear pass/fail gate for starting E3.

## Later
Scheduled execution, additional news sources, dashboard polish, CRM integration, notifications, local-model benchmarking and multi-user workflows are deferred until evidence quality is proven.
