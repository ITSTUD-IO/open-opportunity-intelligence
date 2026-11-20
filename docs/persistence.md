# PostgreSQL persistence and change tracking

## Run locally

```bash
python -m pip install -r requirements.txt
export POSTGRES_PASSWORD='choose-a-local-secret'
docker compose -f infra/docker/docker-compose.yml up -d
export DATABASE_URL="postgresql://opportunity:${POSTGRES_PASSWORD}@localhost:5432/opportunity"
python packages/collectors/collect_to_db.py --source greenhouse --board VERIFIED_BOARD --init-db
```

On Windows PowerShell, set environment variables with `$env:POSTGRES_PASSWORD` and `$env:DATABASE_URL` instead.

## Semantics
- `job_postings`: current canonical snapshot, first/last seen, content fingerprint and active status.
- `job_events`: append-only created/changed/closed/reopened events.
- An unchanged repeat scan refreshes `last_seen` but emits no event.
- Only a successful complete board response is eligible to close missing jobs.
- Each board snapshot is one database transaction with a per-board advisory lock.

## Known constraints
- Initial schema is a bootstrap, not a versioned migration.
- Empty successful responses close all existing jobs on that board. Production collectors should detect suspicious empty responses before persisting.
- Changes to irrelevant fields in source `raw` currently generate change events; refine fingerprint fields after real-world testing.
- Source rate limits, retry/backoff, schedule, collection-run auditing and integration tests remain to be implemented.
- PostgreSQL is bound to localhost for development; do not expose it publicly.
- API licensing, retention and privacy rules must be checked before production use.
