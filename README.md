# wireless-research-intel
Venue-Based Weekly Research Observatory: Crawl metadata from authoritative wireless communication venues. Perform topic clustering. Detect topic trend changes over time. Generate structured research summary.

## Weekly report output
Reports are written to your Obsidian vault folder using `weekly_report.py` and `report_config.yaml`.

Default config:
- `report_dir`: `E:\0 notebook\01 Resources`
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

## Metadata ingestion
Fetch new papers via RSS and store JSON metadata into per-venue folders under `resource/`.

Run:
```powershell
python ingest_rss.py
```

Behavior:
- Each paper is saved as `resource/by_date/YYYY-MM-DD/{doi}.json`
- Existing DOI files are skipped
- Items without DOI are skipped
- SQLite index is stored at `resource/index.sqlite` for fast dedupe/search (lean: no abstract)

Time range:
- First run (previous year): `python ingest_rss.py --lookback-days 365`
- Subsequent runs: `python ingest_rss.py` (uses `resource/last_run.json`)
