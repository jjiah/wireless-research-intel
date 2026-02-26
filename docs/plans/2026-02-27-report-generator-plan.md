# Research Digest Generator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build `generate_report.py` that reads the last N weeks of paper metadata, calls the SiliconFlow API (GLM-5) to produce a structured research digest, and writes a Markdown report to the Obsidian vault.

**Architecture:** Single-pass LLM synthesis — load papers from `resource/by_publication_week/`, build a compact JSONL payload, call `Pro/zai-org/GLM-5` via SiliconFlow's OpenAI-compatible API with a structured prompt based on `templates/report_template.md`, post-process the response to inject Obsidian wiki-links, write to `REPORT_DIR` (already set in `private.env`).

**Tech Stack:** Python 3.13, `openai` SDK (OpenAI-compatible, pointed at SiliconFlow), `pytest` 9.0.2, `pathlib`, `json`, `re`, `statistics`. No other dependencies.

---

## Task 1: Install openai package and add SiliconFlow API key

**Files:**
- Modify: `private.env`

**Step 1: Install openai**
```bash
pip install openai
```
Expected: `Successfully installed openai-...`

**Step 2: Verify**
```bash
python -c "import openai; print(openai.__version__)"
```
Expected: prints a version number like `1.x.x`

**Step 3: Add your SiliconFlow API key to private.env**

Open `private.env` and add this line:
```
SILICONFLOW_API_KEY=your_key_here
```
The file should now look like:
```
REPORT_DIR=E:\0 notebook\01 Resources
SILICONFLOW_API_KEY=sk-...
```

**Step 4: Commit**
```bash
git add -p private.env   # verify no secrets staged accidentally
```
> ⚠️ `private.env` is already gitignored (do not commit it). Skip the commit for this task.

---

## Task 2: Create report_template.md

**Files:**
- Create: `templates/report_template.md`

**Step 1: Create the templates directory and file**

Create `templates/report_template.md` with this exact content:

```markdown
# Wireless Research Digest — {{DATE_RANGE}}

## Summary
- **Papers:** {{TOTAL_PAPERS}} across {{NUM_WEEKS}} weeks ({{DATE_RANGE}})
- **Venues:** {{NUM_VENUES}} venues covered
- {{ONE_LINE_CHARACTERIZATION}}

## Hot Topics

### 1. {{TOPIC_NAME}}
- **Papers this period:** {{COUNT}} | **Venues:** {{VENUES}}
- **Core problem:** {{CORE_PROBLEM}}
- **Key methods:** {{KEY_METHODS}}
- **Representative results:** {{RESULTS}}
- **Challenges & limitations:** {{CHALLENGES}}
- **Representative papers:** {{PAPER_1}}, {{PAPER_2}}, {{PAPER_3}}

---

*(Repeat for 8–12 topics total, numbered sequentially)*

## Trend Signals
- **{{TOPIC}}:** ↑ rising — {{FIRST_HALF_COUNT}} papers in first half → {{SECOND_HALF_COUNT}} in second half
- **{{TOPIC}}:** → stable across the period
- **{{TOPIC}}:** ↓ declining — {{FIRST_HALF_COUNT}} → {{SECOND_HALF_COUNT}}

*(List all notable trends; omit topics with flat counts)*

## Research Gaps
- **{{GAP_TOPIC}}:** {{REASONING_GROUNDED_IN_PAPER_CONTENT}}

*(3–5 gaps; each must name adjacent hot topics that make this a gap)*

## Venue Breakdown

| Topic | TWC | JSAC | TCOM | TSP | WCL | CommMag | ICC | GLOBECOM | TVT | VTC |
|-------|-----|------|------|-----|-----|---------|-----|----------|-----|-----|
| {{TOPIC}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} | {{N}} |

## Suggested Reading
- **{{TITLE}}** — {{VENUE}}, {{CITATIONS}} citations — *{{ONE_LINE_WHY_IT_MATTERS}}*

*(5–7 papers; prioritise highest cited_by_count; commentary must be specific)*
```

**Step 2: Commit**
```bash
git add templates/report_template.md
git commit -m "feat: add report template"
```
Expected: `1 file changed`

