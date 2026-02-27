from __future__ import annotations

import sys
from pathlib import Path

import siliconflow_tools as sft


class DummyAPI:
    def __init__(self, **kwargs):
        self.calls = []

    def create_embeddings(self, **kwargs):
        self.calls.append(("embeddings", kwargs))
        return {"ok": True, "kind": "embeddings", "args": kwargs}

    def create_rerank(self, **kwargs):
        self.calls.append(("rerank", kwargs))
        return {"ok": True, "kind": "rerank", "args": kwargs}

    def create_image_generation(self, **kwargs):
        self.calls.append(("image", kwargs))
        return {"ok": True, "kind": "image", "args": kwargs}

    def upload_batch_file(self, **kwargs):
        self.calls.append(("upload", kwargs))
        return {"ok": True, "kind": "upload", "args": kwargs}

    def list_batch_files(self):
        self.calls.append(("list_files", {}))
        return {"ok": True, "kind": "list_files"}

    def create_batch(self, **kwargs):
        self.calls.append(("create_batch", kwargs))
        return {"ok": True, "kind": "create_batch", "args": kwargs}

    def get_batch(self, **kwargs):
        self.calls.append(("get_batch", kwargs))
        return {"ok": True, "kind": "get_batch", "args": kwargs}

    def list_batches(self, **kwargs):
        self.calls.append(("list_batches", kwargs))
        return {"ok": True, "kind": "list_batches", "args": kwargs}

    def cancel_batch(self, **kwargs):
        self.calls.append(("cancel_batch", kwargs))
        return {"ok": True, "kind": "cancel_batch", "args": kwargs}


def test_embeddings_cli_with_input_file(monkeypatch, tmp_path: Path, capsys):
    input_file = tmp_path / "input.txt"
    input_file.write_text("alpha\nbeta\n", encoding="utf-8")
    dummy = DummyAPI()
    monkeypatch.setattr(sft, "SiliconFlowAPI", lambda **kwargs: dummy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "siliconflow_tools.py",
            "embeddings",
            "--model",
            "BAAI/bge-m3",
            "--input-file",
            str(input_file),
        ],
    )
    rc = sft.run()
    out = capsys.readouterr().out
    assert rc == 0
    assert '"kind": "embeddings"' in out
    assert dummy.calls[0][1]["input_text"] == ["alpha", "beta"]


def test_rerank_cli_with_inline_docs(monkeypatch, capsys):
    dummy = DummyAPI()
    monkeypatch.setattr(sft, "SiliconFlowAPI", lambda **kwargs: dummy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "siliconflow_tools.py",
            "rerank",
            "--model",
            "BAAI/bge-reranker-v2-m3",
            "--query",
            "wireless",
            "--doc",
            "doc-a",
            "--doc",
            "doc-b",
            "--top-n",
            "1",
            "--return-documents",
        ],
    )
    rc = sft.run()
    out = capsys.readouterr().out
    assert rc == 0
    assert '"kind": "rerank"' in out
    kwargs = dummy.calls[0][1]
    assert kwargs["documents"] == ["doc-a", "doc-b"]
    assert kwargs["top_n"] == 1
    assert kwargs["return_documents"] is True


def test_batch_create_json_args(monkeypatch, capsys):
    dummy = DummyAPI()
    monkeypatch.setattr(sft, "SiliconFlowAPI", lambda **kwargs: dummy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "siliconflow_tools.py",
            "batch-create",
            "--input-file-id",
            "file_123",
            "--metadata-json",
            '{"customer":"u1"}',
            "--replace-json",
            '{"model":"Qwen/Qwen3-8B","max_tokens":2000}',
        ],
    )
    rc = sft.run()
    out = capsys.readouterr().out
    assert rc == 0
    assert '"kind": "create_batch"' in out
    kwargs = dummy.calls[0][1]
    assert kwargs["metadata"]["customer"] == "u1"
    assert kwargs["replace"]["model"] == "Qwen/Qwen3-8B"


def test_image_generate_cli_args(monkeypatch, capsys):
    dummy = DummyAPI()
    monkeypatch.setattr(sft, "SiliconFlowAPI", lambda **kwargs: dummy)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "siliconflow_tools.py",
            "image-generate",
            "--model",
            "black-forest-labs/FLUX.1-schnell",
            "--prompt",
            "futuristic city",
            "--image-size",
            "512x512",
            "--batch-size",
            "2",
            "--negative-prompt",
            "blurry",
            "--num-inference-steps",
            "20",
            "--guidance-scale",
            "3.5",
            "--seed",
            "42",
            "--cfg",
            "2.0",
        ],
    )
    rc = sft.run()
    out = capsys.readouterr().out
    assert rc == 0
    assert '"kind": "image"' in out
    kwargs = dummy.calls[0][1]
    assert kwargs["image_size"] == "512x512"
    assert kwargs["batch_size"] == 2
    assert kwargs["negative_prompt"] == "blurry"
    assert kwargs["num_inference_steps"] == 20
    assert kwargs["guidance_scale"] == 3.5
    assert kwargs["seed"] == 42
    assert kwargs["cfg"] == 2.0


def test_embeddings_cli_requires_input(monkeypatch, capsys):
    dummy = DummyAPI()
    monkeypatch.setattr(sft, "SiliconFlowAPI", lambda **kwargs: dummy)
    monkeypatch.setattr(
        sys,
        "argv",
        ["siliconflow_tools.py", "embeddings", "--model", "BAAI/bge-m3"],
    )
    rc = sft.run()
    err = capsys.readouterr().err
    assert rc == 2
    assert "Provide at least one --input or --input-file." in err
