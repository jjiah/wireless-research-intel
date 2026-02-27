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
        "SILICONFLOW_MODEL": "Pro/zai-org/GLM-5",
        "REPORT_WEEKS": "6",
        "REPORT_DIR": "C:\\new-reports",
        "OPENALEX_API_KEY": "oalex-key",
        "OPENALEX_EMAIL": "user@example.com",
    }, follow_redirects=True)
    assert resp.status_code == 200
    private = (app_tmp / "private.env").read_text(encoding="utf-8")
    openalex = (app_tmp / "openalex.env").read_text(encoding="utf-8")
    assert "new-key" in private
    assert "Pro/zai-org/GLM-5" in private
    assert "6" in private
    assert "C:\\new-reports" in private
    assert "oalex-key" in openalex
    assert "user@example.com" in openalex


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
