#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx
from openai import OpenAI

DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"


class SiliconFlowAPIError(RuntimeError):
    """Raised when SiliconFlow HTTP/API calls fail."""


def load_env_file(path: Path) -> None:
    """Load key=value pairs from a .env-like file into os.environ."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"' ")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_siliconflow_config(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> tuple[str, str]:
    """Resolve SiliconFlow credentials from explicit args or environment."""
    load_env_file(Path("private.env"))
    resolved_key = api_key or os.getenv("SILICONFLOW_API_KEY")
    if not resolved_key:
        raise SiliconFlowAPIError("Missing SILICONFLOW_API_KEY in environment/private.env")
    resolved_base = base_url or os.getenv("SILICONFLOW_BASE_URL") or DEFAULT_BASE_URL
    return resolved_key, resolved_base.rstrip("/")


def build_openai_client(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
) -> OpenAI:
    """Build OpenAI-compatible client configured for SiliconFlow."""
    resolved_key, resolved_base = resolve_siliconflow_config(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=resolved_key, base_url=resolved_base)


class SiliconFlowAPI:
    """HTTP wrapper for SiliconFlow non-chat endpoints documented in API references."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 120.0,
    ) -> None:
        resolved_key, resolved_base = resolve_siliconflow_config(api_key=api_key, base_url=base_url)
        self.api_key = resolved_key
        self.base_url = resolved_base
        self.timeout_seconds = timeout_seconds

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if files is None:
            headers["Content-Type"] = "application/json"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body,
                    params=params,
                    files=files,
                    data=data,
                )
        except Exception as exc:
            raise SiliconFlowAPIError(f"Request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text[:500]
            raise SiliconFlowAPIError(f"HTTP {response.status_code} for {path}: {detail}")

        try:
            payload = response.json()
        except Exception as exc:
            raise SiliconFlowAPIError("Non-JSON response returned by SiliconFlow API") from exc
        return payload

    @staticmethod
    def _unwrap_data(payload: dict[str, Any]) -> dict[str, Any]:
        # Batch/file endpoints return wrapper fields: code/message/status/data.
        if isinstance(payload, dict) and "data" in payload and "status" in payload:
            data = payload.get("data")
            if isinstance(data, dict):
                return data
            return {"data": data}
        return payload

    def create_embeddings(
        self,
        *,
        model: str,
        input_text: str | list[str],
        encoding_format: str = "float",
        dimensions: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": model,
            "input": input_text,
            "encoding_format": encoding_format,
        }
        if dimensions is not None:
            body["dimensions"] = dimensions
        payload = self._request("POST", "/embeddings", json_body=body)
        return self._unwrap_data(payload)

    def create_rerank(
        self,
        *,
        model: str,
        query: str,
        documents: list[str],
        top_n: int | None = None,
        return_documents: bool = False,
        max_chunks_per_doc: int | None = None,
        overlap_tokens: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": model,
            "query": query,
            "documents": documents,
            "return_documents": return_documents,
        }
        if top_n is not None:
            body["top_n"] = top_n
        if max_chunks_per_doc is not None:
            body["max_chunks_per_doc"] = max_chunks_per_doc
        if overlap_tokens is not None:
            body["overlap_tokens"] = overlap_tokens
        payload = self._request("POST", "/rerank", json_body=body)
        return self._unwrap_data(payload)

    def create_image_generation(
        self,
        *,
        model: str,
        prompt: str,
        image_size: str = "1024x1024",
        batch_size: int = 1,
        negative_prompt: str | None = None,
        num_inference_steps: int | None = None,
        guidance_scale: float | None = None,
        seed: int | None = None,
        cfg: float | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "image_size": image_size,
            "batch_size": batch_size,
        }
        if negative_prompt is not None:
            body["negative_prompt"] = negative_prompt
        if num_inference_steps is not None:
            body["num_inference_steps"] = num_inference_steps
        if guidance_scale is not None:
            body["guidance_scale"] = guidance_scale
        if seed is not None:
            body["seed"] = seed
        if cfg is not None:
            body["cfg"] = cfg
        payload = self._request("POST", "/images/generations", json_body=body)
        return self._unwrap_data(payload)

    def upload_batch_file(self, *, file_path: Path, purpose: str = "batch") -> dict[str, Any]:
        if not file_path.exists():
            raise SiliconFlowAPIError(f"Batch file not found: {file_path}")
        with file_path.open("rb") as f:
            files = {"file": (file_path.name, f, "application/jsonl")}
            data = {"purpose": purpose}
            payload = self._request("POST", "/files", files=files, data=data)
        return self._unwrap_data(payload)

    def list_batch_files(self) -> dict[str, Any]:
        payload = self._request("GET", "/files")
        return self._unwrap_data(payload)

    def create_batch(
        self,
        *,
        input_file_id: str,
        endpoint: str = "/v1/chat/completions",
        completion_window: str = "24h",
        metadata: dict[str, Any] | None = None,
        replace: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "input_file_id": input_file_id,
            "endpoint": endpoint,
            "completion_window": completion_window,
        }
        if metadata:
            body["metadata"] = metadata
        if replace:
            body["replace"] = replace
        payload = self._request("POST", "/batches", json_body=body)
        return self._unwrap_data(payload)

    def get_batch(self, *, batch_id: str) -> dict[str, Any]:
        payload = self._request("GET", f"/batches/{batch_id}")
        return self._unwrap_data(payload)

    def list_batches(self, *, limit: int | None = None, after: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after
        payload = self._request("GET", "/batches", params=params or None)
        return self._unwrap_data(payload)

    def cancel_batch(self, *, batch_id: str) -> dict[str, Any]:
        payload = self._request("POST", f"/batches/{batch_id}/cancel")
        return self._unwrap_data(payload)


def pretty_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)
