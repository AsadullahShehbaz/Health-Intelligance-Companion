import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals.evaluate_rag_vs_ft import LlamaServerClient, run_arm


class FlakyLLM:
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        if self.calls < 2:
            raise TimeoutError("timed out")

        class _Response:
            content = "Recovered answer"

        return _Response()


def test_llama_server_complete_retries_on_timeout():
    client = object.__new__(LlamaServerClient)
    client.llm = FlakyLLM()

    generated, latency = client.complete("question")

    assert generated == "Recovered answer"
    assert latency >= 0.0
    assert client.llm.calls == 2


def test_run_arm_resumes_from_checkpoint(tmp_path):
    checkpoint_path = tmp_path / "no_rag_results.json"
    checkpoint_path.write_text(
        json.dumps([
            {
                "id": "q001",
                "question": "Already done",
                "reference_answer": "answer",
                "generated": "done",
                "latency_s": 1.0,
                "is_mcq": False,
                "correct_option": None,
                "predicted_option": None,
            }
        ]),
        encoding="utf-8",
    )

    rows = [
        {"id": "q001", "question": "Already done", "reference_answer": "answer"},
        {"id": "q002", "question": "Next question", "reference_answer": "next answer"},
        {"id": "q003", "question": "Final question", "reference_answer": "final answer"},
    ]
    llama = SimpleNamespace(complete=lambda prompt: ("new answer", 0.5))

    results = run_arm(
        "no-rag",
        rows,
        llama,
        retriever=None,
        cfg=SimpleNamespace(OUTPUT_DIR=str(tmp_path)),
        checkpoint_path=checkpoint_path,
    )

    assert [r["id"] for r in results] == ["q002", "q003"]
    assert len(results) == 2
