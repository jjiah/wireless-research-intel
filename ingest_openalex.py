#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote
from urllib.request import Request, urlopen
import time
import ssl
import sqlite3


@dataclass
class Source:
    venue_id: str
    venue_name: str
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


def load_sources(path: Path) -> List[Source]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sources file: {path}")

    sources: List[Source] = []
    venue_id = ""
    venue_name = ""
    openalex_source_ids: List[str] = []
    in_openalex_ids = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            if venue_id and openalex_source_ids:
                sources.append(Source(venue_id, venue_name, openalex_source_ids))
            venue_id = stripped.split(":", 1)[1].strip().strip("\"'")
            venue_name = ""
            openalex_source_ids = []
            in_openalex_ids = False
            continue
        if stripped.startswith("name:"):
            venue_name = stripped.split(":", 1)[1].strip().strip("\"'")
            continue
        if stripped.startswith("openalex_source_ids:"):
            in_openalex_ids = True
            continue
        if in_openalex_ids and stripped.startswith("- "):
            value = stripped.split("-", 1)[1].strip().strip("\"'")
            if value:
                openalex_source_ids.append(value)
            continue
        if in_openalex_ids and stripped and not stripped.startswith("- "):
            in_openalex_ids = False

    if venue_id and openalex_source_ids:
        sources.append(Source(venue_id, venue_name, openalex_source_ids))

    # De-dup by venue_id
    deduped: Dict[str, Source] = {}
    for source in sources:
        deduped[source.venue_id] = source
    return list(deduped.values())


def fetch_json(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    retries: int = 3,
    backoff: float = 1.5,
) -> dict:
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": "wireless-research-intel/0.2 (openalex)",
                    "Accept": "application/json",
                    **(headers or {}),
                },
            )
            context = ssl.create_default_context()
            with urlopen(req, timeout=timeout, context=context) as resp:
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(backoff ** attempt)
    if last_exc:
        raise last_exc
    raise RuntimeError("Failed to fetch JSON.")


def normalize_doi(doi_value: Optional[str]) -> Optional[str]:
    if not doi_value:
        return None
    doi = doi_value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "http://dx.doi.org/"):
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi or None


def reconstruct_abstract(inv_index: Optional[dict]) -> Optional[str]:
    if not inv_index:
        return None
    positions: Dict[int, str] = {}
    for word, indices in inv_index.items():
        if not isinstance(indices, list):
            continue
        for idx in indices:
            if isinstance(idx, int):
                positions[idx] = word
    if not positions:
        return None
    words = [positions[i] for i in sorted(positions.keys())]
    return " ".join(words)


def simplify_authorships(authorships: List[dict]) -> List[dict]:
    simplified: List[dict] = []
    for auth in authorships:
        author = auth.get("author") or {}
        author_name = author.get("display_name")
        if not author_name:
            continue
        institutions = []
        for inst in auth.get("institutions") or []:
            name = inst.get("display_name")
            if name and name not in institutions:
                institutions.append(name)
        simplified.append({"author": author_name, "institutions": institutions})
    return simplified


def openalex_works(
    source_id: str,
    since_date: Optional[str],
    api_key: str,
    email: Optional[str],
) -> List[dict]:
    headers = {"api-key": api_key}
    if email:
        headers["From"] = email

    filter_parts = [f"primary_location.source.id:{source_id}", "type:article|preprint"]
    if since_date:
        filter_parts.append(f"from_publication_date:{since_date}")
    filter_query = ",".join(filter_parts)

    per_page = 200
    cursor = "*"
    works: List[dict] = []
    while cursor:
        url = (
            "https://api.openalex.org/works?"
            f"filter={quote(filter_query)}"
            f"&per-page={per_page}"
            f"&cursor={quote(cursor)}"
            "&select=id,display_name,doi,type,publication_date,primary_location,authorships,keywords,abstract_inverted_index"
        )
        data = fetch_json(url, headers=headers)
        results = data.get("results") or []
        works.extend(results)
        cursor = data.get("meta", {}).get("next_cursor")
        if not results:
            break
    return works


