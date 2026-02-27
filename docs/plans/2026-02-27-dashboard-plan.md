# Local Web Dashboard Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local Flask web dashboard at `http://localhost:5000` to run the pipeline, configure settings, and manage venues without editing files by hand.

**Architecture:** Single `dashboard.py` at repo root; templates in `dashboard/templates/`. Module-level path constants (`REPO_DIR`, `PRIVATE_ENV_PATH`, etc.) make all routes trivially patchable in tests. SSE streams subprocess stdout live to the browser via `EventSource`. No JS framework — Bootstrap 5 CDN + ~20 lines of vanilla JS total.

**Tech Stack:** Python 3.13, Flask, Bootstrap 5 (CDN), vanilla JS `EventSource`

---

## Setup: Install Flask

```bash
cd "e:\59357\Documents\GitHub\wireless-research-intel"
pip install flask
```

Verify:
```bash
python -c "import flask; print(flask.__version__)"
```

Then create `requirements.txt`:
```
flask
```

```bash
git add requirements.txt
git commit -m "chore: add requirements.txt with flask"
```

---

## Task 1: Flask skeleton + helpers + home page

**Files:**
- Create: `dashboard.py`
- Create: `dashboard/templates/base.html`
- Create: `dashboard/templates/index.html`
- Create: `tests/test_dashboard.py`

### Step 1: Write failing tests

Create `tests/test_dashboard.py`:

```python
# tests/test_dashboard.py
import json
import pytest
from pathlib import Path


@pytest.fixture
def patched_app(tmp_path, monkeypatch):
    import dashboard
    monkeypatch.setattr(dashboard, "REPO_DIR", tmp_path)
    monkeypatch.setattr(dashboard, "PRIVATE_ENV_PATH", tmp_path / "private.env")
    monkeypatch.setattr(dashboard, "OPENALEX_ENV_PATH", tmp_path / "openalex.env")
    monkeypatch.setattr(dashboard, "SOURCES_PATH", tmp_path / "sources.yaml")
    monkeypatch.setattr(dashboard, "_pipeline_running", False)
    dashboard.app.config["TESTING"] = True
    return dashboard.app, tmp_path


@pytest.fixture
def client(patched_app):
    app, _ = patched_app
    return app.test_client()


@pytest.fixture
def app_tmp(patched_app):
    _, tmp = patched_app
    return tmp


# ── home page ──────────────────────────────────────────────────────────────

def test_home_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_home_shows_never_when_no_last_run(client):
    resp = client.get("/")
    assert b"Never" in resp.data


def test_home_shows_last_run_date(client, app_tmp):
    (app_tmp / "resource").mkdir()
    (app_tmp / "resource" / "last_run.json").write_text(
        '{"last_run_date": "2026-02-20"}', encoding="utf-8"
    )
    resp = client.get("/")
    assert b"2026-02-20" in resp.data
```

### Step 2: Run to confirm they fail

```bash
cd "e:\59357\Documents\GitHub\wireless-research-intel"
python -m pytest tests/test_dashboard.py -v
```

Expected: `ImportError: No module named 'dashboard'` (or similar).

### Step 3: Create `dashboard.py`

