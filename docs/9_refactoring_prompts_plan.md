# Coding Agent Refactoring Plan (Vite + React Frontend Compatible)
## Project: AI-Powered Personal Health Intelligence Companion

This document provides a step-by-step implementation plan for a coding agent to refactor and simplify the backend. 

> [!IMPORTANT]
> **React Frontend Compatibility Constraint:** The React frontend is 100% complete and communicates directly with the backend. We **MUST NOT** modify existing API endpoint URLs, request payload schemas, or response JSON structures. All API contracts (under `/auth/*` and `/agent/*`) must remain backward-compatible.

---

## Phase 1: Ingestion & OCR Pipeline Refactoring

### Goal
Extract OCR parsing out of the LangGraph flow and run it inside the FastAPI endpoint layer. This keeps heavy image data (`image_base64`) out of the database checkpointer, simplifies the graph state, and maintains `/agent/invoke` request/response compatibility with the React client.

### Prompt for Coding Agent
```text
Refactor the OCR ingestion pipeline to run in the FastAPI API controller layer instead of inside the LangGraph.

Do the following:
1. In `app/api/agent.py`, update the `invoke` endpoint:
   - Check if `req.image_base64` is provided in the request payload.
   - If provided, call `extract_text_from_base64` from `app.core.rag.ocr` to parse the image text synchronously.
   - Pass the extracted OCR text into the `run_agent` service call.
2. In `app/services/agent_service.py`, update `run_agent(req)` and `_build_initial_state`:
   - Receive the extracted OCR text parameter.
   - Inject the OCR text directly into the `ocr_context` key of the initial state.
   - Remove the `image_base64` and `has_image` keys from the initial state initialization.
3. In `app/agent/graph.py`:
   - Remove the `ocr` node and delete the reference to `ocr_node` in the graph compilation.
   - Change the state graph entry point from "ocr" to "translate_in" (which is currently the next node).
4. Do not delete the OCR utility in `app/core/rag/ocr.py`. Ensure that `AgentRequest` and `AgentResponse` structures in `app/schemas/agent.py` are left exactly as is to keep React frontend compatibility intact.
```

### Git Commit Message
```text
refact(ingestion): extract OCR processing to API controller layer and simplify graph state
```

---

## Phase 2: State and Graph Core Simplification

### Goal
Remove the translation nodes from LangGraph. Force the agent to directly process and respond in the language of the query (Urdu script, Roman-Urdu, or English) to eliminate Google Translate API latency, external errors, and context loss.

### Prompt for Coding Agent
```text
Refactor the LangGraph to remove pre- and post-processing translation nodes. The model must process and respond in Urdu/English directly.

Do the following:
1. In `app/agent/graph.py`:
   - Remove references to `translate_in` and `translate_out` nodes.
   - Update the graph structure: set the entry point of the StateGraph directly to the "agent" node.
   - Update edges: the conditional edge from "agent" should route to "tools" (then back to "agent") or route directly to `END` (when the agent issues a final answer).
2. In `app/agent/state.py`, simplify the `AgentState` TypedDict:
   - Keep only essential keys: `patient_id`, `ocr_context`, `tool_call_count`, `messages`.
   - To maintain compatibility with database checkpoint queries in `conversation_service.py` (which the React sidebar uses to load histories), keep the following keys in the state: `raw_input`, `final_response`, `detected_lang`, `needs_rag`, `retrieval_decision`, `retrieved_docs`.
3. In `app/services/agent_service.py`:
   - Update `_build_initial_state` to match the streamlined schema. Set `raw_input` to `req.query`, and initialize the summary checkpoint keys (`final_response`, etc.) as default values.
```

### Git Commit Message
```text
refact(agent): remove translation nodes and direct graph entry to agent node
```

---

## Phase 3: Prompt Engineering & Parser Optimization

### Goal
Update the LLM node to handle bilingual conversation (Urdu script, Roman-Urdu, English) natively. Remove `LlamaGrammar` constraint checks during token generation to speed up local CPU inference, and use robust JSON regex/Pydantic parsing instead.

