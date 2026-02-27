#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from datetime import datetime
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
    cap_count: int = 500,
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


def truncate_abstract(abstract: str, max_words: int = 300) -> str:
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
            (p.get("abstract") or "").replace("|", "/"), max_words=300
        )
        lines.append(f"{title} | {venue} | {week} | {citations} | {abstract}")
    return "\n".join(lines)


def inject_wiki_links(markdown: str) -> str:
    """Wrap topic headings and any remaining quoted paper titles in Obsidian [[wiki-links]]."""
    # Wrap topic headings: ### N. Topic → ### N. [[Topic]]
    result = re.sub(r"(### \d+\.\s+)(?!\[\[)(.+)", r"\1[[\2]]", markdown)
    # Fallback: convert any remaining "Quoted Title" → [[Quoted Title]]
    # (catches paper titles the LLM didn't auto-link)
    result = re.sub(r'"([^"\n]{10,})"', r'[[\1]]', result)
    return result


def write_report(content: str, output_dir: Path, date_str: str) -> Path:
    """Write the report Markdown to output_dir/YYYY-MM-DD-wireless-digest.md."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{date_str}-wireless-digest.md"
    path.write_text(content, encoding="utf-8")
    return path


def call_llm(payload: str, template: str, weeks: int, api_key: str) -> str:
    """Call SiliconFlow GLM-5 with the paper payload and return Markdown."""
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.siliconflow.cn/v1",
    )

    system = (
        "You are a research analyst specialising in wireless communications. "
        "You analyse paper metadata and produce structured research digests. "
        "Be factual and ground every claim in the provided paper abstracts."
    )

    user = (
        f"Here are papers from the past {weeks} weeks across IEEE wireless communications venues.\n"
        "Format per line: title | venue_id | year-month | citation_count | abstract_snippet\n\n"
        "--- PAPERS ---\n"
        f"{payload}\n"
        "--- END PAPERS ---\n\n"
        "Produce a research digest following this exact template structure:\n\n"
        f"{template}\n\n"
        "Guidelines:\n"
        "- Identify 8-12 distinct research topics clustered from the papers above\n"
        "- Each topic subsection must cite specific evidence from the paper abstracts\n"
        "- Trend signals: compare paper counts in the first half vs second half of the window\n"
        "- Research gaps: areas adjacent to hot topics with few or no papers\n"
        "- Suggested reading: highest cited_by_count papers with specific one-line rationale\n"
        "- Output plain Markdown only\n"
        "- Add [[wiki-links]] (Obsidian format) as follows:\n"
        "  * Paper titles in 'Representative papers' and 'Suggested Reading': use [[Paper Title]] format (no quotes)\n"
        "  * Key technical terms in body text: wrap important concepts e.g. [[ISAC]], [[Beamforming]], [[RIS]], [[MIMO]]\n"
        "  * Do NOT add [[wiki-links]] to section headings (## or ###) — those are handled separately\n"
        "- Replace all {{PLACEHOLDERS}} with real content from the papers"
    )

    response = client.chat.completions.create(
        model="Pro/zai-org/GLM-5",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=8192,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError(f"LLM returned no content (finish_reason={response.choices[0].finish_reason})")
    return content


def load_env_file(path: Path) -> None:
    """Load key=value pairs from a .env file into os.environ."""
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate wireless research digest.")
    parser.add_argument("--weeks", type=int, default=4, help="Number of recent weeks to analyse")
    parser.add_argument("--resource-dir", default="resource", help="Path to resource folder")
    args = parser.parse_args()

    load_env_file(Path("openalex.env"))
    load_env_file(Path("private.env"))

    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        print("Missing SILICONFLOW_API_KEY in private.env", file=sys.stderr)
        sys.exit(1)

    report_dir = Path(os.getenv("REPORT_DIR", "reports"))

    resource_dir = Path(args.resource_dir)
    weeks_dir = resource_dir / "by_publication_week"

    print(f"Loading last {args.weeks} weeks from {weeks_dir}...")
    week_dirs = load_weeks(weeks_dir, args.weeks)
    if not week_dirs:
        print("No week folders found.", file=sys.stderr)
        sys.exit(1)

    date_range = f"{week_dirs[0].name} → {week_dirs[-1].name}"
    print(f"  Weeks: {date_range}")

    papers = load_papers(week_dirs)
    print(f"  {len(papers)} papers loaded")
    if not papers:
        print("No papers found in the selected weeks.", file=sys.stderr)
        sys.exit(1)

    payload = build_payload(papers)

    template_path = Path("templates/report_template.md")
    if not template_path.exists():
        print(f"Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    template = template_path.read_text(encoding="utf-8")

    print("Calling SiliconFlow GLM-5...")
    markdown = call_llm(payload, template, args.weeks, api_key)

    markdown = inject_wiki_links(markdown)

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = write_report(markdown, report_dir, date_str)
    print(f"Report written → {out_path}")


if __name__ == "__main__":
    main()
