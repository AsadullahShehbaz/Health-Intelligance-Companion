I'll generate standard BSCS FYP flowcharts for your SRS and integrate them into the document. Let me create the key diagrams: System Architecture, DFDs (Level 0 & 1), Use Case, Activity, Sequence, and ER diagrams.
Here is your **enhanced SRS with complete BSCS FYP standard flowcharts** integrated. All diagrams are generated and available for download below.

---

# Software Requirements Specification (SRS) & Architecture Simplification Plan
## Project: AI-Powered Personal Health Intelligence Companion

---

## List of Figures

| Figure | Title | Diagram Type |
|--------|-------|--------------|
| Figure 1 | System Architecture Diagram | Structural |
| Figure 2 | Context Level DFD (Level 0) | Data Flow |
| Figure 3 | Level 1 DFD | Data Flow |
| Figure 4 | Use Case Diagram | Behavioral |
| Figure 5 | Activity Diagram — Conversation & Diagnosis Flow | Behavioral |
| Figure 6 | Sequence Diagram — Agent Query Processing | Interaction |
| Figure 7 | Entity-Relationship (ER) Diagram — Simplified Schema | Data Model |

---

## 1. Architectural Bottlenecks & Analysis (Current Cons)

Our analysis of the existing codebase shows that the agent structure is over-engineered in several core areas:

### 1.1 Rigid Pre- and Post-Processing Nodes (Translation Overhead)
* **Current Implementation:** `translate_in_node` and `translate_out_node` execute external Google Translate HTTP requests on every message turn.
* **Problems:** High latency, external dependency failures, loss of Urdu/Pakistani medical phrasing, and loss of user emotional nuances.
* **Simplification:** Eliminate these nodes. Force the fine-tuned BioMistral model to reason and respond directly in the user's input language (Urdu, English, or mixed Roman-Urdu).

### 1.2 State Bloat & Redundant Checkpoint Bookkeeping
* **Current Implementation:** `AgentState` contains 15+ tracking properties. To build `tool_results` inside `agent_node`, the code manually scans back through the message history.
* **Problems:** Extreme state size, complex history parsing, and tight coupling with LangGraph checkpointer internals.
* **Simplification:** Streamline state to hold only essential items (conversation messages, patient identifier, and temporary flags). Let standard LangGraph tools condition logic handle updates instead of manual scanning.

### 1.3 OCR Context Pollution in Agent State
* **Current Implementation:** OCR extraction runs inside the graph as the first node `ocr_node`, carrying heavy base64 image data (`image_base64`) inside the state graph checkpoint.
* **Problems:** Bloats the checkpointer database with large base64 strings and mixes payload processing with clinical reasoning logic.
* **Simplification:** Extract OCR text in the API controller layer *prior* to invoking the agent graph. Pass only the parsed text to the agent, eliminating `image_base64` and `ocr_node` from the graph state entirely.

### 1.4 Heavy Grammar Restrictions
* **Current Implementation:** Forced structured output via `LlamaGrammar`.
* **Problems:** CPU inference under grammar constraints slows down token generation speed significantly. If the model fails to output a key, custom patching is needed.
* **Simplification:** Switch to a lighter validation scheme. Instruct the model to return structured JSON in the prompt, and parse/validate using standard Python `json` and Pydantic libraries, falling back gracefully if needed.

### 1.5 Over-Engineered Corrective RAG (CRAG) Heuristics
* **Current Implementation:** `corrective_retrieve` calculates document relevance using arbitrary score thresholds (`RELEVANCE_THRESHOLD = 0.5`) to trigger SerpAPI searches.
* **Problems:** Cosine scores vary wildly. Adding fallback results risks exceeding the llama_cpp model's context window (`n_ctx=2048`).
* **Simplification:** Provide Qdrant retrieval and web search as distinct tools that the agent can choose to call based on its clinical needs, rather than using complex hardcoded decision pipelines.