---

## Task 3: Data loader — load_weeks and load_papers

**Files:**
- Create: `tests/test_generate_report.py` (loader section)
- Create: `generate_report.py` (loader functions only)

**Step 1: Create tests/test_generate_report.py with loader tests**

```python
# tests/test_generate_report.py
import json
import pytest
from pathlib import Path
from generate_report import load_weeks, load_papers


def make_week(tmp_path: Path, name: str, papers: list[dict]) -> Path:
    week_dir = tmp_path / name
    week_dir.mkdir()
    for i, paper in enumerate(papers):
        (week_dir / f"paper_{i}.json").write_text(json.dumps(paper), encoding="utf-8")
    return week_dir


def sample_paper(cited: int = 10) -> dict:
    return {
        "title": "Test Paper",
        "venue_id": "ieee_twc",
        "published": "2025-02-10",
        "cited_by_count": cited,
        "abstract": "This is a test abstract with some words in it.",
    }


# --- load_weeks ---

def test_load_weeks_returns_last_n(tmp_path):
    weeks_dir = tmp_path / "by_publication_week"
    weeks_dir.mkdir()
    for name in ["2025-01-06", "2025-01-13", "2025-01-20", "2025-01-27"]:
        (weeks_dir / name).mkdir()
    result = load_weeks(weeks_dir, n=2)
    assert [d.name for d in result] == ["2025-01-20", "2025-01-27"]


def test_load_weeks_returns_all_if_fewer_than_n(tmp_path):
    weeks_dir = tmp_path / "by_publication_week"
    weeks_dir.mkdir()
    (weeks_dir / "2025-01-06").mkdir()
    result = load_weeks(weeks_dir, n=4)
    assert len(result) == 1


def test_load_weeks_returns_empty_if_dir_missing(tmp_path):
    result = load_weeks(tmp_path / "nonexistent", n=4)
    assert result == []


# --- load_papers ---

def test_load_papers_loads_all_jsons(tmp_path):
    week = make_week(tmp_path, "2025-01-06", [sample_paper(), sample_paper()])
    result = load_papers([week])
    assert len(result) == 2


def test_load_papers_caps_anomalous_week(tmp_path):
    # Normal week: 10 papers; anomalous week: 400 papers (> 3x median)
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=i) for i in range(10)])
    anomalous = make_week(tmp_path, "2025-01-13", [sample_paper(cited=i) for i in range(400)])
    result = load_papers([normal, anomalous], cap_count=300)
    # Normal week uncapped (10), anomalous week capped at 300
    assert len(result) == 310


def test_load_papers_cap_selects_highest_cited(tmp_path):
    papers = [sample_paper(cited=i) for i in range(400)]
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=5)] * 10)
    anomalous = make_week(tmp_path, "2025-01-13", papers)
    result = load_papers([normal, anomalous], cap_count=300)
    anomalous_results = [p for p in result if p["cited_by_count"] >= 0]
    # All 300 from the anomalous week should be the top 300 by citation
    anomalous_citations = sorted(
        [p["cited_by_count"] for p in result if p not in [sample_paper(cited=5)] * 10],
        reverse=True,
    )
    assert anomalous_citations[0] == 399  # highest cited included


def test_load_papers_does_not_cap_normal_week(tmp_path):
    week = make_week(tmp_path, "2025-01-06", [sample_paper() for _ in range(90)])
    result = load_papers([week])
    assert len(result) == 90
```

**Step 2: Run tests — verify they all FAIL**
```bash
cd E:/59357/Documents/GitHub/wireless-research-intel
pytest tests/test_generate_report.py -v -k "loader or load_weeks or load_papers"
```
Expected: `ERROR` (ImportError — generate_report.py does not exist yet)

**Step 3: Create generate_report.py with loader functions**

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
from pathlib import Path


def load_weeks(weeks_dir: Path, n: int) -> list[Path]:
    """Return the last n week directories, sorted by name."""
    if not weeks_dir.exists():
        return []
    dirs = sorted([d for d in weeks_dir.iterdir() if d.is_dir()])
    return dirs[-n:] if len(dirs) >= n else dirs


