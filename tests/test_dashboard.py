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
