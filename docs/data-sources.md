# Initial data sources and collection policy

## MVP connectors
1. **Greenhouse Job Board API** — public jobs for a known employer board token. Endpoint shape: `https://boards-api.greenhouse.io/v1/boards/{board}/jobs`.
2. **Lever Postings API** — public jobs for a known employer site token. Endpoint shape: `https://api.lever.co/v0/postings/{site}?mode=json`.

Both adapters are implemented as opt-in collectors for specific company boards, **not** a market-wide company discovery crawler. Coverage is limited to employers using these systems. API availability, usage rights, rate limits and applicable terms must be reviewed before production use or redistribution. Public availability alone is not a license to republish data.

## Example
```bash
python packages/collectors/job_boards.py --source greenhouse --board YOUR_BOARD --output data/greenhouse.jsonl
python packages/collectors/job_boards.py --source lever --board YOUR_SITE --output data/lever.jsonl
python -m unittest discover -s tests
```

Replace placeholders with verified public board IDs. No keys required for these public endpoints, but do not use the adapters against private endpoints.

## Current limitations
- No automatic board discovery, company enrichment or country-wide coverage
- No database ingestion, scheduling, incremental history or backoff yet
- No evidence of successful live API calls in this commit
- Snapshot output replaces a given file; keep separate output paths per source and board
- Respect source-specific rules, low request volume and privacy requirements before expanding

## Next implementation
Add a registry of opted-in source boards, persistent PostgreSQL snapshots, idempotent upserts, incremental change detection, retry/backoff and operational metrics.
