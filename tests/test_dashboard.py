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
