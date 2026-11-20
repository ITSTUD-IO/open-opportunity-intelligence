# High-level epics

## E1 — Source ingestion
**Outcome:** Retrieve permitted job and company-news records from at least two independent sources.
**Acceptance:** Scheduled incremental runs; canonical URL and timestamp; retries, rate limits and logs; source permissions documented; duplicate fetches do not duplicate records.

## E2 — Company resolution and history
**Outcome:** Group records under a canonical company and detect new or changed signals.
**Acceptance:** Domain/alias matching; ambiguous matches flagged for review; historical snapshots and first/last-seen timestamps.

## E3 — Engineering signal detection
**Outcome:** Classify postings and announcements into platform engineering, cloud, DevOps, modernization, architecture and AI engineering.
**Acceptance:** Rule-based baseline; evidence links; tests with positive and negative examples; explainable signal categories.

## E4 — AI opportunity analysis
**Outcome:** Produce structured, falsifiable business hypotheses.
**Acceptance:** Each hypothesis has source IDs, evidence summary, confidence, caveats, analysis timestamp and model version; schema validation; no unsupported claims presented as facts.

## E5 — Prioritization and review
**Outcome:** Rank relevant companies and capture human decisions.
**Acceptance:** Configurable scoring; separate confidence and priority; statuses relevant, irrelevant, known and needs-review; feedback persisted.

## E6 — Delivery and quality
**Outcome:** Repeatable developer setup and measurable evaluation.
**Acceptance:** Docker Compose, sample synthetic fixtures, tests, README, secret-safe configuration, evaluation report and reproducible run instructions.

## Later
Dashboard polish, CRM integration, additional sources, notifications, local-model benchmarking and multi-user workflows are deferred until evidence quality is proven.
