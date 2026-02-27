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
2. Open `automation/weekly_digest.xml` in a text editor and replace the two
   placeholder path values with your actual repo path (in `<Command>` and `<WorkingDirectory>`).
3. Click **Action → Import Task…**
4. Select the edited `automation/weekly_digest.xml`.
5. The task appears under `\wireless-research-intel\weekly-digest`.

> **Note:** No password is stored. The task runs only while you are logged in — you are fully in control.
> If Monday 08:00 passes while you are logged in but the task hasn't run yet, it will run on your next login (requires network).

To run manually at any time:

```bat
run_pipeline.bat
```

## Dashboard

A local web dashboard for running the pipeline, configuring settings, and managing venues.

**Install:**

```bash
pip install flask
```

**Run:**

```bash
python dashboard.py
```

Open [http://localhost:5000](http://localhost:5000).

| Page | URL | What it does |
| ---- | --- | ------------ |
| Home | `/` | Shows last ingest date and report count |
| Run Pipeline | `/run` | Streams live output of ingest + report |
| Settings | `/settings` | Edit API keys and REPORT\_DIR |
| Venues | `/venues` | Add/remove venues in `sources.yaml` |

## PDF to Markdown (DeepSeek OCR via SiliconFlow)

Standalone converter script:

```powershell
python pdf_to_markdown.py --input path\to\paper.pdf
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure API key (local only)

Put your key in `private.env` (already git-ignored):

```env
SILICONFLOW_API_KEY=your_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-OCR
```

`private.env` must stay local and must not be committed.

### CLI usage

```powershell
python pdf_to_markdown.py `
  --input path\to\paper.pdf `
  --output resource\pdf_markdown\paper.md `
  --chunk-pages 30 `
  --min-chars-per-page 160 `
  --resume `
  --max-retries 3 `
  --timeout-seconds 120
```

Defaults:
- Output root: `resource/pdf_markdown`
- Model: `deepseek-ai/DeepSeek-OCR`
- Base URL: `https://api.siliconflow.cn/v1`

### Large PDFs

The script starts with page-based chunks (`--chunk-pages`) and automatically
splits failed oversized chunks into smaller ranges until they succeed (or reach
single-page chunks).

It also includes an incomplete-output heuristic for multi-page chunks. If a
chunk returns suspiciously short content for its page span, the script
automatically re-splits that chunk and retries on smaller ranges.

For digital PDFs that contain extractable text, the script also uses a
chunk-level fallback: when OCR output is clearly corrupted (for example,
repeated-token noise like `1. 1. 1. ...`), it switches that chunk to native
PDF text extraction and keeps numbered lists/paragraphs.

### Resume interrupted runs

Re-run the same input with `--resume`:

```powershell
python pdf_to_markdown.py --input path\to\paper.pdf --resume
```

Completed chunk markdown is reused; only pending/failed retriable chunks run again.

### Runtime artifacts

Each run uses:
`resource/pdf_markdown/<pdf_stem>-<hash8>/`

Includes:
- `chunks_pdf/`
- `chunks_md/`
- `manifest.json`
- `final.md` (unless `--output` is provided)

### Troubleshooting

- `Missing SILICONFLOW_API_KEY`: set key in `private.env` or process environment.
- Repeated payload/context errors: lower `--chunk-pages`.
- Missing content from large chunks: rerun with `--chunk-pages 1` (safest),
  or lower `--min-chars-per-page` if your document is very image-heavy.
- Rate limit or transient API failures: use `--resume` to continue after retry window.

## SiliconFlow Advanced API Wrapper

`siliconflow_api.py` now provides reusable wrappers aligned with SiliconFlow API docs for:
- Embeddings (`/v1/embeddings`)
- Rerank (`/v1/rerank`)
- Images generations (`/v1/images/generations`)
- Batch file upload/list (`/v1/files`)
- Batch create/get/list/cancel (`/v1/batches...`)

Example:

```python
from pathlib import Path
from siliconflow_api import SiliconFlowAPI

api = SiliconFlowAPI()  # reads SILICONFLOW_API_KEY / SILICONFLOW_BASE_URL

emb = api.create_embeddings(
    model="BAAI/bge-m3",
    input_text=["wireless scheduling", "semantic communication"],
)

rr = api.create_rerank(
    model="BAAI/bge-reranker-v2-m3",
    query="highly relevant wireless survey",
    documents=["doc A", "doc B", "doc C"],
    top_n=2,
    return_documents=True,
)

img = api.create_image_generation(
    model="black-forest-labs/FLUX.1-schnell",
    prompt="futuristic urban air mobility corridor",
    image_size="1024x1024",
    batch_size=1,
)

uploaded = api.upload_batch_file(file_path=Path("requests.jsonl"))
batch = api.create_batch(
    input_file_id=uploaded.get("id") or uploaded["data"]["id"],
    endpoint="/v1/chat/completions",
    completion_window="24h",
)
```

### Command-line utility (`siliconflow_tools.py`)

Call the same APIs without writing Python code:

```powershell
# Embeddings
python siliconflow_tools.py embeddings --model BAAI/bge-m3 --input "hello world"

# Rerank
python siliconflow_tools.py rerank --model BAAI/bge-reranker-v2-m3 --query "wireless" --doc "doc A" --doc "doc B" --top-n 1 --return-documents

# Images
python siliconflow_tools.py image-generate --model black-forest-labs/FLUX.1-schnell --prompt "futuristic air mobility corridor" --image-size 1024x1024 --batch-size 1

# Batch file upload / list
python siliconflow_tools.py batch-upload-file --file .\requests.jsonl
python siliconflow_tools.py batch-list-files

# Batch create / get / list / cancel
python siliconflow_tools.py batch-create --input-file-id file_xxx --endpoint /v1/chat/completions --completion-window 24h
python siliconflow_tools.py batch-get --batch-id batch_xxx
python siliconflow_tools.py batch-list --limit 20
python siliconflow_tools.py batch-cancel --batch-id batch_xxx
```
