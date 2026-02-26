#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote
from urllib.request import Request, urlopen
import ssl


@dataclass
class Venue:
    venue_id: str
    name: str
    type: str
    publisher: str
    openalex_source_ids: List[str]


def load_env_file(path: Path) -> None:
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


def load_sources(path: Path) -> List[Venue]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sources file: {path}")

    venues: List[Venue] = []
    current = {"id": "", "name": "", "type": "", "publisher": "", "openalex_source_ids": []}
    in_openalex_ids = False

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
                        openalex_source_ids=current["openalex_source_ids"],
                    )
                )
            current = {
                "id": stripped.split(":", 1)[1].strip().strip("\"'"),
                "name": "",
                "type": "",
                "publisher": "",
                "openalex_source_ids": [],
            }
            in_openalex_ids = False
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
        if stripped.startswith("openalex_source_ids:"):
            in_openalex_ids = True
            continue
        if in_openalex_ids and stripped.startswith("- "):
            value = stripped.split("-", 1)[1].strip().strip("\"'")
            if value:
                current["openalex_source_ids"].append(value)
            continue
        if in_openalex_ids and stripped and not stripped.startswith("- "):
            in_openalex_ids = False

    if current["id"]:
        venues.append(
            Venue(
                venue_id=current["id"],
                name=current["name"],
                type=current["type"],
                publisher=current["publisher"],
                openalex_source_ids=current["openalex_source_ids"],
            )
        )

    # De-dup by venue_id
    deduped: Dict[str, Venue] = {}
    for venue in venues:
        deduped[venue.venue_id] = venue
    return list(deduped.values())


def save_sources(path: Path, venues: List[Venue]) -> None:
    lines: List[str] = []
    lines.append("version: 4")
    lines.append("updated_by: \"resolve_openalex_ids\"")
    lines.append("notes: \"OpenAlex-only ingestion. Use openalex_source_ids list per venue.\"")
    lines.append("venues:")
    for venue in venues:
        lines.append(f"  - id: {venue.venue_id}")
        lines.append(f"    name: \"{venue.name}\"")
        lines.append(f"    type: \"{venue.type}\"")
        lines.append(f"    publisher: \"{venue.publisher}\"")
        lines.append("    openalex_source_ids:")
        if venue.openalex_source_ids:
            for source_id in venue.openalex_source_ids:
                lines.append(f"      - \"{source_id}\"")
        else:
            lines.append("      - \"\"")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> dict:
    req = Request(
        url,
        headers={
            "User-Agent": "wireless-research-intel/0.2 (openalex-resolve)",
            "Accept": "application/json",
            **(headers or {}),
        },
    )
    context = ssl.create_default_context()
    with urlopen(req, timeout=timeout, context=context) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def resolve_source_id(name: str, api_key: Optional[str], email: Optional[str]) -> Optional[str]:
    headers = {}
    if api_key:
        headers["api-key"] = api_key
    if email:
        headers["From"] = email
    url = f"https://api.openalex.org/sources?search={quote(name)}"
    data = fetch_json(url, headers=headers)
    results = data.get("results") or []
    if not results:
        return None
    openalex_id = results[0].get("id")
    if not openalex_id:
        return None
    return openalex_id.rsplit("/", 1)[-1]


def resolve_source_ids(
    name: str, api_key: Optional[str], email: Optional[str], limit: int
) -> List[str]:
    headers = {}
    if api_key:
        headers["api-key"] = api_key
    if email:
        headers["From"] = email
    url = f"https://api.openalex.org/sources?search={quote(name)}&per-page={max(1, limit)}"
    data = fetch_json(url, headers=headers)
    results = data.get("results") or []
    scored = []
    for item in results:
        openalex_id = item.get("id")
        if not openalex_id:
            continue
        score = item.get("works_count")
        if not isinstance(score, int):
            score = -1
        scored.append((score, openalex_id.rsplit("/", 1)[-1]))
    if any(score >= 0 for score, _ in scored):
        scored.sort(key=lambda x: x[0], reverse=True)
    return [sid for _, sid in scored[:limit]]


def validate_sources(venues: List[Venue], api_key: Optional[str], email: Optional[str]) -> None:
    headers = {}
    if api_key:
        headers["api-key"] = api_key
    if email:
        headers["From"] = email
    for venue in venues:
        if not venue.openalex_source_ids:
            print(f"{venue.venue_id}: missing openalex_source_ids")
            continue
        total = 0
        for source_id in venue.openalex_source_ids:
            url = f"https://api.openalex.org/works?filter=primary_location.source.id:{source_id}&per-page=1"
            try:
                data = fetch_json(url, headers=headers)
                total += data.get("meta", {}).get("count", 0)
            except Exception as exc:
                print(f"{venue.venue_id}: error {exc}")
                total = -1
                break
        try:
            if total >= 0:
                print(f"{venue.venue_id}: count={total}")
        except Exception as exc:
            print(f"{venue.venue_id}: error {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve OpenAlex source IDs for sources.yaml.")
    parser.add_argument("--file", default="sources.yaml")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing openalex_source_id values.")
    parser.add_argument("--validate", action="store_true", help="Validate sources by fetching work counts.")
    parser.add_argument(
        "--discover-conferences",
        type=int,
        help="For conference venues, set top N OpenAlex source IDs from search results.",
    )
    args = parser.parse_args()

    load_env_file(Path("openalex.env"))
    api_key = os.getenv("OPENALEX_API_KEY")
    email = os.getenv("OPENALEX_EMAIL")

    path = Path(args.file)
    venues = load_sources(path)
    updated = 0

    for venue in venues:
        if venue.openalex_source_ids and not args.overwrite:
            continue
        if args.discover_conferences and venue.type == "conference":
            ids = resolve_source_ids(venue.name, api_key, email, args.discover_conferences)
            if ids:
                venue.openalex_source_ids = ids
                updated += 1
            continue
        source_id = resolve_source_id(venue.name, api_key, email)
        if source_id:
            venue.openalex_source_ids = [source_id]
            updated += 1

    save_sources(path, venues)
    print(f"Updated {updated} venues.")
    if args.validate:
        validate_sources(venues, api_key, email)


if __name__ == "__main__":
    main()
