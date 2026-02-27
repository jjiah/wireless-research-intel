#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from siliconflow_api import SiliconFlowAPI, SiliconFlowAPIError, pretty_json


def _read_lines(path: Path) -> list[str]:
    return [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _json_or_none(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    return json.loads(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SiliconFlow API utility CLI.")
    parser.add_argument("--base-url", help="Override SiliconFlow base URL.")
    parser.add_argument("--timeout-seconds", type=float, default=120.0, help="HTTP timeout seconds.")

    sub = parser.add_subparsers(dest="command", required=True)

    p_emb = sub.add_parser("embeddings", help="Create embeddings.")
    p_emb.add_argument("--model", required=True)
    p_emb.add_argument("--input", action="append", dest="inputs", help="Input text (repeatable).")
    p_emb.add_argument("--input-file", type=Path, help="UTF-8 text file, one input per line.")
    p_emb.add_argument("--dimensions", type=int)
    p_emb.add_argument("--encoding-format", default="float")

    p_rr = sub.add_parser("rerank", help="Create rerank.")
    p_rr.add_argument("--model", required=True)
    p_rr.add_argument("--query", required=True)
    p_rr.add_argument("--doc", action="append", dest="docs", help="Document text (repeatable).")
    p_rr.add_argument("--docs-file", type=Path, help="UTF-8 file, one doc per line.")
    p_rr.add_argument("--top-n", type=int)
    p_rr.add_argument("--return-documents", action="store_true")
    p_rr.add_argument("--max-chunks-per-doc", type=int)
    p_rr.add_argument("--overlap-tokens", type=int)

    p_img = sub.add_parser("image-generate", help="Generate images.")
    p_img.add_argument("--model", required=True)
    p_img.add_argument("--prompt", required=True)
    p_img.add_argument("--image-size", default="1024x1024")
    p_img.add_argument("--batch-size", type=int, default=1)
    p_img.add_argument("--negative-prompt")
    p_img.add_argument("--num-inference-steps", type=int)
    p_img.add_argument("--guidance-scale", type=float)
    p_img.add_argument("--seed", type=int)
    p_img.add_argument("--cfg", type=float)

    p_fu = sub.add_parser("batch-upload-file", help="Upload batch JSONL file.")
    p_fu.add_argument("--file", type=Path, required=True)
    p_fu.add_argument("--purpose", default="batch")

    sub.add_parser("batch-list-files", help="List batch files.")

    p_bc = sub.add_parser("batch-create", help="Create batch.")
    p_bc.add_argument("--input-file-id", required=True)
    p_bc.add_argument("--endpoint", default="/v1/chat/completions")
    p_bc.add_argument("--completion-window", default="24h")
    p_bc.add_argument("--metadata-json", help='JSON object, e.g. \'{"customer":"u1"}\'')
    p_bc.add_argument("--replace-json", help='JSON object, e.g. \'{"model":"Qwen/Qwen3-8B"}\'')

    p_bg = sub.add_parser("batch-get", help="Get batch.")
    p_bg.add_argument("--batch-id", required=True)

    p_bl = sub.add_parser("batch-list", help="List batches.")
    p_bl.add_argument("--limit", type=int)
    p_bl.add_argument("--after")

    p_bx = sub.add_parser("batch-cancel", help="Cancel batch.")
    p_bx.add_argument("--batch-id", required=True)

    return parser


def run() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        api = SiliconFlowAPI(base_url=args.base_url, timeout_seconds=args.timeout_seconds)
    except SiliconFlowAPIError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    try:
        if args.command == "embeddings":
            inputs: list[str] = []
            if args.inputs:
                inputs.extend(args.inputs)
            if args.input_file:
                inputs.extend(_read_lines(args.input_file))
            if not inputs:
                raise SiliconFlowAPIError("Provide at least one --input or --input-file.")
            payload = api.create_embeddings(
                model=args.model,
                input_text=inputs if len(inputs) > 1 else inputs[0],
                encoding_format=args.encoding_format,
                dimensions=args.dimensions,
            )
            print(pretty_json(payload))
            return 0

        if args.command == "rerank":
            docs: list[str] = []
            if args.docs:
                docs.extend(args.docs)
            if args.docs_file:
                docs.extend(_read_lines(args.docs_file))
            if not docs:
                raise SiliconFlowAPIError("Provide at least one --doc or --docs-file.")
            payload = api.create_rerank(
                model=args.model,
                query=args.query,
                documents=docs,
                top_n=args.top_n,
                return_documents=args.return_documents,
                max_chunks_per_doc=args.max_chunks_per_doc,
                overlap_tokens=args.overlap_tokens,
            )
            print(pretty_json(payload))
            return 0

        if args.command == "image-generate":
            payload = api.create_image_generation(
                model=args.model,
                prompt=args.prompt,
                image_size=args.image_size,
                batch_size=args.batch_size,
                negative_prompt=args.negative_prompt,
                num_inference_steps=args.num_inference_steps,
                guidance_scale=args.guidance_scale,
                seed=args.seed,
                cfg=args.cfg,
            )
            print(pretty_json(payload))
            return 0

        if args.command == "batch-upload-file":
            payload = api.upload_batch_file(file_path=args.file, purpose=args.purpose)
            print(pretty_json(payload))
            return 0

        if args.command == "batch-list-files":
            payload = api.list_batch_files()
            print(pretty_json(payload))
            return 0

        if args.command == "batch-create":
            payload = api.create_batch(
                input_file_id=args.input_file_id,
                endpoint=args.endpoint,
                completion_window=args.completion_window,
                metadata=_json_or_none(args.metadata_json),
                replace=_json_or_none(args.replace_json),
            )
            print(pretty_json(payload))
            return 0

        if args.command == "batch-get":
            payload = api.get_batch(batch_id=args.batch_id)
            print(pretty_json(payload))
            return 0

        if args.command == "batch-list":
            payload = api.list_batches(limit=args.limit, after=args.after)
            print(pretty_json(payload))
            return 0

        if args.command == "batch-cancel":
            payload = api.cancel_batch(batch_id=args.batch_id)
            print(pretty_json(payload))
            return 0

        raise SiliconFlowAPIError(f"Unsupported command: {args.command}")
    except SiliconFlowAPIError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON argument: {exc}", file=sys.stderr)
        return 2


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
