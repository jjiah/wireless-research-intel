# Design: Local Web Dashboard

**Date:** 2026-02-27
**Status:** Approved

---

## Overview

A lightweight local web dashboard that lets you run the pipeline, configure settings, and manage venues from a browser — without editing files by hand. Runs at `http://localhost:5000` via a single `python dashboard.py` command.

---

## Stack

| Layer | Choice | Reason |
|-------|--------|--------|
| Web framework | Flask | Minimal, zero build step, fits a single-user personal tool |
| Frontend | Bootstrap 5 (CDN) + vanilla JS | No build toolchain; SSE works natively |
| Process execution | `subprocess.Popen` | Streams stdout/stderr line-by-line to browser |
| New dependency | `flask` only | Everything else is stdlib |

---

## File Structure

```
wireless-research-intel/
├── dashboard.py                  ← Flask app (new)
└── dashboard/
    └── templates/
        ├── base.html             ← Bootstrap 5 nav shell
        ├── index.html            ← Home / status
        ├── run.html              ← Pipeline runner + live log
        ├── settings.html         ← Env file editor
        └── venues.html           ← Venue list + add/remove
```

---

## Pages

### `/` — Home

- Reads `resource/last_run.json` → shows last ingest date or "Never"
- Shows `REPORT_DIR` path (from env) and number of reports in it
- Quick "Run Pipeline" button → navigates to `/run`

### `/run` — Run Pipeline

- "Start" button POSTs to `/run/start`, which spawns the subprocess
- SSE endpoint `/run/stream` streams combined stdout+stderr line by line
- Browser `EventSource` appends lines to a `<pre>` scrolling log
- "Running…" spinner while active; final exit code shown on completion
- Runs: `python ingest_openalex.py` then `python generate_report.py --weeks 4`
- Only one pipeline run at a time (second click ignored while running)

### `/settings` — Settings

- Reads `private.env` and `openalex.env` at page load
- Fields:
  - `SILICONFLOW_API_KEY` (`<input type="password">`)
  - `OPENALEX_API_KEY` (`<input type="password">`)
  - `OPENALEX_EMAIL` (`<input type="text">`)
  - `REPORT_DIR` (`<input type="text">`)
- POST to `/settings/save` writes back to the respective `.env` files
- Shows green "Saved" flash on success

### `/venues` — Venues

- Parses `sources.yaml` at page load using the existing `load_sources()` function from `ingest_openalex.py`
- Shows table: venue ID, name, type, OpenAlex source IDs
- **Remove** button per row (POST `/venues/remove/<venue_id>`) with JS confirm dialog
- **Add venue** form at bottom: id, name, type, openalex_source_ids (comma-separated)
  - POST to `/venues/add` — appends to `sources.yaml`
- Writes changes back to `sources.yaml` in the same YAML format

---

## SSE Design

```
Browser                         Flask
  |                               |
  |-- GET /run/stream ----------->|
  |                               | Popen(ingest_openalex.py)
  |<-- data: [line] -------------|
  |<-- data: [line] -------------|  ...
  |                               | Popen(generate_report.py)
  |<-- data: [line] -------------|
  |<-- data: [DONE:0] ----------->|  exit code
  |                               |
```

- Uses `threading` (no async needed): one thread per run, generator yields lines
- Global flag prevents concurrent runs
- `text/event-stream` response with `Cache-Control: no-cache`

---

## Security

- Flask bound to `127.0.0.1` only (`host="127.0.0.1"`)
- No authentication (personal single-user tool)
- API keys always rendered as `<input type="password">` (not shown in page source as plain text)
- `sources.yaml` writes are atomic (write to temp file, rename)

---

## How to Run

```bash
pip install flask
python dashboard.py
# → http://localhost:5000
```

Add to README under a `## Dashboard` section.

---

## Out of Scope

- Report viewer (reports go to Obsidian; reading them there is better)
- Authentication / HTTPS
- Docker / deployment
- Anything beyond `sources.yaml` venue management (no OpenAlex ID resolver UI)