### 1.6 Over-Engineered Authentication & Security Pipelines (Auth Cons)
* **Current Implementation:** High-complexity auth endpoints inside `auth.py` covering Argon2 hashing, database-backed opaque refresh tokens, one-time verification tokens, account deletion, and custom password policy rule validation in `password_policy.py`.
* **Problems:** Bloats the backend codebase with 500+ lines of enterprise-grade security code that is irrelevant for a clinical history prototype, increasing local CPU testing overhead (due to Argon2 hashing rounds).
* **Simplification:** Eliminate one-time verification tokens, email verification, custom password complexity regex policies, and opaque refresh tokens. Keep a simple, single Register/Login endpoint returning medium-term JWTs.

---

## 2. Proposed Simplified Architecture (Target State)

### Figure 1: System Architecture Diagram

![Figure 1: System Architecture](sandbox:///mnt/agents/output/figure1_system_architecture.png)

**Figure 1** illustrates the high-level modular architecture. The system is organized into four layers:

1. **Presentation Layer:** Patient/User interface (Web/Mobile)
2. **API Gateway Layer:** FastAPI controller handling request routing, JWT validation, and OCR pre-processing
3. **Agent Core Layer:** LangGraph execution engine with BioMistral LLM for direct multilingual reasoning
4. **Persistence Layer:** PostgreSQL (checkpoints + auth), Qdrant (vector store), and PostgresStore (semantic memory)

Key architectural decisions visible in Figure 1:
- **OCR extraction occurs at the controller layer**, not inside the graph
- **Translation nodes are completely removed**; BioMistral handles Urdu/English natively
- **Three tool bindings** (fetch_facts, retrieve_docs, save_facts) connect to their respective data stores

---

### Figure 2: Context Level Data Flow Diagram (DFD Level 0)

![Figure 2: DFD Level 0](sandbox:///mnt/agents/output/figure2_dfd_level0.png)

**Figure 2** presents the Context-Level DFD showing the system as a single process bubble interacting with external entities and data stores:

- **External Entities:** Patient/User, Medical Web Sources (SerpAPI)
- **Data Stores:** PostgreSQL Database (auth + checkpoints), Qdrant Vector DB, PostgresStore Memory
- **Data Flows:** Bidirectional patient communication, unidirectional search queries, and persistent memory operations

---

### Figure 3: Level 1 Data Flow Diagram (DFD Level 1)

![Figure 3: DFD Level 1](sandbox:///mnt/agents/output/figure3_dfd_level1.png)

**Figure 3** decomposes the main process into six sub-processes:

| Process ID | Name | Description |
|------------|------|-------------|
| 1.0 | Request Ingestion & OCR Pre-processing | Receives user input, conditionally extracts OCR text |
| 2.0 | Authentication & JWT Validation | Validates bearer tokens, manages simplified auth |
| 3.0 | Agent Node (BioMistral LLM) | Core reasoning, tool selection, and response generation |
| 4.0 | Memory Tool Handler | fetch_facts / save_facts operations on PostgresStore |
| 5.0 | RAG Tool Handler | retrieve_docs from Qdrant with optional web search fallback |
| 6.0 | Response Formatting & Delivery | JSON formatting and HTTP response assembly |

Data Stores (D1–D4):
- **D1:** User Auth DB
- **D2:** Conversation Checkpoints (PostgresSaver)
- **D3:** Patient Facts (PostgresStore)
- **D4:** Qdrant Vector Store

---

### Figure 4: Use Case Diagram

![Figure 4: Use Case Diagram](sandbox:///mnt/agents/output/figure4_use_case.png)

**Figure 4** identifies the primary actors and their interactions:

**Primary Actor:** Patient/User
- Register Account → includes Login
- Login / Authenticate
- Upload Medical Image (OCR)
- Chat / Query Symptoms — extends: Receive Holistic Health Advice, Retrieve Past Medical Facts, Save New Patient Facts, Access Medical Knowledge (RAG)
- View Conversation History

**Secondary Actor:** Admin/Developer
- Monitor System Logs
- Manage Vector DB

**Use Case Relationships:**
- `<<include>>`: Chat requires image upload capability when images are present
- `<<extend>>`: RAG knowledge access may extend to Web Search Fallback when local documents are insufficient

---

### Figure 5: Activity Diagram — Conversation & Diagnosis Flow

![Figure 5: Activity Diagram](sandbox:///mnt/agents/output/figure5_activity_diagram.png)

**Figure 5** models the swimlane-based activity flow across three partitions:

1. **User/Patient:** Initiates query, optionally provides image
2. **API Controller:** Validates JWT, conditionally runs OCR, builds agent state
3. **Agent Core (BioMistral):** Loads conversation history, performs LLM reasoning with tool loops, formats final response

**Key Decision Points:**
- `[image present]` guard condition triggers OCR extraction
- `[Tool Call]` vs `[Final Answer]` loop controls the ReAct-style agent iteration
- Tool execution cycles back to LLM reasoning until a final answer is produced

---

### Figure 6: Sequence Diagram — Agent Query Processing

![Figure 6: Sequence Diagram](sandbox:///mnt/agents/output/figure6_sequence_diagram.png)

**Figure 6** details the temporal interaction between system objects:

**Sequence of Messages:**
1. User → API Controller: `POST /agent/invoke` (query + optional image)
2. API Controller: Extract OCR text (alt fragment `[image present]`)
3. API Controller → LangGraph Agent: `run_agent(state)`
4. LangGraph Agent → BioMistral LLM: `invoke_llm(messages, tools, ocr_context)`
5. BioMistral LLM → LangGraph Agent: `tool_call decision` (fetch_facts)
6. LangGraph Agent → PostgresStore/Qdrant: `fetch_facts(patient_id)`
7. PostgresStore → LangGraph Agent: `return past_facts[]`
8. LangGraph Agent → BioMistral LLM: `invoke_llm(messages + facts)`
9. BioMistral LLM → LangGraph Agent: `tool_call decision` (retrieve_docs)
10. LangGraph Agent → PostgresStore/Qdrant: `retrieve_docs(query)`
11. PostgresStore/Qdrant → LangGraph Agent: `return docs[]`
12. LangGraph Agent → BioMistral LLM: `invoke_llm(messages + facts + docs)`
13. BioMistral LLM → LangGraph Agent: `final_answer JSON`
14. LangGraph Agent → API Controller: `return final_response`
15. API Controller → User: `HTTP 200 OK {diagnosis, advice}`

---

### Figure 7: Entity-Relationship (ER) Diagram — Simplified Schema

![Figure 7: ER Diagram](sandbox:///mnt/agents/output/figure7_er_diagram.png)

**Figure 7** presents the simplified database schema reflecting the architectural simplification:

**Entities:**
- **User (Simplified):** `user_id` (PK), `username` (IDX), `email` (IDX), `password_hash`, `full_name`, `created_at`
- **ConversationThread:** `thread_id` (PK), `user_id` (FK), `checkpoint_json`, `updated_at`
- **PatientFact (PostgresStore):** `fact_id` (PK), `patient_id` (FK), `namespace` (IDX), `semantic_key` (IDX), `fact_value`, `created_at`
- **MedicalDocument:** `doc_id` (PK), `title`, `content_vector`, `source_url`, `category` (IDX)

**Relationships:**
- User `1:N` ConversationThread (one user has many conversation threads)
- User `1:N` PatientFact (one patient owns many semantic memory facts)
- ConversationThread `M:N` MedicalDocument (via retrieval operations)

---

## 2.1 Memory & Conversation Persistence (Retaining LangGraph Backends)
* **Short-Term Memory / Checkpointing:** We will continue to use LangGraph's native `PostgresSaver` checkpointer. This avoids the need to build a manual SQL table and migration pipeline for message history. State serialization and restoration are handled out-of-the-box.
* **Long-Term Memory / Fact Store:** We will continue to use LangGraph's native `PostgresStore` to manage semantic keys (patient facts/emotions) per patient under namespace partitions, avoiding manual database tables for memory items.

## 2.2 Simplified State definition
To keep the checkpoint query in `conversation_service.py` functioning cleanly, the state will be simplified but will retain key summary fields needed by the sidebar:
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

## 2.3 Simplified Authentication Flow
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
* Modify `agent.py` to check for base64 images, run OCR, and extract text *before* calling `run_agent`.
* Remove `ocr_node` from the LangGraph execution flow.

### Phase 2: State and Graph Refactoring
* Rewrite `state.py` to declare the streamlined schema.
* Remove `translate_in` and `translate_out` nodes from `graph.py`. Connect `ocr_context` directly into the agent system prompt.
* Direct the graph entry point directly to the `agent` node.

### Phase 3: Prompt & Prompt Validation Optimization
* Update the system prompt in `agent_node.py` to explicitly prompt for multilingual Urdu/English dialogue.
* Replace the `LlamaGrammar` validation with a clean JSON regex parser / Pydantic validation fallback. Let the LLM output standard JSON strings natively.

### Phase 4: Persistence Integration
* Ensure `agent_service.py` continues to call the compiled LangGraph with the existing `PostgresSaver` checkpointer and `PostgresStore` instance.
* Update state attributes mapping at the end of the graph turn so the sidebar checkpoint loader in `conversation_service.py` remains fully compatible.

### Phase 5: Authentication Simplification
* Refactor `auth.py` to remove the forgot-password, reset-password, change-password, verify-email, and refresh-token endpoints.
* Delete the `RefreshToken` database model and corresponding database tables.
* Replace Argon2 hashing with basic standard bcrypt hashing in `security.py` and remove `password_policy.py` validations.

---

## 5. Verification & Test Plan

To ensure the simplified architecture is fully correct, we will run the following checks:
1. **Validation Tests:** Run mock queries in English, Urdu, and mixed Roman-Urdu to verify that translation-free direct prompting yields correct Urdu output.
2. **Memory Save/Fetch Checks:** Verify that symptoms are stored correctly in the PostgresStore `patient_facts` namespace and fetched during subsequent sessions.
3. **OCR Context Propagation:** Verify that OCR'd text extracted at the API layer is correctly integrated into the prompt context and answered by the LLM.
4. **Latency Comparison:** Log and contrast completion times between the original 5-node graph structure and the new simplified workflow.
5. **Basic Session Verification:** Register a new user, log in, retrieve the JWT access token, and verify that the token can successfully authorize queries to `/agent/invoke` and thread loads.

---

## Download All Flowcharts

| Diagram | Download Link |
|---------|--------------|
| Figure 1 — System Architecture | [Download PNG](sandbox:///mnt/agents/output/figure1_system_architecture.png) |
| Figure 2 — DFD Level 0 | [Download PNG](sandbox:///mnt/agents/output/figure2_dfd_level0.png) |
| Figure 3 — DFD Level 1 | [Download PNG](sandbox:///mnt/agents/output/figure3_dfd_level1.png) |
| Figure 4 — Use Case Diagram | [Download PNG](sandbox:///mnt/agents/output/figure4_use_case.png) |
| Figure 5 — Activity Diagram | [Download PNG](sandbox:///mnt/agents/output/figure5_activity_diagram.png) |
| Figure 6 — Sequence Diagram | [Download PNG](sandbox:///mnt/agents/output/figure6_sequence_diagram.png) |
| Figure 7 — ER Diagram | [Download PNG](sandbox:///mnt/agents/output/figure7_er_diagram.png) |

All diagrams follow **BSCS FYP standard notation** and are ready for inclusion in your final project documentation.