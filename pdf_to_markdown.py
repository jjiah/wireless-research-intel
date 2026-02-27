#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import random
import re
import shutil
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader, PdfWriter

PROMPT = "<image>\n<|grounding|>Convert the document to markdown."
DEFAULT_OUTPUT_ROOT = "resource/pdf_markdown"
DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-OCR"


@dataclass(frozen=True)
class Config:
    input_path: Path
    output_path: Path | None
    output_root: Path
    chunk_pages: int
    max_workers: int
    resume: bool
    max_retries: int
    timeout_seconds: float
    min_chars_per_page: int
    base_url: str
    model: str
    api_key: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_env_file(path: Path) -> None:
    """Load key=value pairs from a .env-like file into os.environ."""
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert local PDF to Markdown via SiliconFlow DeepSeek-OCR."
    )
    parser.add_argument("--input", required=True, help="Input PDF file path.")
    parser.add_argument("--output", help="Final markdown output path.")
    parser.add_argument(
        "--output-root",
        help=f"Directory for runtime artifacts (default: {DEFAULT_OUTPUT_ROOT}).",
    )
    parser.add_argument(
        "--chunk-pages",
        type=int,
        help="Initial pages per chunk (default: 30).",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        help="Reserved for future parallel mode (current implementation processes sequentially).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous manifest for the same input file state.",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        help="Retry count for retriable errors (default: 3).",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        help="Per-request timeout in seconds (default: 120).",
    )
    parser.add_argument(
        "--min-chars-per-page",
        type=int,
        help="Heuristic lower bound used to detect incomplete multi-page OCR output (default: 160).",
    )
    parser.add_argument(
        "--model",
        help=f"OCR model id (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--base-url",
        help=f"SiliconFlow base URL (default: {DEFAULT_BASE_URL}).",
    )
    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> Config:
    load_env_file(Path("private.env"))

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".pdf":
        print(f"Input is not a PDF: {input_path}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("Missing SILICONFLOW_API_KEY in private.env or environment.", file=sys.stderr)
        sys.exit(1)

    output_root = Path(
        args.output_root
        or os.getenv("PDF2MD_OUTPUT_ROOT")
        or DEFAULT_OUTPUT_ROOT
    )
    chunk_pages = int(args.chunk_pages or os.getenv("PDF2MD_CHUNK_PAGES") or 30)
    max_workers = int(args.max_workers or os.getenv("PDF2MD_MAX_WORKERS") or 1)
    max_retries = int(args.max_retries or os.getenv("PDF2MD_MAX_RETRIES") or 3)
    timeout_seconds = float(
        args.timeout_seconds or os.getenv("PDF2MD_TIMEOUT_SECONDS") or 120.0
    )
    min_chars_per_page = int(
        args.min_chars_per_page or os.getenv("PDF2MD_MIN_CHARS_PER_PAGE") or 160
    )
    base_url = args.base_url or os.getenv("SILICONFLOW_BASE_URL") or DEFAULT_BASE_URL
    model = args.model or os.getenv("SILICONFLOW_MODEL") or DEFAULT_MODEL

    if chunk_pages < 1:
        print("--chunk-pages must be >= 1", file=sys.stderr)
        sys.exit(1)
    if max_workers < 1:
        print("--max-workers must be >= 1", file=sys.stderr)
        sys.exit(1)
    if max_retries < 0:
        print("--max-retries must be >= 0", file=sys.stderr)
        sys.exit(1)
    if timeout_seconds <= 0:
        print("--timeout-seconds must be > 0", file=sys.stderr)
        sys.exit(1)
    if min_chars_per_page < 1:
        print("--min-chars-per-page must be >= 1", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).expanduser().resolve() if args.output else None
    return Config(
        input_path=input_path,
        output_path=output_path,
        output_root=output_root,
        chunk_pages=chunk_pages,
        max_workers=max_workers,
        resume=args.resume,
        max_retries=max_retries,
        timeout_seconds=timeout_seconds,
        min_chars_per_page=min_chars_per_page,
        base_url=base_url,
        model=model,
        api_key=api_key,
    )


def compute_run_key(pdf_path: Path) -> str:
    stat = pdf_path.stat()
    source = f"{pdf_path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return digest[:8]


def make_chunk_id(page_start: int, page_end: int) -> str:
    return f"{page_start:06d}_{page_end:06d}"


def build_initial_chunks(page_count: int, chunk_pages: int) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    page = 1
    while page <= page_count:
        end = min(page + chunk_pages - 1, page_count)
        chunk_id = make_chunk_id(page, end)
        chunks.append(
            {
                "id": chunk_id,
                "page_start": page,
                "page_end": end,
                "status": "pending",
                "attempts": 0,
                "error_type": None,
                "duration_sec": None,
                "split_from": None,
            }
        )
        page = end + 1
    return chunks


def new_manifest(
    config: Config,
    run_key: str,
    page_count: int,
    input_pdf_for_manifest: str,
) -> dict[str, Any]:
    return {
        "input_pdf": input_pdf_for_manifest,
        "run_key": run_key,
        "page_count": page_count,
        "chunk_pages_initial": config.chunk_pages,
        "status": "running",
        "started_at": now_iso(),
        "finished_at": None,
        "failures": [],
        "chunks": build_initial_chunks(page_count, config.chunk_pages),
    }


def chunk_pdf_path(chunks_pdf_dir: Path, chunk: dict[str, Any]) -> Path:
    return chunks_pdf_dir / f"chunk_{chunk['id']}.pdf"


def chunk_md_path(chunks_md_dir: Path, chunk: dict[str, Any]) -> Path:
    return chunks_md_dir / f"chunk_{chunk['id']}.md"


def save_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def create_chunk_pdf(source_pdf: Path, page_start: int, page_end: int, out_path: Path) -> None:
    reader = PdfReader(str(source_pdf))
    writer = PdfWriter()
    for page_idx in range(page_start - 1, page_end):
        writer.add_page(reader.pages[page_idx])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as f:
        writer.write(f)


def is_nonempty_file(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_layout_tokens(text: str) -> str:
    cleaned = re.sub(r"<\|[^>]+\|>", " ", text)
    cleaned = re.sub(r"\[\[[0-9,\s]+\]\]", " ", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return normalize_newlines(cleaned)


def clean_ocr_markdown(content: str) -> str:
    """Convert OCR raw layout-tag output into cleaner markdown-like text."""
    text = normalize_newlines(content)
    # Remove detector box payloads.
    text = re.sub(r"<\|det\|>.*?<\|/det\|>", "", text, flags=re.DOTALL)
    # Remove ref-type markers such as <|ref|>title<|/ref|>.
    text = re.sub(r"<\|ref\|>[^<]*<\|/ref\|>", "", text)
    # Drop any remaining tag fragments.
    text = re.sub(r"<\|[^>]+\|>", "", text)
    # Drop empty image placeholder lines after tag removal.
    lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.upper() == "PAGE LEFT INTENTIONALLY BLANK":
            continue
        if stripped in {"image", "image_caption", "title", "text", "sub_title"}:
            continue
        # Drop OCR noise lines that are mostly a tiny token repeated many times
        # (for example: "1. 1. 1. 1. ...").
        tokens = [tok for tok in re.split(r"\s+", stripped) if tok]
        if len(tokens) >= 20:
            normalized = [re.sub(r"[^\w]+$", "", tok) for tok in tokens]
            if normalized and len(set(normalized)) == 1 and len(normalized[0]) <= 4:
                continue
        if re.fullmatch(r"(?:\d+[.)]?\s+){20,}\d+[.)]?", stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines)
    # Recover common flattened bullet formatting from OCR.
    text = text.replace(".- ", ".\n- ")
    text = re.sub(r"\s+- ", "\n- ", text)
    # Normalize excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def has_repeated_short_token_noise(text: str) -> bool:
    for line in normalize_newlines(text).split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        tokens = [tok for tok in re.split(r"\s+", stripped) if tok]
        if len(tokens) < 20:
            continue
        normalized = [re.sub(r"[^\w]+$", "", tok).lower() for tok in tokens]
        if not normalized:
            continue
        unique = set(normalized)
        if len(unique) == 1 and len(next(iter(unique))) <= 4:
            return True
    return False


def count_numbered_list_lines(text: str) -> int:
    return sum(
        1
        for line in normalize_newlines(text).split("\n")
        if re.match(r"^\s*\d+\.\s+\S", line.strip())
    )


def extract_pdf_text(chunk_pdf: Path) -> str:
    try:
        reader = PdfReader(str(chunk_pdf))
        parts = [(page.extract_text() or "") for page in reader.pages]
        return normalize_newlines("\n".join(parts))
    except Exception:
        return ""


def normalize_pdf_extracted_text(text: str) -> str:
    text = normalize_newlines(text)
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    out: list[str] = []
    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append(" ".join(para))
            para = []

    for s in lines:
        if not s:
            flush_para()
            continue
        if s.upper() == "PAGE LEFT INTENTIONALLY BLANK":
            continue
        if re.fullmatch(r"\d{1,3}", s):
            # Likely standalone page number.
            continue
        if re.match(r"^\d+\.\s+\S", s) or re.match(r"^[-*]\s+\S", s):
            flush_para()
            out.append(s)
            continue
        if para and para[-1].endswith("-"):
            para[-1] = para[-1][:-1] + s
        else:
            para.append(s)
    flush_para()
    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result).strip()
    return (result + "\n") if result else ""


def should_use_pdf_text_fallback(
    raw_ocr: str,
    cleaned_ocr: str,
    pdf_text: str,
) -> bool:
    pdf_stripped = pdf_text.strip()
    if not pdf_stripped:
        return False
    if has_repeated_short_token_noise(raw_ocr) or has_repeated_short_token_noise(cleaned_ocr):
        # Even short extracted text can recover severe repeated-token OCR corruption.
        return len(pdf_stripped) >= 40
    if len(pdf_stripped) < 120:
        return False
    pdf_lists = count_numbered_list_lines(pdf_text)
    ocr_lists = count_numbered_list_lines(cleaned_ocr)
    if pdf_lists >= 3 and ocr_lists == 0:
        return True
    if len(cleaned_ocr.strip()) < int(0.6 * len(pdf_text.strip())) and len(pdf_text.strip()) >= 500:
        return True
    return False


def is_likely_incomplete_chunk_output(
    content: str,
    page_count: int,
    min_chars_per_page: int,
) -> bool:
    if page_count <= 1:
        return False
    cleaned = strip_layout_tokens(content).strip()
    if not cleaned:
        return True
    char_threshold = page_count * min_chars_per_page
    return len(cleaned) < char_threshold


def classify_error(exc: Exception) -> str:
    text = str(exc).lower()
    split_keywords = [
        "context length",
        "maximum context",
        "too large",
        "payload",
        "too many tokens",
        "token limit",
        "request entity too large",
    ]
    retriable_keywords = [
        "429",
        "rate limit",
        "timeout",
        "timed out",
        "temporarily unavailable",
        "502",
        "503",
        "504",
        "connection",
    ]
    if any(k in text for k in split_keywords):
        return "split_required"
    if any(k in text for k in retriable_keywords):
        return "retriable"
    return "terminal"


def call_ocr_once(
    *,
    client: Any,
    model: str,
    timeout_seconds: float,
    chunk_pdf: Path,
) -> str:
    b64 = base64.b64encode(chunk_pdf.read_bytes()).decode("utf-8")
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        timeout=timeout_seconds,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:application/pdf;base64,{b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": PROMPT,
                    },
                ],
            }
        ],
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("OCR response contained no content.")
    return normalize_newlines(content)


