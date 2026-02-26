# Metrics Guide

This file defines recommended calculations for the report template metrics. The goal is stable, reproducible metrics using only local JSON + SQLite.

## Coverage
- New works ingested (this week): count of JSON files under `resource/by_date/YYYY-MM-DD` within the report week.
- Total works in local index: `SELECT COUNT(*) FROM papers`.
- Active venues this week: number of unique `venue_id` among the new works.
- Missing abstracts: count of new works with empty or null `abstract`.
- Missing DOIs: count of new works with empty `doi` (should be 0 with current pipeline).
- Deduplicated items: count of items skipped because DOI already existed in `papers`.
- Median pub-to-ingest lag (days): median of `(ingest_date - publication_date)` for new works.

## Clusters
Recommended default: `embedding_hdbscan`.

Inputs:
- Use titles+abstracts when available; otherwise titles only.
- Use a consistent embedding model across weeks.

Metrics:
- Size (this week): number of items assigned to the cluster in the report week.
- Size (baseline): number of items assigned to the cluster in the baseline window.
- Share (this week): size this week / total items this week.
- Share (baseline): size baseline / total items baseline.
- Momentum score: `log((n_current + alpha) / (n_baseline + alpha))`, alpha from `smoothing_alpha`.
- Emergence score: `n_current / max(1, n_baseline)` with a cap on outliers.
- Novelty score: `1 - Jaccard(top_terms_current, top_terms_baseline)` or `1 - cosine(tfidf_current, tfidf_baseline)`.

## Novel phrases
Use n-grams from titles+abstracts.
- current_df: document frequency in current week.
- baseline_df: document frequency in baseline window.
- novelty score: `log((current_df + 1) / (baseline_df + 1))`.

## Method tags
Method tags can be rule-based (keyword match) or LLM classified.
- Rising methods: positive momentum vs baseline.
- Declining methods: negative momentum vs baseline.

## Early impact (optional)
If you have `cited_by_count` from OpenAlex:
- Citation velocity: `cited_by_count / max(1, days_since_publication)`.
- Early impact leaders: top N by citation velocity.

## Cross-venue consensus
Consensus topics are clusters that appear in >= N venues in the current week.

## Quality checks
- Empty titles: should be 0.
- Empty venue_id: should be 0.
- Missing publication_date: track separately and exclude from lag metrics.
