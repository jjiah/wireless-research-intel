# wireless-research-intel
Venue-Based Weekly Research Observatory: Crawl metadata from authoritative wireless communication venues. Perform topic clustering. Detect topic trend changes over time. Generate structured research summary.

## Weekly report output
Reports are written to your Obsidian vault folder using `weekly_report.py` and `report_config.yaml`.

Private config:
- Set `REPORT_DIR` in `private.env` (kept out of git).
- `filename_template`: `weekly-wireless-{week_start}.md`
- `week_start_day`: `sunday`

Run:
```powershell
python weekly_report.py
```

Optional input (JSON or CSV with `title,venue,published,url,abstract`):
```powershell
python weekly_report.py --input data\weekly\items.csv
```

Override week by date (any date inside the target week):
```powershell
python weekly_report.py --date 2026-02-22
```

Metrics definitions:
- See `METRICS.md`.

## Metadata ingestion (OpenAlex-only)
Fetch new papers via OpenAlex and store JSON metadata into per-venue folders under `resource/`.

Run:
```powershell
python ingest_openalex.py
```

Filter venues:
```powershell
python ingest_openalex.py --only ieee_twc,ieee_jsac
python ingest_openalex.py --exclude ieee_vtc,ieee_icc
```

Behavior:
- Each paper is saved as `resource/by_date/YYYY-MM-DD/{doi}.json`
- Existing DOI files are skipped
- Items without DOI are skipped
- SQLite index is stored at `resource/index.sqlite` for fast dedupe/search (lean: no abstract)
- Only OpenAlex works with type `article` or `preprint` are saved (others are skipped)
- Authorships are stored as author + institution names only (lean)

OpenAlex:
```powershell
notepad openalex.env
python ingest_openalex.py --lookback-days 60
```

Sources:
- Add `openalex_source_id` for each venue in `sources.yaml`.

Manage sources:
```powershell
python manage_sources.py list
python manage_sources.py show ieee_twc
python manage_sources.py set-openalex ieee_twc S123456789
python manage_sources.py add --id myconf --name "My Conf" --type conference --publisher IEEE --openalex-source-ids S123,S456
python manage_sources.py remove myconf
```

Auto-resolve OpenAlex source IDs:
```powershell
notepad openalex.env
python resolve_openalex_ids.py
```

Discover multiple sources for conferences:
```powershell
python resolve_openalex_ids.py --discover-conferences 3 --overwrite
```

Validate source IDs:
```powershell
python resolve_openalex_ids.py --validate
```

Time range:
- First run (previous year): `python ingest_openalex.py --lookback-days 365`
- Subsequent runs: `python ingest_openalex.py` (uses `resource/last_run.json`)
