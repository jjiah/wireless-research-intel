#!/usr/bin/env python3
from __future__ import annotations

import json
import re
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
    # Use the lower median (median of the lower half) so anomalous weeks don't
    # inflate the reference baseline. For small lists this equates to min().
    sorted_counts = sorted(counts)
    lower_half = sorted_counts[: max(1, len(sorted_counts) // 2)]
    baseline = statistics.median(lower_half) if len(counts) >= 2 else float("inf")
    threshold = baseline * cap_multiplier

    result: list[dict] = []
    for papers in week_papers:
        if len(papers) > threshold:
            papers = sorted(
                papers,
                key=lambda p: p.get("cited_by_count") or 0,
                reverse=True,
            )[:cap_count]
        result.extend(papers)
    return result


def truncate_abstract(abstract: str, max_words: int = 150) -> str:
    """Return first max_words words of abstract, with ellipsis if truncated."""
    words = abstract.split()
    if len(words) <= max_words:
        return abstract
    return " ".join(words[:max_words]) + "..."


def build_payload(papers: list[dict]) -> str:
    """Build compact pipe-delimited payload for the LLM prompt."""
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


def inject_wiki_links(markdown: str) -> str:
    """Wrap topic headings (### N. Topic) in Obsidian [[wiki-links]]."""
    return re.sub(r"(### \d+\.\s+)(?!\[\[)(.+)", r"\1[[\2]]", markdown)


def write_report(content: str, output_dir: Path, date_str: str) -> Path:
    """Write the report Markdown to output_dir/YYYY-MM-DD-wireless-digest.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{date_str}-wireless-digest.md"
    path.write_text(content, encoding="utf-8")
    return path