```python
#!/usr/bin/env python3
"""Local web dashboard for wireless-research-intel.

Run:
    python dashboard.py
    # then open http://localhost:5000
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from pathlib import Path

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)

# ── path constants (monkeypatched in tests) ───────────────────────────────────
REPO_DIR = Path(__file__).parent
PRIVATE_ENV_PATH = REPO_DIR / "private.env"
OPENALEX_ENV_PATH = REPO_DIR / "openalex.env"
SOURCES_PATH = REPO_DIR / "sources.yaml"

app = Flask(__name__, template_folder="dashboard/templates")
app.secret_key = "local-dashboard-dev-key"  # safe: localhost only

_pipeline_running = False
_pipeline_lock = threading.Lock()

# ── helpers ──────────────────────────────────────────────────────────────────

def load_env_file(path: Path) -> dict[str, str]:
    """Parse key=value lines from a .env file, return as dict."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        result[key.strip()] = value.strip().strip("\"' ")
    return result


def save_env_file(path: Path, data: dict[str, str]) -> None:
    """Write key=value lines to a .env file (skips empty values)."""
    lines = [f"{k}={v}\n" for k, v in data.items() if v]
    path.write_text("".join(lines), encoding="utf-8")


def parse_sources_yaml(path: Path) -> dict:
    """Parse sources.yaml, preserving header and all venue fields.

    Returns {"header": {...}, "venues": [{"id": ..., "name": ..., ...}, ...]}
    """
    if not path.exists():
        return {"header": {}, "venues": []}
    header: dict[str, str] = {}
    venues: list[dict] = []
    current: dict | None = None
    in_venues = False
    in_ids = False
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not in_venues:
            if s.startswith("version:"):
                header["version"] = s.split(":", 1)[1].strip()
            elif s.startswith("updated_by:"):
                header["updated_by"] = s.split(":", 1)[1].strip().strip("\"'")
            elif s.startswith("notes:"):
                header["notes"] = s.split(":", 1)[1].strip().strip("\"'")
            elif s == "venues:":
                in_venues = True
        else:
            if s.startswith("- id:"):
                if current:
                    venues.append(current)
                current = {
                    "id": s.split(":", 1)[1].strip().strip("\"'"),
                    "openalex_source_ids": [],
                }
                in_ids = False
            elif current is not None:
                if s.startswith("name:"):
                    current["name"] = s.split(":", 1)[1].strip().strip("\"'")
                elif s.startswith("type:"):
                    current["type"] = s.split(":", 1)[1].strip().strip("\"'")
                elif s.startswith("publisher:"):
                    current["publisher"] = s.split(":", 1)[1].strip().strip("\"'")
                elif s == "openalex_source_ids:":
                    in_ids = True
                elif in_ids and s.startswith("- "):
                    val = s[1:].strip().strip("\"'")
                    if val:
                        current["openalex_source_ids"].append(val)
                elif in_ids and s and not s.startswith("- "):
                    in_ids = False
    if current:
        venues.append(current)
    return {"header": header, "venues": venues}


def serialize_sources_yaml(data: dict) -> str:
    """Serialize sources data back to YAML string, preserving all fields."""
    h = data.get("header", {})
    lines: list[str] = []
    if "version" in h:
        lines.append(f"version: {h['version']}\n")
    if "updated_by" in h:
        lines.append(f'updated_by: "{h["updated_by"]}"\n')
    if "notes" in h:
        lines.append(f'notes: "{h["notes"]}"\n')
    lines.append("venues:\n")
    for v in data.get("venues", []):
        lines.append(f'  - id: {v["id"]}\n')
        lines.append(f'    name: "{v.get("name", "")}"\n')
        if "type" in v:
            lines.append(f'    type: "{v["type"]}"\n')
        if "publisher" in v:
            lines.append(f'    publisher: "{v["publisher"]}"\n')
        lines.append(f"    openalex_source_ids:\n")
        for sid in v.get("openalex_source_ids", []):
            lines.append(f'      - "{sid}"\n')
    return "".join(lines)


# ── home ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    last_run = None
    last_run_path = REPO_DIR / "resource" / "last_run.json"
    if last_run_path.exists():
        try:
            data = json.loads(last_run_path.read_text(encoding="utf-8"))
            last_run = data.get("last_run_date")
        except Exception:
            pass
    private = load_env_file(PRIVATE_ENV_PATH)
    report_dir = Path(private.get("REPORT_DIR", str(REPO_DIR / "reports")))
    report_count = len(list(report_dir.glob("*.md"))) if report_dir.exists() else 0
    return render_template(
        "index.html",
        last_run=last_run,
        report_dir=report_dir,
        report_count=report_count,
    )


# ── settings placeholder (filled in Task 2) ──────────────────────────────────
# ── venues placeholder (filled in Task 3) ────────────────────────────────────
# ── run placeholder (filled in Task 4) ───────────────────────────────────────


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
```

### Step 4: Create `dashboard/templates/base.html`

First create the directory: `dashboard/templates/` (create `dashboard/__init__.py` is NOT needed — Flask uses it as a plain folder).

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}Wireless Intel{% endblock %}</title>
  <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold" href="/">Wireless Research Intel</a>
      <div class="navbar-nav flex-row gap-3 ms-auto">
        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">Home</a>
        <a class="nav-link {% if '/run' in request.path %}active{% endif %}" href="/run">Run Pipeline</a>
        <a class="nav-link {% if '/settings' in request.path %}active{% endif %}" href="/settings">Settings</a>
        <a class="nav-link {% if '/venues' in request.path %}active{% endif %}" href="/venues">Venues</a>
      </div>
    </div>
  </nav>
  <div class="container-fluid px-4">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for category, message in messages %}
        <div class="alert alert-{{ category }} alert-dismissible" role="alert">
          {{ message }}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      {% endfor %}
    {% endwith %}
    {% block content %}{% endblock %}
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### Step 5: Create `dashboard/templates/index.html`

