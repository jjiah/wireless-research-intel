#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, List


@dataclass
class Record:
    title: str
    venue: str
    published: str
    url: str
    abstract: str


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if value.startswith(("\"", "'")) and value.endswith(("\"", "'")) and len(value) >= 2:
        return value[1:-1]
    return value


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing config: {path}")
    config: dict = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = _strip_quotes(value.strip())
    return config


def load_source_names(path: Path) -> List[str]:
    if not path.exists():
        return []
    names: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            value = stripped.split(":", 1)[1].strip()
            names.append(_strip_quotes(value))
    return names


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def week_start_for(day: date, week_start_day: str) -> date:
    week_start_day = week_start_day.lower()
    # Python weekday: Monday=0, Sunday=6
    target = 6 if week_start_day == "sunday" else 0
    delta = (day.weekday() - target) % 7
    return day - timedelta(days=delta)


def load_records(path: Path) -> List[Record]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        records = []
        for row in data:
            records.append(
                Record(
                    title=str(row.get("title", "")).strip(),
                    venue=str(row.get("venue", "")).strip(),
                    published=str(row.get("published", "")).strip(),
                    url=str(row.get("url", "")).strip(),
                    abstract=str(row.get("abstract", "")).strip(),
                )
            )
        return records
    if path.suffix.lower() == ".csv":
        records = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                records.append(
                    Record(
                        title=str(row.get("title", "")).strip(),
                        venue=str(row.get("venue", "")).strip(),
                        published=str(row.get("published", "")).strip(),
                        url=str(row.get("url", "")).strip(),
                        abstract=str(row.get("abstract", "")).strip(),
                    )
                )
        return records
    raise ValueError("Only .json or .csv inputs are supported.")


def filter_week(records: Iterable[Record], week_start: date, week_end: date) -> List[Record]:
    selected: List[Record] = []
    for rec in records:
        try:
            published = parse_date(rec.published)
        except Exception:
            continue
        if week_start <= published <= week_end:
            selected.append(rec)
    return selected


def render_report(
    week_start: date,
    week_end: date,
    generated_on: date,
    sources: List[str],
    records: List[Record],
) -> str:
    lines: List[str] = []
    lines.append(f"# Weekly Wireless Report (Week of {week_start.isoformat()})")
    lines.append(f"Generated: {generated_on.isoformat()}")
    lines.append("")
    lines.append("## Sources")
    if sources:
        for name in sources:
            lines.append(f"- {name}")
    else:
        lines.append("- (sources.yaml not found or empty)")
    lines.append("")
    lines.append("## Summary")
    if records:
        lines.append(
            f"- Total items this week: {len(records)} (from {week_start.isoformat()} to {week_end.isoformat()})"
        )
    else:
        lines.append("- No items were provided for this week.")
    lines.append("")
    lines.append("## Venue Highlights")
    if records:
        by_venue: dict = {}
        for rec in records:
            by_venue.setdefault(rec.venue or "Unknown Venue", []).append(rec)
        for venue, items in sorted(by_venue.items(), key=lambda x: x[0].lower()):
            lines.append(f"### {venue}")
            for rec in sorted(items, key=lambda r: r.published or "", reverse=True)[:5]:
                if rec.url:
                    lines.append(f"- {rec.title} ({rec.published}) — {rec.url}")
                else:
                    lines.append(f"- {rec.title} ({rec.published})")
            lines.append("")
    else:
        lines.append("- No highlights available.")
    lines.append("")
    lines.append("## Topic Notes")
    lines.append("- Add key topic shifts and emerging areas here.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly wireless report.")
    parser.add_argument("--config", default="report_config.yaml")
    parser.add_argument("--date", help="Date inside the target week (YYYY-MM-DD). Defaults to today.")
    parser.add_argument("--input", help="Optional .json or .csv file with records.")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    week_start_day = config.get("week_start_day", "sunday")
    today = parse_date(args.date) if args.date else date.today()
    week_start = week_start_for(today, week_start_day)
    week_end = week_start + timedelta(days=6)

    sources_file = config.get("sources_file", "sources.yaml")
    sources = load_source_names(Path(sources_file))

    records: List[Record] = []
    if args.input:
        records = filter_week(load_records(Path(args.input)), week_start, week_end)

    report = render_report(week_start, week_end, date.today(), sources, records)

    report_dir = Path(config["report_dir"])
    report_dir.mkdir(parents=True, exist_ok=True)
    filename = config.get("filename_template", "weekly-wireless-{week_start}.md").format(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
    )
    output_path = report_dir / filename
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
