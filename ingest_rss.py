#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
import sqlite3
import ssl


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)
ARNUM_RE = re.compile(r"/document/(\d+)/")
META_KEYWORDS_RE = re.compile(
    r'<meta[^>]+name=["\']keywords["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
META_DOI_RE = re.compile(
    r'<meta[^>]+name=["\']citation_doi["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
META_AUTHOR_RE = re.compile(
    r'<meta[^>]+name=["\']citation_author["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
META_ABSTRACT_RE = re.compile(
    r'<meta[^>]+name=["\']citation_abstract["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
GLOBAL_META_RE = re.compile(r"global\.document\.metadata\s*=\s*(\{.*?\});", re.DOTALL)


@dataclass
class Feed:
    venue_id: str
    venue_name: str
    url: str


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if value.startswith(("\"", "'")) and value.endswith(("\"", "'")) and len(value) >= 2:
        return value[1:-1]
    return value


def load_sources(path: Path) -> List[Feed]:
    if not path.exists():
        raise FileNotFoundError(f"Missing sources file: {path}")

    feeds: List[Feed] = []
    venue_id = ""
    venue_name = ""
    in_feeds = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            venue_id = _strip_quotes(stripped.split(":", 1)[1].strip())
            venue_name = ""
            in_feeds = False
            continue
        if stripped.startswith("name:"):
            venue_name = _strip_quotes(stripped.split(":", 1)[1].strip())
            continue
        if stripped.startswith("feeds:"):
            in_feeds = True
            continue
        if in_feeds and stripped.startswith("url:"):
            url = _strip_quotes(stripped.split(":", 1)[1].strip())
            if url.lower() != "null" and url:
                feeds.append(Feed(venue_id=venue_id, venue_name=venue_name, url=url))

    return feeds


def fetch_xml(url: str, timeout: int = 30) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "wireless-research-intel/0.1 (rss-ingest)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
        },
    )
    context = ssl.create_default_context()
    with urlopen(req, timeout=timeout, context=context) as resp:
        return resp.read()


def fetch_text(url: str, timeout: int = 30) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": "wireless-research-intel/0.1 (html-scrape)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    context = ssl.create_default_context()
    with urlopen(req, timeout=timeout, context=context) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def _text(el: Optional[ET.Element]) -> str:
    if el is None:
        return ""
    return (el.text or "").strip()


def _all_text(el: ET.Element) -> str:
    parts = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(_all_text(child))
        if child.tail:
            parts.append(child.tail)
    return "".join(parts)


def find_doi(texts: Iterable[str]) -> Optional[str]:
    for text in texts:
        if not text:
            continue
        match = DOI_RE.search(text)
        if match:
            return match.group(0).lower()
    return None


def parse_date(texts: Iterable[str]) -> Optional[str]:
    for text in texts:
        if not text:
            continue
        # RSS pubDate
        try:
            dt = parsedate_to_datetime(text)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.date().isoformat()
        except Exception:
            pass
        # ISO dates
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(text, fmt)
                return dt.date().isoformat()
            except Exception:
                continue
    return None


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


def parse_rss(xml_bytes: bytes) -> List[Dict]:
    root = ET.fromstring(xml_bytes)
    items = []

    # RSS 2.0: channel/item
    channel = root.find("channel")
    if channel is not None:
        for item in channel.findall("item"):
            items.append(item)
        return items

    # Atom: entry
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    if entries:
        return entries

    return []


def _find_all_text(item: ET.Element, tag: str) -> List[str]:
    values = []
    for el in item.findall(tag):
        text = _all_text(el).strip()
        if text:
            values.append(text)
    return values


def extract_authors(item: ET.Element) -> List[str]:
    authors: List[str] = []
    # RSS/IEEE often use dc:creator
    authors.extend(_find_all_text(item, "{http://purl.org/dc/elements/1.1/}creator"))
    # Atom author/name
    for author in item.findall("{http://www.w3.org/2005/Atom}author"):
        name = _text(author.find("{http://www.w3.org/2005/Atom}name"))
        if name:
            authors.append(name)
    # Generic author tag
    authors.extend(_find_all_text(item, "author"))
    # De-dup while preserving order
    seen = set()
    result = []
    for name in authors:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def extract_keywords(item: ET.Element) -> List[str]:
    keywords: List[str] = []
    # RSS category tags
    keywords.extend(_find_all_text(item, "category"))
    # Dublin Core subject
    keywords.extend(_find_all_text(item, "{http://purl.org/dc/elements/1.1/}subject"))
    # PRISM keyword
    keywords.extend(_find_all_text(item, "{http://prismstandard.org/namespaces/basic/2.0/}keyword"))
    # De-dup while preserving order
    seen = set()
    result = []
    for kw in keywords:
        kw = kw.strip()
        if not kw:
            continue
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
    return result


def item_fields(item: ET.Element) -> Tuple[str, str, str, str, List[str], List[str], List[str]]:
    texts = []
    for el in item.iter():
        texts.append(_all_text(el))

    title = _text(item.find("title")) or _text(item.find("{http://www.w3.org/2005/Atom}title"))
    link = _text(item.find("link"))
    if not link:
        link_el = item.find("{http://www.w3.org/2005/Atom}link")
        if link_el is not None:
            link = link_el.attrib.get("href", "")
    description = _text(item.find("description")) or _text(item.find("{http://www.w3.org/2005/Atom}summary"))

    pub_candidates = [
        _text(item.find("pubDate")),
        _text(item.find("{http://purl.org/dc/elements/1.1/}date")),
        _text(item.find("{http://purl.org/dc/elements/1.1/}issued")),
        _text(item.find("{http://prismstandard.org/namespaces/basic/2.0/}publicationDate")),
        _text(item.find("{http://www.w3.org/2005/Atom}updated")),
    ]
    published = parse_date(pub_candidates) or ""

    authors = extract_authors(item)
    keywords = extract_keywords(item)
    return title, link, description, published, authors, keywords, texts


def sanitize_doi(doi: str) -> str:
    return doi.replace("/", "_").replace(":", "_")


def extract_arnumber(url: str) -> Optional[str]:
    match = ARNUM_RE.search(url)
    if match:
        return match.group(1)
    return None


def _json_loads_safe(text: str) -> Optional[dict]:
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_from_global_metadata(html: str) -> Tuple[Optional[str], List[str], List[str], Optional[str]]:
    match = GLOBAL_META_RE.search(html)
    if not match:
        return None, [], [], None
    meta = _json_loads_safe(match.group(1))
    if not isinstance(meta, dict):
        return None, [], [], None

    doi = meta.get("doi")
    abstract = meta.get("abstract")

    authors = []
    for author in meta.get("authors", []) or []:
        if isinstance(author, dict):
            name = author.get("fullName") or author.get("name")
            if name:
                authors.append(name)
        elif isinstance(author, str):
            authors.append(author)

    keywords = []
    for block in meta.get("keywords", []) or []:
        if isinstance(block, dict):
            for kw in block.get("kwd", []) or []:
                if kw:
                    keywords.append(kw)

    return doi, authors, keywords, abstract


def enrich_from_ieee_html(url: str) -> Tuple[Optional[str], List[str], List[str], Optional[str]]:
    try:
        html = fetch_text(url)
    except Exception:
        return None, [], [], None

    doi = None
    meta_doi = META_DOI_RE.search(html)
    if meta_doi:
        doi = meta_doi.group(1).strip().lower()
    if not doi:
        doi = find_doi([html])

    authors = [m.group(1).strip() for m in META_AUTHOR_RE.finditer(html)]
    keywords = []
    meta_kw = META_KEYWORDS_RE.search(html)
    if meta_kw:
        keywords = [k.strip() for k in meta_kw.group(1).split(",") if k.strip()]
    meta_abs = META_ABSTRACT_RE.search(html)
    abstract = meta_abs.group(1).strip() if meta_abs else None

    if not doi or not authors or not keywords or not abstract:
        doi2, authors2, keywords2, abstract2 = _extract_from_global_metadata(html)
        if not doi and doi2:
            doi = doi2
        if not authors and authors2:
            authors = authors2
        if not keywords and keywords2:
            keywords = keywords2
        if not abstract and abstract2:
            abstract = abstract2

    # De-dup
    seen = set()
    authors = [a for a in authors if not (a in seen or seen.add(a))]
    seen = set()
    keywords = [k for k in keywords if not (k in seen or seen.add(k))]
    return doi, authors, keywords, abstract


def ingest_feed(feed: Feed, resource_dir: Path, since_date: Optional[str]) -> Tuple[int, int, int]:
    xml_bytes = fetch_xml(feed.url)
    items = parse_rss(xml_bytes)

    by_date_dir = resource_dir / "by_date"
    by_date_dir.mkdir(parents=True, exist_ok=True)

    seen = 0
    added = 0
    skipped_no_doi = 0

    db_path = resource_dir / "index.sqlite"
    conn = sqlite3.connect(db_path)
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

        for item in items:
            title, link, description, published, authors, keywords, texts = item_fields(item)
            if since_date and published:
                if published < since_date:
                    continue
            doi = find_doi([title, link, description] + texts)
            if not doi and link and "ieeexplore.ieee.org" in link:
                doi_html, authors_html, keywords_html, abstract_html = enrich_from_ieee_html(link)
                if doi_html:
                    doi = doi_html
                if authors_html:
                    authors = authors_html
                if keywords_html:
                    keywords = keywords_html
                if abstract_html and (not description or description.lower() == "null"):
                    description = abstract_html
            if not doi:
                skipped_no_doi += 1
                continue

            # Fast dedupe via SQLite.
            cur = conn.execute("SELECT 1 FROM papers WHERE doi = ?", (doi,))
            if cur.fetchone() is not None:
                seen += 1
                continue

            doi_key = sanitize_doi(doi)
            ingest_date = datetime.now(timezone.utc).date().isoformat()
            date_dir = by_date_dir / ingest_date
            date_dir.mkdir(parents=True, exist_ok=True)
            out_path = date_dir / f"{doi_key}.json"
            if out_path.exists():
                seen += 1
                continue

            record = {
                "doi": doi,
                "title": title,
                "venue_id": feed.venue_id,
                "venue_name": feed.venue_name,
                "published": published,
                "url": link,
                "abstract": description,
                "authors": authors,
                "keywords": keywords,
                "source_url": feed.url,
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
    parser = argparse.ArgumentParser(description="Ingest RSS feeds into resource folder.")
    parser.add_argument("--sources", default="sources.yaml", help="Path to sources.yaml")
    parser.add_argument("--resource-dir", default="resource", help="Output folder for per-venue metadata")
    parser.add_argument(
        "--since",
        help="Only include items published on/after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        help="Convenience option to set --since to today minus N days.",
    )
    args = parser.parse_args()

    feeds = load_sources(Path(args.sources))
    if not feeds:
        print("No feeds found in sources.yaml", file=sys.stderr)
        sys.exit(1)

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

    for feed in feeds:
        try:
            added, seen, skipped = ingest_feed(feed, resource_dir, since_date)
            total_added += added
            total_seen += seen
            total_skipped += skipped
            print(f"{feed.venue_id}: +{added} new, {seen} existing, {skipped} skipped (no DOI)")
        except Exception as exc:
            print(f"{feed.venue_id}: error {exc}", file=sys.stderr)

    print(f"Total: +{total_added} new, {total_seen} existing, {total_skipped} skipped (no DOI)")
    save_last_run(state_path, datetime.now(timezone.utc).date().isoformat())


if __name__ == "__main__":
    main()