```html
{% extends "base.html" %}
{% block title %}Home — Wireless Intel{% endblock %}
{% block content %}
<h2>Dashboard</h2>
<div class="row mt-3 g-3">
  <div class="col-md-4">
    <div class="card h-100">
      <div class="card-body">
        <h5 class="card-title text-muted">Last Ingest</h5>
        <p class="card-text fs-3 fw-semibold">{{ last_run or "Never" }}</p>
      </div>
    </div>
  </div>
  <div class="col-md-4">
    <div class="card h-100">
      <div class="card-body">
        <h5 class="card-title text-muted">Reports</h5>
        <p class="card-text fs-3 fw-semibold">
          {{ report_count }} digest{{ 's' if report_count != 1 else '' }}
        </p>
        <small class="text-muted font-monospace">{{ report_dir }}</small>
      </div>
    </div>
  </div>
</div>
<div class="mt-4">
  <a href="/run" class="btn btn-primary btn-lg">Run Pipeline Now</a>
</div>
{% endblock %}
```

### Step 6: Run the tests

```bash
cd "e:\59357\Documents\GitHub\wireless-research-intel"
python -m pytest tests/test_dashboard.py::test_home_returns_200 tests/test_dashboard.py::test_home_shows_never_when_no_last_run tests/test_dashboard.py::test_home_shows_last_run_date -v
```

Expected: all 3 PASS.

### Step 7: Run the full test suite (must still pass)

```bash
python -m pytest tests/ -v
```

Expected: all 32 + 3 = 35 tests pass.

### Step 8: Commit

```bash
git add dashboard.py dashboard/templates/base.html dashboard/templates/index.html tests/test_dashboard.py
git commit -m "feat: add Flask dashboard skeleton with home page"
```

---

## Task 2: Settings page

**Files:**
- Modify: `dashboard.py` (add settings routes)
- Create: `dashboard/templates/settings.html`
- Modify: `tests/test_dashboard.py` (add settings tests)

### Step 1: Write failing tests

Append to `tests/test_dashboard.py`:

```python
# ── settings page ─────────────────────────────────────────────────────────────

def test_settings_returns_200(client):
    resp = client.get("/settings")
    assert resp.status_code == 200


def test_settings_loads_env_values(client, app_tmp):
    (app_tmp / "private.env").write_text("SILICONFLOW_API_KEY=sk-test\nREPORT_DIR=C:\\reports\n", encoding="utf-8")
    (app_tmp / "openalex.env").write_text("OPENALEX_EMAIL=test@example.com\n", encoding="utf-8")
    resp = client.get("/settings")
    assert b"sk-test" in resp.data
    assert b"test@example.com" in resp.data


def test_settings_save_writes_env_files(client, app_tmp):
    resp = client.post("/settings/save", data={
        "SILICONFLOW_API_KEY": "new-key",
        "REPORT_DIR": "C:\\new-reports",
        "OPENALEX_API_KEY": "oalex-key",
        "OPENALEX_EMAIL": "user@example.com",
    }, follow_redirects=True)
    assert resp.status_code == 200
    private = (app_tmp / "private.env").read_text(encoding="utf-8")
    openalex = (app_tmp / "openalex.env").read_text(encoding="utf-8")
    assert "new-key" in private
    assert "C:\\new-reports" in private
    assert "oalex-key" in openalex
    assert "user@example.com" in openalex
```

### Step 2: Run to confirm they fail

```bash
python -m pytest tests/test_dashboard.py -k "settings" -v
```

Expected: FAIL (404 or AttributeError).

### Step 3: Add settings routes to `dashboard.py`

Replace the `# ── settings placeholder` comment with:

