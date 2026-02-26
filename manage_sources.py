#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class Venue:
    venue_id: str
    name: str
    type: str
    publisher: str
    openalex_source_id: Optional[str]


def load_sources(path: Path) -> List[Venue]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sources file: {path}")

    venues: List[Venue] = []
    current = {"id": "", "name": "", "type": "", "publisher": "", "openalex_source_id": None}

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if current["id"]:
                venues.append(
                    Venue(
                        venue_id=current["id"],
                        name=current["name"],
                        type=current["type"],
                        publisher=current["publisher"],
                        openalex_source_id=current["openalex_source_id"],
                    )
                )
            current = {"id": stripped.split(":", 1)[1].strip().strip("\"'"), "name": "", "type": "", "publisher": "", "openalex_source_id": None}
            continue
        if stripped.startswith("name:"):
            current["name"] = stripped.split(":", 1)[1].strip().strip("\"'")
            continue
        if stripped.startswith("type:"):
            current["type"] = stripped.split(":", 1)[1].strip().strip("\"'")
            continue
        if stripped.startswith("publisher:"):
            current["publisher"] = stripped.split(":", 1)[1].strip().strip("\"'")
            continue
        if stripped.startswith("openalex_source_id:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            current["openalex_source_id"] = value if value.lower() != "null" else None

    if current["id"]:
        venues.append(
            Venue(
                venue_id=current["id"],
                name=current["name"],
                type=current["type"],
                publisher=current["publisher"],
                openalex_source_id=current["openalex_source_id"],
            )
        )

    return venues


def save_sources(path: Path, venues: List[Venue]) -> None:
    lines: List[str] = []
    lines.append("version: 3")
    lines.append("updated_by: \"manage_sources\"")
    lines.append("notes: \"OpenAlex-only ingestion. Populate openalex_source_id for each venue.\"")
    lines.append("venues:")
    for venue in venues:
        lines.append(f"  - id: {venue.venue_id}")
        lines.append(f"    name: \"{venue.name}\"")
        lines.append(f"    type: \"{venue.type}\"")
        lines.append(f"    publisher: \"{venue.publisher}\"")
        if venue.openalex_source_id:
            lines.append(f"    openalex_source_id: \"{venue.openalex_source_id}\"")
        else:
            lines.append("    openalex_source_id: null")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_venue(venues: List[Venue], venue_id: str) -> Optional[Venue]:
    for venue in venues:
        if venue.venue_id == venue_id:
            return venue
    return None


def cmd_list(venues: List[Venue]) -> None:
    for venue in venues:
        openalex = venue.openalex_source_id or "-"
        print(f"{venue.venue_id}\t{venue.type}\t{openalex}\t{venue.name}")


def cmd_show(venues: List[Venue], venue_id: str) -> None:
    venue = find_venue(venues, venue_id)
    if not venue:
        raise ValueError(f"Unknown venue_id: {venue_id}")
    print(f"id: {venue.venue_id}")
    print(f"name: {venue.name}")
    print(f"type: {venue.type}")
    print(f"publisher: {venue.publisher}")
    print(f"openalex_source_id: {venue.openalex_source_id or 'null'}")


def cmd_add(venues: List[Venue], venue: Venue) -> None:
    if find_venue(venues, venue.venue_id):
        raise ValueError(f"Venue already exists: {venue.venue_id}")
    venues.append(venue)


def cmd_remove(venues: List[Venue], venue_id: str) -> None:
    before = len(venues)
    venues[:] = [v for v in venues if v.venue_id != venue_id]
    if len(venues) == before:
        raise ValueError(f"Unknown venue_id: {venue_id}")


def cmd_set_openalex(venues: List[Venue], venue_id: str, source_id: str) -> None:
    venue = find_venue(venues, venue_id)
    if not venue:
        raise ValueError(f"Unknown venue_id: {venue_id}")
    venue.openalex_source_id = source_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage sources.yaml (OpenAlex-only).")
    parser.add_argument("--file", default="sources.yaml", help="Path to sources.yaml")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all venues")

    show = sub.add_parser("show", help="Show a venue")
    show.add_argument("venue_id")

    add = sub.add_parser("add", help="Add a venue")
    add.add_argument("--id", required=True)
    add.add_argument("--name", required=True)
    add.add_argument("--type", required=True, choices=["journal", "conference"])
    add.add_argument("--publisher", required=True)
    add.add_argument("--openalex-source-id")

    remove = sub.add_parser("remove", help="Remove a venue")
    remove.add_argument("venue_id")

    set_oa = sub.add_parser("set-openalex", help="Set OpenAlex source id")
    set_oa.add_argument("venue_id")
    set_oa.add_argument("openalex_source_id")

    args = parser.parse_args()
    path = Path(args.file)
    venues = load_sources(path)

    if args.cmd == "list":
        cmd_list(venues)
        return
    if args.cmd == "show":
        cmd_show(venues, args.venue_id)
        return
    if args.cmd == "add":
        cmd_add(
            venues,
            Venue(
                venue_id=args.id,
                name=args.name,
                type=args.type,
                publisher=args.publisher,
                openalex_source_id=args.openalex_source_id,
            ),
        )
    elif args.cmd == "remove":
        cmd_remove(venues, args.venue_id)
    elif args.cmd == "set-openalex":
        cmd_set_openalex(venues, args.venue_id, args.openalex_source_id)

    save_sources(path, venues)


if __name__ == "__main__":
    main()
