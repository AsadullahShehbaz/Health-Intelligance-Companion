# Implementation Plan - Ingestion & OCR Pipeline Refactoring

This plan details the changes to move OCR extraction from the LangGraph workflow to the FastAPI API controller layer. This keeps heavy image data (`image_base64`) out of the database checkpointer, simplifies the graph state, and maintains `/agent/invoke` request/response compatibility with the React client.

## Proposed Changes

---

### API Controller Layer

#### [MODIFY] [agent.py](file:///c:/Fine%20Tuning/code/app/api/agent.py)
- Import `extract_text_from_base64` from `app.core.rag.ocr`.
- Update the `invoke` endpoint:
  - Check if `req.image_base64` is provided.
  - If provided, call `extract_text_from_base64(req.image_base64)` to parse the image text synchronously.
  - Pass the extracted text as a parameter `ocr_text` (defaulting to empty string) into the `run_agent` service call.

### Business Logic / Service Layer

#### [MODIFY] [agent_service.py](file:///c:/Fine%20Tuning/code/app/services/agent_service.py)
- Update `run_agent(req)` function signature to accept `ocr_text: str = ""`.
- Update `_build_initial_state` function signature to accept `ocr_text: str = ""`.
- Update the returned dict in `_build_initial_state`:
  - Remove `"image_base64"` and `"has_image"` keys.
  - Inject the `ocr_text` parameter directly into the `"ocr_context"` key.

### Agent / LangGraph Flow

#### [MODIFY] [graph.py](file:///c:/Fine%20Tuning/code/app/agent/graph.py)
- Remove the import of `ocr_node` from `app.agent.nodes.ocr_node`.
- In `build_health_agent()`:
  - Remove `graph.add_node("ocr", _logged("ocr")(ocr_node))` node addition.
  - Remove `graph.add_edge("ocr", "translate_in")` edge addition.
  - Set the state graph entry point from `"ocr"` to `"translate_in"` by modifying `graph.set_entry_point("ocr")` to `graph.set_entry_point("translate_in")`.

---

## Verification Plan

### Automated Tests
We will verify the implementation by executing the existing OCR test script:
```bash
conda activate ft-project
python app/tests/test-ocr.py
```
This test posts a sample image as `image_base64` to the `/agent/invoke` endpoint, which will trigger the refactored synchronous OCR process in the controller, pass it down to `run_agent`, and verify that the backend returns correct answers based on the image content.

Additionally, we can run general tests to ensure we did not break other flows:
```bash
python app/tests/test_chat.py
```

### Manual Verification
- We will verify that compiling the graph without the `ocr` node succeeds on startup.
- We will check that the response from the API matches the `AgentResponse` schema and contains expected OCR context information.