### Prompt for Coding Agent
```text
Optimize the agent node's prompts and output parsing to handle bilingual input/output without grammar constraints.

Do the following:
1. In `app/agent/nodes/agent_node.py`:
   - Revise the `SYSTEM_PROMPT` to instruct the model to respond directly in the query language (Urdu, Roman-Urdu, or English) with no external translation layers. Ensure the prompt requires the model to output a structured JSON object containing "thought", "action", and "action_input" fields.
   - Remove `LlamaGrammar` import and delete `_GRAMMAR` constraint checks in the `llm()` execution block.
   - Replace the grammar enforcement with standard LLM json output: parse the raw string using standard JSON parsing or a regex fallback (`re.search(r'\{.*\}', raw, re.DOTALL)`).
   - Validate the parsed output against the Pydantic schema `ToolCall`. If parsing fails, fall back gracefully to a friendly conversational message.
   - Ensure the final response formatting (`Diagnosis`, `Confidence`, `Medicines`, etc.) matches the UI layout specifications.
```

### Git Commit Message
```text
refact(agent): optimize system prompt for Urdu/English reasoning and switch to standard JSON parsing
```

---

## Phase 4: Persistence & Sidebar Interface Synchronization

### Goal
Keep the PostgresSaver (`checkpointer`) and PostgresStore (`store`) singletons active. Ensure the final state variables are populated correctly at the end of each turn so that the React sidebar (which reads thread metadata directly from checkpoints) does not break.

### Prompt for Coding Agent
```text
Verify and ensure that the persistence layer and sidebar compatibility remain intact.

Do the following:
1. In `app/agent/nodes/agent_node.py`, when the agent completes its turn (`action == "final_answer"`):
   - Set the state's `final_response` key to the generated answer text.
   - Set `raw_input` to the user's initial question text if it isn't set.
   - Populate `detected_lang`, `needs_rag`, `retrieval_decision`, and `retrieved_docs` metadata keys inside the state so that the React sidebar's API (`/agent/threads`) receives valid data.
2. In `app/services/agent_service.py` and `app/db/lifespan.py`, ensure that the graph is compiled with the existing `checkpointer` (PostgresSaver) and `store` (PostgresStore) instances.
3. Verify that `conversation_service.py` queries read the state fields (`final_response`, `raw_input`, etc.) from checkpoints correctly without raising database errors.
```

### Git Commit Message
```text
fix(persistence): map checkpoint summary keys to retain compatibility with React sidebar API
```

---

## Phase 5: Authentication Simplification

### Goal
Simplify the authentication router by removing unneeded endpoints (forgot-password, reset-password, verify-email, refresh-token) to keep the project focused on history management. Retain standard JWT Register/Login routes, return expected token structures, and swap out slow Argon2 hashing for standard fast bcrypt.

### Prompt for Coding Agent
```text
Simplify the authentication router and security layers while maintaining token response contract compatibility for the React client.

Do the following:
1. In `app/api/auth.py`:
   - Remove unused endpoints: forgot-password, reset-password, change-password, verify-email, and account deletion.
   - Keep only `/register` and `/login` POST endpoints.
   - The React client expects a response matching `TokenResponse` (containing `access_token` and `refresh_token`). Ensure the endpoints return a valid JWT `access_token` and a dummy/mirrored string for `refresh_token` to avoid breaking React's auth state storage handlers.
2. In `app/core/security.py`:
   - Replace the `argon2-cffi` dependency with standard fast `passlib.context.CryptContext` utilizing `bcrypt`.
   - Rewrite `hash_password` and `verify_password` functions to use bcrypt.
3. In `app/deps.py`:
   - Keep `get_current_user` dependency working with the simplified JWT decoding scheme.
4. Delete the unused `RefreshToken` database model and clean up `app/models/refresh_token.py` (and the `token_version` tracking in the `User` model, setting defaults if necessary to avoid database migrations).
```

### Git Commit Message
```text
refact(auth): simplify auth routes to Register/Login with JWT, migrating to bcrypt hashing
```