```python
# ── settings ──────────────────────────────────────────────────────────────────

_PRIVATE_KEYS = ("SILICONFLOW_API_KEY", "REPORT_DIR")
_OPENALEX_KEYS = ("OPENALEX_API_KEY", "OPENALEX_EMAIL")


@app.route("/settings")
def settings():
    private = load_env_file(PRIVATE_ENV_PATH)
    openalex = load_env_file(OPENALEX_ENV_PATH)
    return render_template("settings.html", private=private, openalex=openalex)


@app.route("/settings/save", methods=["POST"])
def settings_save():
    private = {k: request.form.get(k, "") for k in _PRIVATE_KEYS}
    openalex = {k: request.form.get(k, "") for k in _OPENALEX_KEYS}
    save_env_file(PRIVATE_ENV_PATH, private)
    save_env_file(OPENALEX_ENV_PATH, openalex)
    flash("Settings saved.", "success")
    return redirect(url_for("settings"))
```

### Step 4: Create `dashboard/templates/settings.html`

```html
{% extends "base.html" %}
{% block title %}Settings — Wireless Intel{% endblock %}
{% block content %}
<h2>Settings</h2>
<form method="post" action="/settings/save">

  <h5 class="mt-4 border-bottom pb-1">SiliconFlow <small class="text-muted fw-normal">(private.env)</small></h5>

  <div class="mb-3">
    <label class="form-label fw-semibold">SILICONFLOW_API_KEY</label>
    <input type="password" class="form-control font-monospace"
           name="SILICONFLOW_API_KEY"
           value="{{ private.get('SILICONFLOW_API_KEY', '') }}"
           autocomplete="off" placeholder="sk-...">
  </div>

  <div class="mb-3">
    <label class="form-label fw-semibold">REPORT_DIR</label>
    <input type="text" class="form-control font-monospace"
           name="REPORT_DIR"
           value="{{ private.get('REPORT_DIR', '') }}"
           placeholder="e.g. E:\0 notebook\01 Resources">
    <div class="form-text">Directory where weekly digest .md files are written.</div>
  </div>

  <h5 class="mt-4 border-bottom pb-1">OpenAlex <small class="text-muted fw-normal">(openalex.env)</small></h5>

  <div class="mb-3">
    <label class="form-label fw-semibold">OPENALEX_API_KEY</label>
    <input type="password" class="form-control font-monospace"
           name="OPENALEX_API_KEY"
           value="{{ openalex.get('OPENALEX_API_KEY', '') }}"
           autocomplete="off">
  </div>

  <div class="mb-3">
    <label class="form-label fw-semibold">OPENALEX_EMAIL</label>
    <input type="email" class="form-control"
           name="OPENALEX_EMAIL"
           value="{{ openalex.get('OPENALEX_EMAIL', '') }}"
           placeholder="your@email.com">
    <div class="form-text">Used as the From: header in OpenAlex API requests (polite pool).</div>
  </div>

  <button type="submit" class="btn btn-primary">Save Settings</button>
</form>
{% endblock %}
```

### Step 5: Run tests

```bash
python -m pytest tests/test_dashboard.py -k "settings" -v
```

Expected: all 3 settings tests PASS.

### Step 6: Full suite

```bash
python -m pytest tests/ -v
```

Expected: 38 tests pass.

### Step 7: Commit

```bash
git add dashboard.py dashboard/templates/settings.html tests/test_dashboard.py
git commit -m "feat: add settings page (read/write private.env and openalex.env)"
```

---

## Task 3: Venues page

**Files:**
- Modify: `dashboard.py` (add venues routes)
- Create: `dashboard/templates/venues.html`
- Modify: `tests/test_dashboard.py` (add venues tests)

### Step 1: Write failing tests

Append to `tests/test_dashboard.py`:

