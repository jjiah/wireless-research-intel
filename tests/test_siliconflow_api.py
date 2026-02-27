from __future__ import annotations

from pathlib import Path

import siliconflow_api as sfa


class DummyAPI(sfa.SiliconFlowAPI):
    def __init__(self) -> None:
        # Avoid env dependency in tests.
        self.api_key = "k"
        self.base_url = "https://api.siliconflow.cn/v1"
        self.timeout_seconds = 1.0
        self.calls: list[dict] = []

    def _request(  # type: ignore[override]
        self,
        method: str,
        path: str,
        *,
        json_body=None,
        params=None,
        files=None,
        data=None,
    ):
        self.calls.append(
            {
                "method": method,
                "path": path,
                "json": json_body,
                "params": params,
                "files": files,
                "data": data,
            }
        )
        return {"status": True, "data": {"echo": json_body, "path": path}}


def test_create_embeddings_payload():
    api = DummyAPI()
    out = api.create_embeddings(model="BAAI/bge-m3", input_text="hello", dimensions=1024)
    assert out["echo"]["model"] == "BAAI/bge-m3"
    assert out["echo"]["input"] == "hello"
    assert out["echo"]["encoding_format"] == "float"
    assert out["echo"]["dimensions"] == 1024
    assert api.calls[-1]["path"] == "/embeddings"


def test_create_rerank_payload():
    api = DummyAPI()
    out = api.create_rerank(
        model="BAAI/bge-reranker-v2-m3",
        query="wireless",
        documents=["doc1", "doc2"],
        top_n=1,
        return_documents=True,
        max_chunks_per_doc=2,
        overlap_tokens=80,
    )
    body = out["echo"]
    assert body["model"] == "BAAI/bge-reranker-v2-m3"
    assert body["query"] == "wireless"
    assert body["documents"] == ["doc1", "doc2"]
    assert body["top_n"] == 1
    assert body["return_documents"] is True
    assert body["max_chunks_per_doc"] == 2
    assert body["overlap_tokens"] == 80
    assert api.calls[-1]["path"] == "/rerank"


def test_create_image_generation_payload():
    api = DummyAPI()
    out = api.create_image_generation(
        model="black-forest-labs/FLUX.1-schnell",
        prompt="a city skyline",
        image_size="512x512",
        batch_size=2,
        negative_prompt="blurry",
        num_inference_steps=20,
        guidance_scale=3.5,
        seed=42,
        cfg=2.0,
    )
    body = out["echo"]
    assert body["model"] == "black-forest-labs/FLUX.1-schnell"
    assert body["prompt"] == "a city skyline"
    assert body["image_size"] == "512x512"
    assert body["batch_size"] == 2
    assert body["negative_prompt"] == "blurry"
    assert body["num_inference_steps"] == 20
    assert body["guidance_scale"] == 3.5
    assert body["seed"] == 42
    assert body["cfg"] == 2.0
    assert api.calls[-1]["path"] == "/images/generations"


def test_batch_endpoints_payloads_and_paths(tmp_path: Path):
    api = DummyAPI()
    f = tmp_path / "batch.jsonl"
    f.write_text('{"custom_id":"1","method":"POST","url":"/v1/chat/completions","body":{"model":"Qwen/Qwen3-8B"}}\n', encoding="utf-8")

    api.upload_batch_file(file_path=f)
    assert api.calls[-1]["path"] == "/files"
    assert api.calls[-1]["data"] == {"purpose": "batch"}

    api.list_batch_files()
    assert api.calls[-1]["path"] == "/files"
    assert api.calls[-1]["method"] == "GET"

    api.create_batch(
        input_file_id="file_abc123",
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"customer_id": "u1"},
        replace={"model": "Qwen/Qwen3-8B", "max_tokens": 2000},
    )
    assert api.calls[-1]["path"] == "/batches"
    assert api.calls[-1]["json"]["input_file_id"] == "file_abc123"
    assert api.calls[-1]["json"]["endpoint"] == "/v1/chat/completions"
    assert api.calls[-1]["json"]["completion_window"] == "24h"
    assert api.calls[-1]["json"]["metadata"]["customer_id"] == "u1"
    assert api.calls[-1]["json"]["replace"]["model"] == "Qwen/Qwen3-8B"

    api.get_batch(batch_id="batch_123")
    assert api.calls[-1]["path"] == "/batches/batch_123"

    api.list_batches(limit=10, after="batch_100")
    assert api.calls[-1]["path"] == "/batches"
    assert api.calls[-1]["params"] == {"limit": 10, "after": "batch_100"}

    api.cancel_batch(batch_id="batch_123")
    assert api.calls[-1]["path"] == "/batches/batch_123/cancel"
