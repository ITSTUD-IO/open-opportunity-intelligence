"""PostgreSQL persistence for job-board snapshots and observed changes.

Requires psycopg >=3. No schema creation during import.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS job_postings (
 id TEXT PRIMARY KEY,
 source TEXT NOT NULL,
 board TEXT NOT NULL,
 source_job_id TEXT NOT NULL,
 title TEXT NOT NULL,
 url TEXT NOT NULL,
 location TEXT NOT NULL,
 first_seen TIMESTAMPTZ NOT NULL,
 last_seen TIMESTAMPTZ NOT NULL,
 last_changed TIMESTAMPTZ NOT NULL,
 content_hash TEXT NOT NULL,
 raw JSONB NOT NULL,
 active BOOLEAN NOT NULL DEFAULT TRUE,
 UNIQUE (source, board, source_job_id)
);
CREATE TABLE IF NOT EXISTS job_events (
 id BIGSERIAL PRIMARY KEY,
 posting_id TEXT NOT NULL REFERENCES job_postings(id),
 event_type TEXT NOT NULL CHECK (event_type IN ('created','changed','closed','reopened')),
 observed_at TIMESTAMPTZ NOT NULL,
 previous_hash TEXT,
 current_hash TEXT
);
CREATE INDEX IF NOT EXISTS job_events_posting_time_idx ON job_events(posting_id, observed_at);
CREATE TABLE IF NOT EXISTS collection_runs (
 id BIGSERIAL PRIMARY KEY,
 source TEXT NOT NULL,
 board TEXT NOT NULL,
 started_at TIMESTAMPTZ NOT NULL,
 completed_at TIMESTAMPTZ,
 status TEXT NOT NULL,
 records_seen INTEGER,
 error TEXT
);
"""


def fingerprint(job: dict) -> str:
    """Stable fingerprint of business-relevant fields, excluding observed_at."""
    payload = {k: job.get(k) for k in ("title", "url", "location", "raw")}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def upsert_snapshot(conn, source: str, board: str, jobs: list[dict], *, observed_at=None) -> dict:
    """Commit one complete successful board snapshot atomically.

    A failed fetch must never call this function: missing records are interpreted
    as closed only after a successful, complete response.
    """
    now = observed_at or datetime.now(timezone.utc)
    ids = set()
    counts = {"created": 0, "changed": 0, "reopened": 0, "closed": 0, "unchanged": 0}
    with conn.transaction():
        with conn.cursor() as cur:
            # Serialize concurrent snapshots of the same board.
            cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s), hashtext(%s))", (source, board))
            for job in jobs:
                if job["source"] != source or job["board"] != board:
                    raise ValueError("Source/board mismatch")
                if job["id"] in ids:
                    raise ValueError("Duplicate job ID in snapshot")
                ids.add(job["id"])
                digest = fingerprint(job)
                cur.execute("SELECT content_hash, active FROM job_postings WHERE id=%s FOR UPDATE", (job["id"],))
                old = cur.fetchone()
                if old is None:
                    event = "created"
                    cur.execute("""INSERT INTO job_postings
                        (id,source,board,source_job_id,title,url,location,first_seen,last_seen,last_changed,content_hash,raw,active)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,TRUE)""",
                        (job["id"],source,board,job["source_job_id"],job["title"],job["url"],job["location"],now,now,now,digest,json.dumps(job["raw"])))
                else:
                    prior_hash, active = old
                    event = "reopened" if not active else ("changed" if prior_hash != digest else None)
                    cur.execute("""UPDATE job_postings SET title=%s,url=%s,location=%s,last_seen=%s,
                        last_changed=CASE WHEN %s THEN %s ELSE last_changed END,
                        content_hash=%s,raw=%s::jsonb,active=TRUE WHERE id=%s""",
                        (job["title"],job["url"],job["location"],now,bool(event),now,digest,json.dumps(job["raw"]),job["id"]))
                if event:
                    cur.execute("""INSERT INTO job_events
                        (posting_id,event_type,observed_at,previous_hash,current_hash)
                        VALUES (%s,%s,%s,%s,%s)""",
                        (job["id"],event,now,old[0] if old else None,digest))
                    counts[event] += 1
                else:
                    counts["unchanged"] += 1
            # Only close records belonging to the completed board snapshot.
            cur.execute("SELECT id,content_hash FROM job_postings WHERE source=%s AND board=%s AND active=TRUE FOR UPDATE", (source,board))
            for old_id, old_hash in cur.fetchall():
                if old_id not in ids:
                    cur.execute("UPDATE job_postings SET active=FALSE,last_changed=%s WHERE id=%s", (now,old_id))
                    cur.execute("""INSERT INTO job_events
                        (posting_id,event_type,observed_at,previous_hash,current_hash)
                        VALUES (%s,'closed',%s,%s,NULL)""", (old_id,now,old_hash))
                    counts["closed"] += 1
    return counts


def initialize(conn) -> None:
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
