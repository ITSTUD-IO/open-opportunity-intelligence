"""Run a configured public job-board collector and persist its snapshot."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

import psycopg

from job_boards import collect
from storage import initialize, upsert_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("greenhouse", "lever"), required=True)
    parser.add_argument("--board", required=True)
    parser.add_argument("--init-db", action="store_true")
    args = parser.parse_args()
    if not args.board.replace("-", "").replace("_", "").isalnum():
        parser.error("Invalid board identifier")
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        parser.error("DATABASE_URL is required")
    # Fetch before opening a transaction: failed fetches cannot close jobs.
    jobs = collect(args.source, args.board)
    with psycopg.connect(dsn) as conn:
        if args.init_db:
            initialize(conn)
        result = upsert_snapshot(conn, args.source, args.board, jobs)
    print(json.dumps({"source": args.source, "board": args.board, "records": len(jobs), "events": result}))


if __name__ == "__main__":
    main()