```python
# ── venues page ──────────────────────────────────────────────────────────────

SAMPLE_SOURCES_YAML = """\
version: 4
venues:
  - id: ieee_twc
    name: "IEEE Transactions on Wireless Communications"
    type: "journal"
    openalex_source_ids:
      - "S63459445"
"""


def test_venues_returns_200(client, app_tmp):
    (app_tmp / "sources.yaml").write_text(SAMPLE_SOURCES_YAML, encoding="utf-8")
    resp = client.get("/venues")
    assert resp.status_code == 200


def test_venues_lists_existing_venues(client, app_tmp):
    (app_tmp / "sources.yaml").write_text(SAMPLE_SOURCES_YAML, encoding="utf-8")
    resp = client.get("/venues")
    assert b"ieee_twc" in resp.data


def test_venues_add_creates_entry(client, app_tmp):
    (app_tmp / "sources.yaml").write_text(SAMPLE_SOURCES_YAML, encoding="utf-8")
    resp = client.post("/venues/add", data={
        "id": "ieee_wcl",
        "name": "IEEE Wireless Communications Letters",
        "type": "journal",
        "openalex_source_ids": "S2500830676",
    }, follow_redirects=True)
    assert resp.status_code == 200
    content = (app_tmp / "sources.yaml").read_text(encoding="utf-8")
    assert "ieee_wcl" in content
    assert "S2500830676" in content


def test_venues_remove_deletes_entry(client, app_tmp):
    (app_tmp / "sources.yaml").write_text(SAMPLE_SOURCES_YAML, encoding="utf-8")
    resp = client.post("/venues/remove/ieee_twc", follow_redirects=True)
    assert resp.status_code == 200
    content = (app_tmp / "sources.yaml").read_text(encoding="utf-8")
    assert "ieee_twc" not in content


def test_venues_add_duplicate_shows_error(client, app_tmp):
    (app_tmp / "sources.yaml").write_text(SAMPLE_SOURCES_YAML, encoding="utf-8")
    resp = client.post("/venues/add", data={
        "id": "ieee_twc",  # already exists
        "name": "Duplicate",
        "type": "journal",
        "openalex_source_ids": "S999",
    }, follow_redirects=True)
    assert b"already exists" in resp.data
```

### Step 2: Run to confirm they fail

```bash
python -m pytest tests/test_dashboard.py -k "venues" -v
```

Expected: FAIL (404).

### Step 3: Add venues routes to `dashboard.py`

Replace the `# ── venues placeholder` comment with:

```python
# ── venues ────────────────────────────────────────────────────────────────────

@app.route("/venues")
def venues():
    data = parse_sources_yaml(SOURCES_PATH)
    return render_template("venues.html", venues=data["venues"])


@app.route("/venues/add", methods=["POST"])
def venues_add():
    data = parse_sources_yaml(SOURCES_PATH)
    new_id = request.form.get("id", "").strip()
    new_name = request.form.get("name", "").strip()
    new_type = request.form.get("type", "").strip()
    raw_ids = request.form.get("openalex_source_ids", "")
    source_ids = [s.strip() for s in raw_ids.split(",") if s.strip()]
    if not new_id or not source_ids:
        flash("Venue ID and at least one OpenAlex source ID are required.", "danger")
        return redirect(url_for("venues"))
    if any(v["id"] == new_id for v in data["venues"]):
        flash(f"Venue '{new_id}' already exists.", "danger")
        return redirect(url_for("venues"))
    new_venue: dict = {"id": new_id, "name": new_name, "openalex_source_ids": source_ids}
    if new_type:
        new_venue["type"] = new_type
    data["venues"].append(new_venue)
    SOURCES_PATH.write_text(serialize_sources_yaml(data), encoding="utf-8")
    flash(f"Venue '{new_id}' added.", "success")
    return redirect(url_for("venues"))


@app.route("/venues/remove/<venue_id>", methods=["POST"])
def venues_remove(venue_id: str):
    data = parse_sources_yaml(SOURCES_PATH)
    before = len(data["venues"])
    data["venues"] = [v for v in data["venues"] if v["id"] != venue_id]
    if len(data["venues"]) == before:
        flash(f"Venue '{venue_id}' not found.", "danger")
    else:
        SOURCES_PATH.write_text(serialize_sources_yaml(data), encoding="utf-8")
        flash(f"Venue '{venue_id}' removed.", "success")
    return redirect(url_for("venues"))
```

### Step 4: Create `dashboard/templates/venues.html`

