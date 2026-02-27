# Future Improvements

## 1. Larger Payload (Quick Win)

Increase the amount of paper content sent to the LLM.

**Changes in `generate_report.py`:**
- `truncate_abstract(... max_words=150)` → increase to `250–300`
- `load_papers(... cap_count=300)` → increase to `500`

**Trade-off:** higher token cost per run; still within GLM-5 context window.

---

## 2. Historical Trend Tracking (Approach B)

Cache per-paper topic labels in SQLite so week-over-week trends can be computed precisely instead of inferred by the LLM.

**Pipeline:**
1. For each new paper, call LLM (or keyword match) to assign a topic label → store in `resource/index.sqlite`
2. `generate_report.py` queries the DB for topic counts per week → builds a trend table
3. Pass the trend table (not raw abstracts) to LLM for narrative synthesis

**Benefits:**
- Exact trend numbers (not LLM estimates)
- Persistent topic labels enable long-term analysis (months, not just 4 weeks)
- Much smaller LLM prompt (structured table vs. full abstracts)

**New files:** `label_papers.py` (incremental labeler), schema addition to `index.sqlite`

---

## 3. Weekly Automation

Run the full pipeline (ingest + report) automatically.

**Option A — Windows Task Scheduler:**
```
ingest_openalex.py → generate_report.py
```
Schedule weekly on Monday morning.

**Option B — Simple batch script:**
```bat
cd C:\path\to\wireless-research-intel
python ingest_openalex.py
python generate_report.py --weeks 4
```

---

## 4. Personal Research Relevance Filter

Score each paper for relevance to current research focus (UAV mmWave beam codebook design) before building the payload.

**Approach:** keyword list in `private.env` or a small config file. Papers matching keywords get boosted (or exclusively selected) in the payload.

**Benefit:** report focuses on what matters most to Jingjia's current project, not just what's popular.

---

## 5. Obsidian Daily Note Integration

After writing the digest, append a link to it in today's daily note.

**Addition to `main()`:**
```python
daily_note = Path(os.getenv("DAILY_NOTES_DIR")) / f"{date_str}.md"
if daily_note.exists():
    with daily_note.open("a", encoding="utf-8") as f:
        f.write(f"\n- [[{date_str}-wireless-digest]] — weekly research digest\n")
```

**Config:** add `DAILY_NOTES_DIR=C:\path\to\your\obsidian\daily-notes` to `private.env`

---

## 6. Topic Taxonomy Persistence

Save the topic names the LLM generates each week to a running list. Use that list in the next week's prompt to encourage consistent naming — so `[[ISAC]]` doesn't become `[[Integrated Sensing and Communication]]` next week.

**Implementation:** write topic names to `resource/topic_registry.json` after each run; inject into the prompt as "preferred topic names."

---

## Priority Order

| # | Improvement | Effort | Impact |
|---|-------------|--------|--------|
| 1 | Larger payload | 5 min | Medium |
| 2 | Daily note integration | 30 min | High |
| 3 | Topic taxonomy persistence | 1 hr | High |
| 4 | Weekly automation | 1 hr | High |
| 5 | Relevance filter | 2 hr | High |
| 6 | Historical trend tracking | 1 day | Very high |
