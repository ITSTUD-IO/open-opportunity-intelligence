# Manual end-to-end smoke test

No recurring jobs or automated market scans are configured.

## 1. Read-only live API probe

Verify the board token and source permissions before use. Fetch and validate postings without a database:

```bash
python packages/collectors/collect_to_db.py --source greenhouse --board VERIFIED_BOARD --dry-run
python packages/collectors/collect_to_db.py --source lever --board VERIFIED_SITE --dry-run
```

Output includes the count and up to five titles; it does not save postings. A zero-result response fails safely by default.

## 2. Local PostgreSQL integration

Follow [manual-validation.md](manual-validation.md) to start PostgreSQL, set DATABASE_URL and run tests. Use a disposable database for TEST_DATABASE_URL.

```bash
python -m unittest discover -s tests -v
python packages/collectors/collect_to_db.py --source greenhouse --board VERIFIED_BOARD --init-db
```

Repeat the collection to confirm unchanged records produce no additional lifecycle events. A genuine change, closure or reopening requires an observed source change or controlled synthetic integration fixtures.

## 3. Inspect evidence

```sql
SELECT source, board, COUNT(*) FROM job_postings GROUP BY source, board;
SELECT event_type, COUNT(*) FROM job_events GROUP BY event_type;
SELECT posting_id, event_type, observed_at FROM job_events ORDER BY id DESC LIMIT 20;
```

## Safety

- A failed API request or invalid snapshot does not write to the database.
- Empty responses are rejected by default; `--allow-empty` is an explicit override and may close all previously active postings for a board.
- Live endpoints and licensing have **not** yet been verified by these instructions.
- The code is a prototype, not a production crawler.
