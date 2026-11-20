"""Opt-in live Greenhouse E2E evidence; runs against ephemeral CI PostgreSQL."""
import json
import os
import sys
from pathlib import Path

import psycopg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "packages" / "collectors"))
from job_boards import collect
from collect_to_db import validate_snapshot
from storage import initialize, upsert_snapshot

board = os.environ["GREENHOUSE_BOARD"]
if not board or not board.replace("-", "").replace("_", "").isalnum():
    raise ValueError("Invalid Greenhouse board token")

# Fetch once and replay the exact same validated snapshot for deterministic idempotency.
jobs = collect("greenhouse", board)
validate_snapshot(jobs, "greenhouse", board)
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    initialize(conn)
    first = upsert_snapshot(conn, "greenhouse", board, jobs)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM job_postings WHERE source=%s AND board=%s", ("greenhouse", board))
        stored_first = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM job_events WHERE event_type='created'")
        events_first = cur.fetchone()[0]
    assert stored_first == len(jobs), (stored_first, len(jobs))
    assert first["created"] == len(jobs), first

    second = upsert_snapshot(conn, "greenhouse", board, jobs)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM job_postings WHERE source=%s AND board=%s", ("greenhouse", board))
        stored_second = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM job_events WHERE event_type='created'")
        events_second = cur.fetchone()[0]
    assert stored_second == stored_first
    assert events_second == events_first
    assert second == {"created": 0, "changed": 0, "reopened": 0, "closed": 0, "unchanged": len(jobs)}, second

    # Controlled synthetic change: verify detection without altering the public API.
    changed = dict(jobs[0])
    changed["title"] = changed["title"] + " [controlled CI change]"
    changed["raw"] = dict(changed["raw"], _ci_test_change=True)
    updated_jobs = [changed, *jobs[1:]]
    third = upsert_snapshot(conn, "greenhouse", board, updated_jobs)
    assert third["changed"] == 1 and third["unchanged"] == len(jobs) - 1, third
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM job_events WHERE event_type='changed'")
        assert cur.fetchone()[0] == 1

print(json.dumps({"board": board, "fetched": len(jobs), "stored_first": stored_first,
                  "first_events": first, "stored_second": stored_second,
                  "second_events": second, "controlled_change_events": third}, sort_keys=True))
