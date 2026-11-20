"""Public job-board adapters. Explicit company board IDs only; no discovery crawling."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def fetch_json(url: str, *, timeout: int = 15) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "OpenOpportunityIntelligence/0.1 (research prototype)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def normalize(source: str, board: str, job_id: str, title: str, url: str, location: str, raw: dict) -> dict:
    key = hashlib.sha256(f"{source}:{board}:{job_id}".encode()).hexdigest()
    return {"id": key, "source": source, "board": board, "source_job_id": str(job_id),
            "title": title, "url": url, "location": location,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "raw": raw}


def greenhouse(board: str, payload: dict) -> list[dict]:
    jobs = []
    for job in payload.get("jobs", []):
        jobs.append(normalize("greenhouse", board, str(job["id"]), job.get("title", ""),
                              job.get("absolute_url", ""), (job.get("location") or {}).get("name", ""), job))
    return jobs


def lever(board: str, payload: list[dict]) -> list[dict]:
    jobs = []
    for job in payload:
        categories = job.get("categories") or {}
        jobs.append(normalize("lever", board, str(job["id"]), job.get("text", ""),
                              job.get("hostedUrl", ""), categories.get("location", ""), job))
    return jobs


def collect(source: str, board: str) -> list[dict]:
    safe_board = urllib.parse.quote(board, safe="")
    if source == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{safe_board}/jobs?content=true"
        return greenhouse(board, fetch_json(url))
    if source == "lever":
        url = f"https://api.lever.co/v0/postings/{safe_board}?mode=json"
        return lever(board, fetch_json(url))
    raise ValueError(f"Unsupported source: {source}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch public job postings for explicitly configured boards")
    parser.add_argument("--source", choices=("greenhouse", "lever"), required=True)
    parser.add_argument("--board", required=True, help="Company's public board identifier")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.board.replace("-", "").replace("_", "").isalnum():
        parser.error("Board must contain only letters, numbers, dashes or underscores")
    jobs = collect(args.source, args.board)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement makes repeated runs safe for this single-board snapshot.
    temp = args.output.with_suffix(args.output.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        for job in jobs:
            handle.write(json.dumps(job, ensure_ascii=False) + "\n")
    temp.replace(args.output)
    print(f"Saved {len(jobs)} postings from {args.source}/{args.board} to {args.output}")


if __name__ == "__main__":
    main()
