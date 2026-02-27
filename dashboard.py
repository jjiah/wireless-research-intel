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
from datetime import date, timedelta
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


# ── settings ──────────────────────────────────────────────────────────────────

_PRIVATE_KEYS = ("SILICONFLOW_API_KEY", "SILICONFLOW_MODEL", "INGEST_WEEKS", "REPORT_WEEKS", "INGEST_SINCE_DATE", "REPORT_DIR")
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
# ── run pipeline ──────────────────────────────────────────────────────────────

def _build_ingest_cmd(private: dict) -> list[str]:
    """Build ingest_openalex.py command. Uses last_run.json when available,
    falls back to INGEST_WEEKS weeks back, bounded by INGEST_SINCE_DATE floor."""
    ingest_weeks_str = private.get("INGEST_WEEKS", "8").strip()
    ingest_weeks = int(ingest_weeks_str) if ingest_weeks_str.isdigit() and int(ingest_weeks_str) > 0 else 8

    since_date = None
    last_run_path = REPO_DIR / "resource" / "last_run.json"
    if last_run_path.exists():
        try:
            since_date = json.loads(
                last_run_path.read_text(encoding="utf-8")
            ).get("last_run_date")
        except Exception:
            pass

    weeks_since = (date.today() - timedelta(weeks=ingest_weeks)).isoformat()
    if since_date is None or since_date < weeks_since:
        since_date = weeks_since

    floor_date = private.get("INGEST_SINCE_DATE", "2024-01-01").strip() or "2024-01-01"
    if since_date < floor_date:
        since_date = floor_date

    return [sys.executable, str(REPO_DIR / "ingest_openalex.py"), "--since", since_date]


def _build_report_cmd(private: dict) -> list[str]:
    """Build generate_report.py command using REPORT_WEEKS setting."""
    weeks_str = private.get("REPORT_WEEKS", "4").strip()
    weeks = int(weeks_str) if weeks_str.isdigit() and int(weeks_str) > 0 else 4
    return [sys.executable, str(REPO_DIR / "generate_report.py"), "--weeks", str(weeks)]


def _run_cmds_generator(cmds: list[list[str]]):
    """Generator: acquire pipeline lock, stream each command's output as SSE."""
    global _pipeline_running
    with _pipeline_lock:
        if _pipeline_running:
            yield "data: [Pipeline already running. Refresh and try again.]\n\n"
            return
        _pipeline_running = True
    try:
        for script_args in cmds:
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


def _sse_response(cmds: list[list[str]]) -> Response:
    return Response(
        stream_with_context(_run_cmds_generator(cmds)),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/run")
def run_page():
    return render_template("run.html", running=_pipeline_running)


@app.route("/run/ingest/stream")
def run_ingest_stream():
    private = load_env_file(PRIVATE_ENV_PATH)
    return _sse_response([_build_ingest_cmd(private)])


@app.route("/run/report/stream")
def run_report_stream():
    private = load_env_file(PRIVATE_ENV_PATH)
    return _sse_response([_build_report_cmd(private)])


@app.route("/run/stream")
def run_stream():
    private = load_env_file(PRIVATE_ENV_PATH)
    return _sse_response([_build_ingest_cmd(private), _build_report_cmd(private)])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
