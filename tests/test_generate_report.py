# tests/test_generate_report.py
import json
import pytest
from pathlib import Path
from generate_report import load_weeks, load_papers
from generate_report import truncate_abstract, build_payload
from generate_report import inject_wiki_links
from generate_report import write_report
from generate_report import (
    load_topic_registry,
    extract_topics_from_markdown,
    update_topic_registry,
)


def make_week(tmp_path: Path, name: str, papers: list[dict]) -> Path:
    week_dir = tmp_path / name
    week_dir.mkdir()
    for i, paper in enumerate(papers):
        (week_dir / f"paper_{i}.json").write_text(json.dumps(paper), encoding="utf-8")
    return week_dir


def sample_paper(cited: int = 10) -> dict:
    return {
        "title": "Test Paper",
        "venue_id": "ieee_twc",
        "published": "2025-02-10",
        "cited_by_count": cited,
        "abstract": "This is a test abstract with some words in it.",
    }


# --- load_weeks ---

def test_load_weeks_returns_last_n(tmp_path):
    weeks_dir = tmp_path / "by_publication_week"
    weeks_dir.mkdir()
    for name in ["2025-01-06", "2025-01-13", "2025-01-20", "2025-01-27"]:
        (weeks_dir / name).mkdir()
    result = load_weeks(weeks_dir, n=2)
    assert [d.name for d in result] == ["2025-01-20", "2025-01-27"]


def test_load_weeks_returns_all_if_fewer_than_n(tmp_path):
    weeks_dir = tmp_path / "by_publication_week"
    weeks_dir.mkdir()
    (weeks_dir / "2025-01-06").mkdir()
    result = load_weeks(weeks_dir, n=4)
    assert len(result) == 1


def test_load_weeks_returns_empty_if_dir_missing(tmp_path):
    result = load_weeks(tmp_path / "nonexistent", n=4)
    assert result == []


# --- load_papers ---

def test_load_papers_loads_all_jsons(tmp_path):
    week = make_week(tmp_path, "2025-01-06", [sample_paper(), sample_paper()])
    result = load_papers([week])
    assert len(result) == 2


def test_load_papers_caps_anomalous_week(tmp_path):
    # Normal week: 10 papers; anomalous week: 400 papers (> 3x median)
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=i) for i in range(10)])
    anomalous = make_week(tmp_path, "2025-01-13", [sample_paper(cited=i) for i in range(400)])
    result = load_papers([normal, anomalous], cap_count=300)
    # Normal week uncapped (10), anomalous week capped at 300
    assert len(result) == 310


def test_load_papers_cap_selects_highest_cited(tmp_path):
    papers = [sample_paper(cited=i) for i in range(400)]
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=5)] * 10)
    anomalous = make_week(tmp_path, "2025-01-13", papers)
    result = load_papers([normal, anomalous], cap_count=300)
    anomalous_citations = sorted(
        [p["cited_by_count"] for p in result if p not in [sample_paper(cited=5)] * 10],
        reverse=True,
    )
    assert anomalous_citations[0] == 399  # highest cited included


def test_load_papers_does_not_cap_normal_week(tmp_path):
    week = make_week(tmp_path, "2025-01-06", [sample_paper() for _ in range(90)])
    result = load_papers([week])
    assert len(result) == 90


# --- truncate_abstract ---

def test_truncate_short_abstract_unchanged():
    text = "Short abstract here."
    assert truncate_abstract(text, max_words=150) == text


def test_truncate_long_abstract():
    words = ["word"] * 200
    text = " ".join(words)
    result = truncate_abstract(text, max_words=150)
    assert result.endswith("...")
    assert len(result.split()) == 150  # 150 words, last word has "..." appended


# --- build_payload ---

def test_build_payload_produces_jsonl():
    papers = [
        {
            "title": "My Paper",
            "venue_id": "ieee_twc",
            "published": "2025-02-10",
            "cited_by_count": 42,
            "abstract": "Some abstract text.",
        }
    ]
    result = build_payload(papers)
    assert "My Paper" in result
    assert "ieee_twc" in result
    assert "42" in result
    assert "2025-02" in result


def test_build_payload_replaces_pipes_in_title():
    papers = [
        {
            "title": "Paper A | Paper B",
            "venue_id": "ieee_twc",
            "published": "2025-02-10",
            "cited_by_count": 0,
            "abstract": "Abstract.",
        }
    ]
    result = build_payload(papers)
    lines = result.strip().split("\n")
    fields = lines[0].split(" | ")
    assert "|" not in fields[0]  # title field has no stray pipes


# --- inject_wiki_links ---

def test_inject_wiki_links_wraps_topic_headings():
    md = "### 1. Integrated Sensing and Communication\nsome content"
    result = inject_wiki_links(md)
    assert "### 1. [[Integrated Sensing and Communication]]" in result


def test_inject_wiki_links_ignores_other_headings():
    md = "## Summary\n### 1. My Topic\n## Trend Signals"
    result = inject_wiki_links(md)
    assert "## Summary" in result
    assert "## Trend Signals" in result
    assert "[[My Topic]]" in result