def call_ocr_with_retries(
    *,
    client: Any,
    model: str,
    timeout_seconds: float,
    chunk_pdf: Path,
    max_retries: int,
) -> tuple[str | None, int, str | None, str | None]:
    """Return (content, attempts, error_type, error_message)."""
    attempts = 0
    last_message: str | None = None
    for attempt in range(max_retries + 1):
        attempts += 1
        try:
            content = call_ocr_once(
                client=client,
                model=model,
                timeout_seconds=timeout_seconds,
                chunk_pdf=chunk_pdf,
            )
            return content, attempts, None, None
        except Exception as exc:  # pragma: no cover - exercised via tests with fake client
            error_type = classify_error(exc)
            last_message = str(exc)
            if error_type == "split_required":
                return None, attempts, "split_required", last_message
            if error_type == "retriable" and attempt < max_retries:
                sleep_sec = (2**attempt) + random.uniform(0, 0.25)
                time.sleep(sleep_sec)
                continue
            return None, attempts, error_type, last_message
    return None, attempts, "terminal", last_message


def get_chunk_lookup(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {chunk["id"]: chunk for chunk in manifest.get("chunks", [])}


def sort_chunk_ids_by_page(chunks: list[dict[str, Any]]) -> list[str]:
    ordered = sorted(chunks, key=lambda c: (c["page_start"], c["page_end"]))
    return [c["id"] for c in ordered]


def split_chunk(chunk: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]] | None:
    start = int(chunk["page_start"])
    end = int(chunk["page_end"])
    if start >= end:
        return None
    mid = (start + end) // 2
    left = {
        "id": make_chunk_id(start, mid),
        "page_start": start,
        "page_end": mid,
        "status": "pending",
        "attempts": 0,
        "error_type": None,
        "duration_sec": None,
        "split_from": chunk["id"],
    }
    right = {
        "id": make_chunk_id(mid + 1, end),
        "page_start": mid + 1,
        "page_end": end,
        "status": "pending",
        "attempts": 0,
        "error_type": None,
        "duration_sec": None,
        "split_from": chunk["id"],
    }
    return left, right