def load_papers(
    week_dirs: list[Path],
    cap_multiplier: float = 3.0,
    cap_count: int = 300,
) -> list[dict]:
    """Load all papers from week dirs; cap anomalous weeks by citation rank."""
    week_papers: list[list[dict]] = []
    for week_dir in week_dirs:
        papers = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(week_dir.glob("*.json"))
        ]
        week_papers.append(papers)

    counts = [len(w) for w in week_papers]
    threshold = (statistics.median(counts) * cap_multiplier) if len(counts) >= 2 else float("inf")

    result: list[dict] = []
    for papers in week_papers:
        if len(papers) > threshold and len(papers) > cap_count:
            papers = sorted(
                papers,
                key=lambda p: p.get("cited_by_count") or 0,
                reverse=True,
            )[:cap_count]
        result.extend(papers)
    return result
```

**Step 4: Run tests — verify they PASS**
```bash
pytest tests/test_generate_report.py -v -k "load_weeks or load_papers"
```
Expected: all loader tests `PASSED`

**Step 5: Commit**
```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: add data loader with anomaly cap"
```

---

## Task 4: Payload builder — truncate_abstract and build_payload

**Files:**
- Modify: `tests/test_generate_report.py` (append builder tests)
- Modify: `generate_report.py` (append builder functions)

**Step 1: Append these tests to tests/test_generate_report.py**

```python
from generate_report import truncate_abstract, build_payload


# --- truncate_abstract ---

def test_truncate_short_abstract_unchanged():
    text = "Short abstract here."
    assert truncate_abstract(text, max_words=150) == text


def test_truncate_long_abstract():
    words = ["word"] * 200
    text = " ".join(words)
    result = truncate_abstract(text, max_words=150)
    assert result.endswith("...")
    assert len(result.split()) == 151  # 150 words + "..."


# --- build_payload ---

def test_build_payload_produces_jsonl():
    papers = [
        {
            "title": "My Paper",
            "venue_id": "ieee_twc",
            "published": "2025-02-10",
            "cited_by_count": 42,
            "abstract": "Some abstract text.",
        }
    ]
    result = build_payload(papers)
    assert "My Paper" in result
    assert "ieee_twc" in result
    assert "42" in result
    assert "2025-02" in result


def test_build_payload_replaces_pipes_in_title():
    papers = [
        {
            "title": "Paper A | Paper B",
            "venue_id": "ieee_twc",
            "published": "2025-02-10",
            "cited_by_count": 0,
            "abstract": "Abstract.",
        }
    ]
    result = build_payload(papers)
    lines = result.strip().split("\n")
    fields = lines[0].split(" | ")
    assert "|" not in fields[0]  # title field has no stray pipes
```

**Step 2: Run tests — verify they FAIL**
```bash
pytest tests/test_generate_report.py -v -k "truncate or build_payload"
```
Expected: `ImportError` — functions not defined yet

**Step 3: Append to generate_report.py**

```python
def truncate_abstract(abstract: str, max_words: int = 150) -> str:
    """Return first max_words words of abstract, with ellipsis if truncated."""
    words = abstract.split()
    if len(words) <= max_words:
        return abstract
    return " ".join(words[:max_words]) + "..."


def build_payload(papers: list[dict]) -> str:
    """Build compact pipe-delimited JSONL payload for the LLM prompt."""
    lines: list[str] = []
    for p in papers:
        title = (p.get("title") or "").replace("|", "/")
        venue = p.get("venue_id") or "unknown"
        week = (p.get("published") or "")[:7]  # YYYY-MM
        citations = p.get("cited_by_count") or 0
        abstract = truncate_abstract(
            (p.get("abstract") or "").replace("|", "/"), max_words=150
        )
        lines.append(f"{title} | {venue} | {week} | {citations} | {abstract}")
    return "\n".join(lines)
```

**Step 4: Run tests — verify they PASS**
```bash
pytest tests/test_generate_report.py -v -k "truncate or build_payload"
```
Expected: all builder tests `PASSED`

**Step 5: Commit**
```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: add payload builder"
```

---

## Task 5: Post-processor — inject_wiki_links

**Files:**
- Modify: `tests/test_generate_report.py` (append post-processor tests)
- Modify: `generate_report.py` (append post-processor function)

**Step 1: Append these tests**

```python
from generate_report import inject_wiki_links