def test_inject_wiki_links_handles_multiple_topics():
    md = "### 1. Topic A\n### 2. Topic B\n### 3. Topic C"
    result = inject_wiki_links(md)
    assert "[[Topic A]]" in result
    assert "[[Topic B]]" in result
    assert "[[Topic C]]" in result


def test_inject_wiki_links_wraps_quoted_paper_titles():
    md = '- **Representative papers:** "Deep Learning for Beamforming in mmWave" (TWC, 8 citations)'
    result = inject_wiki_links(md)
    assert "[[Deep Learning for Beamforming in mmWave]]" in result
    assert '"Deep Learning for Beamforming in mmWave"' not in result


def test_inject_wiki_links_ignores_short_quoted_strings():
    # Short quoted strings (< 10 chars) should not be wrapped
    md = 'The method is "optimal" in this case.'
    result = inject_wiki_links(md)
    assert '"optimal"' in result
    assert "[[optimal]]" not in result



# --- write_report ---

def test_write_report_creates_file(tmp_path):
    path = write_report("# Report", tmp_path, "2026-02-27")
    assert path.exists()
    assert path.name == "2026-02-27-wireless-digest.md"


def test_write_report_creates_parent_dir(tmp_path):
    out_dir = tmp_path / "nested" / "dir"
    write_report("# Report", out_dir, "2026-02-27")
    assert out_dir.exists()


def test_write_report_content_correct(tmp_path):
    content = "# My Report\nSome content."
    path = write_report(content, tmp_path, "2026-02-27")
    assert path.read_text(encoding="utf-8") == content


def test_truncate_abstract_default_is_300_words():
    words = ["word"] * 350
    text = " ".join(words)
    result = truncate_abstract(text)  # uses default max_words, no explicit arg
    assert len(result.split()) == 300  # 300 words, last "word..." appended


def test_load_papers_default_cap_is_500(tmp_path):
    # anomalous week triggers cap — verify default cap is 500 not 300
    normal = make_week(tmp_path, "2025-01-06", [sample_paper(cited=i) for i in range(10)])
    anomalous = make_week(tmp_path, "2025-01-13", [sample_paper(cited=i) for i in range(600)])
    result = load_papers([normal, anomalous])  # uses default cap_count, no explicit arg
    # normal (10) + capped anomalous (500)
    assert len(result) == 510


def test_load_papers_excludes_missing_abstract(tmp_path):
    no_abstract = {**sample_paper(), "abstract": ""}
    null_abstract = {**sample_paper(), "abstract": None}
    whitespace_abstract = {**sample_paper(), "abstract": "   "}
    with_abstract = sample_paper()
    week = make_week(tmp_path, "2025-01-06", [no_abstract, null_abstract, whitespace_abstract, with_abstract])
    result = load_papers([week])
    assert len(result) == 1
    assert result[0]["abstract"] == with_abstract["abstract"]


# --- load_topic_registry ---

def test_load_topic_registry_returns_empty_when_missing(tmp_path):
    result = load_topic_registry(tmp_path / "topic_registry.json")
    assert result == []


def test_load_topic_registry_returns_list(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC", "Beamforming"], "updated": "2026-02-27"}')
    assert load_topic_registry(path) == ["ISAC", "Beamforming"]


def test_load_topic_registry_ignores_corrupt_file(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text("not json")
    assert load_topic_registry(path) == []


def test_load_topic_registry_returns_empty_for_missing_key(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"updated": "2026-01-01"}')  # valid JSON but no "topics" key
    assert load_topic_registry(path) == []


# --- extract_topics_from_markdown ---

def test_extract_topics_finds_wiki_link_headings():
    md = "### 1. [[ISAC]]\n### 2. [[Beamforming]]\n## Other Section"
    result = extract_topics_from_markdown(md)
    assert result == ["ISAC", "Beamforming"]


def test_extract_topics_returns_empty_when_no_matches():
    md = "## Summary\nNo topic headings here."
    assert extract_topics_from_markdown(md) == []


def test_extract_topics_ignores_non_numbered_headings():
    md = "### [[Not Numbered]]\n### 1. [[ISAC]]"
    result = extract_topics_from_markdown(md)
    assert result == ["ISAC"]


def test_extract_topics_deduplicates():
    md = "### 1. [[ISAC]]\n### 2. [[ISAC]]"
    result = extract_topics_from_markdown(md)
    assert result == ["ISAC"]


# --- update_topic_registry ---

def test_update_topic_registry_creates_file(tmp_path):
    path = tmp_path / "topic_registry.json"
    update_topic_registry(path, ["ISAC", "RIS"])
    assert path.exists()
    data = json.loads(path.read_text())
    assert "ISAC" in data["topics"]
    assert "RIS" in data["topics"]


def test_update_topic_registry_merges_with_existing(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC"], "updated": "2026-01-01"}')
    update_topic_registry(path, ["RIS", "Beamforming"])
    data = json.loads(path.read_text())
    assert data["topics"] == ["ISAC", "RIS", "Beamforming"]


def test_update_topic_registry_deduplicates(tmp_path):
    path = tmp_path / "topic_registry.json"
    path.write_text('{"topics": ["ISAC"], "updated": "2026-01-01"}')
    update_topic_registry(path, ["ISAC", "RIS"])
    data = json.loads(path.read_text())
    assert data["topics"].count("ISAC") == 1
