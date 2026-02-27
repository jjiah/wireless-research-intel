# Design: Three Improvements — Larger Payload, Topic Taxonomy, Weekly Automation

**Date:** 2026-02-27
**Status:** Approved

---

## Overview

Three improvements from `docs/future-improvements.md`:

1. **Larger payload** — increase abstract length and paper cap
2. **Topic taxonomy persistence** — save and reuse LLM-generated topic names for consistency
3. **Weekly automation** — Windows Task Scheduler with missed-run recovery

---

## Improvement 1: Larger Payload

### Changes in `generate_report.py`

| Parameter | Before | After |
|-----------|--------|-------|
| `truncate_abstract(max_words=...)` | 150 | 300 |
| `load_papers(cap_count=...)` | 300 | 500 |

### Token budget

Each paper line ≈ 430 input tokens (300-word abstract + title/venue/week/citations).
500 papers ≈ ~215k tokens — sits near GLM-5's context limit; 1000 would exceed it (~430k).
No changes to output `max_tokens=8192`.

---

## Improvement 2: Topic Taxonomy Persistence

### Goal

Prevent the LLM from naming the same concept differently across runs (e.g. "ISAC" vs "Integrated Sensing and Communication").

### Design

**Storage:** `resource/topic_registry.json`

```json
{
  "topics": ["ISAC", "Beamforming", "RIS", "UAV Communications"],
  "updated": "2026-02-27"
}
```

**Flow (per run):**

1. `load_topic_registry(path)` — read existing topics (returns `[]` if file absent)
2. Inject into LLM prompt (if registry non-empty):
   ```
   - Prefer these previously used topic names when appropriate: ISAC, Beamforming, …
   ```
3. After `call_llm()` returns, parse topic names from `### N. [[Topic]]` headings using regex
4. `update_topic_registry(path, new_topics, existing_topics)` — merge, deduplicate by exact match, write back

**Deduplication strategy:**
- Primary: LLM prompt injection (LLM reuses names it's shown)
- Secondary: exact-string dedup on save (no duplicates in the JSON list)
- Optional fallback: user may maintain `resource/topic_aliases.json` with entries like
  `{"Integrated Sensing and Communication": "ISAC"}` — applied during extraction

### New functions in `generate_report.py`

- `load_topic_registry(path: Path) -> list[str]`
- `extract_topics_from_markdown(markdown: str) -> list[str]`
- `update_topic_registry(path: Path, new_topics: list[str]) -> None`

---

## Improvement 3: Weekly Automation

### Files

**`run_pipeline.bat`** (repo root)

```bat
@echo off
cd /d E:\59357\Documents\GitHub\wireless-research-intel
python ingest_openalex.py
python generate_report.py --weeks 4
```

**`automation/weekly_digest.xml`** — Task Scheduler import file

Key settings:
- Trigger: Weekly, Monday, 08:00
- Action: `run_pipeline.bat`
- `<StartWhenAvailable>true</StartWhenAvailable>` — catches up if computer was off
- Run As: current user (password entered at import time)

### User instructions (added to README.md)

> **Automation**
> To schedule the pipeline on Windows, open Task Scheduler → Action → Import Task → select `automation/weekly_digest.xml`.
> The task runs every Monday at 08:00. If the computer was off, it will run on next startup.

---

## Files Changed / Created

| File | Change |
|------|--------|
| `generate_report.py` | Bump constants; add 3 topic-registry functions; call them in `main()` |
| `resource/topic_registry.json` | Created on first run (not committed) |
| `resource/topic_aliases.json` | Optional; user-maintained; committed as empty `{}` template |
| `run_pipeline.bat` | New |
| `automation/weekly_digest.xml` | New |
| `README.md` | Add "Automation" section |

---

## Out of Scope

- Improvements #4 (relevance filter) and #5 (historical trend tracking) are deferred.
- No changes to `ingest_openalex.py`.
- No new external dependencies.