def append_failure(manifest: dict[str, Any], chunk_id: str, error_type: str, message: str | None) -> None:
    manifest.setdefault("failures", []).append(
        {
            "chunk_id": chunk_id,
            "error_type": error_type,
            "message": message or "",
            "time": now_iso(),
        }
    )


def queue_for_resume(manifest: dict[str, Any], chunks_md_dir: Path) -> list[str]:
    queue: list[str] = []
    for chunk in sorted(manifest.get("chunks", []), key=lambda c: (c["page_start"], c["page_end"])):
        md_path = chunk_md_path(chunks_md_dir, chunk)
        if chunk["status"] == "done" and is_nonempty_file(md_path):
            continue
        if chunk["status"] == "done" and not is_nonempty_file(md_path):
            chunk["status"] = "pending"
        if chunk["status"] in {"pending", "failed_retriable"}:
            queue.append(chunk["id"])
    return queue


def dedupe_boundary_overlap(left: str, right: str, max_lines: int = 20) -> tuple[str, str]:
    left_lines = normalize_newlines(left).split("\n")
    right_lines = normalize_newlines(right).split("\n")
    limit = min(max_lines, len(left_lines), len(right_lines))
    overlap = 0
    for size in range(limit, 0, -1):
        if left_lines[-size:] == right_lines[:size]:
            overlap = size
            break
    if overlap > 0:
        right_lines = right_lines[overlap:]
    return "\n".join(left_lines), "\n".join(right_lines)


