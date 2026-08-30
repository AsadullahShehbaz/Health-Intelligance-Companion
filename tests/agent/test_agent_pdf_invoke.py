from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_agent_invoke_merges_pdf_text(monkeypatch):
    payload = {
        "patient_id": "123",
        "query": "Interpret this report",
        "pdf_base64": "ZmFrZS1wZGY=",
    }

    monkeypatch.setattr(
        "app.api.agent.extract_text_from_pdf_base64",
        lambda *_args, **_kwargs: "PDF text extracted here",
    )

    with patch("app.api.agent.run_agent", return_value={
        "answer": "done",
        "detected_lang": "en",
        "needs_rag": False,
        "sources": [],
        "save_memory": False,
    }) as mock_run_agent:
        response = client.post("/agent/invoke", json=payload)

    assert response.status_code == 200
    assert mock_run_agent.call_args.args[1] == "PDF text extracted here"
