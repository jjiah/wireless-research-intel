# Design: Weekly Research Digest Generator
**Date:** 2026-02-27
**Status:** Approved

## Overview

A Python script that reads the last 4 weeks of paper metadata from `resource/by_publication_week/`, sends a structured prompt to the Claude API, and writes a Markdown research digest directly to the Obsidian vault at `E:\0 notebook\01 Resources\`.

---

## Files

```
wireless-research-intel/
├── generate_report.py          ← main script
├── templates/
│   └── report_template.md      ← canonical template (generated first; drives the prompt)
└── resource/by_publication_week/

Output → E:\0 notebook\01 Resources\YYYY-MM-DD-wireless-digest.md
```

No local report backup. Reports are written exclusively to the vault.

---

## Invocation

```bash
python generate_report.py            # default: last 4 weeks
python generate_report.py --weeks 8  # configurable
```

---

## Data Loading

1. Sort `by_publication_week/` folder names (ISO dates sort lexicographically).
2. Take the last N folders (default N=4).
3. **Anomalous batch cap:** any week with paper count > 3× median of the selected weeks is capped at 300 papers, sorted by `cited_by_count` descending.
4. Per-paper payload: `title` + first 150 words of `abstract` + `venue_id` + `cited_by_count`. All other fields stripped.
5. Token estimate: ~400 papers × ~180 tokens ≈ 72k input tokens (within 200k context limit).

---

## Prompt Design

- Single API call (system + user message).
- User message contains:
  - Compact JSONL block: one paper per line — `title | venue | week | cited_by_count | abstract_snippet`
  - Explicit instruction to produce the report following the template structure.
- Model: `claude-sonnet-4-6`

---

## Report Structure (per template)

```
# Wireless Research Digest — [date range]

## Summary
- N papers · W weeks · X venues
- 1-line characterization of the period

## Hot Topics
### 1. [Topic Name]
- **Core problem:**
- **Key methods:**
- **Representative results:**
- **Challenges & limitations:**
- **Representative papers:** [[Title 1]], [[Title 2]]

(8–12 topics total)

## Trend Signals
- Topics growing week-over-week (comparing first half vs second half of the window)

## Research Gaps
- 3–5 underexplored areas adjacent to hot topics, with reasoning

## Venue Breakdown
| Topic | TWC | JSAC | TCOM | TSP | CommMag | … |

## Suggested Reading
- [[Title]] — venue, N citations — *one-line why it matters*
(5–7 papers)
```

---

## Post-processing

After Claude returns the Markdown:
- Wrap topic names in `[[...]]` (wiki-links) for Obsidian graph connectivity.
- Write output to `E:\0 notebook\01 Resources\YYYY-MM-DD-wireless-digest.md`.

---

## Implementation Order

1. Create `templates/report_template.md` — the Markdown template.
2. Write `generate_report.py`:
   a. Data loader (week selection + anomaly cap)
   b. Payload builder (compact JSONL)
   c. Claude API call
   d. Post-processor (wiki-link injection)
   e. File writer (vault path)