def ensure_fence_balance(text: str) -> str:
    fence_count = sum(1 for line in normalize_newlines(text).split("\n") if line.strip().startswith("```"))
    if fence_count % 2 == 1:
        return text.rstrip() + "\n```" + "\n"
    return text


def merge_markdown(chunks_in_order: list[str]) -> str:
    if not chunks_in_order:
        return ""
    merged = normalize_newlines(chunks_in_order[0]).strip("\n")
    for chunk_text in chunks_in_order[1:]:
        left, right = dedupe_boundary_overlap(merged, normalize_newlines(chunk_text))
        merged = left.rstrip("\n")
        right = right.strip("\n")
        if right:
            merged = merged + "\n\n" + right
    merged = ensure_fence_balance(merged)
    return merged.rstrip() + "\n"


def build_client(api_key: str, base_url: str) -> Any:
    from siliconflow_api import build_openai_client

    return build_openai_client(api_key=api_key, base_url=base_url)


def process(config: Config) -> int:
    if config.max_workers > 1:
        print("Note: current implementation is sequential; --max-workers is reserved.", file=sys.stderr)

    run_key = compute_run_key(config.input_path)
    run_dir = config.output_root / f"{config.input_path.stem}-{run_key}"
    chunks_pdf_dir = run_dir / "chunks_pdf"
    chunks_md_dir = run_dir / "chunks_md"
    logs_dir = run_dir / "logs"
    manifest_path = run_dir / "manifest.json"

    if run_dir.exists() and not config.resume:
        shutil.rmtree(run_dir)

    run_dir.mkdir(parents=True, exist_ok=True)
    chunks_pdf_dir.mkdir(parents=True, exist_ok=True)
    chunks_md_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    page_count = len(PdfReader(str(config.input_path)).pages)
    if page_count == 0:
        print("Input PDF has no pages.", file=sys.stderr)
        return 1

    input_pdf_manifest_value = str(config.input_path)
    if config.resume and manifest_path.exists():
        manifest = load_manifest(manifest_path)
        if manifest.get("run_key") != run_key:
            print("Existing manifest run key does not match current input file state.", file=sys.stderr)
            return 1
    else:
        manifest = new_manifest(
            config=config,
            run_key=run_key,
            page_count=page_count,
            input_pdf_for_manifest=input_pdf_manifest_value,
        )
        save_manifest(manifest_path, manifest)

    client = build_client(api_key=config.api_key, base_url=config.base_url)
    chunk_lookup = get_chunk_lookup(manifest)
    queue = queue_for_resume(manifest, chunks_md_dir)

    while queue:
        chunk_id = queue.pop(0)
        chunk = chunk_lookup.get(chunk_id)
        if not chunk:
            continue

        md_path = chunk_md_path(chunks_md_dir, chunk)
        if chunk["status"] == "done" and is_nonempty_file(md_path):
            continue

        pdf_path = chunk_pdf_path(chunks_pdf_dir, chunk)
        if not pdf_path.exists():
            create_chunk_pdf(
                source_pdf=config.input_path,
                page_start=int(chunk["page_start"]),
                page_end=int(chunk["page_end"]),
                out_path=pdf_path,
            )

        begin = time.monotonic()
        content, attempts, error_type, error_message = call_ocr_with_retries(
            client=client,
            model=config.model,
            timeout_seconds=config.timeout_seconds,
            chunk_pdf=pdf_path,
            max_retries=config.max_retries,
        )
        chunk["attempts"] = int(chunk.get("attempts", 0)) + attempts
        chunk["duration_sec"] = round(time.monotonic() - begin, 3)

        if content is not None:
            page_span = int(chunk["page_end"]) - int(chunk["page_start"]) + 1
            if is_likely_incomplete_chunk_output(
                content=content,
                page_count=page_span,
                min_chars_per_page=config.min_chars_per_page,
            ):
                content = None
                error_type = "split_required"
                error_message = (
                    f"incomplete multi-page OCR output heuristic triggered "
                    f"(pages={page_span}, min_chars_per_page={config.min_chars_per_page})"
                )
            else:
                cleaned_content = clean_ocr_markdown(content)
                pdf_text_raw = extract_pdf_text(pdf_path)
                if should_use_pdf_text_fallback(content, cleaned_content, pdf_text_raw):
                    normalized_pdf_text = normalize_pdf_extracted_text(pdf_text_raw)
                    if normalized_pdf_text:
                        cleaned_content = normalized_pdf_text
                md_path.write_text(cleaned_content, encoding="utf-8")
                chunk["status"] = "done"
                chunk["error_type"] = None
                save_manifest(manifest_path, manifest)
                continue

        if error_type == "split_required":
            children = split_chunk(chunk)
            if children is None:
                chunk["status"] = "failed_retriable"
                chunk["error_type"] = "split_required_single_page"
                append_failure(manifest, chunk_id, chunk["error_type"], error_message)
                save_manifest(manifest_path, manifest)
                continue

            left, right = children
            chunk["status"] = "split"
            chunk["error_type"] = "split_required"
            # Split parent artifacts are not meaningful output; remove stale md if present.
            if md_path.exists():
                md_path.unlink(missing_ok=True)
            for child in (left, right):
                existing = chunk_lookup.get(child["id"])
                if existing is None:
                    manifest["chunks"].append(child)
                    chunk_lookup[child["id"]] = child
                elif existing["status"] != "done":
                    existing["status"] = "pending"
                if child["id"] not in queue:
                    queue.append(child["id"])

            queue = sorted(
                queue,
                key=lambda cid: (
                    chunk_lookup[cid]["page_start"],
                    chunk_lookup[cid]["page_end"],
                ),
            )
            save_manifest(manifest_path, manifest)
            continue

        if error_type == "retriable":
            chunk["status"] = "failed_retriable"
        else:
            chunk["status"] = "failed_terminal"
        chunk["error_type"] = error_type
        append_failure(manifest, chunk_id, error_type or "unknown", error_message)
        save_manifest(manifest_path, manifest)

    failed_chunks = [
        c for c in manifest.get("chunks", [])
        if c["status"] in {"failed_retriable", "failed_terminal"}
    ]
    if failed_chunks:
        failed_terminal = [c for c in failed_chunks if c["status"] == "failed_terminal"]
        failed_retriable = [c for c in failed_chunks if c["status"] == "failed_retriable"]
        manifest["status"] = "failed"
        manifest["finished_at"] = now_iso()
        save_manifest(manifest_path, manifest)
        if failed_terminal:
            print(
                "Run failed with terminal errors "
                f"({len(failed_terminal)} terminal, {len(failed_retriable)} retriable). "
                "Fix credentials/config first, then rerun without --resume "
                f"(or remove run dir): {manifest_path}",
                file=sys.stderr,
            )
        else:
            print(
                f"Run failed. {len(failed_chunks)} chunk(s) need attention or resume. Manifest: {manifest_path}",
                file=sys.stderr,
            )
        return 2

    # Keep only failures for currently failed chunks (drop recovered history).
    failed_ids = {
        c["id"] for c in manifest.get("chunks", [])
        if c["status"] in {"failed_retriable", "failed_terminal"}
    }
    manifest["failures"] = [
        f for f in manifest.get("failures", [])
        if f.get("chunk_id") in failed_ids
    ]

    done_chunks = [c for c in manifest.get("chunks", []) if c["status"] == "done"]
    done_chunks_sorted = sorted(done_chunks, key=lambda c: (c["page_start"], c["page_end"]))
    merged_parts: list[str] = []
    for chunk in done_chunks_sorted:
        md_path = chunk_md_path(chunks_md_dir, chunk)
        if not is_nonempty_file(md_path):
            print(f"Missing markdown chunk output: {md_path}", file=sys.stderr)
            return 2
        merged_parts.append(md_path.read_text(encoding="utf-8"))

    final_md = merge_markdown(merged_parts)
    final_path = config.output_path or (run_dir / "final.md")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(final_md, encoding="utf-8")

    manifest["status"] = "completed"
    manifest["finished_at"] = now_iso()
    save_manifest(manifest_path, manifest)

    total_retries = sum(max(int(c.get("attempts", 1)) - 1, 0) for c in manifest["chunks"])
    print(f"Pages: {page_count}")
    print(f"Chunks completed: {len(done_chunks_sorted)}")
    print(f"Retries: {total_retries}")
    print(f"Failures: 0")
    print(f"Output: {final_path}")
    return 0


def main() -> None:
    args = parse_args()
    config = resolve_config(args)
    code = process(config)
    sys.exit(code)


if __name__ == "__main__":
    main()