```html
{% extends "base.html" %}
{% block title %}Venues — Wireless Intel{% endblock %}
{% block content %}
<h2>Venues
  <small class="text-muted fw-normal fs-6">{{ venues | length }} configured</small>
</h2>

<table class="table table-striped align-middle mt-3">
  <thead class="table-dark">
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>Type</th>
      <th>OpenAlex Source IDs</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    {% for v in venues %}
    <tr>
      <td><code>{{ v.id }}</code></td>
      <td>{{ v.name }}</td>
      <td><span class="badge bg-secondary">{{ v.get('type', '') }}</span></td>
      <td><small class="font-monospace text-muted">{{ v.openalex_source_ids | join(', ') }}</small></td>
      <td>
        <form method="post" action="/venues/remove/{{ v.id }}"
              onsubmit="return confirm('Remove {{ v.id }}?')">
          <button class="btn btn-sm btn-outline-danger">Remove</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<h5 class="mt-5 border-bottom pb-2">Add Venue</h5>
<form method="post" action="/venues/add" class="row g-3 mt-1">
  <div class="col-md-2">
    <label class="form-label">Venue ID <span class="text-danger">*</span></label>
    <input type="text" class="form-control font-monospace" name="id"
           placeholder="ieee_twc" required>
  </div>
  <div class="col-md-4">
    <label class="form-label">Name</label>
    <input type="text" class="form-control" name="name"
           placeholder="IEEE Transactions on Wireless Communications">
  </div>
  <div class="col-md-2">
    <label class="form-label">Type</label>
    <select class="form-select" name="type">
      <option value="journal">journal</option>
      <option value="conference">conference</option>
    </select>
  </div>
  <div class="col-md-4">
    <label class="form-label">OpenAlex Source IDs (comma-separated) <span class="text-danger">*</span></label>
    <input type="text" class="form-control font-monospace" name="openalex_source_ids"
           placeholder="S12345678, S87654321" required>
  </div>
  <div class="col-12">
    <button type="submit" class="btn btn-success">Add Venue</button>
  </div>
</form>
{% endblock %}
```

### Step 5: Run tests

```bash
python -m pytest tests/test_dashboard.py -k "venues" -v
```

Expected: all 5 venues tests PASS.

### Step 6: Full suite

```bash
python -m pytest tests/ -v
```

Expected: 43 tests pass.

### Step 7: Commit

```bash
git add dashboard.py dashboard/templates/venues.html tests/test_dashboard.py
git commit -m "feat: add venues page (list/add/remove from sources.yaml)"
```

---

## Task 4: Run pipeline page + SSE

**Files:**
- Modify: `dashboard.py` (add run routes)
- Create: `dashboard/templates/run.html`
- Modify: `tests/test_dashboard.py` (add run tests)

### Step 1: Write failing tests

Append to `tests/test_dashboard.py`:

```python
# ── run page ──────────────────────────────────────────────────────────────────

def test_run_page_returns_200(client):
    resp = client.get("/run")
    assert resp.status_code == 200


def test_run_stream_content_type(client, monkeypatch):
    """SSE endpoint returns text/event-stream."""
    import dashboard

    class MockProc:
        def __init__(self):
            self.stdout = iter([])
            self.returncode = 0
        def wait(self):
            pass

    monkeypatch.setattr(dashboard.subprocess, "Popen", lambda *a, **k: MockProc())
    resp = client.get("/run/stream")
    assert resp.status_code == 200
    assert "text/event-stream" in resp.content_type


def test_run_stream_done_ok_on_success(client, monkeypatch):
    """Stream ends with [DONE:OK] when both scripts exit 0."""
    import dashboard

    class MockProc:
        def __init__(self):
            self.stdout = iter(["output line\n"])
            self.returncode = 0
        def wait(self):
            pass

    monkeypatch.setattr(dashboard.subprocess, "Popen", lambda *a, **k: MockProc())
    resp = client.get("/run/stream")
    body = resp.get_data(as_text=True)
    assert "[DONE:OK]" in body


def test_run_stream_done_failed_on_error(client, monkeypatch):
    """Stream ends with [DONE:FAILED] when a script exits non-zero."""
    import dashboard

    class MockProc:
        def __init__(self):
            self.stdout = iter([])
            self.returncode = 1
        def wait(self):
            pass

    monkeypatch.setattr(dashboard.subprocess, "Popen", lambda *a, **k: MockProc())
    resp = client.get("/run/stream")
    body = resp.get_data(as_text=True)
    assert "[DONE:FAILED]" in body
```

### Step 2: Run to confirm they fail

```bash
python -m pytest tests/test_dashboard.py -k "run" -v
```

Expected: FAIL (404).

### Step 3: Add run routes to `dashboard.py`

Replace the `# ── run placeholder` comment with:

