# Software Requirements Specification (SRS) & Architecture Simplification Plan
## Project: AI-Powered Personal Health Intelligence Companion

This document provides a comprehensive plan to simplify the project's current architecture before proceeding with code modifications. The target of this plan is to improve runtime latency, reduce compute overhead (especially for local CPU-bound execution), eliminate brittle external API dependencies, and enhance code maintainability while maintaining the university-approved project proposal goals.

---

## 1. Architectural Bottlenecks & Analysis (Current Cons)

Our analysis of the existing codebase shows that the agent structure is over-engineered in several core areas:

```
[Current Graph Flow]
User Input ──> ocr ──> translate_in (Google Translate API) ──> agent (LlamaGrammar constrained)
                                                                 │  ▲
                                                                 ▼  │
                                                              tools (Fetch facts / CRAG / Save)
                                                                 │
                                                                 ▼
                                                       translate_out (Google Translate API) ──> final_response
```

### 1.1 Rigid Pre- and Post-Processing Nodes (Translation Overhead)
* **Current Implementation:** [translate_in_node](file:///c:/Fine%20Tuning/code/app/agent/nodes/translate_node.py#L9) and [translate_out_node](file:///c:/Fine%20Tuning/code/app/agent/nodes/translate_node.py#L22) execute external Google Translate HTTP requests on every message turn.
* **Problems:** High latency, external dependency failures, loss of Urdu/Pakistani medical phrasing, and loss of user emotional nuances.
* **Simplification:** Eliminate these nodes. Force the fine-tuned BioMistral model to reason and respond directly in the user's input language (Urdu, English, or mixed Roman-Urdu).

### 1.2 State Bloat & Redundant Checkpoint Bookkeeping
* **Current Implementation:** [AgentState](file:///c:/Fine%20Tuning/code/app/agent/state.py#L6) contains 15+ tracking properties. To build `tool_results` inside [agent_node](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py#L75-L87), the code manually scans back through the message history.
* **Problems:** Extreme state size, complex history parsing, and tight coupling with LangGraph checkpointer internals.
* **Simplification:** Streamline state to hold only essential items (conversation messages, patient identifier, and temporary flags). Let standard LangGraph tools condition logic handle updates instead of manual scanning.

### 1.3 OCR Context Pollution in Agent State
* **Current Implementation:** OCR extraction runs inside the graph as the first node [ocr_node](file:///c:/Fine%20Tuning/code/app/agent/nodes/ocr_node.py#L9), carrying heavy base64 image data (`image_base64`) inside the state graph checkpoint.
* **Problems:** Bloats the checkpointer database with large base64 strings and mixes payload processing with clinical reasoning logic.
* **Simplification:** Extract OCR text in the API controller layer *prior* to invoking the agent graph. Pass only the parsed text to the agent, eliminating `image_base64` and `ocr_node` from the graph state entirely.

### 1.4 Heavy Grammar Restrictions
* **Current Implementation:** Forced structured output via [LlamaGrammar](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py#L16).
* **Problems:** CPU inference under grammar constraints slows down token generation speed significantly. If the model fails to output a key, custom patching is needed.
* **Simplification:** Switch to a lighter validation scheme. Instruct the model to return structured JSON in the prompt, and parse/validate using standard Python `json` and Pydantic libraries, falling back gracefully if needed.

### 1.5 Over-Engineered Corrective RAG (CRAG) Heuristics
* **Current Implementation:** [corrective_retrieve](file:///c:/Fine%20Tuning/code/app/core/rag/corrective_rag.py#L92) calculates document relevance using arbitrary score thresholds (`RELEVANCE_THRESHOLD = 0.5`) to trigger SerpAPI searches.
* **Problems:** Cosine scores vary wildly. Adding fallback results risks exceeding the llama_cpp model's context window (`n_ctx=2048`).
* **Simplification:** Provide Qdrant retrieval and web search as distinct tools that the agent can choose to call based on its clinical needs, rather than using complex hardcoded decision pipelines.

### 1.6 Over-Engineered Authentication & Security Pipelines (Auth Cons)
* **Current Implementation:** High-complexity auth endpoints inside [auth.py](file:///c:/Fine%20Tuning/code/app/api/auth.py) covering Argon2 hashing, database-backed opaque refresh tokens, one-time verification tokens, account deletion, and custom password policy rule validation in [password_policy.py](file:///c:/Fine%20Tuning/code/app/core/password_policy.py).
* **Problems:** Bloats the backend codebase with 500+ lines of enterprise-grade security code that is irrelevant for a clinical history prototype, increasing local CPU testing overhead (due to Argon2 hashing rounds).
* **Simplification:** Eliminate one-time verification tokens, email verification, custom password complexity regex policies, and opaque refresh tokens. Keep a simple, single Register/Login endpoint returning medium-term JWTs.

---

## 2. Proposed Simplified Architecture (Target State)

```
[Simplified Ingestion (Controller Layer)]
User Request ──> API Controller ──> Run OCR (if image present) ──> Raw Text Context
                                                                           │
                                                                           ▼
[Simplified Agent Graph Flow]                                       [Agent State]
                                                                * patient_id
Entry Node ──> Agent Node (BioMistral Direct Urdu/English) ──>   * messages
                   │  ▲                                         * ocr_context
                   ▼  │                                         * tool_call_count
             Tool Node (fetch_facts, retrieve_docs, save_facts)
                   │
                   ▼ (Done / final_answer called)
                  END ──> Return final_response
```

### 2.1 Memory & Conversation Persistence (Retaining LangGraph Backends)
* **Short-Term Memory / Checkpointing:** We will continue to use LangGraph's native [PostgresSaver](file:///c:/Fine%20Tuning/code/app/db/lifespan.py#L19) checkpointer. This avoids the need to build a manual SQL table and migration pipeline for message history. State serialization and restoration are handled out-of-the-box.
* **Long-Term Memory / Fact Store:** We will continue to use LangGraph's native [PostgresStore](file:///c:/Fine%20Tuning/code/app/db/lifespan.py#L20) to manage semantic keys (patient facts/emotions) per patient under namespace partitions, avoiding manual database tables for memory items.

### 2.2 Simplified State definition
To keep the checkpoint query in [conversation_service.py](file:///c:/Fine%20Tuning/code/app/services/conversation_service.py) functioning cleanly, the state will be simplified but will retain key summary fields needed by the sidebar:
* `patient_id` (str)
* `ocr_context` (str)
* `tool_call_count` (int)
* `messages` (List of messages, managed automatically by LangGraph `add_messages`)
* `raw_input` (str) - The user's raw query (needed for the sidebar title).
* `final_response` (str) - The final response text (used to filter completed turns).
* `detected_lang` (str) - Optional metadata for language detection UI tags.
* `needs_rag` (bool) - Meta tag indicating if vector retrieval was used.
* `retrieval_decision` (str) - Meta tag indicating correctness status.
* `retrieved_docs` (list) - Meta list of sources for transparency.

### 2.3 Simplified Authentication Flow
* **Standard Register/Login:** Users register with basic parameters (`username`, `email`, `password`, `full_name`). Login returns a direct access token (JWT) valid for a medium-to-long period (e.g. 7 days).
* **Remove Opaque Refresh Tokens:** Delete the `RefreshToken` database model and `/auth/refresh` endpoint. Session longevity is handled purely via the medium-term JWT expiration.
* **Basic Password Hashing:** Use standard fast hashing (such as standard sha256 or basic bcrypt) to avoid the high local CPU processing overhead of Argon2 hashing during development testing.
* **Drop Extra Validation Code:** Remove password complexity checkers (e.g. upper/special character requirements) in favor of a simple minimum-length constraint (e.g., minimum 6 characters). Remove email confirmation and token-version check loops.

---

## 3. Software Requirements Specification (SRS) Refinement

### 3.1 Functional Requirements (FRs)
1. **Symptom Elicitation:** The system must converse naturally in Urdu and English (mixed/Roman-Urdu included) to ask relevant follow-up questions.
2. **Multimodal Ingestion:** Extract text from base64-encoded prescriptions or medical reports using OCR prior to starting the chat session.
3. **Persistent Patient Memory:** 
   * Retrieve past medical facts (e.g. chronic conditions, medication allergies) when starting a conversation.
   * Save newly confirmed patient facts (symptom, onset, status) to the PostgresStore.
4. **Clinical Information Retrieval (RAG):** Access evidence-based medical databases (Qdrant) or fall back to external web search when querying general medical knowledge.
5. **Holistic Response Generation:** Produce diagnosis summaries with holistic recommendation sections (medicines, Pakistani diet, exercise, and warnings on when to see a doctor).
6. **Basic Authenticated Sessions:** Support basic login/registration to tie patients to their persistent patient facts stored in the PostgresStore.

### 3.2 Non-Functional Requirements (NFRs)
1. **Performance/Latency:** Average response time must be under 5 seconds on local hardware. Removing external API translation nodes and grammar validation constraints directly supports this.
2. **Reliability:** The system must gracefully handle network failures (e.g. web search failures, database connection resets) by falling back to local reasoning.
3. **Simplicity & Maintainability:** The codebase must use native framework structures (e.g. LangChain tool binding and standard state schemas) to ensure ease of testing.

---

## 4. Refactoring Step-by-Step Plan

Before starting implementation, the refactoring will follow this sequence:

### Phase 1: Ingestion Pipeline Clean-up
* Modify [agent.py](file:///c:/Fine%20Tuning/code/app/api/agent.py) to check for base64 images, run OCR, and extract text *before* calling `run_agent`.
* Remove [ocr_node](file:///c:/Fine%20Tuning/code/app/agent/nodes/ocr_node.py) from the LangGraph execution flow.

### Phase 2: State and Graph Refactoring
* Rewrite [state.py](file:///c:/Fine%20Tuning/code/app/agent/state.py) to declare the streamlined schema.
* Remove `translate_in` and `translate_out` nodes from [graph.py](file:///c:/Fine%20Tuning/code/app/agent/graph.py). Connect `ocr_context` directly into the agent system prompt.
* Direct the graph entry point directly to the `agent` node.

### Phase 3: Prompt & Prompt Validation Optimization
* Update the system prompt in [agent_node.py](file:///c:/Fine%20Tuning/code/app/agent/nodes/agent_node.py) to explicitly prompt for multilingual Urdu/English dialogue.
* Replace the `LlamaGrammar` validation with a clean JSON regex parser / Pydantic validation fallback. Let the LLM output standard JSON strings natively.

### Phase 4: Persistence Integration
* Ensure [agent_service.py](file:///c:/Fine%20Tuning/code/app/services/agent_service.py) continues to call the compiled LangGraph with the existing `PostgresSaver` checkpointer and `PostgresStore` instance.
* Update state attributes mapping at the end of the graph turn so the sidebar checkpoint loader in [conversation_service.py](file:///c:/Fine%20Tuning/code/app/services/conversation_service.py) remains fully compatible.

### Phase 5: Authentication Simplification
* Refactor [auth.py](file:///c:/Fine%20Tuning/code/app/api/auth.py) to remove the forgot-password, reset-password, change-password, verify-email, and refresh-token endpoints.
* Delete the `RefreshToken` database model and corresponding database tables.
* Replace Argon2 hashing with basic standard bcrypt hashing in [security.py](file:///c:/Fine%20Tuning/code/app/core/security.py) and remove [password_policy.py](file:///c:/Fine%20Tuning/code/app/core/password_policy.py) validations.

---

## 5. Verification & Test Plan

To ensure the simplified architecture is fully correct, we will run the following checks:
1. **Validation Tests:** Run mock queries in English, Urdu, and mixed Roman-Urdu to verify that translation-free direct prompting yields correct Urdu output.
2. **Memory Save/Fetch Checks:** Verify that symptoms are stored correctly in the PostgresStore `patient_facts` namespace and fetched during subsequent sessions.
3. **OCR Context Propagation:** Verify that OCR'd text extracted at the API layer is correctly integrated into the prompt context and answered by the LLM.
4. **Latency Comparison:** Log and contrast completion times between the original 5-node graph structure and the new simplified workflow.
5. **Basic Session Verification:** Register a new user, log in, retrieve the JWT access token, and verify that the token can successfully authorize queries to `/agent/invoke` and thread loads.

