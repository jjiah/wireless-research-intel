# Three Improvements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement larger LLM payload, topic taxonomy persistence, and Windows Task Scheduler automation for the weekly research digest pipeline.

**Architecture:** All changes confined to `generate_report.py` (constants + 3 new functions + `main()` wiring), two new automation files (`run_pipeline.bat`, `automation/weekly_digest.xml`), and a README update. No new dependencies.

**Tech Stack:** Python 3.13, stdlib only (`re`, `json`, `pathlib`), Windows Task Scheduler XML

---

## Task 1: Larger Payload — bump default constants

**Files:**
- Modify: `generate_report.py:56` (truncate_abstract default), `generate_report.py:72-73` (build_payload call), `generate_report.py:26` (load_papers default)
- Test: `tests/test_generate_report.py`

### Step 1: Write failing tests for new defaults

Add to the end of `tests/test_generate_report.py`:

```python
def test_truncate_abstract_default_is_300_words():
    words = ["word"] * 350
    text = " ".join(words)
    result = truncate_abstract(text)  # uses default max_words
    assert len(result.split()) == 300  # 300 words, last "word..." appended


def test_load_papers_default_cap_is_500(tmp_path):
    # anomalous week triggers cap — verify default cap is 500 not 300
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=i) for i in range(10)])
    anomalous = make_week(tmp_path, "2025-01-13", [sample_paper(cited=i) for i in range(600)])
    result = load_papers([normal, anomalous])  # uses default cap_count
    # normal (10) + capped anomalous (500)
    assert len(result) == 510
```

### Step 2: Run to confirm they fail

```bash
pytest tests/test_generate_report.py::test_truncate_abstract_default_is_300_words tests/test_generate_report.py::test_load_papers_default_cap_is_500 -v
```

Expected: both FAIL (defaults are currently 150 and 300).

### Step 3: Change the defaults in `generate_report.py`

In `truncate_abstract` (line 56), change:
```python
def truncate_abstract(abstract: str, max_words: int = 150) -> str:
```
to:
```python
def truncate_abstract(abstract: str, max_words: int = 300) -> str:
```

In `build_payload` (lines 72-73), change:
```python
        abstract = truncate_abstract(
            (p.get("abstract") or "").replace("|", "/"), max_words=150
        )
```
to:
```python
        abstract = truncate_abstract(
            (p.get("abstract") or "").replace("|", "/"), max_words=300
        )
```

In `load_papers` (line 26), change:
```python
def load_papers(
    week_dirs: list[Path],
    cap_multiplier: float = 3.0,
    cap_count: int = 300,
) -> list[dict]:
```
to:
```python
def load_papers(
    week_dirs: list[Path],
    cap_multiplier: float = 3.0,
    cap_count: int = 500,
) -> list[dict]:
```

### Step 4: Run the full test suite

```bash
pytest tests/test_generate_report.py -v
```

Expected: all tests PASS (existing tests pass explicit values, so they are unaffected).

### Step 5: Commit

```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: increase payload defaults to 300-word abstracts and 500-paper cap"
```

---

## Task 2: Topic taxonomy persistence — three new functions

**Files:**
- Modify: `generate_report.py`
- Test: `tests/test_generate_report.py`

Three functions to add: `load_topic_registry`, `extract_topics_from_markdown`, `update_topic_registry`.
Then wire them into `call_llm` (inject preferred names) and `main()` (save after run).

### Step 1: Write failing tests

Add to `tests/test_generate_report.py`:

```python
from generate_report import (
    load_topic_registry,
    extract_topics_from_markdown,
    update_topic_registry,
)


# --- load_topic_registry ---

def test_load_topic_registry_returns_empty_when_missing(tmp_path):
    result = load_topic_registry(tmp_path / "topic_registry.json")
    assert result == []


def test_load_topic_registry_returns_list(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC", "Beamforming"], "updated": "2026-02-27"}')
    assert load_topic_registry(path) == ["ISAC", "Beamforming"]


def test_load_topic_registry_ignores_corrupt_file(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text("not json")
    assert load_topic_registry(path) == []


# --- extract_topics_from_markdown ---

def test_extract_topics_finds_wiki_link_headings():
    md = "### 1. [[ISAC]]\n### 2. [[Beamforming]]\n## Other Section"
    result = extract_topics_from_markdown(md)
    assert result == ["ISAC", "Beamforming"]


def test_extract_topics_returns_empty_when_no_matches():
    md = "## Summary\nNo topic headings here."
    assert extract_topics_from_markdown(md) == []


def test_extract_topics_ignores_non_numbered_headings():
    md = "### [[Not Numbered]]\n### 1. [[ISAC]]"
    result = extract_topics_from_markdown(md)
    assert result == ["ISAC"]


# --- update_topic_registry ---

def test_update_topic_registry_creates_file(tmp_path):
    path = tmp_path / "topic_registry.json"
    update_topic_registry(path, ["ISAC", "RIS"])
    assert path.exists()
    data = json.loads(path.read_text())
    assert "ISAC" in data["topics"]
    assert "RIS" in data["topics"]


def test_update_topic_registry_merges_with_existing(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC"], "updated": "2026-01-01"}')
    update_topic_registry(path, ["RIS", "Beamforming"])
    data = json.loads(path.read_text())
    assert data["topics"] == ["ISAC", "RIS", "Beamforming"]


def test_update_topic_registry_deduplicates(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC"], "updated": "2026-01-01"}')
    update_topic_registry(path, ["ISAC", "RIS"])
    data = json.loads(path.read_text())
    assert data["topics"].count("ISAC") == 1
```

### Step 2: Run to confirm they fail

```bash
pytest tests/test_generate_report.py -k "topic_registry or extract_topics or update_topic" -v
```