# --- inject_wiki_links ---

def test_inject_wiki_links_wraps_topic_headings():
    md = "### 1. Integrated Sensing and Communication\nsome content"
    result = inject_wiki_links(md)
    assert "### 1. [[Integrated Sensing and Communication]]" in result


def test_inject_wiki_links_ignores_other_headings():
    md = "## Summary\n### 1. My Topic\n## Trend Signals"
    result = inject_wiki_links(md)
    assert "## Summary" in result
    assert "## Trend Signals" in result
    assert "[[My Topic]]" in result


def test_inject_wiki_links_handles_multiple_topics():
    md = "### 1. Topic A\n### 2. Topic B\n### 3. Topic C"
    result = inject_wiki_links(md)
    assert "[[Topic A]]" in result
    assert "[[Topic B]]" in result
    assert "[[Topic C]]" in result
```

**Step 2: Run tests — verify they FAIL**
```bash
pytest tests/test_generate_report.py -v -k "wiki"
```
Expected: `ImportError`

**Step 3: Append to generate_report.py**

```python
import re


def inject_wiki_links(markdown: str) -> str:
    """Wrap topic headings (### N. Topic) in Obsidian [[wiki-links]]."""
    return re.sub(r"(### \d+\.\s+)(.+)", r"\1[[\2]]", markdown)
```

> Note: add `import re` at the top of the file with the other imports.

**Step 4: Run tests — verify they PASS**
```bash
pytest tests/test_generate_report.py -v -k "wiki"
```
Expected: all post-processor tests `PASSED`

**Step 5: Commit**
```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: add wiki-link post-processor"
```

---

## Task 6: File writer — write_report

**Files:**
- Modify: `tests/test_generate_report.py` (append writer tests)
- Modify: `generate_report.py` (append writer function)

**Step 1: Append these tests**

```python
from generate_report import write_report


# --- write_report ---

def test_write_report_creates_file(tmp_path):
    path = write_report("# Report", tmp_path, "2026-02-27")
    assert path.exists()
    assert path.name == "2026-02-27-wireless-digest.md"


def test_write_report_creates_parent_dir(tmp_path):
    out_dir = tmp_path / "nested" / "dir"
    write_report("# Report", out_dir, "2026-02-27")
    assert out_dir.exists()


def test_write_report_content_correct(tmp_path):
    content = "# My Report\nSome content."
    path = write_report(content, tmp_path, "2026-02-27")
    assert path.read_text(encoding="utf-8") == content
