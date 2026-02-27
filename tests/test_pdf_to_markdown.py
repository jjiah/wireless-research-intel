from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest
from pypdf import PdfWriter

import pdf_to_markdown as p2m


def write_pdf(path: Path, pages: int) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=300)
    with path.open("wb") as f:
        writer.write(f)


def make_args(**overrides):
    defaults = {
        "input": "input.pdf",
        "output": None,
        "output_root": None,
        "chunk_pages": None,
        "max_workers": None,
        "resume": False,
        "max_retries": None,
        "timeout_seconds": None,
        "min_chars_per_page": None,
        "model": None,
        "base_url": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_build_initial_chunks_typical_and_edge():
    chunks = p2m.build_initial_chunks(page_count=7, chunk_pages=3)
    assert [(c["page_start"], c["page_end"]) for c in chunks] == [(1, 3), (4, 6), (7, 7)]
    one = p2m.build_initial_chunks(page_count=1, chunk_pages=30)
    assert len(one) == 1
    assert one[0]["id"] == p2m.make_chunk_id(1, 1)


def test_split_chunk_behavior():
    chunk = {
        "id": p2m.make_chunk_id(1, 8),
        "page_start": 1,
        "page_end": 8,
    }
    left, right = p2m.split_chunk(chunk)
    assert (left["page_start"], left["page_end"]) == (1, 4)
    assert (right["page_start"], right["page_end"]) == (5, 8)
    single = {"id": p2m.make_chunk_id(2, 2), "page_start": 2, "page_end": 2}
    assert p2m.split_chunk(single) is None


def test_merge_markdown_normalization_dedupe_and_fence_balance():
    a = "line1\r\nline2\r\n```\ncode"
    b = "line2\nline3"
    merged = p2m.merge_markdown([a, b])
    assert "\r" not in merged
    assert "line2\n\nline2" not in merged
    assert merged.strip().endswith("```")


def test_incomplete_multi_page_heuristic():
    short = "<|ref|>title<|/ref|>\nCover page only"
    assert p2m.is_likely_incomplete_chunk_output(short, page_count=5, min_chars_per_page=120)
    long_text = ("\n".join([f"Line {i} with enough content." for i in range(30)]))
    assert not p2m.is_likely_incomplete_chunk_output(long_text, page_count=5, min_chars_per_page=20)


def test_clean_ocr_markdown_removes_layout_tokens():
    raw = (
        "<|ref|>title<|/ref|><|det|>[[1,2,3,4]]<|/det|>\n"
        "# Heading\n\n"
        "<|ref|>text<|/ref|><|det|>[[5,6,7,8]]<|/det|>\n"
        "Line one.- Bullet two\n"
    )
    cleaned = p2m.clean_ocr_markdown(raw)
    assert "<|ref|>" not in cleaned
    assert "<|det|>" not in cleaned
    assert "# Heading" in cleaned
    assert "Line one." in cleaned
    assert "- Bullet two" in cleaned


def test_clean_ocr_markdown_drops_repeated_number_noise_and_blank_page():
    raw = (
        "PAGE LEFT INTENTIONALLY BLANK\n"
        "1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1. 1.\n"
        "Useful sentence stays.\n"
    )
    cleaned = p2m.clean_ocr_markdown(raw)
    assert "PAGE LEFT INTENTIONALLY BLANK" not in cleaned
    assert "1. 1. 1." not in cleaned
    assert "Useful sentence stays." in cleaned


def test_has_repeated_short_token_noise():
    noisy = "1. " * 40
    assert p2m.has_repeated_short_token_noise(noisy)
    normal = "1. First item\n2. Second item\n3. Third item"
    assert not p2m.has_repeated_short_token_noise(normal)


def test_normalize_pdf_extracted_text_preserves_numbered_list():
    raw = (
        "Header line\n"
        "1. First point\n"
        "2. Second point\n"
        "3. Third point\n"
        "PAGE LEFT INTENTIONALLY BLANK\n"
    )
    normalized = p2m.normalize_pdf_extracted_text(raw)
    assert "PAGE LEFT INTENTIONALLY BLANK" not in normalized
    assert "1. First point" in normalized
    assert "2. Second point" in normalized
    assert "3. Third point" in normalized


def test_should_use_pdf_text_fallback_for_repeated_noise():
    raw_ocr = ("1. " * 50).strip()
    cleaned_ocr = raw_ocr
    pdf_text = (
        "1. Informs other operators\n"
        "2. Enables strategic deconfliction\n"
        "3. Enables restriction distribution\n"
    )
    assert p2m.should_use_pdf_text_fallback(raw_ocr, cleaned_ocr, pdf_text)


def test_resolve_config_precedence_and_env_loading(tmp_path, monkeypatch):
    pdf = tmp_path / "input.pdf"
    write_pdf(pdf, pages=1)
    (tmp_path / "private.env").write_text(
        "\n".join(
            [
                "SILICONFLOW_API_KEY=env_key",
                "SILICONFLOW_BASE_URL=https://env.base/v1",
                "SILICONFLOW_MODEL=env/model",
                "PDF2MD_CHUNK_PAGES=19",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)

    args = make_args(
        input=str(pdf),
        base_url="https://cli.base/v1",
        model="cli/model",
        chunk_pages=7,
    )
    config = p2m.resolve_config(args)
    assert config.api_key == "env_key"
    assert config.base_url == "https://cli.base/v1"
    assert config.model == "cli/model"
    assert config.chunk_pages == 7


def test_resolve_config_missing_key_exits(tmp_path, monkeypatch):
    pdf = tmp_path / "input.pdf"
    write_pdf(pdf, pages=1)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    args = make_args(input=str(pdf))
    with pytest.raises(SystemExit) as exc:
        p2m.resolve_config(args)
    assert exc.value.code == 1


def test_call_ocr_with_retries_retriable_then_success(monkeypatch):
    calls = {"n": 0}

    def fake_once(**kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("429 rate limit")
        return "ok"

    sleeps: list[float] = []
    monkeypatch.setattr(p2m, "call_ocr_once", fake_once)
    monkeypatch.setattr(p2m.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(p2m.random, "uniform", lambda a, b: 0.0)

    content, attempts, err_type, err_msg = p2m.call_ocr_with_retries(
        client=object(),
        model="m",
        timeout_seconds=10,
        chunk_pdf=Path("x.pdf"),
        max_retries=3,
    )
    assert content == "ok"
    assert attempts == 3
    assert err_type is None
    assert err_msg is None
    assert sleeps == [1.0, 2.0]


def test_call_ocr_with_retries_split_required(monkeypatch):
    monkeypatch.setattr(
        p2m,
        "call_ocr_once",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("payload too large")),
    )
    content, attempts, err_type, _ = p2m.call_ocr_with_retries(
        client=object(),
        model="m",
        timeout_seconds=10,
        chunk_pdf=Path("x.pdf"),
        max_retries=3,
    )
    assert content is None
    assert attempts == 1
    assert err_type == "split_required"


def make_config(tmp_path: Path, input_pdf: Path, resume: bool = False) -> p2m.Config:
    return p2m.Config(
        input_path=input_pdf,
        output_path=None,
        output_root=tmp_path / "resource" / "pdf_markdown",
        chunk_pages=2,
        max_workers=1,
        resume=resume,
        max_retries=1,
        timeout_seconds=30,
        min_chars_per_page=1,
        base_url="https://api.siliconflow.com/v1",
        model="deepseek-ai/DeepSeek-OCR",
        api_key="dummy",
    )


def test_process_multi_chunk_happy_path(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    write_pdf(pdf, pages=5)
    config = make_config(tmp_path, pdf, resume=False)

    monkeypatch.setattr(p2m, "build_client", lambda **kwargs: object())

    def fake_call(**kwargs):
        chunk_pdf = kwargs["chunk_pdf"]
        chunk_id = chunk_pdf.stem.replace("chunk_", "")
        return f"markdown-{chunk_id}\n", 1, None, None

    monkeypatch.setattr(p2m, "call_ocr_with_retries", fake_call)
    code = p2m.process(config)
    assert code == 0

    run_key = p2m.compute_run_key(pdf)
    run_dir = config.output_root / f"{pdf.stem}-{run_key}"
    final_path = run_dir / "final.md"
    assert final_path.exists()
    content = final_path.read_text(encoding="utf-8")
    assert "markdown-000001_000002" in content
    assert "markdown-000003_000004" in content
    assert "markdown-000005_000005" in content
    assert content.index("000001_000002") < content.index("000003_000004")
    assert content.index("000003_000004") < content.index("000005_000005")


def test_process_adaptive_split_on_oversize(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    write_pdf(pdf, pages=4)
    config = make_config(tmp_path, pdf, resume=False)
    config = p2m.Config(**{**config.__dict__, "chunk_pages": 4})  # start as one chunk

    monkeypatch.setattr(p2m, "build_client", lambda **kwargs: object())

    def fake_call(**kwargs):
        chunk_pdf = kwargs["chunk_pdf"]
        page_count = len(p2m.PdfReader(str(chunk_pdf)).pages)
        chunk_id = chunk_pdf.stem.replace("chunk_", "")
        if page_count > 2:
            return None, 1, "split_required", "payload too large"
        return f"ok-{chunk_id}", 1, None, None

    monkeypatch.setattr(p2m, "call_ocr_with_retries", fake_call)
    code = p2m.process(config)
    assert code == 0

    run_key = p2m.compute_run_key(pdf)
    manifest_path = config.output_root / f"{pdf.stem}-{run_key}" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    statuses = {c["id"]: c["status"] for c in manifest["chunks"]}
    assert statuses["000001_000004"] == "split"
    assert statuses["000001_000002"] == "done"
    assert statuses["000003_000004"] == "done"


def test_process_resume_skips_completed_chunks(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    write_pdf(pdf, pages=4)
    config = make_config(tmp_path, pdf, resume=False)

    monkeypatch.setattr(p2m, "build_client", lambda **kwargs: object())
    touched: list[str] = []

    def first_run_call(**kwargs):
        chunk_id = kwargs["chunk_pdf"].stem.replace("chunk_", "")
        touched.append(chunk_id)
        if chunk_id == "000003_000004":
            return None, 2, "retriable", "429 rate limit"
        return f"ok-{chunk_id}", 1, None, None

    monkeypatch.setattr(p2m, "call_ocr_with_retries", first_run_call)
    first_code = p2m.process(config)
    assert first_code == 2
    assert touched == ["000001_000002", "000003_000004"]

    touched_resume: list[str] = []

    def second_run_call(**kwargs):
        chunk_id = kwargs["chunk_pdf"].stem.replace("chunk_", "")
        touched_resume.append(chunk_id)
        return f"ok-{chunk_id}", 1, None, None

    monkeypatch.setattr(p2m, "call_ocr_with_retries", second_run_call)
    resume_config = make_config(tmp_path, pdf, resume=True)
    second_code = p2m.process(resume_config)
    assert second_code == 0
    assert touched_resume == ["000003_000004"]


def test_process_heuristic_split_on_short_multi_page_output(tmp_path, monkeypatch):
    pdf = tmp_path / "doc.pdf"
    write_pdf(pdf, pages=4)
    config = make_config(tmp_path, pdf, resume=False)
    config = p2m.Config(**{**config.__dict__, "chunk_pages": 4, "min_chars_per_page": 100})

    monkeypatch.setattr(p2m, "build_client", lambda **kwargs: object())

    def fake_call(**kwargs):
        chunk_id = kwargs["chunk_pdf"].stem.replace("chunk_", "")
        if chunk_id == "000001_000004":
            return "cover-only", 1, None, None
        return f"ok-{chunk_id} with enough text " * 20, 1, None, None

    monkeypatch.setattr(p2m, "call_ocr_with_retries", fake_call)
    code = p2m.process(config)
    assert code == 0

    run_key = p2m.compute_run_key(pdf)
    manifest_path = config.output_root / f"{pdf.stem}-{run_key}" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    statuses = {c["id"]: c["status"] for c in manifest["chunks"]}
    assert statuses["000001_000004"] == "split"
    assert statuses["000001_000002"] == "done"
    assert statuses["000003_000004"] == "done"