Expected: all FAIL with ImportError or similar.

### Step 3: Add three functions to `generate_report.py`

Add after the `inject_wiki_links` function (line 86) and before `write_report`:

```python
def load_topic_registry(path: Path) -> list[str]:
    """Return saved topic names from topic_registry.json, or [] if absent/corrupt."""
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("topics") or []
    except Exception:
        return []


def extract_topics_from_markdown(markdown: str) -> list[str]:
    """Parse topic names from ### N. [[Topic]] headings in LLM output."""
    return re.findall(r"### \d+\.\s+\[\[(.+?)\]\]", markdown)


def update_topic_registry(path: Path, new_topics: list[str]) -> None:
    """Merge new_topics into registry JSON (exact-string dedup, order-preserving)."""
    existing = load_topic_registry(path)
    merged = list(dict.fromkeys(existing + new_topics))
    data = {"topics": merged, "updated": datetime.now().strftime("%Y-%m-%d")}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
```

### Step 4: Run the new tests

```bash
pytest tests/test_generate_report.py -k "topic_registry or extract_topics or update_topic" -v
```

Expected: all PASS.

### Step 5: Wire preferred_topics into `call_llm`

Change the `call_llm` signature (line 97) from:
```python
def call_llm(payload: str, template: str, weeks: int, api_key: str) -> str:
```
to:
```python
def call_llm(payload: str, template: str, weeks: int, api_key: str, preferred_topics: list[str] | None = None) -> str:
```

In the user message, change the guidelines block ending from:
```python
        "- Replace all {{PLACEHOLDERS}} with real content from the papers"
```
to:
```python
        "- Replace all {{PLACEHOLDERS}} with real content from the papers"
        + (
            f"\n- Prefer these previously used topic names when appropriate: {', '.join(preferred_topics)}"
            if preferred_topics
            else ""
        )
```

### Step 6: Wire registry into `main()`

In `main()`, after the `resource_dir` and `weeks_dir` setup lines, add:

```python
    registry_path = resource_dir / "topic_registry.json"
    preferred_topics = load_topic_registry(registry_path)
    if preferred_topics:
        print(f"  Using {len(preferred_topics)} preferred topic names from registry")
```

Change the `call_llm` call from:
```python
    markdown = call_llm(payload, template, args.weeks, api_key)
```
to:
```python
    markdown = call_llm(payload, template, args.weeks, api_key, preferred_topics or None)
```

After `markdown = inject_wiki_links(markdown)`, add:

```python
    new_topics = extract_topics_from_markdown(markdown)
    if new_topics:
        update_topic_registry(registry_path, new_topics)
        print(f"  Topic registry updated ({len(new_topics)} topics found)")
```

### Step 7: Run full test suite

```bash
pytest tests/test_generate_report.py -v
```

Expected: all tests PASS.

### Step 8: Commit

```bash
git add generate_report.py tests/test_generate_report.py
git commit -m "feat: add topic taxonomy persistence for consistent topic naming across runs"
```

---

## Task 3: Weekly automation — bat script + Task Scheduler XML + README

**Files:**
- Create: `run_pipeline.bat`
- Create: `automation/weekly_digest.xml`
- Modify: `README.md`

No tests needed for these (they are configuration files).

### Step 1: Create `run_pipeline.bat`

Create file at repo root:

```bat
@echo off
REM Weekly wireless research digest pipeline
REM Run manually or via Windows Task Scheduler (see automation/weekly_digest.xml)

cd /d E:\59357\Documents\GitHub\wireless-research-intel

echo [%DATE% %TIME%] Starting ingest...
python ingest_openalex.py
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: ingest_openalex.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Generating report...
python generate_report.py --weeks 4
if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERROR: generate_report.py failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Pipeline complete.
```

### Step 2: Create `automation/weekly_digest.xml`

Create `automation/` directory, then create `automation/weekly_digest.xml`:

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Weekly wireless research digest: ingest OpenAlex papers and generate Obsidian report.</Description>
    <URI>\wireless-research-intel\weekly-digest</URI>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-03-02T08:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <WeeksInterval>1</WeeksInterval>
        <DaysOfWeek>
          <Monday />
        </DaysOfWeek>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Enabled>true</Enabled>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>E:\59357\Documents\GitHub\wireless-research-intel\run_pipeline.bat</Command>
      <WorkingDirectory>E:\59357\Documents\GitHub\wireless-research-intel</WorkingDirectory>
    </Exec>
  </Actions>
  <Principals>
    <Principal id="Author">
      <LogonType>Password</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
</Task>
```

> **Note on `StartWhenAvailable`:** If Monday 08:00 is missed (computer off), the task runs as soon as the computer is on and network is available.

### Step 3: Add Automation section to `README.md`

Append to the end of `README.md`:

```markdown
## Automation

To run the full pipeline (ingest + report) automatically every Monday at 08:00:

1. Open **Task Scheduler** (search in Start menu).
2. Click **Action → Import Task…**
3. Select `automation/weekly_digest.xml` from this repo.
4. Enter your Windows account password when prompted.
5. The task appears under `\wireless-research-intel\weekly-digest`.

If your computer is off at 08:00, the task runs on next startup (requires network).

To run manually at any time:
```bat
run_pipeline.bat
```
```

### Step 4: Verify files look correct

```bash
cat run_pipeline.bat
cat automation/weekly_digest.xml
```

### Step 5: Commit

```bash
git add run_pipeline.bat automation/weekly_digest.xml README.md
git commit -m "feat: add weekly automation via Windows Task Scheduler"
```

---

## Final: Run full test suite and confirm clean state

```bash
pytest tests/test_generate_report.py -v
git status
```

Expected:
- All tests pass
- Working tree clean
