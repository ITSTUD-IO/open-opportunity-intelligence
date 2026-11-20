"""Manually collect a public job board and persist a complete snapshot."""
from __future__ import annotations

import argparse
import json
import os

from job_boards import collect


def validate_snapshot(jobs: list[dict], source: str, board: str, allow_empty: bool = False) -> None:
    """Reject suspicious snapshots before any database write."""
    if not isinstance(jobs, list):
        raise ValueError("Collector must return a list")
    if not jobs and not allow_empty:
        raise ValueError("Empty response rejected: rerun with --allow-empty only after verifying the board")
    ids = set()
    for job in jobs:
        if job.get("source") != source or job.get("board") != board:
            raise ValueError("Unexpected source or board in response")
        if not all(job.get(key) for key in ("id", "source_job_id", "title", "url")):
            raise ValueError("Incomplete posting in response")
        if job["id"] in ids:
            raise ValueError("Duplicate posting in response")
        ids.add(job["id"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("greenhouse", "lever"), required=True)
    parser.add_argument("--board", required=True)
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and validate without database writes")
    parser.add_argument("--allow-empty", action="store_true", help="Explicitly allow empty snapshot (may close all jobs)")
    args = parser.parse_args()
    if not args.board.replace("-", "").replace("_", "").isalnum():
        parser.error("Invalid board identifier")
    if not args.dry_run and not os.environ.get("DATABASE_URL"):
        parser.error("DATABASE_URL is required unless --dry-run is used")

    # A failed or malformed response must never close existing postings.
    jobs = collect(args.source, args.board)
    validate_snapshot(jobs, args.source, args.board, allow_empty=args.allow_empty)
    if args.dry_run:
        print(json.dumps({"source": args.source, "board": args.board,
                          "records": len(jobs), "dry_run": True,
                          "sample_titles": [j["title"] for j in jobs[:5]]}))
        return

    import psycopg
    from storage import initialize, upsert_snapshot

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        if args.init_db:
            initialize(conn)
        result = upsert_snapshot(conn, args.source, args.board, jobs)
    print(json.dumps({"source": args.source, "board": args.board,
                      "records": len(jobs), "events": result}))


if __name__ == "__main__":
    main()
