#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional


@dataclass
class Stats:
    scanned: int = 0
    copied: int = 0
    moved: int = 0
    skipped_missing_pubdate: int = 0
    skipped_invalid_pubdate: int = 0
    skipped_invalid_json: int = 0
    skipped_exists: int = 0


def iter_json_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for path in root.rglob("*.json"):
        if path.is_file():
            yield path


def sanitize_filename(value: str) -> str:
    return value.replace("/", "_").replace(":", "_").strip()


def parse_publication_date(record: dict) -> Optional[date]:
    raw = (record.get("publication_date") or record.get("published") or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def week_start_for(day: date, week_start_day: str) -> date:
    week_start_day = week_start_day.lower()
    target = 0 if week_start_day == "monday" else 6
    delta = (day.weekday() - target) % 7
    return day - timedelta(days=delta)


def target_subfolder(pub_date: date, group_by: str, week_start_day: str) -> str:
    if group_by == "day":
        return pub_date.isoformat()
    return week_start_for(pub_date, week_start_day).isoformat()


def target_filename(path: Path, record: dict) -> str:
    doi = (record.get("doi") or "").strip().lower()
    if doi:
        return f"{sanitize_filename(doi)}.json"
    return path.name


def load_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def organize(
    input_root: Path,
    output_root: Path,
    group_by: str,
    week_start_day: str,
    move: bool,
    dry_run: bool,
) -> Stats:
    stats = Stats()
    for src_path in iter_json_files(input_root):
        stats.scanned += 1
        record = load_json(src_path)
        if record is None:
            stats.skipped_invalid_json += 1
            continue

        pub_date = parse_publication_date(record)
        if pub_date is None:
            raw = (record.get("publication_date") or record.get("published") or "").strip()
            if raw:
                stats.skipped_invalid_pubdate += 1
            else:
                stats.skipped_missing_pubdate += 1
            continue

        subfolder = target_subfolder(pub_date, group_by, week_start_day)
        target_dir = output_root / subfolder
        dst_path = target_dir / target_filename(src_path, record)
        if dst_path.exists():
            stats.skipped_exists += 1
            continue

        if not dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            if move:
                shutil.move(str(src_path), str(dst_path))
            else:
                shutil.copy2(src_path, dst_path)

        if move:
            stats.moved += 1
        else:
            stats.copied += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reorganize paper JSON files into publication-based day or week subfolders."
    )
    parser.add_argument(
        "--input-root",
        default="resource/by_date",
        help="Root folder containing ingest-date JSON files.",
    )
    parser.add_argument(
        "--output-root",
        help="Output root for publication-based subfolders.",
    )
    parser.add_argument(
        "--group-by",
        default="day",
        choices=["day", "week"],
        help="Group files by exact publication day or publication week.",
    )
    parser.add_argument(
        "--week-start-day",
        default="monday",
        choices=["monday", "sunday"],
        help="Week convention used for week folder naming.",
    )
    parser.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without writing files.",
    )
    args = parser.parse_args()

    input_root = Path(args.input_root)
    if args.output_root:
        output_root = Path(args.output_root)
    elif args.group_by == "day":
        output_root = Path("resource/by_publication_date")
    else:
        output_root = Path("resource/by_publication_week")

    if not input_root.exists():
        raise FileNotFoundError(f"Input root not found: {input_root}")

    started = datetime.now().isoformat()
    stats = organize(
        input_root=input_root,
        output_root=output_root,
        group_by=args.group_by,
        week_start_day=args.week_start_day,
        move=args.move,
        dry_run=args.dry_run,
    )

    mode = "move" if args.move else "copy"
    print(f"Started: {started}")
    print(f"Mode: {mode}{' (dry-run)' if args.dry_run else ''}")
    print(f"Grouping: {args.group_by}")
    print(f"Input: {input_root}")
    print(f"Output: {output_root}")
    print("---")
    print(f"Scanned: {stats.scanned}")
    print(f"Copied: {stats.copied}")
    print(f"Moved: {stats.moved}")
    print(f"Skipped (exists): {stats.skipped_exists}")
    print(f"Skipped (missing pub date): {stats.skipped_missing_pubdate}")
    print(f"Skipped (invalid pub date): {stats.skipped_invalid_pubdate}")
    print(f"Skipped (invalid json): {stats.skipped_invalid_json}")


if __name__ == "__main__":
    main()
