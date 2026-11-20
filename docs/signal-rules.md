# Rule-based engineering signals (E3 vertical slice)

Run against a **persistent, explicitly populated** PostgreSQL database:

```bash
DATABASE_URL=postgresql://... python packages/signals/rules.py --board VERIFIED_BOARD --limit 1000
```

This command is read-only and prints JSON. It does **not** fetch job boards, run a market scan, create permanent signals, or schedule any activity. The ephemeral GitHub Actions database from the previous live test is gone after the run.

Categories: platform engineering, cloud, DevOps/SRE, modernization, architecture, and AI engineering. Rules match title and explicit description, never unrelated metadata. Output includes evidence posting ID/URL, matching field and term, rule version, confidence heuristic and provisional grouping by source + board. A title match is medium confidence; a description-only match is low confidence. Neither is evidence of consulting purchasing intent.

**Limitations:** The current Greenhouse collection uses the default API jobs response, which often does not include descriptions. Results are therefore title-heavy and likely miss signals. HTML descriptions are not yet cleaned, source board identity is not verified as a canonical company, and rule precision/recall have not been evaluated on reviewed postings. Group counts are not an opportunity ranking. Review false positives and add curated fixtures before LLM hypotheses or scoring.