```

**Step 2: Run tests — verify they FAIL**
```bash
pytest tests/test_generate_report.py -v -k "write_report"
```
Expected: `ImportError`

**Step 3: Append to generate_report.py**

```python
def write_report(content: str, output_dir: Path, date_str: str) -> Path:
    """Write the report Markdown to output_dir/YYYY-MM-DD-wireless-digest.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{date_str}-wireless-digest.md"
    path.write_text(content, encoding="utf-8")
    return path
```

**Step 4: Run tests — verify they PASS**
```bash
pytest tests/test_generate_report.py -v -k "write_report"
```
Expected: all writer tests `PASSED`

**Step 5: Run the full test suite**
```bash
pytest tests/test_generate_report.py -v
```
Expected: all tests `PASSED`

**Step 6: Commit**
```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: add report file writer"
```

---

## Task 7: Wire up LLM call and CLI entrypoint

**Files:**
- Modify: `generate_report.py` (add imports, call_llm, main)

**Step 1: Add imports at the top of generate_report.py**

Replace the existing imports block with:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path
```

**Step 2: Append call_llm to generate_report.py**

```python
def call_llm(payload: str, template: str, weeks: int, api_key: str) -> str:
    """Call SiliconFlow GLM-5 with the paper payload and return Markdown."""
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1",
    )

    system = (
        "You are a research analyst specialising in wireless communications. "
        "You analyse paper metadata and produce structured research digests. "
        "Be factual and ground every claim in the provided paper abstracts."
    )

    user = (
        f"Here are papers from the past {weeks} weeks across IEEE wireless communications venues.\n"
        "Format per line: title | venue_id | year-month | citation_count | abstract_snippet\n\n"
        "--- PAPERS ---\n"
        f"{payload}\n"
        "--- END PAPERS ---\n\n"
        "Produce a research digest following this exact template structure:\n\n"
        f"{template}\n\n"
        "Guidelines:\n"
        "- Identify 8-12 distinct research topics clustered from the papers above\n"
        "- Each topic subsection must cite specific evidence from the paper abstracts\n"
        "- Trend signals: compare paper counts in the first half vs second half of the window\n"
        "- Research gaps: areas adjacent to hot topics with few or no papers\n"
        "- Suggested reading: highest cited_by_count papers with specific one-line rationale\n"
        "- Output plain Markdown only; do not add [[wiki-links]] (added in post-processing)\n"
        "- Replace all {{PLACEHOLDERS}} with real content from the papers"
    )

    response = client.chat.completions.create(
        model="Pro/zai-org/GLM-5",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=8192,
    )
    return response.choices[0].message.content
```

**Step 3: Append load_env_file and main to generate_report.py**

```python
def load_env_file(path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"' ")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate wireless research digest.")
    parser.add_argument("--weeks", type=int, default=4, help="Number of recent weeks to analyse")
    parser.add_argument("--resource-dir", default="resource", help="Path to resource folder")
    args = parser.parse_args()

    load_env_file(Path("openalex.env"))
    load_env_file(Path("private.env"))

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("Missing SILICONFLOW_API_KEY in private.env", file=sys.stderr)
        sys.exit(1)

    report_dir = Path(os.getenv("REPORT_DIR", "reports"))

    resource_dir = Path(args.resource_dir)
    weeks_dir = resource_dir / "by_publication_week"

    print(f"Loading last {args.weeks} weeks from {weeks_dir}...")
    week_dirs = load_weeks(weeks_dir, args.weeks)
    if not week_dirs:
        print("No week folders found.", file=sys.stderr)
        sys.exit(1)

    date_range = f"{week_dirs[0].name} → {week_dirs[-1].name}"
    print(f"  Weeks: {date_range}")

    papers = load_papers(week_dirs)
    print(f"  {len(papers)} papers loaded")

    payload = build_payload(papers)

    template_path = Path("templates/report_template.md")
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    template = template_path.read_text(encoding="utf-8")

    print("Calling SiliconFlow GLM-5...")
    markdown = call_llm(payload, template, args.weeks, api_key)

    markdown = inject_wiki_links(markdown)

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = write_report(markdown, report_dir, date_str)
    print(f"Report written → {out_path}")


if __name__ == "__main__":
    main()
```

**Step 4: Run full test suite to confirm nothing broken**
```bash
pytest tests/test_generate_report.py -v
```
Expected: all tests `PASSED`

**Step 5: Commit**
```bash
git add generate_report.py
git commit -m "feat: wire up SiliconFlow GLM-5 call and CLI entrypoint"
```

---

## Task 8: Smoke test end-to-end

**Step 1: Add SILICONFLOW_API_KEY to private.env if not done in Task 1**

**Step 2: Run the script**
```bash
cd E:/59357/Documents/GitHub/wireless-research-intel
python generate_report.py --weeks 4
```
Expected output:
```
Loading last 4 weeks from resource/by_publication_week...
  Weeks: 2025-12-15 → 2026-01-26
  NNN papers loaded
Calling SiliconFlow GLM-5...
Report written → E:\0 notebook\01 Resources\2026-02-27-wireless-digest.md
```

**Step 3: Open the report in Obsidian and verify**
- [ ] All 8–12 topic headings have `[[wiki-links]]`
- [ ] Each topic has: Core problem, Key methods, Results, Challenges, Representative papers
- [ ] Trend Signals section present
- [ ] Research Gaps section present
- [ ] Venue Breakdown table present
- [ ] Suggested Reading section present

**Step 4: Final commit**
```bash
git add .
git commit -m "feat: research digest generator complete"
```
