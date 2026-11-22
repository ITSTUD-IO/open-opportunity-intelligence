"""DACH comparison harness: explicit boards only, never silently treat missing data as zero."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from packages.collectors.job_boards import collect
from packages.signals.opportunity import aggregate

TARGETS = [
    {"company": "commercetools", "country": "DE", "source": "greenhouse", "board": "commercetools", "status": "candidate"},
    {"company": "Personio", "country": "DE", "source": None, "board": None, "status": "discovery_required"},
    {"company": "n8n", "country": "DE", "source": None, "board": None, "status": "discovery_required"},
    {"company": "Ehrhardt Partner Group", "country": "DE", "source": None, "board": None, "status": "custom_career_site"},
]


def benchmark(targets=TARGETS, collector=collect):
    results = []
    for target in targets:
        row = dict(target)
        if not target["source"] or not target["board"]:
            row.update({"result": "not_collected", "reason": "No verified supported public board identifier"})
            results.append(row)
            continue
        try:
            jobs = collector(target["source"], target["board"])
            profiles = aggregate(jobs)
            row.update({"result": "ok", "postings": len(jobs),
                        "profile": profiles[0] if profiles else None,
                        "reason": None if profiles else "No matching technical signals"})
        except Exception as exc:
            row.update({"result": "error", "reason": str(exc)})
        results.append(row)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("out/dach-benchmark.json"))
    args = parser.parse_args()
    result = benchmark()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps([{"company": r["company"], "result": r["result"],
                       "postings": r.get("postings"), "score": (r.get("profile") or {}).get("score")}
                      for r in result["results"]], ensure_ascii=False))


if __name__ == "__main__":
    main()
