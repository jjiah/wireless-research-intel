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
    openalex_source_id: Optional[str]


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
            current = {
                "id": stripped.split(":", 1)[1].strip().strip("\"'"),
                "name": "",
                "type": "",
                "publisher": "",
                "openalex_source_id": None,
            }
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
    lines.append("updated_by: \"resolve_openalex_ids\"")
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve OpenAlex source IDs for sources.yaml.")
    parser.add_argument("--file", default="sources.yaml")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing openalex_source_id values.")
    args = parser.parse_args()

    load_env_file(Path("openalex.env"))
    api_key = os.getenv("OPENALEX_API_KEY")
    email = os.getenv("OPENALEX_EMAIL")

    path = Path(args.file)
    venues = load_sources(path)
    updated = 0

    for venue in venues:
        if venue.openalex_source_id and not args.overwrite:
            continue
        source_id = resolve_source_id(venue.name, api_key, email)
        if source_id:
            venue.openalex_source_id = source_id
            updated += 1

    save_sources(path, venues)
    print(f"Updated {updated} venues.")


if __name__ == "__main__":
    main()
