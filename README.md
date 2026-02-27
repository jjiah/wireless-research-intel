# wireless-research-intel

OpenAlex metadata ingestion for wireless venues with incremental updates and publication-week storage.

## What this project now does
1. Fetch new paper metadata since the last run date.
2. Store each new paper JSON into publication-week folders:
   - `resource/by_publication_week/<week_start>/<doi>.json`

## Core scripts
- `ingest_openalex.py`: ingest metadata from OpenAlex and write weekly-organized JSON files.
- `organize_by_publication_date.py`: reorganize existing JSON files by publication `day` or `week`.
- `manage_sources.py`: manage venue source config in `sources.yaml`.
- `resolve_openalex_ids.py`: discover/validate OpenAlex source IDs.

## Incremental ingestion (since last run)
State file:
- `resource/last_run.json`

Behavior:
- If `--since` is not provided, `ingest_openalex.py` uses `resource/last_run.json`.
- After run, it updates `resource/last_run.json`.
- DOI-based dedupe is enforced via `resource/index.sqlite`.

Run:
```powershell
python ingest_openalex.py
```

First run / backfill example:
```powershell
python ingest_openalex.py --lookback-days 365
```

Manual date override example:
```powershell
python ingest_openalex.py --since 2026-01-01
```

Bounded range example:
```powershell
python ingest_openalex.py --since 2024-12-23 --until 2024-12-29
```

Note:
- When using a custom date window (`--since`, `--until`, or `--lookback-days`), `resource/last_run.json` is not updated.

## Publication-week organization
By default, ingestion writes to:
- `resource/by_publication_week/<week_start>/<doi>.json`

Week convention:
```powershell
python ingest_openalex.py --week-start-day monday
python ingest_openalex.py --week-start-day sunday
```

## Reorganize existing legacy data
If you already have files in other layouts (for example `resource/by_date`), reorganize them:

By publication week:
```powershell
python organize_by_publication_date.py --input-root resource/by_date --output-root resource/by_publication_week --group-by week --week-start-day monday
```

By publication day:
```powershell
python organize_by_publication_date.py --input-root resource/by_date --output-root resource/by_publication_date --group-by day
```

## Sources
Manage venues in `sources.yaml`:
```powershell
python manage_sources.py list
python manage_sources.py show ieee_twc
python manage_sources.py set-openalex ieee_twc S123456789
```

Auto-resolve source IDs:
```powershell
python resolve_openalex_ids.py
python resolve_openalex_ids.py --validate
```

## Automation

To run the full pipeline (ingest + report) automatically every Monday at 08:00:

1. Open **Task Scheduler** (search in Start menu).
2. Click **Action → Import Task…**
3. Select `automation/weekly_digest.xml` from this repo.
4. Enter your Windows account password when prompted.
5. The task appears under `\wireless-research-intel\weekly-digest`.

If your computer is off at 08:00, the task runs on next startup (requires network).

To run manually at any time:

```bat
run_pipeline.bat
```