def load_last_run(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("last_run_date")
    except Exception:
        return None


def save_last_run(path: Path, date_str: str) -> None:
    payload = {"last_run_date": date_str, "updated_at": datetime.now(timezone.utc).isoformat()}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def ingest_source(
    source: Source,
    resource_dir: Path,
    since_date: Optional[str],
    api_key: str,
    email: Optional[str],
) -> Tuple[int, int, int]:
    works: List[dict] = []
    for source_id in source.openalex_source_ids:
        works.extend(openalex_works(source_id, since_date, api_key, email))

    by_date_dir = resource_dir / "by_date"
    by_date_dir.mkdir(parents=True, exist_ok=True)

    db_path = resource_dir / "index.sqlite"
    conn = sqlite3.connect(db_path)
    added = 0
    seen = 0
    skipped_no_doi = 0
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                doi TEXT PRIMARY KEY,
                title TEXT,
                venue_id TEXT,
                venue_name TEXT,
                published TEXT,
                url TEXT,
                source_url TEXT,
                fetched_at TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_venue ON papers(venue_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_published ON papers(published)")

        for work in works:
            doi = normalize_doi(work.get("doi"))
            if not doi:
                skipped_no_doi += 1
                continue

            cur = conn.execute("SELECT 1 FROM papers WHERE doi = ?", (doi,))
            if cur.fetchone() is not None:
                seen += 1
                continue

            ingest_date = datetime.now(timezone.utc).date().isoformat()
            date_dir = by_date_dir / ingest_date
            date_dir.mkdir(parents=True, exist_ok=True)
            out_path = date_dir / f"{doi.replace('/', '_').replace(':', '_')}.json"
            if out_path.exists():
                seen += 1
                continue

            authorships = work.get("authorships") or []
            authors = []
            for auth in authorships:
                author = auth.get("author") or {}
                name = author.get("display_name")
                if name:
                    authors.append(name)
            seen_auth = set()
            authors = [a for a in authors if not (a in seen_auth or seen_auth.add(a))]

            keywords = []
            for kw in work.get("keywords") or []:
                name = kw.get("display_name")
                if name:
                    keywords.append(name)
            seen_kw = set()
            keywords = [k for k in keywords if not (k in seen_kw or seen_kw.add(k))]

            abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
            primary_location = work.get("primary_location") or {}
            url = primary_location.get("landing_page_url") or work.get("id") or work.get("doi")

            record = {
                "doi": doi,
                "title": work.get("display_name") or "",
                "openalex_id": work.get("id"),
                "openalex_type": work.get("type"),
                "publication_date": work.get("publication_date"),
                "primary_location": primary_location,
                "venue_id": source.venue_id,
                "venue_name": source.venue_name,
                "published": work.get("publication_date") or "",
                "url": url,
                "abstract": abstract or "",
                "authors": authors,
                "authorships": simplify_authorships(authorships),
                "keywords": keywords,
                "source_url": "openalex",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

            conn.execute(
                """
                INSERT OR IGNORE INTO papers
                (doi, title, venue_id, venue_name, published, url, source_url, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["doi"],
                    record["title"],
                    record["venue_id"],
                    record["venue_name"],
                    record["published"],
                    record["url"],
                    record["source_url"],
                    record["fetched_at"],
                ),
            )
            added += 1
        conn.commit()
    finally:
        conn.close()

    return added, seen, skipped_no_doi


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest OpenAlex works into resource folder.")
    parser.add_argument("--sources", default="sources.yaml", help="Path to sources.yaml")
    parser.add_argument("--resource-dir", default="resource", help="Output folder for per-venue metadata")
    parser.add_argument("--since", help="Only include items published on/after this date (YYYY-MM-DD).")
    parser.add_argument(
        "--lookback-days",
        type=int,
        help="Convenience option to set --since to today minus N days.",
    )
    parser.add_argument(
        "--only",
        help="Comma-separated venue_ids to include (e.g., ieee_twc,ieee_jsac).",
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated venue_ids to exclude.",
    )
    args = parser.parse_args()

    load_env_file(Path("openalex.env"))
    load_env_file(Path("private.env"))

    api_key = os.getenv("OPENALEX_API_KEY")
    email = os.getenv("OPENALEX_EMAIL")
    if not api_key:
        print("Missing OPENALEX_API_KEY. Set it in openalex.env.", file=sys.stderr)
        sys.exit(1)

    sources = load_sources(Path(args.sources))
    if not sources:
        print("No OpenAlex sources found in sources.yaml", file=sys.stderr)
        sys.exit(1)

    only_set = set()
    exclude_set = set()
    if args.only:
        only_set = {v.strip() for v in args.only.split(",") if v.strip()}
    if args.exclude:
        exclude_set = {v.strip() for v in args.exclude.split(",") if v.strip()}

    resource_dir = Path(args.resource_dir)
    resource_dir.mkdir(parents=True, exist_ok=True)
    state_path = resource_dir / "last_run.json"

    since_date = args.since
    if args.lookback_days is not None:
        since_date = (datetime.now(timezone.utc).date() - timedelta(days=args.lookback_days)).isoformat()
    if not since_date:
        since_date = load_last_run(state_path)

    total_added = 0
    total_seen = 0
    total_skipped = 0

    for source in sources:
        if not source.openalex_source_ids:
            print(f"{source.venue_id}: missing openalex_source_id", file=sys.stderr)
            continue
        if only_set and source.venue_id not in only_set:
            continue
        if exclude_set and source.venue_id in exclude_set:
            continue
        try:
            added, seen, skipped = ingest_source(source, resource_dir, since_date, api_key, email)
            total_added += added
            total_seen += seen
            total_skipped += skipped
            print(f"{source.venue_id}: +{added} new, {seen} existing, {skipped} skipped (no DOI)")
        except Exception as exc:
            print(f"{source.venue_id}: error {exc}", file=sys.stderr)

    print(f"Total: +{total_added} new, {total_seen} existing, {total_skipped} skipped (no DOI)")
    save_last_run(state_path, datetime.now(timezone.utc).date().isoformat())


if __name__ == "__main__":
    main()
