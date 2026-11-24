# Opportunity Intelligence MVP (PR #6)

## Scope
The MVP converts deterministic technical hiring signals into **company-board research priorities**, not predicted consulting purchases. It deliberately does not claim to resolve a verified legal company entity or infer buyer intent.

### Aggregation
- Input: active normalized postings already stored by the Greenhouse collector.
- Group key: `source:board`, explicitly marked `unverified_source_board`.
- Deduplicate by posting ID per board. Count a posting once per signal category and once for volume, even if it matches multiple keywords.
- No external enrichment or LLM calls.

### Explainable scoring v1 (0–100)
Category presence adds fixed points (one contribution per category, regardless of number of matches):

| Category | Points |
|---|---:|
| Architecture | 18 |
| Cloud | 15 |
| Platform engineering | 20 |
| DevOps | 15 |
| AI engineering | 17 |
| Modernization | 20 |

- Breadth: +5 for each additional distinct category beyond the first, capped at +15.
- Volume: +2 for each additional distinct posting with at least one signal, capped at +15.
- Final score: `min(100, category points + breadth + volume)`.
- The JSON includes `raw_score`, individual contributions, category counts, and evidence URLs. Weights can be supplied to `aggregate(..., weights=...)` and are validated.
- Scores saturate quickly for large employers. They are intended for initial triage and require empirical calibration before comparing organizations of very different sizes.

### CLI
Requires a configured PostgreSQL database with the schema and postings from the existing collector:

```bash
PYTHONPATH=. python packages/signals/opportunity.py \
  --board stripe --limit 10000 \
  --json-out out/stripe-opportunities.json \
  --markdown-out out/stripe-opportunities.md
```

The command is **read-only** against the database and creates JSON and Markdown reports locally. Do not commit generated reports containing large external job descriptions; the reports include evidence snippets (matched terms), titles, and URLs.

### Stripe validation
The regression test `tests/test_opportunity.py` uses representative **synthetic excerpts** for Stripe postings:
- Secure Devices and Professional Services yield platform, cloud, DevOps, architecture, and AI signals.
- Brand Designer and Technical Recruiter false positives are suppressed.
- Account Executive remains negative.

The live Stripe board contained 778 postings in the PR #5 validation snapshot, but that snapshot is not stored in the repository. The MVP does **not** claim to have produced a full 778-posting opportunity report without a new live collection or a stored database snapshot. Use the existing opt-in live Greenhouse workflow to verify current postings and run the CLI against its database when available.

### Next iteration
1. Resolve company identity with explicit provenance.
2. Calibrate weights with more human-reviewed companies, especially smaller employers.
3. Add time-window changes and freshness once dated snapshots are available.
4. Introduce a separate confidence/relevance dimension; never label a research score as purchase probability.