```python
# ── run pipeline ──────────────────────────────────────────────────────────────

@app.route("/run")
def run_page():
    return render_template("run.html", running=_pipeline_running)


@app.route("/run/stream")
def run_stream():
    def generate():
        global _pipeline_running
        with _pipeline_lock:
            if _pipeline_running:
                yield "data: [Pipeline already running. Refresh and try again.]\n\n"
                return
            _pipeline_running = True
        try:
            scripts = [
                [sys.executable, str(REPO_DIR / "ingest_openalex.py")],
                [sys.executable, str(REPO_DIR / "generate_report.py"), "--weeks", "4"],
            ]
            for script_args in scripts:
                name = Path(script_args[1]).name
                yield f"data: Running {name}...\n\n"
                proc = subprocess.Popen(
                    script_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(REPO_DIR),
                )
                assert proc.stdout is not None
                for line in proc.stdout:
                    yield f"data: {line.rstrip()}\n\n"
                proc.wait()
                if proc.returncode != 0:
                    yield f"data: ERROR: {name} exited with code {proc.returncode}\n\n"
                    yield "data: [DONE:FAILED]\n\n"
                    return
                yield f"data: {name} completed successfully.\n\n"
            yield "data: [DONE:OK]\n\n"
        finally:
            _pipeline_running = False

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

### Step 4: Create `dashboard/templates/run.html`

```html
{% extends "base.html" %}
{% block title %}Run Pipeline — Wireless Intel{% endblock %}
{% block content %}
<h2>Run Pipeline</h2>
<p class="text-muted">
  Runs <code>ingest_openalex.py</code> then
  <code>generate_report.py --weeks 4</code> and streams live output.
</p>

{% if running %}
  <div class="alert alert-warning">Pipeline is currently running. Try again in a moment.</div>
{% else %}
  <button id="startBtn" class="btn btn-success btn-lg" onclick="startPipeline()">
    Start Pipeline
  </button>
{% endif %}

<pre id="log"
     class="mt-3 p-3 bg-dark text-light rounded font-monospace small"
     style="min-height: 120px; max-height: 520px; overflow-y: auto; display: none;"></pre>

<div id="statusMsg" class="mt-2 fw-semibold"></div>

<script>
function startPipeline() {
  const btn = document.getElementById('startBtn');
  const log = document.getElementById('log');
  const msg = document.getElementById('statusMsg');

  btn.disabled = true;
  btn.textContent = 'Running...';
  log.style.display = 'block';
  log.textContent = '';
  msg.textContent = '';

  const es = new EventSource('/run/stream');

  es.onmessage = function(e) {
    if (e.data === '[DONE:OK]') {
      es.close();
      msg.innerHTML = '<span class="text-success">Pipeline completed successfully.</span>';
      btn.textContent = 'Run Again';
      btn.disabled = false;
      return;
    }
    if (e.data === '[DONE:FAILED]') {
      es.close();
      msg.innerHTML = '<span class="text-danger">Pipeline failed. See log above.</span>';
      btn.textContent = 'Retry';
      btn.disabled = false;
      return;
    }
    log.textContent += e.data + '\n';
    log.scrollTop = log.scrollHeight;
  };

  es.onerror = function() {
    es.close();
    msg.innerHTML = '<span class="text-danger">Connection lost.</span>';
    btn.textContent = 'Retry';
    btn.disabled = false;
  };
}
</script>
{% endblock %}
```

### Step 5: Run tests

```bash
python -m pytest tests/test_dashboard.py -k "run" -v
```

Expected: all 4 run tests PASS.

### Step 6: Full suite

```bash
python -m pytest tests/ -v
```

Expected: 47 tests pass.

### Step 7: Commit

```bash
git add dashboard.py dashboard/templates/run.html tests/test_dashboard.py
git commit -m "feat: add run pipeline page with SSE live log"
```

---

## Task 5: README update

**Files:**
- Modify: `README.md`

### Step 1: Append a `## Dashboard` section to `README.md`

Add this at the end of the file:

```markdown

## Dashboard

A local web dashboard for running the pipeline, configuring settings, and managing venues.

**Install:**
```bash
pip install flask
```

**Run:**
```bash
python dashboard.py
```

Open [http://localhost:5000](http://localhost:5000).

| Page | URL | What it does |
|------|-----|-------------|
| Home | `/` | Shows last ingest date and report count |
| Run Pipeline | `/run` | Streams live output of ingest + report |
| Settings | `/settings` | Edit API keys and REPORT_DIR |
| Venues | `/venues` | Add/remove venues in `sources.yaml` |
```

### Step 2: Commit

```bash
git add README.md
git commit -m "docs: add Dashboard section to README"
```

---

## Smoke Test (manual)

```bash
python dashboard.py
# Open http://localhost:5000 in browser
# Verify: Home, Run, Settings, Venues pages all load
# Verify: Settings save round-trips correctly
# Verify: Venues add/remove work
```

---

## Final: Full test suite

```bash
python -m pytest tests/ -v
```

Expected: 47 tests pass, working tree clean.
