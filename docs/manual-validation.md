# Manual integration validation

No recurring scheduler is enabled. Every collection run is explicitly started by an operator.

## Prerequisites
- Python 3.11+, Docker with Compose
- PostgreSQL running locally
- A verified public Greenhouse board ID or Lever site ID
- Confirmed permitted usage of the source endpoint
- Never point TEST_DATABASE_URL at a production database

## Start local PostgreSQL
```bash
python -m pip install -r requirements.txt
export POSTGRES_PASSWORD='local-dev-password'
docker compose -f infra/docker/docker-compose.yml up -d
export DATABASE_URL="postgresql://opportunity:${POSTGRES_PASSWORD}@127.0.0.1:5432/opportunity"
export TEST_DATABASE_URL="$DATABASE_URL"
```

## Run tests manually
```bash
python -m unittest discover -s tests -v
```

The integration tests use unique synthetic job and board IDs, but leave test rows in the configured database. Use a disposable development database.

## Collect a real board manually
```bash
python packages/collectors/collect_to_db.py --source greenhouse --board VERIFIED_BOARD --init-db
# or:
python packages/collectors/collect_to_db.py --source lever --board VERIFIED_SITE --init-db
```

Repeat the same command to verify unchanged records. Only after a complete successful response can the collector mark missing jobs as closed. Avoid running against a board returning suspiciously empty results until safeguards are implemented.

## Inspect events
```sql
SELECT source, board, count(*) FROM job_postings GROUP BY source, board;
SELECT event_type, count(*) FROM job_events GROUP BY event_type;
SELECT posting_id, event_type, observed_at FROM job_events ORDER BY id DESC LIMIT 20;
```

## Pending before production
- Source permission and rate-limit verification
- Empty-response safeguards, HTTP retries and backoff
- Schema migrations and isolation of integration-test data
- External integration test execution and evidence of successful live calls
