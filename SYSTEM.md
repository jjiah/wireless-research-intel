# System Overview
This repo will host the crawlers, normalization, topic modeling, and reporting code.

Planned pipeline stages:
1. Fetch metadata from RSS or HTML sources.
2. Normalize records into a common schema.
3. Persist to SQLite and weekly CSV snapshots.
4. Embed abstracts and cluster into topics.
5. Track weekly topic deltas and generate reports.
