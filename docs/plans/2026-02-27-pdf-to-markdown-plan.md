# PDF to Markdown (DeepSeek OCR via SiliconFlow) Plan

## Summary
Implement a standalone Python CLI (`pdf_to_markdown.py`) that:
1. Converts local PDF files to Markdown through SiliconFlow + DeepSeek OCR.
2. Automatically chunks large PDFs and adaptively splits chunks when payload/context limits are hit.
3. Persists per-chunk outputs and runtime metadata to support reliable resume.
4. Merges chunk markdown into a single clean `final.md`.

Secrets are loaded from `private.env` and process environment only. No secrets are hardcoded or written to generated artifacts.

## Public Interface
```bash
python pdf_to_markdown.py \
  --input <pdf> \
  [--output <md>] \
  [--chunk-pages 30] \
  [--max-workers 1] \
  [--resume] \
  [--output-root resource/pdf_markdown] \
  [--model deepseek-ai/DeepSeek-OCR] \
  [--base-url https://api.siliconflow.com/v1] \
  [--max-retries 3] \
  [--timeout-seconds 120]
```

## Runtime Layout
For each input PDF state (path + size + mtime), create:
`resource/pdf_markdown/<pdf_stem>-<hash8>/`

Subfolders:
- `chunks_pdf/`: generated chunk PDFs
- `chunks_md/`: OCR markdown results per chunk
- `logs/`: reserved runtime directory
- `manifest.json`: chunk states, attempts, errors, run timestamps

## Behavior
1. Load `private.env`.
2. Resolve config precedence: CLI > env var > defaults.
3. Validate key and input path.
4. Create or resume run via `manifest.json`.
5. Process pending chunks:
   - Generate chunk PDF from source pages.
   - OCR with retry/backoff for transient errors.
   - If request too large, split chunk into two smaller chunks.
6. If all chunks done, merge markdown in page order:
   - normalize line endings
   - remove exact overlap at chunk boundaries
   - close unmatched markdown code fence if needed
7. Write final output (`--output` or run dir `final.md`).

## Security
- Key source: `SILICONFLOW_API_KEY` from env/private.env only.
- Never include key in logs, manifest, or output markdown.
- Keep `private.env` local and git-ignored.

## Testing Scope
- Config/env precedence + missing-key fail-fast
- Chunk building/splitting
- Retry classification and behavior
- Adaptive split flow
- Resume skipping completed chunks
- Merge normalization and fence balancing

