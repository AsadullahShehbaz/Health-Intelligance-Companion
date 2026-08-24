# 🩺 Health Intelligence Companion

An empathetic, multilingual AI health companion for Pakistani users — combining a **fine-tuned BioMistral LLM**, a **LangGraph multi-agent pipeline**, **RAG over a medical knowledge base**, **long-term patient memory**, **OCR for lab reports/prescriptions**, and **voice interaction** — served through a FastAPI backend and a React 19 + Tailwind frontend.

> Built as an end-to-end applied ML/AI engineering project: from dataset curation and LLM fine-tuning (Kaggle) → GGUF quantization → local inference → production agent orchestration, RAG, and full-stack deployment.

---

## ✨ Features

- **🎯 Fine-tuned medical LLM** — BioMistral-7B, QLoRA fine-tuned on an 83K-example curated dataset, quantized to GGUF and served locally. *([full write-up below](#-fine-tuning-pipeline-biomistral-7b--qlora--gguf))*
- **🔍 Agent-gated RAG** — a tool-calling router decides per-turn whether to query a 5,844-document Qdrant knowledge base and/or the live web, so retrieval only fires when it's actually needed. *([full write-up below](#-retrieval-augmented-generation-rag))*
- **Multi-stage agent graph (LangGraph)** — `Remember → RAG Router → Tools → Chat`, giving clean separation between memory extraction, retrieval decisions, and final response generation.
- **Long-term structured patient memory** — every turn is scanned for atomic, category-tagged facts (identity, symptoms, medications, lab results, lifestyle, emotional state) with deduplication and supersession logic, so the assistant reasons holistically instead of re-asking what it already knows.
- **OCR for medical documents** — lab reports and prescriptions (images) are parsed via a vision LLM into structured clinical text, then merged into the conversation context.
- **Voice mode** — speech-to-text (Groq Whisper) and streaming text-to-speech (Edge TTS) for hands-free interaction.
- **Full auth system** — JWT access tokens + rotating, hashed-at-rest opaque refresh tokens, with revocation on logout.
- **Persistent, resumable conversations** — LangGraph checkpointing (Postgres) means every thread can be restored, listed, and inspected turn-by-turn.
- **Memory dashboard** — patients can view and edit the structured facts the system has stored about them.

---

## 🏗️ Architecture

### High-Level System Architecture

```mermaid
flowchart TD
    subgraph Frontend["🌐 Frontend (React 19 + Tailwind)"]
        UI[Chat UI / Voice Modal / Memory Dashboard]
        Auth[Auth Context / JWT Management]
    end

    subgraph Backend["⚙️ Backend (FastAPI)"]
        API[API Routes: /agent, /auth, /chat, /voice, /memory]
        Agent[LangGraph Agent Orchestrator]
        Checkpointer[(Postgres Checkpointer)]
    end

    subgraph AgentGraph["🧠 LangGraph Agent Graph"]
        Remember[🧠 Remember Node<br/>Extract & Deduplicate Patient Facts]
        Router[🔀 RAG Router Node<br/>Tool-Calling Decision]
        Tools[🔧 Tools Node<br/>Execute Retrieval]
        Chat[💬 Chat Node<br/>BioMistral Local GGUF]
    end

    subgraph Memory["💾 Memory & Knowledge"]
        PatientMem[(Patient Memory<br/>Qdrant + Postgres)]
        KnowledgeBase[(Medical Knowledge Base<br/>Qdrant: 5,844 docs)]
        WebSearch[🌐 Web Search<br/>SerpAPI]
    end

    subgraph External["☁️ External Services"]
        Groq[Groq API<br/>Router LLM + Whisper + Vision]
        EdgeTTS[Edge TTS<br/>Streaming Speech]
        LocalLLM[Local LLM Server<br/>llama.cpp / BioMistral GGUF]
    end

    UI --> API
    Auth --> API
    API --> Agent
    Agent --> Checkpointer
    Agent --> Remember
    Remember --> PatientMem
    Remember --> Router
    Router -->|needs retrieval| Tools
    Router -->|no tools needed| Chat
    Tools --> KnowledgeBase
    Tools --> WebSearch
    Tools --> Chat
    Chat --> LocalLLM
    Chat --> PatientMem
    Chat --> API
    API --> Groq
    API --> EdgeTTS
```

### Agent Graph Flow (Per Turn)

```mermaid
flowchart TD
    Start([User Message + Context]) --> Remember
    Remember -->|Extract facts\nUpdate memory| Router
    Router -->|Tool calls needed| Tools
    Router -->|No tools needed| Chat
    Tools -->|Retrieved context| Chat
    Chat -->|Generate response| End([Final Response])
    
    style Remember fill:#e3f2fd,stroke:#1976d2
    style Router fill:#fff3e0,stroke:#f57c00
    style Tools fill:#e8f5e9,stroke:#388e3c
    style Chat fill:#fce4ec,stroke:#c2185b
    style Start fill:#f3e5f5,stroke:#7b1fa2
    style End fill:#f3e5f5,stroke:#7b1fa2
```

### RAG Router Decision Logic

```mermaid
flowchart TD
    Input[User Message] --> Analyze{Medical/Health\nKeywords?}
    Analyze -->|Yes| CheckTools{Which Tools?}
    Analyze -->|No| Skip[Skip Retrieval]
    CheckTools -->|Internal KB| Qdrant[Query Qdrant\nVector Search]
    CheckTools -->|Current/External| SerpAPI[Search Web\nSerpAPI]
    CheckTools -->|Both| Both[Qdrant + SerpAPI]
    Qdrant --> Merge[Merge & Format Results]
    SerpAPI --> Merge
    Both --> Merge
    Merge --> RouterOut[Return to Router Node]
    Skip --> RouterOut
    
    style Analyze fill:#fff3e0,stroke:#f57c00
    style CheckTools fill:#fff3e0,stroke:#f57c00
    style Skip fill:#e8f5e9,stroke:#388e3c
    style Merge fill:#e3f2fd,stroke:#1976d2
```

### Memory Extraction & Deduplication Flow

```mermaid
flowchart TD
    Turn[New Conversation Turn] --> Extract[LLM Extracts\nAtomic Facts]
    Extract --> Categorize[Categorize Facts:\nIdentity, Symptoms, Meds,\nLabs, Lifestyle, Emotion]
    Categorize --> Dedup{Duplicate\nExists?}
    Dedup -->|Yes| Compare{New Info\nSupersedes?}
    Dedup -->|No| Store[Store New Fact]
    Compare -->|Yes| Update[Update Existing Fact]
    Compare -->|No| Discard[Discard New Fact]
    Update --> Persist[Persist to Qdrant + Postgres]
    Store --> Persist
    Discard --> Persist
    Persist --> NextTurn[Available for\nNext Turn Context]
    
    style Extract fill:#e3f2fd,stroke:#1976d2
    style Categorize fill:#e3f2fd,stroke:#1976d2
    style Dedup fill:#fff3e0,stroke:#f57c00
    style Compare fill:#fff3e0,stroke:#f57c00
    style Persist fill:#e8f5e9,stroke:#388e3c
```

- **Remember** extracts and deduplicates structured patient facts each turn.
- **RAG Router** (Groq, tool-calling) decides whether internal medical knowledge and/or a live web search are needed for *this* message — purely conversational turns skip retrieval entirely.
- **Tools** execute the selected retrievals (Qdrant vector search / SerpAPI) and flatten results into plain-text context.
- **Chat** is the locally-hosted, fine-tuned BioMistral model, which produces the final response using patient memory + OCR + retrieved context, cross-referencing categories (e.g. checking active medications before suggesting new ones).

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| **LLM orchestration** | LangGraph, LangChain, LangSmith (tracing) |
| **Local inference** | Fine-tuned BioMistral, quantized to GGUF, served via `llama.cpp` / OpenAI-compatible endpoint |
| **Routing / tool-calling** | Groq (`ChatGroq`, tool-calling model) |
| **Vector search** | Qdrant + `sentence-transformers/all-MiniLM-L6-v2` |
| **Web search** | SerpAPI |
| **OCR / Vision** | Groq vision model for medical document extraction |
| **Speech** | Groq Whisper (STT), Edge TTS (streaming TTS) |
| **Backend** | FastAPI, SQLAlchemy (async), Alembic, Postgres, JWT auth |
| **Frontend** | React 19, Vite, Tailwind CSS 4 |
| **Testing** | pytest (`unit` / `integration` / `live` markers), pytest-asyncio, pytest-cov |
| **ML experimentation** | Jupyter notebooks (data collection → cleaning → generation → fine-tuning → GGUF conversion → RAG KB build), Kaggle |

---

## 📁 Project Structure

```
.
├── app/
│   ├── agent/           # LangGraph nodes, state, tools, memory schema
│   ├── api/              # FastAPI routers (auth, chat, agent, voice, memory)
│   ├── core/              # LLM client, RAG (embedder/OCR/Qdrant), security
│   ├── db/                # Async session, connection pool, checkpointer lifespan
│   ├── models/            # SQLAlchemy models (user, tokens)
│   ├── schemas/           # Pydantic request/response schemas
│   ├── services/          # Business logic (chat, agent, memory, voice, titles)
│   └── tests/             # App-level tests
├── frontend/               # React 19 + Vite + Tailwind SPA
│   └── src/
│       ├── components/     # Chat UI, voice modal, memory dashboard, sidebar, auth modals
│       ├── context/        # Auth & conversations React context
│       └── utils/          # API client, session, formatting helpers
├── notebooks/              # Full ML pipeline: data collection → cleaning → generation →
│                           # fine-tuning → GGUF conversion → RAG KB build → voice agent
├── tests/                  # Top-level test suite (agent, api, core, db, services)
├── contextBuilder.py       # Utility that generates a full codebase context dump
├── requirements.txt
└── pyproject.toml
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Postgres database
- A running local LLM server (llama.cpp / any OpenAI-compatible endpoint) hosting the fine-tuned BioMistral GGUF model
- API keys: Groq, SerpAPI, Qdrant Cloud (or self-hosted), LangSmith, HuggingFace

### 1. Backend setup

```bash
git clone <your-repo-url>
cd <repo>
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
# LangSmith
LANGCHAIN_TRACING_V2=True
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=health-companion

# Database & Vector Store
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your_qdrant_key

# Auth
HF_TOKEN=your_huggingface_token
SECRET_KEY=change_me_to_a_random_secret

# Local LLM (BioMistral GGUF, served OpenAI-compatible)
LLM_MODEL=biomistral
LLM_BASE_URL=http://localhost:8080/v1
LLM_API_KEY=not-needed-for-local-server

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# Third-party APIs
SERP_API_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b
```

Run the API:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` (interactive docs at `/docs`).

### 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### 3. Running tests

```bash
pytest                          # all tests
pytest -m unit                  # fast, fully-mocked unit tests
pytest -m integration           # ASGI client + mocked external services
RUN_LIVE_TESTS=1 pytest -m live # requires real Postgres/Qdrant/LLM
pytest --cov=app --cov-report=term-missing
```

---

## 🔌 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create an account, returns access + refresh tokens |
| `POST` | `/auth/login` | Authenticate, returns access + refresh tokens |
| `POST` | `/auth/refresh` | Rotate a refresh token for a new token pair |
| `POST` | `/auth/logout` | Revoke a refresh token |
| `GET`  | `/auth/me` | Current authenticated user |
| `POST` | `/agent/invoke` | Run one turn through the full agent graph (supports optional OCR image) |
| `GET`  | `/agent/threads` | List a patient's conversation threads (sidebar) |
| `GET`  | `/agent/threads/{thread_id}` | Full transcript of one conversation |
| `POST` | `/chat/stream` | Raw streaming chat completion (bypasses the agent graph) |
| `GET`  | `/memory/patient/{patient_id}` | Fetch categorized patient memories |
| `PATCH`| `/memory/patient/{patient_id}/{memory_id}` | Edit a stored memory record |
| `POST` | `/voice/interact` | Local mic capture → agent → spoken response |
| `POST` | `/voice/stt` | Transcribe an uploaded audio clip |
| `POST` | `/voice/tts` | Synthesize and stream speech from text |
| `POST` | `/voice/stop` | Stop any in-progress audio playback |

---

## 🎯 Fine-Tuning Pipeline (BioMistral-7B → QLoRA → GGUF)

### Pipeline Overview

```mermaid
flowchart LR
    subgraph Data["📊 Data Preparation"]
        Collect[Data Collection\nMultiple Sources]
        Clean[Cleaning &\nDeduplication]
        Merge[Merging &\nFormatting]
        Generate[Synthetic\nData Generation]
        Validate[Validation Split\n9,043 examples]
    end

    subgraph Training["🏋️ Fine-Tuning (QLoRA)"]
        Base[BioMistral-7B\nBase Model]
        Quantize[4-bit Quantization\nBitsAndBytes nf4]
        LoRA[LoRA Adapters\nr=16, α=32]
        Train[Training\n42M params / 3.8B]
    end

    subgraph Deploy["🚀 Deployment"]
        MergeAdapters[Merge Adapters\ninto Base Weights]
        Convert[Convert to GGUF\nQuantize Q4_K_M]
        Publish[Publish to HF Hub\nasadullahshehbaz/biomistral-health-gguf]
        Serve[Local Server\nllama.cpp OpenAI-compatible]
    end

    Collect --> Clean --> Merge --> Generate --> Validate
    Validate --> Base
    Base --> Quantize --> LoRA --> Train
    Train --> MergeAdapters --> Convert --> Publish --> Serve
    
    style Base fill:#f3e5f5,stroke:#7b1fa2
    style Train fill:#fff3e0,stroke:#f57c00
    style Serve fill:#e8f5e9,stroke:#388e3c
```

### QLoRA Configuration Details

```mermaid
flowchart TD
    Config[QLoRA Config] --> Quant[4-bit Quantization\nnf4 + Double Quant]
    Config --> LoRAConf[LoRA Config\nr=16, α=32, dropout=0.05]
    Config --> Target[Target Modules:\nq_proj, k_proj, v_proj, o_proj\ngate_proj, up_proj, down_proj]
    Config --> Compute[Compute Dtype: float16]
    Config --> Trainable[Trainable Params: ~42M / 3.8B\n≈ 1.1%]
    
    style Config fill:#e3f2fd,stroke:#1976d2
    style Trainable fill:#fce4ec,stroke:#c2185b
```

---

## 🔍 Retrieval-Augmented Generation (RAG)

### RAG Pipeline Overview

```mermaid
flowchart TD
    subgraph Build["🏗️ Knowledge Base Build (Offline)"]
        Sources[Data Sources:\nDisease DB, PubMedQA,\nChatDoctor]
        Embed[Embed with\nMiniLM-L6-v2\n384-dim]
        Index[Index in Qdrant\nCosine Distance\n5,844 documents]
        Payload[Metadata:\nsource, category, disease]
    end

    subgraph Runtime["⚡ Runtime Retrieval"]
        Query[User Query] --> EmbedQuery[Embed Query\nSame MiniLM]
        EmbedQuery --> Search[Vector Search\nscore_threshold=0.3]
        Search --> Filter[Optional Category\nFilter]
        Filter --> Retry{Retry on\nFailure?}
        Retry -->|Yes| Search
        Retry -->|No| Format[Format Results\nSource-tagged]
    end

    subgraph Agentic["🤖 Agentic Routing"]
        Router[Groq Router LLM\nTool-Calling] --> Decide{Need\nRetrieval?}
        Decide -->|Yes| ToolCall[Call Tools:\nQdrant / SerpAPI]
        Decide -->|No| Skip[Skip Retrieval]
        ToolCall --> Flatten[Flatten & Tag\n[source]: text]
        Flatten --> ChatCtx[Pass to Chat Node]
        Skip --> ChatCtx
    end

    Sources --> Embed --> Index --> Payload
    Payload -.->|Runtime| Search
    ChatCtx --> Final[Final BioMistral\nResponse with Citations]
    
    style Sources fill:#e3f2fd,stroke:#1976d2
    style Router fill:#fff3e0,stroke:#f57c00
    style Final fill:#e8f5e9,stroke:#388e3c
```

### Knowledge Base Composition

```mermaid
pie title Knowledge Base: 5,844 Documents
    "ChatDoctor (Patient Cases)" : 4944
    "PubMedQA (Research)" : 500
    "Disease DB (Triples)" : 400
```

### Agentic Router Tool Decision

```mermaid
flowchart TD
    Message[User Message] --> Router[Router LLM\nGroq gpt-oss-120b]
    Router --> Analyze[Analyze Intent:\nMedical? Symptoms? Meds?]
    Analyze --> Decision{Tools Needed?}
    Decision -->|Pure Chat| NoTools[No Tool Calls\nDirect to Chat Node]
    Decision -->|Medical Query| Tools[Available Tools:]
    Tools --> Tool1[🔍 retrieve_medical_knowledge\n→ Qdrant Vector Search]
    Tools --> Tool2[🌐 search_web_medical\n→ SerpAPI Web Search]
    Tool1 --> Execute[Execute Selected Tools]
    Tool2 --> Execute
    Execute --> Results[Return Formatted\nContext to Router]
    Results --> ChatNode[Chat Node Receives\nMemory + Context]
    NoTools --> ChatNode
    
    style Router fill:#fff3e0,stroke:#f57c00
    style Decision fill:#fff3e0,stroke:#f57c00
    style ChatNode fill:#e8f5e9,stroke:#388e3c
```

---

## 🎙️ Voice Interaction Flow

```mermaid
flowchart TD
    subgraph Input["🎤 Voice Input"]
        Mic[User Speaks] --> Capture[Capture Audio\nFrontend MediaRecorder]
        Capture --> STT[STT: Groq Whisper\nTranscribe Audio]
    end

    subgraph Processing["🧠 Agent Processing"]
        STT --> Agent[/agent/invoke\nFull Agent Graph]
        Agent --> RememberV[Remember Node]
        RememberV --> RouterV[RAG Router]
        RouterV --> ToolsV[Tools if Needed]
        ToolsV --> ChatV[Chat Node\nBioMistral]
        ChatV --> Response[Text Response]
    end

    subgraph Output["🔊 Voice Output"]
        Response --> TTS[TTS: Edge TTS\nStreaming Synthesis]
        TTS --> Stream[Stream Audio Chunks\nto Frontend]
        Stream --> Playback[Browser Audio\nPlayback]
    end

    style STT fill:#e3f2fd,stroke:#1976d2
    style Agent fill:#fff3e0,stroke:#f57c00
    style TTS fill:#e8f5e9,stroke:#388e3c
    style Playback fill:#fce4ec,stroke:#c2185b
```

## 🧪 Full ML Pipeline (Notebooks)

### Notebook Pipeline Flow

```mermaid
flowchart LR
    subgraph Phase1["📥 Phase 1: Data Engineering"]
        NB1[1_data_collection.ipynb]
        NB2[2_data_cleaning.ipynb]
        NB3[3_data_merging.ipynb]
        NB4[4_data_generation.ipynb]
        NB4_1[4.1_data_generation.ipynb]
        NB7[7_urdu-data-collection.ipynb]
    end

    subgraph Phase2["🏋️ Phase 2: Model Training"]
        NB5[5_model_training.ipynb\nQLoRA Fine-tuning]
    end

    subgraph Phase3["🚀 Phase 3: Inference & Deployment"]
        NB9[9_training_to_inference.ipynb]
        NB11[11_convert-to-gguf.ipynb]
    end

    subgraph Phase4["🔍 Phase 4: RAG & Memory"]
        NB12[12_build-rag-kb.ipynb\nQdrant Indexing]
        NB14[14_memory-store.ipynb\nLangGraph Memory]
    end

    subgraph Phase5["🎙️ Phase 5: Voice"]
        NB15[15_voice_agent.ipynb\nSTT/TTS Prototype]
        NBV[voice-agent.py\nIntegration]
    end

    NB1 --> NB2 --> NB3 --> NB4 --> NB4_1
    NB7 --> NB4_1
    NB4_1 --> NB5
    NB5 --> NB9 --> NB11
    NB11 -.->|GGUF Model| Production[Production Serving]
    NB3 -.->|Clean Data| NB12
    NB12 --> NB14
    NB14 -.->|Memory Schema| Production
    NB15 --> NBV
    NBV -.->|Voice Service| Production
    
    style NB5 fill:#fff3e0,stroke:#f57c00
    style NB11 fill:#e8f5e9,stroke:#388e3c
    style NB12 fill:#e3f2fd,stroke:#1976d2
    style Production fill:#f3e5f5,stroke:#7b1fa2
```

---

## 📷 OCR for Medical Documents

```mermaid
flowchart TD
    Upload[User Uploads Image\nLab Report / Prescription] --> Vision[Groq Vision Model\nExtract Structured Text]
    Vision --> Parse[Parse & Structure:\n- Patient Info\n- Test Results\n- Medications\n- Doctor Notes]
    Parse --> Context[Merge into\nConversation Context]
    Context --> Agent[Agent Graph\nProcess with Context]
    Agent --> Response[Response References\nOCR Data]
    
    style Vision fill:#e3f2fd,stroke:#1976d2
    style Parse fill:#fff3e0,stroke:#f57c00
    style Agent fill:#e8f5e9,stroke:#388e3c
```

## 🔐 Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DB[(Postgres)]

    User->>Frontend: Enter credentials
    Frontend->>Backend: POST /auth/login
    Backend->>DB: Verify user + hash
    DB-->>Backend: User record
    Backend->>Backend: Generate JWT access token (15m)
    Backend->>Backend: Generate opaque refresh token
    Backend->>DB: Store hashed refresh token + expiry
    Backend-->>Frontend: Access token + Refresh token (httpOnly cookie)
    Frontend->>Frontend: Store access token in memory
    
    Note over Frontend,Backend: Subsequent Requests
    
    Frontend->>Backend: API Request + Authorization: Bearer <access>
    Backend->>Backend: Validate JWT signature + expiry
    Backend-->>Frontend: Protected resource
    
    Note over Frontend,Backend: Token Refresh
    
    Frontend->>Backend: POST /auth/refresh + Refresh cookie
    Backend->>DB: Lookup hashed refresh token
    DB-->>Backend: Token record (valid, not revoked)
    Backend->>Backend: Revoke old, issue new pair
    Backend->>DB: Store new hashed refresh token
    Backend-->>Frontend: New access + refresh tokens
    
    Note over Frontend,Backend: Logout
    
    Frontend->>Backend: POST /auth/logout + Refresh cookie
    Backend->>DB: Mark refresh token revoked
    Backend-->>Frontend: 204 No Content
```

---

## 📌 Roadmap

- [ ] Automated evaluation suite (retrieval quality, response safety/factuality, latency) — *coming soon*
- [ ] Multi-turn voice conversation streaming
- [ ] Expanded Urdu/Roman-Urdu evaluation coverage

---

## ⚠️ Disclaimer

This project is an educational/portfolio AI system and is **not a certified medical device**. It does not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical concerns.

---

## 👤 Author

Built by **Asad Ullah** — BSCS student, Kaggle Notebooks & Datasets Grandmaster, with hands-on experience across two remote ML internships. This project reflects an applied AI/ML engineering journey covering data engineering, LLM fine-tuning, RAG, agentic systems, and full-stack deployment.

- Kaggle: [kaggle.com/asadullahcreative](https://www.kaggle.com/asadullahcreative)

---

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.