# System Overview
This repo hosts metadata ingestion and normalization tooling for wireless-research sources.

Current pipeline stages:
1. Fetch metadata from OpenAlex sources listed in `sources.yaml`.
2. Normalize records into a common JSON schema.
3. Persist DOI index to SQLite for dedupe (`resource/index.sqlite`).
4. Write normalized records into publication-week folders (`resource/by_publication_week/<week_start>/`).
5. Track incremental ingestion state via `resource/last_run.json`.
