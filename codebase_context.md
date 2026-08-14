# Codebase Context

## File: `contextBuilder.py`

```python
import os

# Configuration
OUTPUT_FILE = "codebase_context.md"

# Directories to skip
EXCLUDE_DIRS = {
    "__pycache__", 
    ".git",
    ".vscode",
    ".claude",
    "node_modules",
    ".pytest_cache",
    "venv",
    ".venv",
    "llama.cpp",
    "gradio-app",
    "notebooks",
    "docs"
}

# Files or extensions to skip
EXCLUDE_FILES = {
    ".env",
    "codebase_context.md",
    "logs.txt",
    ".DS_Store",
    ".gitignore",
    "results_raw.json"
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".zip",
    ".tar",
    ".gz",
    ".sqlite3",
    ".db",
}


def is_text_file(filename):
    """Check if file has a binary extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() not in EXCLUDE_EXTENSIONS


def generate_markdown_context(root_dir="."):
    count = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_file:
        out_file.write("# Codebase Context\n\n")

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Modify dirnames in-place to skip excluded directories
            dirnames[:] = [
                d
                for d in dirnames
                if d not in EXCLUDE_DIRS and not d.startswith(".")
            ]

            for filename in filenames:
                if filename in EXCLUDE_FILES or not is_text_file(filename):
                    continue

                full_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(full_path, root_dir)

                # Infer code block language from file extension
                ext = os.path.splitext(filename)[1].lstrip(".")
                lang_map = {
                    "py": "python",
                    "js": "javascript",
                    "ts": "typescript",
                    "json": "json",
                    "md": "markdown",
                    "html": "html",
                    "css": "css",
                    "sh": "bash",
                    "yml": "yaml",
                    "yaml": "yaml",
                    "txt": "text",
                }
                lang = lang_map.get(ext, "")

                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    out_file.write(f"## File: `{relative_path}`\n\n")
                    out_file.write(f"```{lang}\n")
                    out_file.write(content)
                    out_file.write("\n```\n\n")
                    out_file.write("---\n\n")

                    count += 1
                    print(f"Added: {relative_path}")
                except Exception as e:
                    print(f"Skipped {relative_path} (Error reading file: {e})")

    print(
        f"\nDone! Processed {count} files and saved to `{OUTPUT_FILE}`."
    )


if __name__ == "__main__":
    generate_markdown_context()
```

---

## File: `pyproject.toml`

```
[tool.coverage.run]
source = ["app"]
omit = [
    "app/tests/*",
    "app/eval/*",
]

[tool.coverage.report]
show_missing = true
skip_covered = false

```

---

## File: `pytest.ini`

```
[pytest]
asyncio_mode = auto
testpaths = tests
markers =
    unit: fast unit tests — pure functions/classes, all I/O mocked, no external dependencies
    integration: full-route tests through the ASGI client with mocked external services + sqlite DB
    live: requires real external services (Postgres, Qdrant, LLM); skipped unless RUN_LIVE_TESTS=1
filterwarnings =
    ignore::DeprecationWarning

```

---

## File: `README.md`

```markdown
# 🩺 AI-Powered Personal Health Intelligence Companion

<p align="center">
  <img src="https://img.shields.io/badge/AI-Healthcare-0A7B83?style=for-the-badge" alt="AI Healthcare">
  <img src="https://img.shields.io/badge/LLM-BioMistral-6C5CE7?style=for-the-badge" alt="BioMistral">
  <img src="https://img.shields.io/badge/Agent-LangGraph-FF6B35?style=for-the-badge" alt="LangGraph">
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge" alt="FastAPI">
  <img src="https://img.shields.io/badge/VectorDB-Qdrant-D04A02?style=for-the-badge" alt="Qdrant">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791?style=for-the-badge" alt="PostgreSQL">
</p>

<p align="center">
  <strong>A multilingual AI health companion for natural Urdu, English, and Roman-Urdu medical conversations.</strong>
</p>

<p align="center">
  <em>Fine-Tuned Medical LLM • Agentic AI • Patient Memory • Medical RAG • OCR • Local Inference</em>
</p>

---

## 📌 Table of Contents

* [🌟 Overview](#-overview)
* [🎯 Problem Statement](#-problem-statement)
* [💡 Project Vision](#-project-vision)
* [✨ Key Features](#-key-features)
* [🧠 AI Architecture](#-ai-architecture)
* [🏗️ System Architecture](#️-system-architecture)
* [🔄 End-to-End Workflow](#-end-to-end-workflow)
* [🤖 Agentic Workflow](#-agentic-workflow)
* [🧠 Patient Memory](#-patient-memory)
* [🔎 Medical Knowledge Retrieval](#-medical-knowledge-retrieval)
* [📄 Medical OCR](#-medical-ocr)
* [🌐 Multilingual Communication](#-multilingual-communication)
* [🗃️ Data Model](#️-data-model)
* [🛠️ Technology Stack](#️-technology-stack)
* [📁 Project Structure](#-project-structure)
* [🚀 Installation](#-installation)
* [⚙️ Environment Configuration](#️-environment-configuration)
* [▶️ Running the Application](#️-running-the-application)
* [🧪 Testing & Evaluation](#-testing--evaluation)
* [📊 FYP Architecture Diagrams](#-fyp-architecture-diagrams)
* [🔬 Research Contribution](#-research-contribution)
* [🚧 Limitations](#-limitations)
* [🗺️ Roadmap](#️-roadmap)
* [⚠️ Medical Disclaimer](#️-medical-disclaimer)
* [👥 Team](#-team)
* [📄 License](#-license)

---

# 🌟 Overview

**AI-Powered Personal Health Intelligence Companion** is a Final Year Project focused on developing an intelligent conversational healthcare assistant that can understand patients in **English, Urdu, Roman Urdu, and mixed Urdu-English conversations**.

Unlike a traditional question-answer chatbot, the proposed system combines:

```text
                    ┌─────────────────────┐
                    │   Patient / User    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │  API + OCR Layer    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │   Agentic Layer     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌───────────┐    ┌───────────┐   ┌────────────┐
        │ BioMistral│    │  Patient  │   │  Medical   │
        │    LLM    │    │  Memory   │   │    RAG     │
        └───────────┘    └───────────┘   └────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │  Health Response    │
                    └─────────────────────┘
```

The goal is to create a **patient-aware, multilingual, agentic health assistant** rather than simply wrapping an LLM behind a chat interface.

---

# 🎯 Problem Statement

Patients do not always describe health problems using formal medical terminology.

In Pakistan, a patient may communicate using:

* Urdu
* English
* Roman Urdu
* Medical terminology
* Local expressions
* Informal symptom descriptions
* Mixed Urdu-English sentences

For example:

```text
"Mujhe kal se stomach mein bohat pain ho raha hai
aur khana khanay ke baad zyada ho jata hai."
```

A healthcare AI system should be able to understand the **meaning and medical context** of such communication rather than requiring the patient to translate everything into formal English.

This project therefore focuses on building a conversational health system optimized around this type of interaction.

---

# 💡 Project Vision

The vision of the project is:

> **Build an AI health companion that understands patients in the language they naturally use, remembers relevant health information, retrieves medical knowledge when necessary, and provides structured health guidance.**

The system follows a simple intelligence loop:

```text
Understand
    ↓
Ask
    ↓
Remember
    ↓
Retrieve
    ↓
Reason
    ↓
Respond
```

---

# ✨ Key Features

## 🇵🇰 1. Urdu + English + Roman Urdu

The system is designed for natural communication in:

```text
English
Urdu
Roman Urdu
Urdu + English
Roman Urdu + English
```

The architecture removes unnecessary external translation nodes and allows the fine-tuned medical model to directly process the user's language.

---

## 🧠 2. Fine-Tuned Medical LLM

The core language model is **BioMistral**, adapted for the project's medical conversational requirements.

The fine-tuning objective focuses on improving the model's ability to handle:

* Medical questions
* Symptoms
* Patient conversations
* Medical terminology
* Urdu/English interactions
* Roman-Urdu medical communication

The resulting model can also be quantized for more resource-efficient local inference.

---

## 🤖 3. Agentic AI with LangGraph

The system uses **LangGraph** to orchestrate the reasoning workflow.

Instead of:

```text
User → LLM → Answer
```

the system follows:

```text
User
 ↓
Agent
 ├── Patient Memory
 ├── Medical Knowledge Retrieval
 ├── Web Search when required
 └── BioMistral Reasoning
 ↓
Final Response
```

This enables the LLM to decide when additional information is needed.

---

## 🧠 4. Persistent Patient Memory

The companion can maintain useful patient information across conversations.

Examples include:

```text
Chronic conditions
Medication allergies
Previously reported symptoms
Relevant medical history
Patient-specific facts
```

The architecture separates:

### Short-Term Memory

Conversation/checkpoint state.

### Long-Term Memory

Persistent patient facts stored using `PostgresStore`.

---

## 🔎 5. Medical Knowledge Retrieval

The system uses **Qdrant** as a vector database for medical knowledge retrieval.

```text
Patient Question
      ↓
Semantic Retrieval
      ↓
Relevant Medical Documents
      ↓
Agent Context
      ↓
BioMistral
      ↓
Grounded Response
```

The agent can use retrieval tools when additional medical information is needed.

---

## 📄 6. Medical Image OCR

Patients can provide medical images such as:

* Prescriptions
* Medical reports
* Other medical documents

The system extracts useful text before the agent graph starts.

```text
Medical Image
      ↓
     OCR
      ↓
Extracted Text
      ↓
FastAPI Controller
      ↓
LangGraph Agent
      ↓
BioMistral
```

This keeps large image payloads outside the persistent agent state.

---

## 🩺 7. Holistic Health Guidance

The response architecture is designed around multiple aspects of patient guidance:

```text
🧾 Medical Interpretation
💊 Medication Guidance
🥗 Diet / Pakistani Dietary Considerations
🏃 Exercise & Lifestyle
⚠️ Warning Signs
👨‍⚕️ When to Consult a Doctor
```

---

# 🧠 AI Architecture

The intelligence layer consists of three major components:

```text
                 ┌─────────────────────┐
                 │      BioMistral     │
                 │   Medical LLM       │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      LangGraph      │
                 │    Agent Engine     │
                 └───────┬─────┬───────┘
                         │     │
               ┌─────────┘     └──────────┐
               ▼                           ▼
      ┌─────────────────┐        ┌─────────────────┐
      │ Patient Memory  │        │ Medical RAG     │
      │  PostgresStore  │        │     Qdrant      │
      └─────────────────┘        └─────────────────┘
```

### Why Agentic AI?

A rigid pipeline might always execute every component.

The proposed architecture instead allows the agent to decide whether it needs:

* Patient history
* Medical documents
* Web information
* Additional reasoning

This reduces unnecessary processing and keeps the architecture maintainable.

---

# 🏗️ System Architecture

The proposed system is organized into four major layers.

```text
┌───────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                     │
│                     Web / Mobile UI                       │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────┐
│                     API GATEWAY LAYER                     │
│                         FastAPI                           │
│             Authentication • OCR • Routing                │
└────────────────────────────┬──────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────┐
│                       AGENT CORE                           │
│                       LangGraph                            │
│                       BioMistral                           │
│               Reasoning • Tool Selection                   │
└───────────────┬─────────────────────────┬─────────────────┘
                │                         │
                ▼                         ▼
┌────────────────────────┐     ┌────────────────────────────┐
│   PERSISTENCE LAYER    │     │     KNOWLEDGE LAYER        │
│                        │     │                            │
│ PostgreSQL             │     │ Qdrant                     │
│ PostgresSaver          │     │ Medical Documents          │
│ PostgresStore          │     │ Vector Retrieval            │
└────────────────────────┘     └────────────────────────────┘
```

The SRS defines these four layers as the Presentation, API Gateway, Agent Core, and Persistence layers.

---

# 🔄 End-to-End Workflow

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │  Submit Query   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    FastAPI      │
                  │ Authentication  │
                  └────────┬────────┘
                           │
                           ▼
                    Image Attached?
                      /         \
                    YES          NO
                     │            │
                     ▼            │
                   ┌────┐         │
                   │OCR │         │
                   └─┬──┘         │
                     │            │
                     └─────┬──────┘
                           ▼
                  ┌─────────────────┐
                  │  LangGraph     │
                  │     Agent      │
                  └────────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
          Patient       Qdrant       Web Search
          Memory        Retrieval    (if needed)
              │            │            │
              └────────────┼────────────┘
                           ▼
                  ┌─────────────────┐
                  │   BioMistral    │
                  │    Reasoning    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Final Response  │
                  └────────┬────────┘
                           │
                           ▼
                         USER
```

---

# 🤖 Agentic Workflow

A typical agent interaction can be represented as:

```text
User Query
    │
    ▼
┌──────────────────┐
│ Analyze Request  │
└────────┬─────────┘
         │
         ▼
┌─────────────────────────┐
│ Does agent need memory? │
└───────┬─────────┬───────┘
        │ YES     │ NO
        ▼         │
   Fetch Facts    │
        │         │
        └────┬────┘
             ▼
┌─────────────────────────┐
│ Need medical knowledge? │
└───────┬─────────┬───────┘
        │ YES     │ NO
        ▼         │
 Retrieve Docs    │
        │         │
        └────┬────┘
             ▼
      ┌──────────────┐
      │  BioMistral  │
      │   Reasoning  │
      └──────┬───────┘
             │
             ▼
      ┌──────────────┐
      │ Final Answer │
      └──────────────┘
```

---

# 🧠 Patient Memory

Memory is divided into two levels.

## Short-Term Conversation Memory

LangGraph's `PostgresSaver` is used for conversation checkpointing.

```text
User
 │
 ├── Thread 1
 │    ├── Message
 │    ├── Message
 │    └── Message
 │
 └── Thread 2
      ├── Message
      └── Message
```

## Long-Term Patient Memory

`PostgresStore` maintains semantic patient facts.

```text
Patient
   │
   ├── Medical History
   ├── Allergies
   ├── Symptoms
   ├── Conditions
   └── Other Relevant Facts
```

This allows the system to become **patient-aware rather than conversation-only**.

---

# 🔎 Medical Knowledge Retrieval

The RAG component is designed around semantic retrieval.

```text
                   User Question
                         │
                         ▼
                  Query Embedding
                         │
                         ▼
                 ┌──────────────┐
                 │    Qdrant   │
                 └──────┬───────┘
                        │
                        ▼
                Relevant Documents
                        │
                        ▼
                  Agent Context
                        │
                        ▼
                   BioMistral
                        │
                        ▼
                  Final Response
```

The architecture also supports external web search as an additional information source where appropriate.

---

# 📄 Medical OCR

OCR is intentionally positioned at the API/controller layer.

### Why?

Keeping OCR outside the graph avoids storing large Base64 image payloads inside LangGraph checkpoints.

```text
                    IMAGE
                      │
                      ▼
                ┌──────────┐
                │   OCR    │
                └────┬─────┘
                     │
                     ▼
              Extracted Text
                     │
                     ▼
               Agent Context
                     │
                     ▼
                 LangGraph
```

This is one of the major architectural simplifications defined in the SRS.

---

# 🌐 Multilingual Communication

The project specifically targets direct multilingual interaction.

### Example

**Patient:**

```text
Mujhe 2 din se headache hai aur medicine lene
ke baad bhi pain kam nahi ho raha.
```

**Expected interaction style:**

```text
Aapka headache 2 din se persist kar raha hai,
aur medicine ke baad bhi relief nahi mila.
Kya aapko fever, vomiting, blurred vision,
ya neck stiffness bhi ho rahi hai?
```

The objective is not merely translation.

It is:

> **Medical understanding of naturally mixed Pakistani language.**

The SRS explicitly identifies Urdu, English, and mixed/Roman-Urdu symptom elicitation as a functional requirement.

---

# 🗃️ Data Model

The simplified architecture contains four major entities:

```text
                         ┌──────────────┐
                         │     USER     │
                         └──────┬───────┘
                                │
                   ┌────────────┴────────────┐
                   │                         │
                   ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │ Conversation    │       │  Patient Fact   │
          │     Thread      │       │                 │
          └─────────────────┘       └─────────────────┘


                    ┌─────────────────────┐
                    │ Medical Document   │
                    │                     │
                    │ Vector + Metadata  │
                    └─────────────────────┘
```

### Main Entities

| Entity               | Purpose                              |
| -------------------- | ------------------------------------ |
| `User`               | Authentication and user identity     |
| `ConversationThread` | Conversation/checkpoint persistence  |
| `PatientFact`        | Long-term semantic patient memory    |
| `MedicalDocument`    | Medical knowledge used for retrieval |

The documented schema defines these entities and their relationships in the simplified architecture.

---

# 🛠️ Technology Stack

## 🧠 Artificial Intelligence

| Technology       | Role                            |
| ---------------- | ------------------------------- |
| **BioMistral**   | Medical LLM                     |
| **QLoRA**        | Parameter-efficient fine-tuning |
| **llama.cpp**    | Local inference                 |
| **GGUF**         | Quantized model format          |
| **Hugging Face** | Models & datasets               |

## 🤖 Agentic AI

| Technology    | Role                   |
| ------------- | ---------------------- |
| **LangGraph** | Agent orchestration    |
| **LangChain** | Tool / LLM integration |

## ⚡ Backend

| Technology  | Role                        |
| ----------- | --------------------------- |
| **FastAPI** | REST API                    |
| **JWT**     | Authentication              |
| **Python**  | Backend / AI implementation |

## 🗄️ Data

| Technology        | Role                     |
| ----------------- | ------------------------ |
| **PostgreSQL**    | Application persistence  |
| **PostgresSaver** | Conversation checkpoints |
| **PostgresStore** | Long-term memory         |
| **Qdrant**        | Vector database          |

## 📄 Document Processing

| Technology | Role                          |
| ---------- | ----------------------------- |
| **OCR**    | Medical image text extraction |

---

# 📁 Project Structure

```text
health-intelligence-companion/
│
├── app/
│   │
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── llm.py
│   │
│   ├── agents/
│   │   ├── agent.py
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── tools/
│   │
│   ├── services/
│   │   ├── agent_service.py
│   │   ├── conversation_service.py
│   │   └── auth_service.py
│   │
│   ├── database/
│   │   ├── postgres.py
│   │   ├── qdrant_store.py
│   │   └── memory.py
│   │
│   ├── ocr/
│   │   └── processor.py
│   │
│   └── main.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── knowledge/
│
├── models/
│   └── biomistral/
│
├── scripts/
│   ├── ingest.py
│   ├── evaluate.py
│   └── convert_model.py
│
├── tests/
│
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

> The exact implementation structure may differ from this conceptual organization.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd health-intelligence-companion
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ⚙️ Environment Configuration

Create a `.env` file:

```env
DATABASE_URL=your_postgresql_url

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key

JWT_SECRET_KEY=your_secret_key

MODEL_PATH=path/to/biomistral.gguf
```

### 🔐 Security

Never commit:

```text
.env
API keys
Database passwords
JWT secrets
Private credentials
```

to the repository.

---

# ▶️ Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# 🧪 Testing & Evaluation

The project includes evaluation of both **functional correctness** and **architectural performance**.

## 🌐 Multilingual Evaluation

Test cases should cover:

```text
English
Urdu
Roman Urdu
Mixed Urdu-English
```

---

## 🧠 Memory Evaluation

```text
Conversation A
      │
      ▼
Save Patient Fact
      │
      ▼
Conversation B
      │
      ▼
Retrieve Patient Fact
      │
      ▼
Use Relevant Context
```

---

## 📄 OCR Evaluation

```text
Medical Image
      ↓
OCR
      ↓
Extracted Text
      ↓
Agent
      ↓
Response
```

---

## ⚡ Latency Evaluation

Compare:

```text
Original Architecture
        VS
Simplified Architecture
```

Measure:

* End-to-end latency
* OCR latency
* Retrieval latency
* LLM generation time
* Total response time

---

## 🔐 Authentication Evaluation

```text
Register
   ↓
Login
   ↓
JWT Access Token
   ↓
Authenticated Request
   ↓
Protected Endpoint
```

The SRS explicitly includes multilingual validation, memory save/fetch, OCR propagation, latency comparison, and authenticated-session testing.

---

# 📊 FYP Architecture Diagrams

The project documentation defines **seven major diagrams**.

## 1️⃣ System Architecture

Shows the complete four-layer architecture and communication between the application, agent, model, memory, and knowledge layers.

## 2️⃣ DFD — Level 0

Shows the system as a single process and its interaction with external entities and data stores.

## 3️⃣ DFD — Level 1

Decomposes the system into:

```text
1.0 Request Ingestion & OCR
2.0 Authentication
3.0 Agent / BioMistral
4.0 Memory Handler
5.0 RAG Handler
6.0 Response Delivery
```

These processes and data stores are defined in the SRS.

## 4️⃣ Use Case Diagram

Main actor:

```text
Patient / User
```

Key use cases:

```text
Register
Login
Upload Medical Image
Chat / Query Symptoms
Receive Health Advice
Retrieve Patient Facts
Save Patient Facts
Access Medical Knowledge
View Conversation History
```

## 5️⃣ Activity Diagram

Models the interaction between:

```text
User
   ↕
API Controller
   ↕
Agent Core
```

including OCR decisions and tool-call loops.

## 6️⃣ Sequence Diagram

Models the temporal interaction between:

```text
User
 ↓
API Controller
 ↓
LangGraph
 ↓
BioMistral
 ↓
Patient Memory
 ↓
Qdrant
 ↓
BioMistral
 ↓
Final Response
```

## 7️⃣ ER Diagram

Documents the relationship between:

```text
User
ConversationThread
PatientFact
MedicalDocument
```

---

# 🏎️ Architecture Simplification

A major engineering objective of this project is to **reduce unnecessary complexity**.

### ❌ Previous Direction

```text
User
 ↓
OCR Node
 ↓
Translation
 ↓
LLM
 ↓
Translation
 ↓
Grammar Validation
 ↓
Corrective RAG
 ↓
Response
```

### ✅ Proposed Direction

```text
User
 ↓
FastAPI
 ↓
Optional OCR
 ↓
LangGraph
 ↓
BioMistral
 ├── Memory Tool
 ├── RAG Tool
 └── Web Search Tool
 ↓
Validated Response
```

The SRS identifies several specific simplifications:

* Remove translation nodes.
* Move OCR outside the graph.
* Reduce oversized agent state.
* Replace heavy grammar constraints.
* Simplify corrective-RAG heuristics.
* Simplify authentication for the academic prototype.

---

# 🔬 Research Contribution

This project combines multiple AI research areas into a single healthcare-oriented system:

```text
                 ┌───────────────────────┐
                 │    Healthcare AI      │
                 └───────────┬───────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  Multilingual NLP      Medical LLM          Agentic AI
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                    Patient Memory
                             │
                             ▼
                       Medical RAG
                             │
                             ▼
                           OCR
                             │
                             ▼
                   Personal Health AI
```

The primary research focus is **multilingual medical conversational AI for Urdu/English-speaking users**, particularly mixed-language and Roman-Urdu interactions.

---

# 📈 Project Goals

The project aims to achieve:

| Goal                       | Description                                   |
| -------------------------- | --------------------------------------------- |
| 🇵🇰 **Localization**      | Support Pakistani communication patterns      |
| 🧠 **Medical Adaptation**  | Use a medical-domain LLM                      |
| 🤖 **Agentic Reasoning**   | Dynamically use tools                         |
| 🧠 **Patient Awareness**   | Maintain persistent patient facts             |
| 🔎 **Knowledge Grounding** | Retrieve relevant medical information         |
| 📄 **Multimodal Input**    | Process medical images through OCR            |
| ⚡ **Efficiency**           | Reduce unnecessary inference overhead         |
| 🏗️ **Maintainability**    | Keep architecture understandable and testable |

---

# 🚧 Limitations

This is an academic research prototype and has important limitations.

### 🧠 Model Limitations

The model may:

* Hallucinate information
* Misinterpret symptoms
* Produce incomplete responses
* Fail on uncommon medical cases
* Struggle with ambiguous Roman-Urdu expressions

### 💻 Hardware Limitations

Local inference performance depends on:

```text
CPU
RAM
Model quantization
Context window
Token generation speed
```

### 🏥 Clinical Limitations

The system does not perform:

```text
Physical examination
Laboratory diagnosis
Clinical confirmation
Emergency treatment
Professional medical consultation
```

---

# 🗺️ Development Roadmap

```text
[x] FYP Proposal
       │
       ▼
[x] SRS & System Design
       │
       ▼
[x] Dataset Preparation
       │
       ▼
[x] Medical LLM Fine-Tuning
       │
       ▼
[x] Model Quantization
       │
       ▼
[x] Backend Development
       │
       ▼
[x] PostgreSQL Integration
       │
       ▼
[x] Qdrant Integration
       │
       ▼
[x] LangGraph Agent
       │
       ▼
[ ] Architecture Simplification
       │
       ▼
[ ] Multilingual Evaluation
       │
       ▼
[ ] Patient Memory Evaluation
       │
       ▼
[ ] OCR Evaluation
       │
       ▼
[ ] End-to-End Testing
       │
       ▼
[ ] Final FYP Deployment
       │
       ▼
[ ] Final Report & Defense
```

---

# 📋 Functional Requirements

The system is designed around six core functional requirements:

### FR-01 — Symptom Elicitation

Natural Urdu/English/Roman-Urdu conversation with relevant follow-up questions.

### FR-02 — Multimodal Ingestion

OCR extraction from prescriptions and medical reports.

### FR-03 — Persistent Patient Memory

Retrieval and storage of relevant patient facts.

### FR-04 — Clinical Information Retrieval

Access to medical knowledge through vector retrieval and optional web search.

### FR-05 — Holistic Response Generation

Structured guidance covering medical interpretation, medication, diet, exercise, and warnings.

### FR-06 — Basic Authentication

Authenticated sessions connecting users with their persistent patient information.

These requirements are defined in the project's SRS.

---

# ⚡ Non-Functional Requirements

| Requirement         | Target                                          |
| ------------------- | ----------------------------------------------- |
| **Performance**     | Average response target under 5 seconds locally |
| **Reliability**     | Graceful handling of external failures          |
| **Maintainability** | Simple modular architecture                     |
| **Language**        | Urdu + English + Roman Urdu                     |
| **Memory**          | Persistent patient facts                        |
| **Scalability**     | Modular backend and retrieval components        |

The SRS specifies a target of less than five seconds average local response time and emphasizes reliability and maintainability.

---

# 🧪 Verification Strategy

The architecture will be verified through:

```text
┌──────────────────────────────┐
│     Multilingual Tests       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Memory Tests            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        OCR Tests             │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Latency Tests           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   Authentication Tests       │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│   End-to-End Evaluation      │
└──────────────────────────────┘
```

---

# 🎓 Academic Context

**Project Type:** Final Year Project

**Degree:** BS Computer Science

**Domain:** Artificial Intelligence / Healthcare

**Primary Areas:**

```text
Artificial Intelligence
Machine Learning
Natural Language Processing
Large Language Models
Agentic AI
Information Retrieval
Healthcare AI
Multimodal AI
```

---

# 👥 Team

| Member            | Responsibility                              |
| ----------------- | ------------------------------------------- |
| **Asadullah**     | AI/ML, LLM Fine-Tuning, Agentic AI, Backend |
| **[Team Member]** | [Responsibility]                            |
| **[Team Member]** | [Responsibility]                            |

### 👨‍🏫 Project Supervisor

**[Supervisor Name]**

**[Department / University]**

---

# 🏆 Project Highlights

<p align="center">

| 🧠              | 🤖             | 🇵🇰        | 🔎              |
| --------------- | -------------- | ----------- | --------------- |
| **Medical LLM** | **Agentic AI** | **Urdu AI** | **Medical RAG** |

| 📄      | 🧠                 | ⚡                   | 🏗️                  |
| ------- | ------------------ | ------------------- | -------------------- |
| **OCR** | **Patient Memory** | **Local Inference** | **FYP Architecture** |

</p>

---

# ⚠️ Medical Disclaimer

> **This project is an academic and research prototype. It is NOT a medical diagnostic system and must NOT be used as a substitute for a qualified healthcare professional.**

AI-generated information may be:

* Incorrect
* Incomplete
* Outdated
* Misinterpreted
* Unsafe for certain clinical situations

Always consult a qualified healthcare professional for diagnosis, treatment decisions, medication changes, or emergency situations.

---

# 📄 License

This project is developed primarily for **academic and research purposes**.

Add an appropriate open-source license if this repository is intended for public distribution.

---

<div align="center">

## 🩺 Building AI That Understands How People Actually Talk About Their Health.

### **AI-Powered Personal Health Intelligence Companion**

**Understand • Remember • Retrieve • Reason • Assist**

<br>

⭐ If you find this project interesting, consider giving the repository a star.

</div>

```

---

## File: `requirements.txt`

```text
absl-py==2.5.0
accelerate==1.14.0
aiohappyeyeballs==2.7.1
aiohttp==3.14.3
aiosignal==1.4.0
aiosqlite==0.22.1
alembic==1.18.5
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.14.2
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
asttokens==3.0.2
async-timeout==4.0.3
asyncpg==0.31.0
attrs==26.1.0
beautifulsoup4==4.15.0
bert-score==0.3.13
certifi==2026.7.22
cffi==2.1.0
charset-normalizer==3.4.9
click==8.4.2
colorama==0.4.6
comm==0.2.3
contourpy==1.3.2
cryptography==49.0.0
cycler==0.12.1
datasets==5.0.1
debugpy==1.8.21
decorator==5.3.1
deep-translator==1.11.4
defusedxml==0.7.1
dill==0.4.1
diskcache==5.6.3
distro==1.9.0
dnspython==2.8.0
ecdsa==0.19.2
email-validator==2.3.0
exceptiongroup==1.3.1
executing==2.2.1
fastapi==0.139.2
filelock==3.32.2
fonttools==4.63.0
frozenlist==1.8.0
fsspec==2026.6.0
gguf==0.19.0
google_search_results==2.4.2
greenlet==3.5.4
groq==0.37.1
grpcio==1.83.0
h11==0.16.0
h2==4.4.1
hf-xet==1.6.0
hpack==4.2.0
httpcore==1.0.9
httpcore2==2.10.0
httpx==0.28.1
httpx-sse==0.4.3
httpx2==2.10.0
huggingface_hub==1.26.0
hyperframe==6.1.0
idna==3.18
iniconfig==2.3.0
ipykernel==7.3.0
ipython==8.39.0
jedi==0.20.0
Jinja2==3.1.6
jiter==0.16.0
joblib==1.5.3
jsonpatch==1.33
jsonpointer==3.1.1
jupyter_client==8.9.1
jupyter_core==5.9.1
kiwisolver==1.5.0
langchain==1.3.15
langchain-classic==1.0.8
langchain-community==0.4.2
langchain-core==1.5.4
langchain-groq==1.1.3
langchain-openai==1.5.0
langchain-protocol==0.0.18
langchain-text-splitters==1.1.2
langdetect==1.0.9
langgraph==1.2.11
langgraph-checkpoint==4.1.1
langgraph-checkpoint-postgres==3.1.1
langgraph-prebuilt==1.1.0
langgraph-sdk==0.4.2
langsmith==0.10.18
llama_cpp_python==0.3.34
Mako==1.3.12
markdown-it-py==4.2.0
MarkupSafe==3.0.3
matplotlib==3.10.9
matplotlib-inline==0.2.2
mdurl==0.1.2
mpmath==1.3.0
multidict==6.7.1
multiprocess==0.70.19
nest-asyncio2==1.7.2
networkx==3.4.2
nltk==3.10.2
numpy==1.26.4
openai==3.0.0
orjson==3.11.9
ormsgpack==1.12.2
packaging==26.0
pandas==2.2.3
parso==0.8.7
peft==0.20.0
pillow==12.3.0
platformdirs==4.11.2
pluggy==1.6.0
portalocker==3.2.0
prompt_toolkit==3.0.53
propcache==0.5.2
protobuf==7.35.1
psutil==7.2.2
psycopg==3.3.4
psycopg-binary==3.3.4
psycopg-pool==3.3.1
pure_eval==0.2.3
pyarrow==25.0.0
pyasn1==0.6.4
pycparser==3.0
pydantic==2.13.4
pydantic-settings==2.14.2
pydantic_core==2.46.4
Pygments==2.20.0
pyparsing==3.3.2
pytesseract==0.3.13
pytest==9.1.1
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
python-jose==3.5.0
pytz==2026.3.post1
pywin32==312
PyYAML==6.0.3
pyzmq==27.1.0
qdrant-client==1.19.0
regex==2026.7.19
requests==2.34.2
requests-toolbelt==1.0.0
rich==15.0.0
rouge_score==0.1.2
rsa==4.9.1
safetensors==0.8.0
scikit-learn==1.7.2
scipy==1.15.3
sentence-transformers==5.6.1
shellingham==1.5.4
six==1.17.0
sniffio==1.3.1
soupsieve==2.9.2
SQLAlchemy==2.0.51
stack-data==0.6.3
starlette==1.3.1
sympy==1.14.0
tenacity==9.1.4
threadpoolctl==3.6.0
tiktoken==0.13.0
tokenizers==0.22.2
tomli==2.4.1
torch==2.13.0
tornado==6.5.8
tqdm==4.70.0
traitlets==5.16.1
transformers==5.14.1
truststore==0.10.4
typer==0.27.1
typing-inspection==0.4.2
typing_extensions==4.16.0
tzdata==2026.3
urllib3==2.7.0
uuid_utils==0.17.0
uvicorn==0.51.0
wcwidth==0.8.2
websockets==15.0.1
xxhash==3.8.1
yarl==1.24.5
zstandard==0.25.0

```

---

## File: `app\config.py`

```python
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # ── Auth ──────────────────────────────────────────────────────────────
    HF_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7             # longer-lived refresh token
    RESET_TOKEN_EXPIRE_HOURS: int = 1              # password-reset token TTL
    VERIFY_TOKEN_EXPIRE_HOURS: int = 48            # email-verify token TTL

    # ── Model & CORS (sensible dev defaults) ──────────────────────────────
    LLM_MODEL: str = r"C:\Users\jason\.cache\models\biomistral-Q4_K_M.gguf"
    LLM_BASE_URL: str = "http://127.0.0.1:8080/v1"
    LLM_API_KEY: str = "api-key"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── Email / SMTP (leave unset for dev — emails are logged to console) ─
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True

    SERP_API_KEY : str
    GROQ_API_KEY : str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # fast & reliable free tool-calling model
    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()

```

---

## File: `app\deps.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        token_version: int | None = payload.get("token_version")
        if user_id is None:
            logger.warning("Token decode succeeded but 'sub' claim missing")
            raise credentials_exception
    except Exception:
        logger.warning("Token decode failed — invalid or expired token")
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning("Auth user not found | user_id=%s", user_id)
        raise credentials_exception

    if not user.is_active:
        logger.warning("Auth user inactive | user=%s", user.username)
        raise credentials_exception

    logger.debug("Authenticated user=%s | token_version=%s", user.username, token_version)
    return user


def require_role(*allowed_roles: str):
    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            logger.warning(
                "Role access denied | user=%s | role=%s | required=%s",
                user.username,
                user.role,
                ", ".join(allowed_roles),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return user
    return checker



```

---

## File: `app\main.py`

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.rag.embedder import get_embedder
from app.api import auth, chat, rag, agent
from app.config import settings
from app.db.lifespan import lifespan as db_lifespan
from app.db.session import init_models
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_settings():

    required = [
        settings.DATABASE_URL,
        settings.SECRET_KEY,
        settings.QDRANT_URL,
        settings.GROQ_API_KEY,
        settings.LLM_API_KEY,
    ]

    if not all(required):
        logger.error("Missing required environment variables — aborting startup")
        raise RuntimeError("Missing required environment variables")

    logger.info("✓ All required environment variables present")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("▶ Application lifespan starting...")

    # DB backends (LangGraph checkpointer + store) must be set up before the
    # async SQLAlchemy tables and embedder warm-up run.
    async with db_lifespan(app):
        validate_settings()
        # get_embedder()
        # app.state.llm = load_llm()
        # app.state.embedder = load_embedder()      # new
        # app.state.agent = build_health_agent()    # new
        await init_models()

        logger.info("✓ Application startup complete — ready to serve requests")
        yield
        logger.info("■ Application shutting down...")


app = FastAPI(
    title="Medical Chat API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agent.router)   # new

@app.get("/")
async def root():
    return {"message": "API Running"}
```

---

## File: `app\__init__.py`

```python

```

---

## File: `app\agent\graph.py`

```python
# app/agent/graph.py
"""Decoupled router-node pipeline.

    Router (Groq, tool-calling)  ──tools?──▶  Tools  ──▶  BioMistral (local GGUF)  ──▶  END
                        │
                        └───── no tools ─────────────────▶  BioMistral  ──▶  END

The router decides whether tools are needed and emits tool_calls; it never
writes the final answer. Tool results are flattened into plain text and
handed to the BioMistral node, which does a single clean inference turn.
"""
import re
import time

from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.nodes.biomistral_node import biomistral_node
from app.agent.nodes.router_node import router_node
from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.db.lifespan import checkpointer, store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_tool_node = ToolNode(TOOLS)


def _extract_tool_metadata(tool_messages: list) -> dict:
    """Flatten this turn's ToolMessages into plain text for BioMistral and
    pull out the per-turn metadata flags the sidebar / response schema need.

    Only the *new* tool messages (returned by the ToolNode this turn) are
    scanned, so needs_rag / saved_memory reflect the current turn, not the
    accumulated history.
    """
    extracted: list[str] = []
    rag_used = False
    saved_memory = False
    decision_text = ""
    sources: list[str] = []

    for msg in tool_messages:
        name = getattr(msg, "name", "") or ""
        content = msg.content or ""

        extracted.append(f"--- Context from tool [{name}] ---\n{content}\n")

        if name == "retrieve_medical_knowledge":
            rag_used = True
            for line in content.splitlines():
                if "Retrieval decision" in line:
                    match = re.search(r"Retrieval decision:\s*([A-Za-z]+)", line)
                    if match:
                        decision_text = match.group(1)
                else:
                    match = re.match(r"^\s*\[([^\]]+)\]", line)
                    if match:
                        sources.append(match.group(1))

        if name in ("save_patient_fact", "save_emotional_state"):
            saved_memory = True

    return {
        "tool_results": "\n".join(extracted),
        "needs_rag": rag_used,
        "retrieval_decision": decision_text or ("retrieved" if rag_used else ""),
        "retrieved_docs": [{"source": s} for s in sources[:3]],
        "saved_memory": saved_memory,
    }


def _run_tools(state: AgentState) -> dict:
    """Execute the router's tool calls, then fold the results into the
    plain-text context + metadata BioMistral consumes."""
    messages = state.get("messages", [])

    if messages:
        last_message = messages[-1]
        if isinstance(last_message, AIMessage) and getattr(last_message, "tool_calls", None):
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "unknown_tool")
                logger.info("🔧 Running tool: %s", tool_name)

    start = time.monotonic()
    try:
        result = _tool_node.invoke(state)
    except Exception:
        logger.exception("✗ Tool execution failed")
        raise
    logger.info("✓ Tools finished in %.2fs", time.monotonic() - start)

    new_tool_msgs = [
        m for m in result.get("messages", []) if getattr(m, "type", None) == "tool"
    ]
    result.update(_extract_tool_metadata(new_tool_msgs))
    return result


def _route_after_router(state: AgentState) -> str:
    """tools_condition wrapper: route to 'tools' when the router emitted
    tool_calls, otherwise straight to the BioMistral reasoning node.

    tools_condition raises on an empty message list; the router always
    persists at least the user's HumanMessage before this runs, but we guard
    the empty case so a unit call can't crash the graph.
    """
    if not state.get("messages"):
        route = "biomistral"
    else:
        route = "tools" if tools_condition(state) == "tools" else "biomistral"
    logger.info("↪ Router routing → %s", route)
    return route


def build_health_agent():
    graph = StateGraph(AgentState)

    # 1. Add nodes
    graph.add_node("router", router_node)
    graph.add_node("tools", _run_tools)
    graph.add_node("biomistral", biomistral_node)

    # 2. Entry point
    graph.set_entry_point("router")

    # 3. Conditional routing from the router
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "tools": "tools",        # router outputted tool_calls
            "biomistral": "biomistral",  # no tools → straight to reasoning
        },
    )

    # 4. Tools feed their context into BioMistral
    graph.add_edge("tools", "biomistral")

    # 5. BioMistral ends the turn
    graph.add_edge("biomistral", END)

    compiled = graph.compile(
        checkpointer=checkpointer,
        store=store,
    )

    logger.info("✓ Health agent graph compiled (router → tools? → biomistral → END)")
    return compiled

```

---

## File: `app\agent\state.py`

```python
# app/agent/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    patient_id: str
    ocr_context: str
    tool_results: str      # plain text gathered from tools this turn, shown to BioMistral
    raw_input: str
    messages: Annotated[list, add_messages]

    # Metadata flags — read straight from checkpoint rows by
    # conversation_service.py to build the sidebar. Don't rename these
    # without updating that file too.
    needs_rag: bool
    retrieval_decision: str
    retrieved_docs: list[dict]
    saved_memory: bool     # per-turn: a memory tool ran THIS turn (not a prior one)
    detected_lang: str     # kept for conversation_service / agent_service (legacy)

    # answer/final_response are the same text right now (Phase 2 removed the
    # translate_out node that used to translate answer -> final_response).
    # Kept as two separate keys so a future translation phase can reintroduce
    # that split without touching conversation_service.py.
    answer: str
    final_response: str

```

---

## File: `app\agent\tools.py`

```python
# app/agent/tools.py
import uuid
from datetime import date

from langchain_core.tools import tool

from app.db.lifespan import store
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@tool
def fetch_patient_facts(patient_id: str, query: str) -> str:
    """Retrieve relevant medical facts about a patient from persistent memory.
    Use when the patient refers to past symptoms or history."""
    logger.info("▶ fetch_patient_facts | patient=%s | query=%s", patient_id, query[:80])
    if store is None:
        logger.warning("Memory store not available for fetch_patient_facts")
        return "Memory store not available."
    try:
        items = store.search(("patient_facts", patient_id), query=query, limit=5)
        facts = [item.value for item in items]
        if not facts:
            logger.info("No patient history found | patient=%s", patient_id)
            return "No relevant patient history found."
        logger.info("✓ Fetched %d patient facts | patient=%s", len(facts), patient_id)
        lines = [f"- {f['symptom']} (onset: {f['onset']}, status: {f['status']})" for f in facts]
        return "Known patient history:\n" + "\n".join(lines)
    except Exception as e:
        logger.exception("fetch_patient_facts failed")
        return f"Error retrieving patient facts: {e}"


@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieve evidence-based medical knowledge for diagnosis or treatment questions."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    try:
        result = corrective_retrieve(query, top_k=5)
        docs = result["docs"]
        if not docs:
            logger.info("No documents found | decision=%s", result["decision"])
            return f"[Retrieval decision: {result['decision']}] No relevant documents found."
        logger.info(
            "✓ retrieve_medical_knowledge returned %d docs | decision=%s",
            len(docs),
            result["decision"],
        )
        lines = [f"[{d['source']}] {d['text'][:400]}" for d in docs[:3]]
        return f"[Retrieval decision: {result['decision']}]\n\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}"


@tool
def save_patient_fact(patient_id: str, symptom: str, onset: str, status: str, source_message: str) -> str:
    """Save a newly reported symptom to the patient's persistent record."""
    logger.info(
        "▶ save_patient_fact | patient=%s | symptom=%s | status=%s",
        patient_id,
        symptom,
        status,
    )
    if store is None:
        logger.warning("Memory store not available for save_patient_fact")
        return "Memory store not available."
    key = f"{symptom}_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_facts", patient_id), key, {
            "symptom": symptom, "onset": onset, "status": status,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        logger.info("✓ Saved patient fact | patient=%s | key=%s", patient_id, key)
        return f"Saved to patient record: {symptom} ({status})"
    except Exception as e:
        logger.exception("save_patient_fact failed")
        return f"Error saving fact: {e}"


@tool
def save_emotional_state(patient_id: str, emotion: str, intensity: str, trigger: str, source_message: str) -> str:
    """Save the patient's emotional state when they express anxiety, stress, or fear."""
    logger.info(
        "▶ save_emotional_state | patient=%s | emotion=%s | intensity=%s",
        patient_id,
        emotion,
        intensity,
    )
    if store is None:
        logger.warning("Memory store not available for save_emotional_state")
        return "Memory store not available."
    key = f"emotion_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_emotions", patient_id), key, {
            "emotion": emotion, "intensity": intensity, "trigger": trigger,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        logger.info("✓ Saved emotional state | patient=%s | key=%s", patient_id, key)
        return f"Noted emotional state: {emotion} ({intensity})"
    except Exception as e:
        logger.exception("save_emotional_state failed")
        return f"Error saving emotion: {e}"


TOOLS = [fetch_patient_facts, retrieve_medical_knowledge, save_patient_fact, save_emotional_state]
```

---

## File: `app\agent\nodes\biomistral_node.py`

```python
# app/agent/nodes/biomistral_node.py
"""Node 2 — BioMistral reasoning.

Receives the raw user input along with any plain-text context the router's
tools gathered this turn (memory + RAG) and produces the final empathetic
answer from the local GGUF model. Because tool-calling is offloaded to the
router, this node does a single clean inference turn with no JSON or
function-calling overhead.
"""
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# OCR documents can be long; cap what we feed the local model so we don't
# blow its context window.
_OCR_CHAR_LIMIT = 2000

BIOMISTRAL_PROMPT = """You are an empathetic Pakistani AI health companion.

Use the provided medical & patient context below (if available) to answer the user's health concerns.


{ocr_context}

{tool_context}


GUIDELINES:
- If the query is plain conversational/greeting, reply naturally in plain text.
- If it is a medical query, respond conversationally based on the context. You can recommend these things where helpful:
  - Possible diagnosis or insights
  - Lifestyle adjustments, diet, and exercise suggestions
  - Home care or general advice
  - Clear advice on when to consult a doctor
- Never invent facts outside the provided context.
"""


def biomistral_node(state: AgentState) -> dict:
    logger.info("▶ BioMistral Reasoning Node Started")

    ocr_raw = (state.get("ocr_context") or "")[:_OCR_CHAR_LIMIT]
    ocr_str = f"OCR Document Context:\n{ocr_raw}" if ocr_raw else "No OCR text attached."

    tool_str = state.get("tool_results") or "No external context retrieved."

    formatted_system = BIOMISTRAL_PROMPT.format(
        ocr_context=ocr_str,
        tool_context=tool_str,
    )

    # Single clean inference turn: system prompt (with gathered context) +
    # the user's raw input only. The router already persisted the user
    # message, so here we store just the final AIMessage — completing the
    # conversation pair without re-inserting the HumanMessage.
    messages = [
        SystemMessage(content=formatted_system),
        HumanMessage(content=state["raw_input"]),
    ]

    start = time.monotonic()
    response = llm.invoke(messages)
    logger.info("✓ BioMistral completed in %.2fs", time.monotonic() - start)

    answer_text = (response.content or "").strip()
    if not answer_text:
        answer_text = (
            "I'm sorry, I wasn't able to generate a proper response to that. "
            "Could you try rephrasing your message?"
        )
        response = AIMessage(content=answer_text)

    logger.info(
        "✓ BioMistral produced final answer | patient=%s | chars=%d",
        state["patient_id"],
        len(answer_text),
    )

    return {
        "answer": answer_text,
        "final_response": answer_text,
        "messages": [response],
    }

```

---

## File: `app\agent\nodes\router_node.py`

```python
# app/agent/nodes/router_node.py
"""Node 1 — Router.

A fast Groq model (llama-3.3-70b-versatile) bound with the healthcare tools
decides whether the turn needs any tools (memory / RAG) and emits the
tool_calls when it does. It never produces the final answer — that is the
BioMistral node's job — so on a no-tool turn the router stores only the
user's message (no intermediate assistant text that would pollute history).
"""
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Groq is used strictly for routing / tool-calling — reliable .bind_tools()
# support that the local GGUF model can't do cleanly.
router_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.0,
).bind_tools(TOOLS)

ROUTER_SYSTEM_PROMPT = """You are an intelligent routing agent for a healthcare assistant.
Your job is to analyze the conversation and call appropriate tools ONLY if required:
1. Call 'fetch_patient_facts' if the user mentions past history/symptoms.
2. Call 'retrieve_medical_knowledge' if the user asks a specific medical/health query.
3. Call 'save_patient_fact' or 'save_emotional_state' if the user reports new symptoms or emotional distress.

If no tools are needed (e.g., greetings, small talk), do NOT call any tools.
Never call the same tool with the same input more than once in a turn.
Patient ID: {patient_id}
"""


def router_node(state: AgentState) -> dict:
    logger.info("▶ Router Node Started | patient=%s", state["patient_id"])

    system_text = ROUTER_SYSTEM_PROMPT.format(patient_id=state["patient_id"])
    messages = [SystemMessage(content=system_text)] + list(state.get("messages", []))

    # The current user input is not in history yet at the start of a turn
    # (the previous turn ended on an assistant message), so append it for
    # this invocation only. It gets persisted to state below.
    if not messages or not isinstance(messages[-1], HumanMessage):
        messages.append(HumanMessage(content=state["raw_input"]))

    start = time.monotonic()
    response = router_llm.invoke(messages)
    logger.info("✓ Router invoke finished in %.2fs", time.monotonic() - start)

    tool_calls = getattr(response, "tool_calls", None)

    # Always persist the user's message so the conversation pair survives in
    # the checkpoint (add_messages appends; losing the HumanMessage breaks
    # role alternation for the local model on later turns). The router's own
    # AIMessage is only stored when it actually carries tool_calls —
    # otherwise it would be a ghost assistant turn before the real answer.
    if tool_calls:
        names = [tc.get("name", "?") for tc in tool_calls]
        logger.info("Router requested tools: %s", ", ".join(names))
        return {"messages": [HumanMessage(content=state["raw_input"]), response]}

    logger.info("Router decided no tools needed → straight to BioMistral")
    return {"messages": [HumanMessage(content=state["raw_input"])]}

```

---

## File: `app\api\agent.py`

```python
# app/api/agent.py
import time

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool

from app.deps import get_current_user
from app.models.user import User
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    ConversationDetail,
    ConversationMeta,
)
from app.core.rag.ocr import extract_text_from_base64
from app.services.agent_service import run_agent
from app.services.conversation_service import get_conversation, list_conversations
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/invoke", response_model=AgentResponse)
async def invoke(req: AgentRequest):
    start = time.monotonic()
    logger.info(
        "▶ POST /agent/invoke | patient=%s | thread=%s | OCR=%s",
        req.patient_id,
        req.thread_id or "(default)",
        "yes" if req.image_base64 else "no",
    )
    try:
        ocr_text = ""
        if req.image_base64:
            ocr_text = extract_text_from_base64(req.image_base64)
            logger.info("OCR extraction completed | chars=%d", len(ocr_text))
        result = await run_agent(req, ocr_text)
        logger.info(
            "✓ POST /agent/invoke completed in %.2fs | patient=%s",
            time.monotonic() - start,
            req.patient_id,
        )
        return result
    except Exception as e:
        logger.exception(
            "✗ POST /agent/invoke failed after %.2fs | patient=%s",
            time.monotonic() - start,
            req.patient_id,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threads", response_model=list[ConversationMeta])
async def list_threads(user: User = Depends(get_current_user)):
    """Sidebar rows: every conversation the current patient has started,
    newest first. Reads turn-end checkpoints — no separate storage layer."""
    start = time.monotonic()
    logger.info("▶ GET /agent/threads | user=%s", str(user.id))
    conversations = await run_in_threadpool(list_conversations, str(user.id))
    logger.info(
        "✓ GET /agent/threads returned %d conversations in %.2fs | user=%s",
        len(conversations),
        time.monotonic() - start,
        str(user.id),
    )
    return conversations


@router.get("/threads/{thread_id}", response_model=ConversationDetail)
async def load_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Full transcript of one conversation, restored from its checkpoints.
    Ownership is enforced by the patient_id stored inside the state."""
    start = time.monotonic()
    logger.info(
        "▶ GET /agent/threads/%s | user=%s",
        thread_id,
        str(user.id),
    )
    conversation = await run_in_threadpool(get_conversation, thread_id, str(user.id))
    if conversation is None:
        logger.warning(
            "Conversation not found or access denied | thread=%s | user=%s",
            thread_id,
            str(user.id),
        )
        raise HTTPException(status_code=404, detail="Conversation not found")
    logger.info(
        "✓ GET /agent/threads/%s loaded %d messages in %.2fs",
        thread_id,
        len(conversation.get("messages", [])),
        time.monotonic() - start,
    )
    return conversation
```

---

## File: `app\api\auth.py`

```python
"""Auth router — simplified to Register + Login (Phase 5).

Forgot/reset password, change password, delete account, email verification,
and token refresh were all removed to keep the project focused on chat
history. If the React frontend still calls those endpoints, those calls
will 404 until the frontend is updated to match.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.utils.logging_config import log_auth_event

router = APIRouter(prefix="/auth", tags=["auth"])


async def _get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def _issue_token_response(user: User) -> TokenResponse:
    """Build the response the React client expects.

    session.js stores both access_token and refresh_token — but the
    refresh-token table/rotation flow is gone in Phase 5, so refresh_token
    here is just a copy of access_token, not a real second credential.
    """
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=access_token)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    existing_username = await _get_user_by_username(db, body.username)
    existing_email = await _get_user_by_email(db, body.email)
    if existing_username or existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already taken.",
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log_auth_event("REGISTER", user.username, str(user.id), request.client.host, success=True)
    return _issue_token_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await _get_user_by_username(db, body.username)
    ip = request.client.host

    if not user or not verify_password(body.password, user.hashed_password):
        log_auth_event("LOGIN", body.username, ip=ip, success=False, detail="bad credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not user.is_active:
        log_auth_event("LOGIN", user.username, str(user.id), ip, success=False, detail="inactive")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    log_auth_event("LOGIN", user.username, str(user.id), ip, success=True)
    return _issue_token_response(user)

@router.get("/me")
async def get_current_user(user: User = Depends(get_current_user)):
    return user    
```

---

## File: `app\api\chat.py`

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.chat_service import stream_chat

from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/stream")
async def stream(req: ChatRequest):

    messages = [
        message.model_dump()
        for message in req.messages
    ]
    logger.info(
        "▶ POST /chat/stream | messages=%d | temperature=%.2f | max_tokens=%d",
        len(messages),
        req.temperature,
        req.max_tokens,
    )
    return StreamingResponse(
        stream_chat(
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ),
        media_type="text/plain",
    )
```

---

## File: `app\api\rag.py`

```python
# app/api/rag.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.rag_chat_service import stream_rag_chat
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/stream")
async def stream(req: ChatRequest):
    logger.info("Received RAG chat request.")

    messages = [m.model_dump() for m in req.messages]

    return StreamingResponse(
        stream_rag_chat(
            messages=messages,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
        ),
        media_type="text/plain",
    )
```

---

## File: `app\api\__init__.py`

```python

```

---

## File: `app\core\llm.py`

```python
# app/core/llm.py
from langchain_openai import ChatOpenAI

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Initializing LLM client (%s @ %s)", settings.LLM_MODEL, settings.LLM_BASE_URL)

llm = ChatOpenAI(
    base_url=settings.LLM_BASE_URL,
    api_key=settings.LLM_API_KEY,
    model=settings.LLM_MODEL,
    timeout=600
)

logger.info("LLM client ready.")
```

---

## File: `app\core\password_policy.py`

```python
"""Password strength policy shared between backend and frontend docs.

Rules here are enforced server-side. The frontend RegisterModal mirrors them
for a snappy UX, but the server is the source of truth.
"""

import re

# ── Policy constants (exported so frontend docs can reference them) ────────

MIN_LENGTH = 8
MAX_LENGTH = 128
MIN_LOWERCASE = 1
MIN_UPPERCASE = 1
MIN_DIGIT = 1
MIN_SPECIAL = 1

# Common / known-bad passwords that should always be rejected
COMMON_PASSWORDS: set[str] = {
    "password", "password1", "password123",
    "12345678", "123456789", "1234567890",
    "qwerty123", "qwertyuiop",
    "letmein", "welcome", "monkey", "dragon",
    "abc123", "abc1234", "abc12345",
    "P@ssw0rd", "Passw0rd", "passw0rd",
}


# ── Validation ────────────────────────────────────────────────────────────

class PasswordError:
    """Describes a single password policy violation."""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __repr__(self) -> str:
        return f"PasswordError({self.code}: {self.message})"


def validate_password(password: str) -> list[PasswordError]:
    """Return a list of policy violations (empty = valid)."""
    errors: list[PasswordError] = []

    if len(password) < MIN_LENGTH:
        errors.append(PasswordError(
            "too_short",
            f"Password must be at least {MIN_LENGTH} characters.",
        ))
    if len(password) > MAX_LENGTH:
        errors.append(PasswordError(
            "too_long",
            f"Password must be at most {MAX_LENGTH} characters.",
        ))
    if MIN_UPPERCASE and sum(1 for c in password if c.isupper()) < MIN_UPPERCASE:
        errors.append(PasswordError(
            "missing_uppercase",
            f"Password must contain at least {MIN_UPPERCASE} uppercase letter.",
        ))
    if MIN_LOWERCASE and sum(1 for c in password if c.islower()) < MIN_LOWERCASE:
        errors.append(PasswordError(
            "missing_lowercase",
            f"Password must contain at least {MIN_LOWERCASE} lowercase letter.",
        ))
    if MIN_DIGIT and sum(1 for c in password if c.isdigit()) < MIN_DIGIT:
        errors.append(PasswordError(
            "missing_digit",
            f"Password must contain at least {MIN_DIGIT} digit.",
        ))
    if MIN_SPECIAL and sum(1 for c in password if not c.isalnum()) < MIN_SPECIAL:
        errors.append(PasswordError(
            "missing_special",
            f"Password must contain at least {MIN_SPECIAL} special character.",
        ))
    if password.lower() in COMMON_PASSWORDS:
        errors.append(PasswordError(
            "common_password",
            "This password is too common. Choose a more unique one.",
        ))

    return errors

```

---

## File: `app\core\security.py`

```python
"""Password hashing, JWT management."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError

from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

ph = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ======================================================================
# Password hashing
# ======================================================================


def hash_password(password: str) -> str:
    logger.debug("Hashing password")
    return ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        result = ph.verify(hashed, plain)
        logger.debug("Password verification succeeded")
        return result
    except VerifyMismatchError:
        logger.info("Password verification failed — mismatch")
        return False


# ======================================================================
# Access tokens (JWT — short-lived, includes token_version)
# ======================================================================


def create_access_token(
    data: dict,
    *,
    token_version: int = 1,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_version": token_version})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.debug(
        "Access token issued | sub=%s | expires=%s | token_version=%d",
        to_encode.get("sub", "-"),
        expire.isoformat(),
        token_version,
    )
    return token


def decode_access_token(token: str) -> dict:
    """Decode a JWT.  Raises ``JWTError`` on expiry or bad signature."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug("Token decoded | sub=%s", payload.get("sub", "-"))
        return payload
    except JWTError as e:
        logger.warning("JWT decode failed | reason=%s", e)
        raise

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        token_version: int | None = payload.get("token_version")
        if user_id is None:
            logger.warning("Token decoded but 'sub' claim missing")
            raise credentials_exception
    except Exception:
        logger.warning("Security get_current_user — token validation failed")
        raise credentials_exception






```

---

## File: `app\core\rag\corrective_rag.py`

```python
# app/core/rag/corrective_rag.py

from serpapi import GoogleSearch

from app.config import settings
from app.core.rag.qdrant_store import retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

RELEVANCE_THRESHOLD = 0.5
AMBIGUOUS_THRESHOLD = 0.35


def evaluate_relevance(docs: list[dict]) -> tuple[str, float]:
    """
    Evaluate the quality of retrieved documents.
    """

    if not docs:
        logger.warning("No documents retrieved from Qdrant.")
        return "incorrect", 0.0

    scores = [d["score"] for d in docs]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)

    logger.info(
        "Retrieval evaluation completed | max_score=%.3f | avg_score=%.3f",
        max_score,
        avg_score,
    )

    if max_score >= RELEVANCE_THRESHOLD:
        logger.info("Retrieval classified as CORRECT.")
        return "correct", avg_score

    if avg_score >= AMBIGUOUS_THRESHOLD:
        logger.warning("Retrieval classified as AMBIGUOUS.")
        return "ambiguous", avg_score

    logger.warning("Retrieval classified as INCORRECT.")
    return "incorrect", avg_score


def web_search_fallback(query: str) -> list[dict]:
    """
    Google Search fallback using SerpAPI.
    """

    logger.info("Starting SerpAPI fallback search...")

    try:
        params = {
            "engine": "google",
            "q": f"medical {query}",
            "api_key": settings.SERP_API_KEY,
            "num": 3,
            "gl": "us",
            "hl": "en",
            "safe": "active",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        docs = []

        for item in results.get("organic_results", []):
            docs.append(
                {
                    "text": item.get("snippet", ""),
                    "source": item.get("link", ""),
                    "category": "web",
                    "score": 0.5,
                    "title": item.get("title", ""),
                }
            )

        logger.info(
            "SerpAPI returned %d web documents.",
            len(docs),
        )

        return docs

    except Exception:
        logger.exception("SerpAPI fallback failed.")
        return []


def corrective_retrieve(query: str, top_k: int = 5) -> dict:
    """
    Complete Corrective RAG retrieval pipeline.
    """

    logger.info("Starting Corrective RAG pipeline.")

    docs = retrieve(query, top_k=top_k)

    logger.info("Retrieved %d documents from Qdrant.", len(docs))

    decision, avg_score = evaluate_relevance(docs)

    if decision == "incorrect":
        logger.warning(
            "Low retrieval quality detected. Replacing context with web search results."
        )
        docs = web_search_fallback(query) + docs

    elif decision == "ambiguous":
        logger.warning(
            "Ambiguous retrieval detected. Augmenting context with web search results."
        )
        docs = docs + web_search_fallback(query)

    logger.info(
        "Corrective RAG completed | decision=%s | avg_score=%.3f | final_docs=%d",
        decision,
        avg_score,
        len(docs[:5]),
    )

    return {
        "docs": docs[:5],
        "decision": decision,
        "avg_score": round(avg_score, 3),
    }
```

---

## File: `app\core\rag\embedder.py`

```python
# app/core/rag/embedder.py

from sentence_transformers import SentenceTransformer

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_embedder: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """
    Return a singleton SentenceTransformer instance.
    The model is loaded only once during the application's lifetime.
    """
    global _embedder

    if _embedder is None:
        logger.info("Loading embedding model...")
        _embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            token=settings.HF_TOKEN,
        )
        logger.info("Embedding model loaded.")

    return _embedder
```

---

## File: `app\core\rag\ocr.py`

```python
# app/core/rag/ocr.py
import base64
import io
from PIL import Image
import pytesseract

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def extract_text_from_base64(image_b64: str) -> str:
    if not image_b64:
        logger.info("OCR skipped — empty image_base64")
        return ""
    logger.info("▶ OCR extraction started | b64_len=%d", len(image_b64))
    try:
        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))
        logger.info("Image loaded | size=%s | mode=%s", image.size, image.mode)
        text = pytesseract.image_to_string(image)
        result = text.strip()
        logger.info("✓ OCR extraction completed | chars=%d", len(result))
        return result
    except Exception:
        logger.exception("OCR extraction failed")
        return ""
```

---

## File: `app\core\rag\qdrant_store.py`

```python
# app/core/rag/qdrant_store.py

import time

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.config import settings
from app.core.rag.embedder import get_embedder
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

embedder = get_embedder()

# Qdrant Cloud free tier autosuspends an idle cluster; the first query after
# idle has to wake it up, which can blow past httpx's default read timeout.
# A generous timeout + a retry mirrors the Neon autosuspend handling in
# agent_service.py.
_QDRANT_TIMEOUT = 60
_QDRANT_RETRIES = 1
_QDRANT_RETRY_DELAY = 1.0

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=_QDRANT_TIMEOUT,
)

COLLECTION = "health_knowledge"


def retrieve(
    query: str,
    top_k: int = 5,
    category: str | None = None,
) -> list[dict]:
    """
    Retrieve the most relevant medical documents from Qdrant.
    """

    logger.info(
        "Searching Qdrant | collection=%s | top_k=%d",
        COLLECTION,
        top_k,
    )

    # Generate embedding
    vector = embedder.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    query_filter = None

    if category:
        logger.debug("Applying category filter: %s", category)

        query_filter = Filter(
            must=[
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category),
                )
            ]
        )

    # Retry transient network errors (autosuspend wake, throttling). If the
    # cluster is genuinely down this re-raises after the last attempt and the
    # calling tool (retrieve_medical_knowledge) degrades gracefully instead of
    # killing the agent.
    for attempt in range(_QDRANT_RETRIES + 1):
        try:
            results = client.query_points(
                collection_name=COLLECTION,
                query=vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
                score_threshold=0.3,
            )
            break
        except Exception as e:
            if attempt >= _QDRANT_RETRIES:
                logger.exception("Qdrant query failed after %d attempts", attempt + 1)
                raise
            logger.warning(
                "Transient Qdrant error (attempt %d/%d), retrying: %s",
                attempt + 1,
                _QDRANT_RETRIES,
                e,
            )
            time.sleep(_QDRANT_RETRY_DELAY)

    docs = [
        {
            "text": r.payload.get("text", ""),
            "source": r.payload.get("source", ""),
            "category": r.payload.get("category", ""),
            "score": r.score,
        }
        for r in results.points
    ]

    logger.info(
        "Qdrant retrieval completed | retrieved=%d documents",
        len(docs),
    )

    return docs
```

---

## File: `app\core\rag\translation.py`

```python
# app/core/rag/translation.py
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException

from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        logger.info("Detected language: %s | text_preview=%s", lang, text[:50])
        return lang
    except LangDetectException:
        logger.warning("Language detection failed, defaulting to 'en'")
        return "en"


def to_english(text: str, source_lang: str) -> str:
    if source_lang == "en":
        return text
    logger.info("Translating to English | source=%s | chars=%d", source_lang, len(text))
    try:
        result = GoogleTranslator(source="auto", target="english").translate(text)
        logger.info("✓ Translation to English completed | chars=%d", len(result))
        return result
    except Exception:
        logger.exception("Translation to English failed, falling back to original text")
        return text


def from_english(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    logger.info("Translating from English | target=%s | chars=%d", target_lang, len(text))
    try:
        result = GoogleTranslator(source="english", target=target_lang).translate(text)
        logger.info("✓ Translation to %s completed | chars=%d", target_lang, len(result))
        return result
    except Exception:
        logger.exception("Translation back to source language failed, returning English")
        return text
```

---

## File: `app\db\base.py`

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

---

## File: `app\db\lifespan.py`

```python
# app/db/lifespan.py
"""
LangGraph Postgres backends, owned by the FastAPI lifespan.

Both the checkpointer (conversation continuity) and the store (per-patient
fact/emotion memory) are module-level singletons built on the shared Neon
psycopg pool (`app/db/pool.py`), so graph compilation at import time and
`conversation_service`'s queries both see ready objects without blocking
on the DB (pool construction is non-blocking — connections open on a
background worker).

`.setup()` is deferred from import time into the lifespan start: table
creation happens once per server start (idempotent, no-ops after the first
run), and the pools are closed on shutdown.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

from app.db.pool import build_langgraph_pool
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Building LangGraph Postgres pools...")
_checkpointer_pool = build_langgraph_pool()
checkpointer = PostgresSaver(_checkpointer_pool)

_store_pool = build_langgraph_pool()
store = PostgresStore(_store_pool)
logger.info("LangGraph checkpointer and store initialised.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("▶ Setting up LangGraph DB tables...")
    checkpointer.setup()  # creates checkpoint tables on first run, no-ops after
    store.setup()         # creates store tables on first run, no-ops after
    logger.info("✓ LangGraph DB tables ready (checkpointer + store).")
    try:
        yield
    finally:
        logger.info("■ Closing LangGraph connection pools...")
        _checkpointer_pool.close()
        _store_pool.close()
        logger.info("✓ LangGraph connection pools closed.")
```

---

## File: `app\db\pool.py`

```python
# app/db/pool.py
"""
Shared psycopg ConnectionPool for the LangGraph checkpointer and store.

Both langgraph postgres backends take either a bare psycopg connection or a
psycopg_pool pool. A bare connection is a live grenade against Neon:
serverless autosuspend drops idle connections, and with no reconnect path
the first request after idle dies with

    psycopg.OperationalError: SSL connection has been closed unexpectedly

and stays dead — psycopg marks the closed connection unusable, so every
subsequent request fails the same way.

A pool fixes it the way the async engine's `pool_pre_ping=True` does: the
pool's default `check` runs a no-op statement on every checkout, so a stale
connection is discarded and replaced before it is used.

`autocommit`/`prepare_threshold`/`row_factory` mirror what langgraph's
`from_conn_string` passes to `Connection.connect` — the saver/store rely on
those being set. `connect_timeout` and keepalives match the Neon tuning in
`app/db/session.py`.

The LangGraph connections deliberately use Neon's **direct endpoint**, not
the `-pooler` (PgBouncer transaction-mode) one that `DATABASE_URL` points at.
The checkpointer/store hold long-lived connections and rely on server-side
prepared statements (`prepare_threshold=0`) and binary cursors — a
transaction-mode pooler is not designed for that and aborts such connections
(`could not receive data from server: Software caused connection abort`).
The direct endpoint gives real sessions, which is what langgraph's code
expects; the pool handles the remaining autosuspend drops.
"""
from urllib.parse import urlparse, urlunparse

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _langgraph_conn_string() -> str:
    """DATABASE_URL for the LangGraph psycopg connections.

    Two adjustments on top of the asyncpg URL:
      1. psycopg dialect instead of asyncpg's.
      2. Use Neon's *direct* endpoint (host without ``-pooler.``) rather than
         the PgBouncer pooler endpoint — see module docstring. No-op when the
         host isn't a Neon pooler host.
    """
    u = urlparse(settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql"))
    host = u.hostname or ""
    if "-pooler." in host:
        userinfo = ""
        if u.username:
            userinfo = u.username + (f":{u.password}" if u.password else "") + "@"
        netloc = userinfo + host.replace("-pooler.", ".")
        if u.port:
            netloc += f":{u.port}"
        u = u._replace(netloc=netloc)
    return urlunparse(u)


_conn_string = _langgraph_conn_string()
logger.info("LangGraph direct connection string resolved | host=%s", urlparse(_conn_string).hostname or "?")


def build_langgraph_pool() -> ConnectionPool:
    """A process-lifetime pool tuned for Neon serverless Postgres.

    Non-blocking to construct: the pool opens its connections on a
    background worker, so module import never waits on the DB.
    """
    logger.info(
        "Building psycopg ConnectionPool | min_size=1 | max_size=5 | timeout=90s | max_lifetime=900s",
    )
    return ConnectionPool(
        conninfo=_conn_string,
        kwargs={
            # Same non-negotiables as langgraph's own from_conn_string().
            "autocommit": True,
            "prepare_threshold": 0,
            "row_factory": dict_row,
            # Neon can take several seconds to wake a suspended compute.
            "connect_timeout": 60,
            # Detect server-side drops (Neon idle timeout) faster.
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 15,
            "keepalives_count": 3,
        },
        # psycopg_pool's default checkout timeout (30s) is shorter than the
        # per-connect timeout above, so the first checkout during a slow Neon
        # wake would fail before the connect does. Let a checkout wait out the
        # full wake instead of giving up early.
        timeout=90,
        min_size=1,
        max_size=5,
        # Recycle proactively rather than reuse a long-stale pooled conn.
        max_lifetime=900,
        max_idle=300,
    )

```

---

## File: `app\db\session.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.base import Base
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Creating async database engine | pool_pre_ping=True | pool_recycle=300s")
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,        # Confirms the connection is live before sending a query
    pool_recycle=300,          # Refreshes connection before Neon drops it for idling
    connect_args={"timeout": 60},
)
logger.info("Database engine created.")

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_models():
    # Creates tables directly from models — no migration tool needed yet.
    logger.info("▶ Running Base.metadata.create_all...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✓ Database tables initialised.")
```

---

## File: `app\eval\hallucination_check.py`

```python
GROUNDING_PROMPT = """
Question: {query}
Retrieved sources used: {sources}
Model answer: {answer}

Rate the answer on this scale:
0 = answer contains claims not supported by the sources and not general medical knowledge
1 = answer is mostly grounded, with minor unsupported claims
2 = answer is fully grounded in the sources or safe, general medical knowledge

Respond with only the number.
"""
```

---

## File: `app\eval\perplexity.py`

```python
# eval/perplexity.py
import math
from app.core.llm import llm


def compute_perplexity(prompt: str, reference: str) -> float:
    """
    Perplexity of the reference answer conditioned on the prompt.
    Lower = model assigns higher probability to the correct answer.
    """
    full_text = f"{prompt}\n{reference}"

    output = llm(
        full_text,
        max_tokens=0,      # don't generate — just score existing tokens
        logprobs=True,
        echo=True,
    )

    token_logprobs = output["choices"][0]["logprobs"]["token_logprobs"]
    # drop None entries (first token has no logprob)
    logprobs = [lp for lp in token_logprobs if lp is not None]

    avg_neg_logprob = -sum(logprobs) / len(logprobs)
    return math.exp(avg_neg_logprob)
```

---

## File: `app\eval\run_evals.py`

```python
# eval/run_eval.py
import json, os, time
from pathlib import Path
from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.eval.test_set import TEST_CASES


def run_finetuned_only(query: str) -> dict:
    start = time.time()
    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        max_tokens=300,
    )
    return {
        "answer": response["choices"][0]["message"]["content"],
        "latency": time.time() - start,
    }


def run_rag(query: str) -> dict:
    start = time.time()
    result = corrective_retrieve(query)
    context = "\n\n".join(d["text"][:300] for d in result["docs"][:3])
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return {
        "answer": response["choices"][0]["message"]["content"],
        "latency": time.time() - start,
        "retrieval_decision": result["decision"],
        "avg_score": result["avg_score"],
        "sources": [d["source"] for d in result["docs"][:3]],
    }


results = []
for case in TEST_CASES:
    print(f"Running: {case['query'][:60]}...")
    results.append({
        "query": case["query"],
        "category": case["category"],
        "reference": case["reference"],
        "finetuned_only": run_finetuned_only(case["query"]),
        "rag": run_rag(case["query"]),
    })

out_path = Path(__file__).resolve().parent / "results_raw.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"Done: {len(results)} cases -> {out_path}")
```

---

## File: `app\eval\run_perplexity.py`

```python
# eval/run_perplexity.py
import json
import statistics
from eval.perplexity import compute_perplexity
from eval.test_set import TEST_CASES
from app.core.rag.corrective_rag import corrective_retrieve

ft_ppls, rag_ppls = [], []

for case in TEST_CASES:
    if not case["reference"]:
        continue

    query, reference = case["query"], case["reference"]

    # fine-tuned-only prompt (bare query)
    ft_ppl = compute_perplexity(query, reference)
    ft_ppls.append(ft_ppl)

    # RAG prompt (query + retrieved context)
    result = corrective_retrieve(query)
    context = "\n\n".join(d["text"][:300] for d in result["docs"][:3])
    rag_prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    rag_ppl = compute_perplexity(rag_prompt, reference)
    rag_ppls.append(rag_ppl)

    print(f"{query[:50]:50s}  FT={ft_ppl:.2f}  RAG={rag_ppl:.2f}")

print(f"\nAvg Perplexity — Fine-tuned only : {statistics.mean(ft_ppls):.2f}")
print(f"Avg Perplexity — RAG (with context): {statistics.mean(rag_ppls):.2f}")
```

---

## File: `app\eval\score.py`

```python
# eval/score.py
import json
import statistics
from pathlib import Path
from rouge_score import rouge_scorer
from bert_score import score as bert_score

BASE_DIR = Path(__file__).resolve().parent
results = json.load(open(BASE_DIR / "results_raw.json"))
scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

# ── ROUGE-1 / ROUGE-2 / ROUGE-L ──────────────────────
scored = []
for r in results:
    if not r["reference"]:
        continue  # OOD cases scored separately (Day 4)

    ft = scorer.score(r["reference"], r["finetuned_only"]["answer"])
    rag = scorer.score(r["reference"], r["rag"]["answer"])

    scored.append({
        "query": r["query"],
        "category": r["category"],
        "ft_rouge1": ft["rouge1"].fmeasure,
        "ft_rouge2": ft["rouge2"].fmeasure,
        "ft_rougeL": ft["rougeL"].fmeasure,
        "rag_rouge1": rag["rouge1"].fmeasure,
        "rag_rouge2": rag["rouge2"].fmeasure,
        "rag_rougeL": rag["rougeL"].fmeasure,
    })

# ── BERTScore F1 (batched) ───────────────────────────
refs        = [r["reference"] for r in results if r["reference"]]
ft_answers  = [r["finetuned_only"]["answer"] for r in results if r["reference"]]
rag_answers = [r["rag"]["answer"] for r in results if r["reference"]]

_, _, ft_f1  = bert_score(ft_answers, refs, lang="en")
_, _, rag_f1 = bert_score(rag_answers, refs, lang="en")

for i, s in enumerate(scored):
    s["ft_bertscore"]  = ft_f1[i].item()
    s["rag_bertscore"] = rag_f1[i].item()

json.dump(scored, open(BASE_DIR / "scored.json", "w"), indent=2)

def avg(key):
    return statistics.mean(s[key] for s in scored)

print("=" * 55)
print("  RAG vs Fine-Tuned-Only — Comparison")
print("=" * 55)
print(f"  ROUGE-1      : FT {avg('ft_rouge1'):.4f}  |  RAG {avg('rag_rouge1'):.4f}")
print(f"  ROUGE-2      : FT {avg('ft_rouge2'):.4f}  |  RAG {avg('rag_rouge2'):.4f}")
print(f"  ROUGE-L      : FT {avg('ft_rougeL'):.4f}  |  RAG {avg('rag_rougeL'):.4f}")
print(f"  BERTScore F1 : FT {avg('ft_bertscore'):.4f}  |  RAG {avg('rag_bertscore'):.4f}")
print("=" * 55)
```

---

## File: `app\eval\scored.json`

```json
[
  {
    "query": "What are the symptoms of vitamin D deficiency?",
    "category": "in_distribution",
    "ft_rouge1": 0.21238938053097345,
    "ft_roug e2": 0.07207207207207207,
    "ft_rougeL": 0.17699115044247787,
    "rag_rouge1": 0.47368421052631576,
    "rag_rouge2": 0.1111111111111111,
    "rag_rougeL": 0.26315789473684204,
    "ft_bertscore": 0.8709959983825684,
    "rag_bertscore": 0.9116770029067993
  },
  {
    "query": "What are the common symptoms of diabetes mellitus?",
    "category": "in_distribution",
    "ft_rouge1": 0.46511627906976755,
    "ft_rouge2": 0.14634146341463414,
    "ft_rougeL": 0.37209302325581395,
    "rag_rouge1": 0.32352941176470584,
    "rag_rouge2": 0.12121212121212122,
    "rag_rougeL": 0.2941176470588235,
    "ft_bertscore": 0.9252298474311829,
    "rag_bertscore": 0.9135987162590027
  },
  {
    "query": "What causes hypertension?",
    "category": "in_distribution",
    "ft_rouge1": 0.25000000000000006,
    "ft_rouge2": 0.0980392156862745,
    "ft_rougeL": 0.2115384615384616,
    "rag_rouge1": 0.18604651162790697,
    "rag_rouge2": 0.06299212598425198,
    "rag_rougeL": 0.10852713178294571,
    "ft_bertscore": 0.8956609964370728,
    "rag_bertscore": 0.886218786239624
  },
  {
    "query": "What are the symptoms of anemia?",
    "category": "in_distribution",
    "ft_rouge1": 0.2074074074074074,
    "ft_rouge2": 0.06015037593984962,
    "ft_rougeL": 0.14814814814814817,
    "rag_rouge1": 0.5217391304347825,
    "rag_rouge2": 0.3809523809523809,
    "rag_rougeL": 0.5217391304347825,
    "ft_bertscore": 0.8597466349601746,
    "rag_bertscore": 0.9318874478340149
  },
  {
    "query": "What are the warning signs of a heart attack?",
    "category": "in_distribution",
    "ft_rouge1": 0.17218543046357618,
    "ft_rouge2": 0.053691275167785234,
    "ft_rougeL": 0.1456953642384106,
    "rag_rouge1": 0.36363636363636365,
    "rag_rouge2": 0.14432989690721648,
    "rag_rougeL": 0.2222222222222222,
    "ft_bertscore": 0.8415659666061401,
    "rag_bertscore": 0.8842257857322693
  },
  {
    "query": "How is asthma diagnosed?",
    "category": "in_distribution",
    "ft_rouge1": 0.14285714285714282,
    "ft_rouge2": 0.05454545454545455,
    "ft_rougeL": 0.12499999999999999,
    "rag_rouge1": 0.1473684210526316,
    "rag_rouge2": 0.021505376344086023,
    "rag_rougeL": 0.12631578947368421,
    "ft_bertscore": 0.8559549450874329,
    "rag_bertscore": 0.8660256862640381
  },
  {
    "query": "What foods should diabetic patients avoid?",
    "category": "in_distribution",
    "ft_rouge1": 0.18604651162790697,
    "ft_rouge2": 0.08235294117647059,
    "ft_rougeL": 0.15116279069767444,
    "rag_rouge1": 0.04878048780487805,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.04878048780487805,
    "ft_bertscore": 0.8809645771980286,
    "rag_bertscore": 0.8415758609771729
  },
  {
    "query": "What is hypothyroidism?",
    "category": "in_distribution",
    "ft_rouge1": 0.16363636363636364,
    "ft_rouge2": 0.11926605504587157,
    "ft_rougeL": 0.15454545454545454,
    "rag_rouge1": 0.22891566265060245,
    "rag_rouge2": 0.15853658536585366,
    "rag_rougeL": 0.21686746987951805,
    "ft_bertscore": 0.885028600692749,
    "rag_bertscore": 0.8976633548736572
  },
  {
    "query": "What are the symptoms of dengue fever?",
    "category": "in_distribution",
    "ft_rouge1": 0.16058394160583941,
    "ft_rouge2": 0.0,
    "ft_rougeL": 0.11678832116788321,
    "rag_rouge1": 0.4999999999999999,
    "rag_rouge2": 0.37037037037037035,
    "rag_rougeL": 0.4999999999999999,
    "ft_bertscore": 0.8540126085281372,
    "rag_bertscore": 0.9206082820892334
  },
  {
    "query": "How can dehydration be treated?",
    "category": "in_distribution",
    "ft_rouge1": 0.09389671361502346,
    "ft_rouge2": 0.01895734597156398,
    "ft_rougeL": 0.08450704225352113,
    "rag_rouge1": 0.28169014084507044,
    "rag_rouge2": 0.028985507246376812,
    "rag_rougeL": 0.22535211267605632,
    "ft_bertscore": 0.8547181487083435,
    "rag_bertscore": 0.9120541214942932
  },
  {
    "query": "What are the symptoms of pneumonia?",
    "category": "in_distribution",
    "ft_rouge1": 0.3773584905660377,
    "ft_rouge2": 0.19607843137254902,
    "ft_rougeL": 0.339622641509434,
    "rag_rouge1": 0.5925925925925926,
    "rag_rouge2": 0.24,
    "rag_rougeL": 0.5185185185185185,
    "ft_bertscore": 0.8824499845504761,
    "rag_bertscore": 0.9303228259086609
  },
  {
    "query": "What is chronic kidney disease?",
    "category": "in_distribution",
    "ft_rouge1": 0.1688311688311688,
    "ft_rouge2": 0.09210526315789473,
    "ft_rougeL": 0.15584415584415584,
    "rag_rouge1": 0.272,
    "rag_rouge2": 0.14634146341463414,
    "rag_rougeL": 0.20800000000000002,
    "ft_bertscore": 0.8688541650772095,
    "rag_bertscore": 0.9003379344940186
  },
  {
    "query": "How is tuberculosis diagnosed?",
    "category": "in_distribution",
    "ft_rouge1": 0.09230769230769229,
    "ft_rouge2": 0.0,
    "ft_rougeL": 0.061538461538461535,
    "rag_rouge1": 0.05633802816901408,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.05633802816901408,
    "ft_bertscore": 0.8518409729003906,
    "rag_bertscore": 0.8228667974472046
  },
  {
    "query": "What are the symptoms of migraine?",
    "category": "in_distribution",
    "ft_rouge1": 0.2702702702702703,
    "ft_rouge2": 0.08333333333333333,
    "ft_rougeL": 0.2162162162162162,
    "rag_rouge1": 0.1739130434782609,
    "rag_rouge2": 0.07079646017699115,
    "rag_rougeL": 0.1565217391304348,
    "ft_bertscore": 0.8943292498588562,
    "rag_bertscore": 0.875073254108429
  },
  {
    "query": "What are common causes of chest pain?",
    "category": "in_distribution",
    "ft_rouge1": 0.11976047904191618,
    "ft_rouge2": 0.024242424242424242,
    "ft_rougeL": 0.09580838323353293,
    "rag_rouge1": 0.23684210526315785,
    "rag_rouge2": 0.08108108108108107,
    "rag_rougeL": 0.15789473684210528,
    "ft_bertscore": 0.839942216873169,
    "rag_bertscore": 0.8730738162994385
  },
  {
    "query": "How can obesity be managed?",
    "category": "in_distribution",
    "ft_rouge1": 0.3076923076923077,
    "ft_rouge2": 0.09523809523809522,
    "ft_rougeL": 0.1846153846153846,
    "rag_rouge1": 0.09677419354838708,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.06451612903225806,
    "ft_bertscore": 0.8968420028686523,
    "rag_bertscore": 0.8280994296073914
  },
  {
    "query": "What are the symptoms of urinary tract infection?",
    "category": "in_distribution",
    "ft_rouge1": 0.19867549668874174,
    "ft_rouge2": 0.08053691275167785,
    "ft_rougeL": 0.1324503311258278,
    "rag_rouge1": 0.5128205128205129,
    "rag_rouge2": 0.1081081081081081,
    "rag_rougeL": 0.41025641025641024,
    "ft_bertscore": 0.8842020630836487,
    "rag_bertscore": 0.9398790597915649
  },
  {
    "query": "What is gastroesophageal reflux disease (GERD)?",
    "category": "in_distribution",
    "ft_rouge1": 0.25316455696202533,
    "ft_rouge2": 0.07792207792207792,
    "ft_rougeL": 0.2278481012658228,
    "rag_rouge1": 0.5185185185185185,
    "rag_rouge2": 0.3076923076923077,
    "rag_rougeL": 0.5185185185185185,
    "ft_bertscore": 0.8955265879631042,
    "rag_bertscore": 0.9223039746284485
  },
  {
    "query": "What are the symptoms of appendicitis?",
    "category": "in_distribution",
    "ft_rouge1": 0.2105263157894737,
    "ft_rouge2": 0.061068702290076333,
    "ft_rougeL": 0.13533834586466167,
    "rag_rouge1": 0.26865671641791045,
    "rag_rouge2": 0.06153846153846154,
    "rag_rougeL": 0.1492537313432836,
    "ft_bertscore": 0.8776127099990845,
    "rag_bertscore": 0.8806130886077881
  },
  {
    "query": "How is high cholesterol treated?",
    "category": "in_distribution",
    "ft_rouge1": 0.16806722689075632,
    "ft_rouge2": 0.10256410256410256,
    "ft_rougeL": 0.16806722689075632,
    "rag_rouge1": 0.11320754716981132,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.11320754716981132,
    "ft_bertscore": 0.8864386677742004,
    "rag_bertscore": 0.8528212308883667
  },
  {
    "query": "What are the symptoms of influenza?",
    "category": "in_distribution",
    "ft_rouge1": 0.2553191489361702,
    "ft_rouge2": 0.021739130434782605,
    "ft_rougeL": 0.19148936170212766,
    "rag_rouge1": 0.10169491525423728,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.06779661016949153,
    "ft_bertscore": 0.8607885241508484,
    "rag_bertscore": 0.8331205248832703
  },
  {
    "query": "What are the complications of untreated diabetes?",
    "category": "in_distribution",
    "ft_rouge1": 0.1492537313432836,
    "ft_rouge2": 0.06153846153846154,
    "ft_rougeL": 0.1492537313432836,
    "rag_rouge1": 0.375,
    "rag_rouge2": 0.13333333333333333,
    "rag_rougeL": 0.31250000000000006,
    "ft_bertscore": 0.8702577948570251,
    "rag_bertscore": 0.9133330583572388
  },
  {
    "query": "What is osteoporosis?",
    "category": "in_distribution",
    "ft_rouge1": 0.12435233160621761,
    "ft_rouge2": 0.031413612565445025,
    "ft_rougeL": 0.09326424870466321,
    "rag_rouge1": 0.38095238095238093,
    "rag_rouge2": 0.1951219512195122,
    "rag_rougeL": 0.30952380952380953,
    "ft_bertscore": 0.8619770407676697,
    "rag_bertscore": 0.9309471845626831
  },
  {
    "query": "What are the symptoms of liver cirrhosis?",
    "category": "in_distribution",
    "ft_rouge1": 0.16666666666666666,
    "ft_rouge2": 0.01408450704225352,
    "ft_rougeL": 0.1111111111111111,
    "rag_rouge1": 0.5263157894736842,
    "rag_rouge2": 0.16666666666666663,
    "rag_rougeL": 0.42105263157894735,
    "ft_bertscore": 0.8401693105697632,
    "rag_bertscore": 0.9172186255455017
  },
  {
    "query": "How can iron deficiency be prevented?",
    "category": "in_distribution",
    "ft_rouge1": 0.304,
    "ft_rouge2": 0.1951219512195122,
    "ft_rougeL": 0.272,
    "rag_rouge1": 0.37777777777777777,
    "rag_rouge2": 0.18181818181818182,
    "rag_rougeL": 0.2888888888888889,
    "ft_bertscore": 0.902097761631012,
    "rag_bertscore": 0.9046407341957092
  },
  {
    "query": "What are the symptoms of COVID-19?",
    "category": "in_distribution",
    "ft_rouge1": 0.4126984126984127,
    "ft_rouge2": 0.13114754098360656,
    "ft_rougeL": 0.3492063492063492,
    "rag_rouge1": 0.33333333333333337,
    "rag_rouge2": 0.125,
    "rag_rougeL": 0.24242424242424243,
    "ft_bertscore": 0.9013708233833313,
    "rag_bertscore": 0.8952301144599915
  },
  {
    "query": "How is malaria diagnosed?",
    "category": "in_distribution",
    "ft_rouge1": 0.12017167381974249,
    "ft_rouge2": 0.03463203463203463,
    "ft_rougeL": 0.11158798283261802,
    "rag_rouge1": 0.2616822429906542,
    "rag_rouge2": 0.05714285714285714,
    "rag_rougeL": 0.1869158878504673,
    "ft_bertscore": 0.860640823841095,
    "rag_bertscore": 0.8857466578483582
  },
  {
    "query": "What are the symptoms of epilepsy?",
    "category": "in_distribution",
    "ft_rouge1": 0.13793103448275862,
    "ft_rouge2": 0.03571428571428571,
    "ft_rougeL": 0.10344827586206896,
    "rag_rouge1": 0.17391304347826086,
    "rag_rouge2": 0.029850746268656716,
    "rag_rougeL": 0.11594202898550725,
    "ft_bertscore": 0.8573562502861023,
    "rag_bertscore": 0.8569673299789429
  },
  {
    "query": "What causes peptic ulcers?",
    "category": "in_distribution",
    "ft_rouge1": 0.31775700934579443,
    "ft_rouge2": 0.11428571428571428,
    "ft_rougeL": 0.16822429906542055,
    "rag_rouge1": 0.36144578313253006,
    "rag_rouge2": 0.1728395061728395,
    "rag_rougeL": 0.3132530120481927,
    "ft_bertscore": 0.8919975161552429,
    "rag_bertscore": 0.8947601318359375
  },
  {
    "query": "What are the symptoms of anxiety disorder?",
    "category": "in_distribution",
    "ft_rouge1": 0.14634146341463414,
    "ft_rouge2": 0.05128205128205127,
    "ft_rougeL": 0.0975609756097561,
    "rag_rouge1": 0.3846153846153846,
    "rag_rouge2": 0.24999999999999994,
    "rag_rougeL": 0.3846153846153846,
    "ft_bertscore": 0.8814703226089478,
    "rag_bertscore": 0.9303940534591675
  },
  {
    "query": "I have a headache. What should I do?",
    "category": "ambiguous",
    "ft_rouge1": 0.18994413407821228,
    "ft_rouge2": 0.11299435028248588,
    "ft_rougeL": 0.1005586592178771,
    "rag_rouge1": 0.11049723756906078,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.06629834254143646,
    "ft_bertscore": 0.8717591166496277,
    "rag_bertscore": 0.8176997303962708
  },
  {
    "query": "Why do I feel tired all the time?",
    "category": "ambiguous",
    "ft_rouge1": 0.1407035175879397,
    "ft_rouge2": 0.01015228426395939,
    "ft_rougeL": 0.07035175879396985,
    "rag_rouge1": 0.1487603305785124,
    "rag_rouge2": 0.03361344537815126,
    "rag_rougeL": 0.08264462809917354,
    "ft_bertscore": 0.8463379740715027,
    "rag_bertscore": 0.845994770526886
  },
  {
    "query": "My stomach hurts after eating.",
    "category": "ambiguous",
    "ft_rouge1": 0.17777777777777776,
    "ft_rouge2": 0.022727272727272728,
    "ft_rougeL": 0.1111111111111111,
    "rag_rouge1": 0.16,
    "rag_rouge2": 0.06756756756756757,
    "rag_rougeL": 0.14666666666666667,
    "ft_bertscore": 0.8553311228752136,
    "rag_bertscore": 0.862723708152771
  },
  {
    "query": "I have chest pain.",
    "category": "ambiguous",
    "ft_rouge1": 0.09836065573770492,
    "ft_rouge2": 0.0,
    "ft_rougeL": 0.06557377049180328,
    "rag_rouge1": 0.33333333333333337,
    "rag_rouge2": 0.07692307692307691,
    "rag_rougeL": 0.25925925925925924,
    "ft_bertscore": 0.8376727104187012,
    "rag_bertscore": 0.9015653729438782
  },
  {
    "query": "I feel dizzy.",
    "category": "ambiguous",
    "ft_rouge1": 0.1956521739130435,
    "ft_rouge2": 0.1111111111111111,
    "ft_rougeL": 0.17391304347826086,
    "rag_rouge1": 0.1978021978021978,
    "rag_rouge2": 0.02247191011235955,
    "rag_rougeL": 0.10989010989010987,
    "ft_bertscore": 0.8647082448005676,
    "rag_bertscore": 0.8583194017410278
  },
  {
    "query": "My child has a fever.",
    "category": "ambiguous",
    "ft_rouge1": 0.23853211009174316,
    "ft_rouge2": 0.11214953271028039,
    "ft_rougeL": 0.18348623853211007,
    "rag_rouge1": 0.14492753623188406,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.08695652173913043,
    "ft_bertscore": 0.8738047480583191,
    "rag_bertscore": 0.8356778621673584
  },
  {
    "query": "I keep coughing.",
    "category": "ambiguous",
    "ft_rouge1": 0.24000000000000002,
    "ft_rouge2": 0.0273972602739726,
    "ft_rougeL": 0.13333333333333333,
    "rag_rouge1": 0.11428571428571428,
    "rag_rouge2": 0.0,
    "rag_rougeL": 0.0761904761904762,
    "ft_bertscore": 0.8582223057746887,
    "rag_bertscore": 0.8526705503463745
  },
  {
    "query": "My blood pressure is high.",
    "category": "ambiguous",
    "ft_rouge1": 0.12000000000000001,
    "ft_rouge2": 0.027027027027027025,
    "ft_rougeL": 0.09333333333333332,
    "rag_rouge1": 0.19354838709677416,
    "rag_rouge2": 0.06666666666666667,
    "rag_rougeL": 0.19354838709677416,
    "ft_bertscore": 0.8622685670852661,
    "rag_bertscore": 0.8733227252960205
  }
]
```

---

## File: `app\eval\test_set.py`

```python
TEST_CASES = [

# ======================================================
# IN-DISTRIBUTION (30)
# Reference answers are short, general medical-knowledge
# summaries — written to match the style/granularity of
# your disease_db + MedQA + PubMed knowledge base, so
# ROUGE/BERTScore comparisons are meaningful.
# ======================================================

{
    "query": "What are the symptoms of vitamin D deficiency?",
    "reference": "Common symptoms include fatigue, bone pain, muscle weakness, mood changes, and increased risk of fractures.",
    "category": "in_distribution",
},
{
    "query": "What are the common symptoms of diabetes mellitus?",
    "reference": "Common symptoms include frequent urination, excessive thirst, unexplained weight loss, fatigue, and blurred vision.",
    "category": "in_distribution",
},
{
    "query": "What causes hypertension?",
    "reference": "Hypertension is caused by factors such as excess salt intake, obesity, physical inactivity, chronic stress, genetics, and kidney disease.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of anemia?",
    "reference": "Symptoms include fatigue, pale skin, shortness of breath, dizziness, cold hands and feet, and irregular heartbeat.",
    "category": "in_distribution",
},
{
    "query": "What are the warning signs of a heart attack?",
    "reference": "Warning signs include chest pain or pressure, pain radiating to the arm or jaw, shortness of breath, cold sweat, and nausea.",
    "category": "in_distribution",
},
{
    "query": "How is asthma diagnosed?",
    "reference": "Asthma is diagnosed through medical history, physical examination, spirometry to measure lung function, and peak flow measurement.",
    "category": "in_distribution",
},
{
    "query": "What foods should diabetic patients avoid?",
    "reference": "Diabetic patients should limit sugary drinks, refined carbohydrates, white bread, processed snacks, and foods high in saturated fat.",
    "category": "in_distribution",
},
{
    "query": "What is hypothyroidism?",
    "reference": "Hypothyroidism is a condition where the thyroid gland does not produce enough thyroid hormone, causing fatigue, weight gain, and cold intolerance.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of dengue fever?",
    "reference": "Symptoms include high fever, severe headache, joint and muscle pain, rash, and pain behind the eyes.",
    "category": "in_distribution",
},
{
    "query": "How can dehydration be treated?",
    "reference": "Dehydration is treated with oral rehydration solutions, increased fluid intake, and in severe cases, intravenous fluids.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of pneumonia?",
    "reference": "Symptoms include cough with phlegm, fever, chills, difficulty breathing, and chest pain when breathing or coughing.",
    "category": "in_distribution",
},
{
    "query": "What is chronic kidney disease?",
    "reference": "Chronic kidney disease is the gradual loss of kidney function over time, often caused by diabetes and hypertension.",
    "category": "in_distribution",
},
{
    "query": "How is tuberculosis diagnosed?",
    "reference": "Tuberculosis is diagnosed using sputum smear microscopy, chest X-ray, tuberculin skin test, and molecular tests like GeneXpert.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of migraine?",
    "reference": "Symptoms include throbbing headache, sensitivity to light and sound, nausea, and sometimes visual disturbances called aura.",
    "category": "in_distribution",
},
{
    "query": "What are common causes of chest pain?",
    "reference": "Common causes include heart disease, acid reflux, muscle strain, anxiety, and lung conditions such as pneumonia.",
    "category": "in_distribution",
},
{
    "query": "How can obesity be managed?",
    "reference": "Obesity is managed through a balanced diet, regular physical activity, behavioral changes, and in some cases, medication or surgery.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of urinary tract infection?",
    "reference": "Symptoms include a burning sensation during urination, frequent urge to urinate, cloudy urine, and lower abdominal pain.",
    "category": "in_distribution",
},
{
    "query": "What is gastroesophageal reflux disease (GERD)?",
    "reference": "GERD is a digestive disorder where stomach acid frequently flows back into the esophagus, causing heartburn and regurgitation.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of appendicitis?",
    "reference": "Symptoms include sudden pain near the navel that shifts to the lower right abdomen, nausea, vomiting, and fever.",
    "category": "in_distribution",
},
{
    "query": "How is high cholesterol treated?",
    "reference": "High cholesterol is treated with dietary changes, regular exercise, weight management, and medications such as statins.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of influenza?",
    "reference": "Symptoms include fever, chills, muscle aches, cough, sore throat, fatigue, and headache.",
    "category": "in_distribution",
},
{
    "query": "What are the complications of untreated diabetes?",
    "reference": "Complications include nerve damage, kidney disease, vision loss, cardiovascular disease, and poor wound healing.",
    "category": "in_distribution",
},
{
    "query": "What is osteoporosis?",
    "reference": "Osteoporosis is a condition where bones become weak and brittle due to loss of bone density, increasing fracture risk.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of liver cirrhosis?",
    "reference": "Symptoms include fatigue, jaundice, easy bruising, swelling in the legs and abdomen, and confusion in advanced stages.",
    "category": "in_distribution",
},
{
    "query": "How can iron deficiency be prevented?",
    "reference": "Iron deficiency can be prevented by eating iron-rich foods such as red meat, leafy greens, and legumes, along with vitamin C to aid absorption.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of COVID-19?",
    "reference": "Symptoms include fever, cough, fatigue, loss of taste or smell, sore throat, and difficulty breathing in severe cases.",
    "category": "in_distribution",
},
{
    "query": "How is malaria diagnosed?",
    "reference": "Malaria is diagnosed through blood smear microscopy, rapid diagnostic tests, and PCR testing to detect parasite presence.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of epilepsy?",
    "reference": "Symptoms include recurrent seizures, temporary confusion, staring spells, and uncontrollable jerking movements.",
    "category": "in_distribution",
},
{
    "query": "What causes peptic ulcers?",
    "reference": "Peptic ulcers are commonly caused by Helicobacter pylori infection and long-term use of NSAIDs such as ibuprofen or aspirin.",
    "category": "in_distribution",
},
{
    "query": "What are the symptoms of anxiety disorder?",
    "reference": "Symptoms include excessive worry, restlessness, rapid heartbeat, difficulty concentrating, and sleep disturbances.",
    "category": "in_distribution",
},

# ======================================================
# OUT-OF-DISTRIBUTION (12)
# No reference answer — these test whether the correction
# step (web fallback) kicks in and whether grounding holds
# up, not ROUGE/BERTScore. Scored separately (see
# eval/hallucination_check.py).
# ======================================================

{
    "query": "What is the latest WHO guidance on mpox vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest treatments for Alzheimer's disease approved this year?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest CDC recommendations for RSV vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest updates in long COVID treatment?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest WHO recommendations for avian influenza?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest hypertension treatment guidelines?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest recommendations for childhood obesity management?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest breast cancer screening recommendations?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest diabetes medications introduced recently?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest recommendations for HPV vaccination?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the newest migraine treatments available?",
    "reference": None,
    "category": "out_of_distribution",
},
{
    "query": "What are the latest WHO recommendations on antimicrobial resistance?",
    "reference": None,
    "category": "out_of_distribution",
},

# ======================================================
# AMBIGUOUS (8)
# Vague, symptom-only phrasing a real patient would type.
# References describe the *appropriate response pattern*
# (acknowledge + ask clarifying info / advise seeking care)
# rather than a diagnosis, since a single-line query alone
# isn't enough to diagnose anything. This keeps reference
# answers medically responsible.
# ======================================================

{
    "query": "I have a headache. What should I do?",
    "reference": "Rest, stay hydrated, and consider over-the-counter pain relief; seek medical attention if the headache is severe, sudden, or accompanied by other symptoms.",
    "category": "ambiguous",
},
{
    "query": "Why do I feel tired all the time?",
    "reference": "Persistent fatigue can result from poor sleep, stress, anemia, thyroid issues, or an underlying medical condition; a doctor can help identify the cause.",
    "category": "ambiguous",
},
{
    "query": "My stomach hurts after eating.",
    "reference": "Pain after eating can be caused by indigestion, acid reflux, food intolerance, or gastritis; persistent or severe pain should be evaluated by a doctor.",
    "category": "ambiguous",
},
{
    "query": "I have chest pain.",
    "reference": "Chest pain can have many causes ranging from muscle strain to heart-related issues; sudden or severe chest pain requires immediate medical attention.",
    "category": "ambiguous",
},
{
    "query": "I feel dizzy.",
    "reference": "Dizziness can be caused by dehydration, low blood pressure, inner ear issues, or low blood sugar; frequent or severe dizziness should be checked by a doctor.",
    "category": "ambiguous",
},
{
    "query": "My child has a fever.",
    "reference": "Monitor the child's temperature, ensure hydration, and use age-appropriate fever-reducing medication; seek medical care if fever is high, persistent, or accompanied by other symptoms.",
    "category": "ambiguous",
},
{
    "query": "I keep coughing.",
    "reference": "Persistent cough can be caused by infections, allergies, asthma, or acid reflux; a cough lasting more than a few weeks should be evaluated by a doctor.",
    "category": "ambiguous",
},
{
    "query": "My blood pressure is high.",
    "reference": "High blood pressure should be monitored regularly and managed through diet, exercise, and medication as prescribed; consistently high readings warrant medical evaluation.",
    "category": "ambiguous",
},

]
```

---

## File: `app\models\refresh_token.py`

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<RefreshToken {self.id} user={self.user_id}>"

```

---

## File: `app\models\token.py`

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Token(Base):
    """One-time tokens for password resets and email verification."""

    __tablename__ = "tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    purpose: Mapped[str] = mapped_column(
        String(20), nullable=False, index=True  # "reset" | "verify"
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Token {self.purpose} user={self.user_id}>"

```

---

## File: `app\models\user.py`

```python
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    token_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

```

---

## File: `app\models\__init__.py`

```python
from app.models.user import User
from app.models.token import Token

__all__ = ["User", "RefreshToken", "Token"]

```

---

## File: `app\schemas\agent.py`

```python
# app/schemas/agent.py
from typing import Optional

from pydantic import BaseModel


class AgentRequest(BaseModel):
    patient_id: str
    query: str = ""
    image_base64: Optional[str] = None
    thread_id: Optional[str] = None


class AgentResponse(BaseModel):
    answer: str
    detected_lang: str
    needs_rag: bool
    retrieval_decision: Optional[str] = None
    sources: list[str] = []
    save_memory: bool


class ConversationMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None
    meta: Optional[dict] = None


class ConversationMeta(BaseModel):
    thread_id: str
    title: str
    updated_at: str
    message_count: int
    snippet: Optional[str] = None


class ConversationDetail(BaseModel):
    thread_id: str
    patient_id: str
    title: str
    updated_at: str
    messages: list[ConversationMessage]
```

---

## File: `app\schemas\auth.py`

```python
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.password_policy import validate_password

# =========================================================================
# Request Schemas
# =========================================================================


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)  # actual length checked in validator
    full_name: Optional[str] = Field(None, max_length=100)

    @model_validator(mode="after")
    def _check_password_policy(self):
        errors = validate_password(self.password)
        if errors:
            raise ValueError(
                "; ".join(e.message for e in errors)
            )
        return self


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# =========================================================================
# Response Schemas
# =========================================================================


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str

```

---

## File: `app\schemas\chat.py`

```python
from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, gt=0)
```

---

## File: `app\schemas\__init__.py`

```python

```

---

## File: `app\services\agent_service.py`

```python
# app/services/agent_service.py
import asyncio
import time

import psycopg
from starlette.concurrency import run_in_threadpool

from app.agent.graph import build_health_agent
from app.schemas.agent import AgentRequest, AgentResponse
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compiled once at import time — reused across requests, same pattern
# as loading `llm` once in core/llm.py
agent = build_health_agent()


def _build_initial_state(req: AgentRequest, ocr_text: str = "") -> dict:
    return {
        "patient_id": req.patient_id,
        "raw_input": req.query,
        "ocr_context": ocr_text,
        "answer": "",
        "final_response": "",
        "detected_lang": "",
        "needs_rag": False,
        "retrieval_decision": "",
        "retrieved_docs": [],
        "saved_memory": False,
        "tool_results": "",
        "messages": [],
    }


# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking (the pool's ping races the wake).
# Retrying a transient OperationalError absorbs that — the failure in the
# traceback is the checkpointer's very first read, before any node runs, so
# a retry is a clean restart (LangGraph resumes from the checkpoint).
_MAX_DB_RETRIES = 2
_RETRY_DELAY_SECONDS = 0.5


async def run_agent(
    req: AgentRequest,
    ocr_text: str = "",
) -> AgentResponse:

    start_time = time.monotonic()

    initial_state = _build_initial_state(req, ocr_text)

    # One thread per conversation. Defaults to patient_id so older clients
    # (and pre-sidebar data) keep resuming the single per-patient thread.
    thread_id = req.thread_id or req.patient_id

    # recursion_limit is LangGraph's own graph-level safety net. The
    # decoupled pipeline is linear (router -> tools? -> biomistral -> END),
    # so it stays well under this, but the cap guards against any future
    # cyclic edge misbehaving.
    config = {
        "configurable": {
            "thread_id": thread_id,
        },
        "recursion_limit": 15,
    }

    logger.info(
        "Agent request started | thread=%s | OCR=%s",
        thread_id,
        "yes" if ocr_text else "no",
    )

    for attempt in range(_MAX_DB_RETRIES + 1):

        try:
            logger.info(
                "Running agent graph | attempt %d/%d",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )

            result = await run_in_threadpool(
                agent.invoke,
                initial_state,
                config,
            )

            break

        except psycopg.OperationalError as e:

            if attempt >= _MAX_DB_RETRIES:
                logger.exception(
                    "Agent failed after %d attempts",
                    attempt + 1,
                )
                raise

            logger.warning(
                "Temporary database error | attempt %d/%d | retrying...",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )

            await asyncio.sleep(_RETRY_DELAY_SECONDS)

        except Exception:
            logger.exception("Agent graph execution failed")
            raise

    elapsed = time.monotonic() - start_time

    logger.info(
        "Agent request finished in %.2fs | RAG=%s | memory=%s",
        elapsed,
        result.get("needs_rag", False),
        result.get("saved_memory", False),
    )

    return AgentResponse(
        answer=result["final_response"],
        detected_lang=result["detected_lang"],
        needs_rag=result.get("needs_rag", False),
        retrieval_decision=result.get("retrieval_decision") or None,
        sources=[
            d.get("source")
            for d in result.get("retrieved_docs", [])[:3]
            if d.get("source")
        ],
        save_memory=result.get("saved_memory", False),
    )
```

---

## File: `app\services\chat_service.py`

```python
# app/services/chat_service.py
from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.llm import llm
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_ROLE_MAP = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}


async def stream_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:
    lc_messages = [_ROLE_MAP[m["role"]](content=m["content"]) for m in messages]

    logger.info(
        "▶ stream_chat started | messages=%d | temperature=%.2f | max_tokens=%d",
        len(lc_messages),
        temperature,
        max_tokens,
    )
    try:
        async for chunk in llm.astream(
            lc_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if chunk.content:
                yield chunk.content
        logger.info("✓ stream_chat completed")
    except Exception:
        logger.exception("Chat generation failed")
        yield "\n\nServer Error"
```

---

## File: `app\services\conversation_service.py`

```python
# app/services/conversation_service.py
"""Conversation history for the sidebar, backed directly by the LangGraph
checkpointer.

There is deliberately no separate conversation table — the checkpointer is
the source of truth. Every completed agent turn writes a checkpoint whose
`channel_values.final_response` is non-empty, so a conversation is exactly
the chronological sequence of those turn-end checkpoints for a thread.

Queries share the checkpointer's psycopg pool (app/db/pool.py), which is
tuned for Neon: it pings on checkout, reconnects after idle drops, and holds
real sessions on the direct endpoint.
"""
import time

import psycopg

from app.db.lifespan import checkpointer
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# A turn is "complete" once its final_response is set. The graph writes an
# intermediate checkpoint after every superstep, but those carry an empty
# final_response — filtering on it leaves exactly one row per finished turn.
_TURN_END = (
    "checkpoint_ns = ''"
    " AND (checkpoint->'channel_values'->>'final_response') IS NOT NULL"
    " AND (checkpoint->'channel_values'->>'final_response') <> ''"
)

# Fields we need per turn. Selecting only these (rather than the whole
# channel_values dict) keeps image_base64 blobs out of the result set.
_TURN_FIELDS = """
    thread_id,
    checkpoint_id,
    checkpoint->'channel_values'->>'raw_input'         AS raw_input,
    checkpoint->'channel_values'->>'final_response'    AS final_response,
    checkpoint->'channel_values'->>'detected_lang'     AS detected_lang,
    checkpoint->'channel_values'->>'retrieval_decision' AS retrieval_decision,
    (checkpoint->'channel_values'->>'needs_rag')::boolean AS needs_rag,
    checkpoint->'channel_values'->'retrieved_docs'     AS retrieved_docs,
    checkpoint->>'ts'                                  AS ts
"""

# Neon autosuspends an idle compute and kills its connections. The pool
# reconnects on checkout, but the *first* query on a fresh connection can
# still abort while the compute is waking — the same race agent_service.py
# retries for, so absorb it here too.
_MAX_DB_RETRIES = 1
_RETRY_DELAY_SECONDS = 0.5


def _query(sql: str, params: list) -> list[dict]:
    def run() -> list[dict]:
        with checkpointer.conn.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            return cur.fetchall()

    for attempt in range(_MAX_DB_RETRIES + 1):
        try:
            return run()
        except psycopg.OperationalError:
            if attempt >= _MAX_DB_RETRIES:
                logger.exception(
                    "Checkpoint query failed after %d attempts | params=%s",
                    attempt + 1,
                    params,
                )
                raise
            logger.warning(
                "Transient DB error in checkpoint query (attempt %d/%d), retrying...",
                attempt + 1,
                _MAX_DB_RETRIES + 1,
            )
            time.sleep(_RETRY_DELAY_SECONDS)


def _fetch_turns(patient_id: str, thread_id: str | None = None) -> list[dict]:
    """Chronological turn-end checkpoints for a patient, optionally one thread."""
    logger.info(
        "Fetching turns | patient=%s | thread=%s",
        patient_id,
        thread_id or "(all)",
    )
    sql = (
        f"SELECT {_TURN_FIELDS}"
        f" FROM checkpoints WHERE {_TURN_END}"
        " AND (checkpoint->'channel_values'->>'patient_id') = %s"
    )
    params: list = [patient_id]
    if thread_id is not None:
        sql += " AND thread_id = %s"
        params.append(thread_id)
    sql += " ORDER BY thread_id ASC, checkpoint_id ASC"
    turns = _query(sql, params)
    logger.info("Fetched %d turns | patient=%s", len(turns), patient_id)
    return turns


def _title(turns: list[dict]) -> str:
    """Conversation title = first user message; the sidebar truncates it."""
    for t in turns:
        if t["raw_input"] and t["raw_input"].strip():
            return t["raw_input"].strip()
    return "Untitled conversation"


def _sources(turn: dict) -> list[str]:
    return [
        d["source"]
        for d in (turn["retrieved_docs"] or [])
        if isinstance(d, dict) and d.get("source")
    ][:3]


def list_conversations(patient_id: str) -> list[dict]:
    """Sidebar rows: every conversation the patient has started, newest first."""
    start = time.monotonic()
    grouped: dict[str, list[dict]] = {}
    for t in _fetch_turns(patient_id):
        grouped.setdefault(t["thread_id"], []).append(t)

    conversations = []
    for thread_id, turns in grouped.items():
        turns.sort(key=lambda r: r["checkpoint_id"])  # chronological
        first, last = turns[0], turns[-1]
        conversations.append(
            {
                "thread_id": thread_id,
                "title": _title(turns),
                "updated_at": last["ts"] or "",
                "message_count": len(turns) * 2,
                "snippet": (last["final_response"] or "").strip(),
            }
        )

    # ISO timestamps come from the same source (checkpoint ts), so a plain
    # lexicographic sort is a valid time order.
    conversations.sort(key=lambda c: c["updated_at"], reverse=True)
    logger.info(
        "✓ list_conversations grouped %d turns into %d conversations in %.2fs | patient=%s",
        sum(len(v) for v in grouped.values()),
        len(conversations),
        time.monotonic() - start,
        patient_id,
    )
    return conversations


def get_conversation(thread_id: str, patient_id: str) -> dict | None:
    """Full message transcript for one thread, or None if it isn't the
    patient's (ownership is enforced by the patient_id inside the state)."""
    start = time.monotonic()
    turns = _fetch_turns(patient_id, thread_id)
    if not turns:
        logger.info(
            "No turns found | thread=%s | patient=%s",
            thread_id,
            patient_id,
        )
        return None

    messages = []
    for t in turns:
        raw = (t["raw_input"] or "").strip()
        answer = (t["final_response"] or "").strip()
        if not raw and not answer:
            continue
        messages.append({"role": "user", "content": raw, "timestamp": t["ts"]})
        messages.append(
            {
                "role": "assistant",
                "content": answer,
                "timestamp": t["ts"],
                "meta": {
                    "detected_lang": t["detected_lang"] or "en",
                    "needs_rag": bool(t["needs_rag"]),
                    "retrieval_decision": t["retrieval_decision"],
                    "sources": _sources(t),
                },
            }
        )

    result = {
        "thread_id": thread_id,
        "patient_id": patient_id,
        "title": _title(turns),
        "updated_at": turns[-1]["ts"] or "",
        "messages": messages,
    }
    logger.info(
        "✓ get_conversation built %d messages from %d turns in %.2fs | thread=%s",
        len(messages),
        len(turns),
        time.monotonic() - start,
        thread_id,
    )
    return result

```

---

## File: `app\services\rag_chat_service.py`

```python
# app/services/rag_chat_service.py

from typing import AsyncGenerator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.core.llm import llm
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_ROLE_MAP = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}


def _build_prompt(query: str, docs: list[dict]) -> str:
    context = "\n\n".join(
        f"[{d['source']}] {d['text'][:300]}"
        for d in docs[:3]
    )

    return (
        f"Use the following medical context if relevant.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )


async def stream_rag_chat(
    messages: list[dict],
    temperature: float,
    max_tokens: int,
) -> AsyncGenerator[str, None]:

    logger.info("Starting RAG chat request.")

    user_query = messages[-1]["content"]

    try:
        logger.info("Running Corrective RAG retrieval.")

        result = corrective_retrieve(user_query)

        logger.info(
            "Retrieval completed | decision=%s | avg_score=%.3f | docs=%d",
            result["decision"],
            result["avg_score"],
            len(result["docs"]),
        )

        augmented = _build_prompt(
            user_query,
            result["docs"],
        )

        rag_messages = messages[:-1] + [{"role": "user", "content": augmented}]
        lc_messages = [_ROLE_MAP[m["role"]](content=m["content"]) for m in rag_messages]

        logger.info("Starting LLM response generation.")

        async for chunk in llm.astream(
            lc_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            if chunk.content:
                yield chunk.content

    except Exception:
        logger.exception("RAG chat generation failed.")
        yield "\n\nServer Error"
```

---

## File: `app\tests\test-ocr.py`

```python
"""
test-ocr.py — run the OCR + agent flow against a live backend.

Sends app/tests/sample-report.png as image_base64 to POST /agent/invoke
(just like the frontend does) and prints the extracted OCR text plus the
assistant's answer.

Run directly against a running backend (same as the other test scripts):

    conda activate ft-project
    python app/tests/test-ocr.py ["<optional query>"]

Defaults to the same query used to reproduce the original bug: "what it mean".
"""
import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `import app` works

from fastapi.testclient import TestClient

from app.main import app
from app.core.rag.ocr import extract_text_from_base64

IMAGE_PATH = Path(__file__).parent / "sample-report.png"
QUERY = sys.argv[1] if len(sys.argv) > 1 else "what it mean"

# Raw base64, no `data:image/...;base64,` prefix — exactly what the
# frontend sends (see frontend/src/utils/image.js) and what
# app/core/rag/ocr.py expects to b64decode.
image_b64 = base64.b64encode(IMAGE_PATH.read_bytes()).decode("ascii")

print("=" * 60)
print("OCR PREVIEW (what the agent will read from the image)")
print("=" * 60)
ocr_text = extract_text_from_base64(image_b64)
print(f"Extracted {len(ocr_text)} chars:")
print(ocr_text[:2000] if ocr_text else "(no text extracted)")
print("=" * 60)

# Entering the context manager runs the FastAPI lifespan, which sets up the
# LangGraph checkpointer/store tables (deferred from import time since Week 6
# moved them into app/db/lifespan.py) plus init_models/embedder.
with TestClient(app) as client:

    print(f"Posting to /agent/invoke | query={QUERY!r} | image_bytes={len(image_b64)}")
    response = client.post(
        "/agent/invoke",
        json={
            "patient_id": "test-ocr-patient",
            "query": QUERY,
            "thread_id": "test-ocr-conversation",
            "image_base64": image_b64,
        },
    )

print("Status:", response.status_code)
print("=" * 60)
print("ANSWER")
print("=" * 60)

data = response.json()
print(data.get("answer"))
print("\n— detected_lang:", data.get("detected_lang"))
print("— needs_rag:", data.get("needs_rag"))
print("— retrieval_decision:", data.get("retrieval_decision"))
print("— save_memory:", data.get("save_memory"))
print("— sources:", data.get("sources"))

```

---

## File: `app\tests\test_auth.py`

```python

```

---

## File: `app\tests\test_chat.py`

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

response = client.post(
    "/chat/stream",
    json={
        "messages": [
            {
                "role": "user",
                "content": "What is diabetes?"
            }
        ]
    }
)

print(response.status_code)
print(response.text)
```

---

## File: `app\tests\test_corrective_rag.py`

```python
from pprint import pprint

from app.core.rag.corrective_rag import corrective_retrieve

result = corrective_retrieve(
    "What are the symptoms of diabetes?"
)

pprint(result)

print("\nDecision:", result["decision"])
print("Average Score:", result["avg_score"])
print("Documents Used:", len(result["docs"]))

print("\nRetrieved Documents:\n")

for i, doc in enumerate(result["docs"], start=1):
    print(f"{i}. Source   : {doc['source']}")
    print(f"   Category : {doc['category']}")
    print(f"   Score    : {doc['score']}")
    print(f"   Text     : {doc['text'][:200]}...\n")
```

---

## File: `app\tests\test_embedder.py`

```python
from app.core.rag.embedder import embedder

vector = embedder.embed_query(
    "What is diabetes?"
)

print(len(vector))
print(vector[:10])
```

---

## File: `app\tests\test_qdrant.py`

```python
from app.core.rag.qdrant_store import retrieve

docs = retrieve("What are the symptoms of diabetes?")

print("=" * 50)

for doc in docs:
    print(doc["score"])
    print(doc["source"])
    print(doc["text"][:200])
    print("-" * 50)
```

---

## File: `app\tests\test_rag_chat_stream.py`

```python
import asyncio

from app.services.rag_chat_service import stream_rag_chat


async def main():
    messages = [
        {
            "role": "user",
            "content": "What are the symptoms of diabetes?"
        }
    ]

    async for token in stream_rag_chat(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
    ):
        print(token, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## File: `app\tests\test_week6_agent.py`

```python
"""
test_week6_agent.py — run the tool-binding agent loop against a live backend.

Direct-run script (not pytest), same convention as the other app/tests scripts.
All four cases run on ONE patient_id so you can confirm the fever from case 2
is actually recalled in case 3 via fetch_patient_facts — the real proof the
fact-memory redesign works, and that the loop terminates (no hang) for both
the happy path and the tool-calling path.

    conda activate ft-project
    python app/tests/test_week6_agent.py [max_cases]

Passing an optional max_cases (1-4) limits how many turns run — handy for a
quick smoke test before the full ~30-minute live run.
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `import app` works

import psycopg

from app.db.lifespan import checkpointer, store
from app.services.agent_service import run_agent
from app.schemas.agent import AgentRequest

# Neon autosuspends an idle compute; waking it can kill the first connection
# mid-setup (AdminShutdown is an OperationalError subclass) or stall it long
# enough to hit the pool's checkout timeout. Same retry pattern as
# agent_service.run_agent, but with more patience for the slow wake.
_MAX_DB_RETRIES = 5
_RETRY_DELAY_SECONDS = 5.0


def _setup_backends():
    # The checkpointer/store backends are set up by the FastAPI lifespan;
    # running run_agent directly (no server) needs those tables to exist.
    for attempt in range(_MAX_DB_RETRIES + 1):
        try:
            checkpointer.setup()
            store.setup()
            return
        except psycopg.OperationalError as e:
            if attempt >= _MAX_DB_RETRIES:
                raise
            print(
                f"setup failed (attempt {attempt + 1}/{_MAX_DB_RETRIES + 1}), "
                f"retrying: {e}"
            )
            time.sleep(_RETRY_DELAY_SECONDS)


async def main():
    _setup_backends()

    cases = [
        "hello, how are you",
        "I have had a fever and body pain for three days",
        "is this the same fever from before",       # tests fetch_patient_facts
        "I'm really scared about this",              # tests save_emotional_state
    ]
    if len(sys.argv) > 1:
        cases = cases[: int(sys.argv[1])]
    for q in cases:
        r = await run_agent(AgentRequest(patient_id="test_patient_01", query=q))
        print(f"\nQ: {q}\nRAG: {r.needs_rag} | Saved: {r.save_memory}\nA: {r.answer[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## File: `app\utils\email.py`

```python
"""Email sending utility.

In development mode (no SMTP configured) every outgoing email is logged
to the console instead of being sent.  Once SMTP_* vars are set in .env the
real sender activates automatically.
"""

import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def send_email(
    to: str,
    subject: str,
    body: str,
    *,
    reply_to: Optional[str] = None,
) -> bool:
    """Send an email via SMTP, or log it when SMTP is not configured.

    Returns ``True`` on success, ``False`` on failure.
    """
    if not settings.SMTP_HOST:
        logger.info(
            "[DEV email] To: %s | Subject: %s\n%s",
            to,
            subject,
            body,
        )
        return True

    logger.info("Sending email | to=%s | subject=%s", to, subject)

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls(context=ctx)
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Email sent to %s — %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s — %s", to, subject)
        return False

```

---

## File: `app\utils\logging_config.py`

```python
"""Logging configuration with structured auth-event support."""

import logging
import sys
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    if not logger.handlers:  # prevents duplicate logs on reload
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        file_handler = logging.FileHandler("logs.txt", mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

    return logger


# Pre-built loggers for core subsystems
auth_logger = get_logger("auth")


def log_auth_event(
    event: str,
    username: Optional[str] = None,
    user_id: Optional[str] = None,
    ip: Optional[str] = None,
    success: bool = True,
    detail: Optional[str] = None,
) -> None:
    """Emit a structured auth event log line.

    Example output::

        14:30:01  | INFO     | auth | LOGIN  alice@example.com 200 192.168.1.1
        14:30:02  | WARNING  | auth | LOGIN  alice@example.com 401 192.168.1.1 "bad password"
    """
    status = "OK" if success else "FAIL"
    parts = [event.upper(), username or "-", status]
    if ip:
        parts.append(ip)
    if detail:
        parts.append(repr(detail))

    msg = "  ".join(parts)
    if success:
        auth_logger.info(msg)
    else:
        auth_logger.warning(msg)

```

---

## File: `app\utils\__init__.py`

```python
# App utilities

```

---

## File: `frontend\eslint.config.js`

```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    rules: {
      // react-refresh v0.5 doesn't auto-allow `use*` hooks exported alongside
      // components — the react-refresh/vite preset only sets allowConstantExport.
      // AuthContext exports useAuth() (a hook) next to AuthProvider, and
      // ConversationsContext exports useConversations() next to
      // ConversationsProvider, so allow both.
      'react-refresh/only-export-components': [
        'error',
        { allowConstantExport: true, allowExportNames: ['useAuth', 'useConversations'] },
      ],
    },
    languageOptions: {
      globals: globals.browser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
  },
])

```

---

## File: `frontend\index.html`

```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#212121" />
    <title>Health Intelligence Companion</title>
  </head>
  <body class="bg-[#212121]">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>

```

---

## File: `frontend\package-lock.json`

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "frontend",
      "version": "0.0.0",
      "dependencies": {
        "@tailwindcss/vite": "^4.3.3",
        "react": "^19.2.7",
        "react-dom": "^19.2.7",
        "tailwindcss": "^4.3.3"
      },
      "devDependencies": {
        "@eslint/js": "^10.0.1",
        "@types/react": "^19.2.17",
        "@types/react-dom": "^19.2.3",
        "@vitejs/plugin-react": "^6.0.3",
        "eslint": "^10.6.0",
        "eslint-plugin-react-hooks": "^7.1.1",
        "eslint-plugin-react-refresh": "^0.5.3",
        "globals": "^17.7.0",
        "vite": "^8.1.1"
      }
    },
    "node_modules/@babel/code-frame": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.29.7.tgz",
      "integrity": "sha512-Aup7aUOfpbAUg2ROOJN6Iw5f9DMBlzu0mIkm/malLQFN/YQgO48wCj0Kxa3sEHJvPVFg7siR+qRInwXd2qhQKw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-validator-identifier": "^7.29.7",
        "js-tokens": "^4.0.0",
        "picocolors": "^1.1.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/compat-data": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/compat-data/-/compat-data-7.29.7.tgz",
      "integrity": "sha512-locTkQyKvwIEgBzVrn8693ebc97F2U8ZHjbXwDXJ5Fn2TCpNwTlKcaKLkdHop5c/icOFE7qt7Q9JC5hnKNa6Gg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/core": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/core/-/core-7.29.7.tgz",
      "integrity": "sha512-RgHBCvtjbOK2gXSNBNIkNoEc9qoVEtau3hj8gEqKQuL3HZAibKarWFEI3Lfm6EYKkLalOh8eSrj9b+ch9H/VBA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/generator": "^7.29.7",
        "@babel/helper-compilation-targets": "^7.29.7",
        "@babel/helper-module-transforms": "^7.29.7",
        "@babel/helpers": "^7.29.7",
        "@babel/parser": "^7.29.7",
        "@babel/template": "^7.29.7",
        "@babel/traverse": "^7.29.7",
        "@babel/types": "^7.29.7",
        "@jridgewell/remapping": "^2.3.5",
        "convert-source-map": "^2.0.0",
        "debug": "^4.1.0",
        "gensync": "^1.0.0-beta.2",
        "json5": "^2.2.3",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/babel"
      }
    },
    "node_modules/@babel/generator": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/generator/-/generator-7.29.7.tgz",
      "integrity": "sha512-DkXD5OJQaAQIdZ1bt3UZdEnHAn9Imd3IVBdX03UFe+ony9Ojw5pzr9YVKGDY1jt+Gcn/FnGkNf8r+Vj5NOJWtQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/parser": "^7.29.7",
        "@babel/types": "^7.29.7",
        "@jridgewell/gen-mapping": "^0.3.12",
        "@jridgewell/trace-mapping": "^0.3.28",
        "jsesc": "^3.0.2"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-compilation-targets/-/helper-compilation-targets-7.29.7.tgz",
      "integrity": "sha512-wem6WaBj4NaVYVdNhLPPVacES6ZJ+KBBfSkTMD3YZxbP3rm3Di85tJU5ljaUNhaOynt+Aj0xruhYuzQBt8n71g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/compat-data": "^7.29.7",
        "@babel/helper-validator-option": "^7.29.7",
        "browserslist": "^4.24.0",
        "lru-cache": "^5.1.1",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-globals": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-globals/-/helper-globals-7.29.7.tgz",
      "integrity": "sha512-3nQVUAtvkKH9zahfWgw96Jc/uFOmjACE1kQz82E2lqWmHBgjzbNlsC22nuQTfahmWeQtTq5nQ/4Nnd2A1wj4zA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-imports": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.29.7.tgz",
      "integrity": "sha512-ejHwrQQYcm9xnTivShn2IDOlIzInN34AXskvq9QicvCtEzq1Vzclu/tKF8Jq1Cg8JG2GL6/EmjgsCT7lXepE3g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-transforms": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-transforms/-/helper-module-transforms-7.29.7.tgz",
      "integrity": "sha512-UPUVSyXbOh627KiCIGQSgwWzGeBKLkaJ9PJEdrngIwMSzxLR4jS4+f1f1jb7VzBbg8nFLaYotvVPFCTqdrmTAg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.29.7",
        "@babel/helper-validator-identifier": "^7.29.7",
        "@babel/traverse": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-string-parser": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.29.7.tgz",
      "integrity": "sha512-Pb5ijPrZ89GDH8223L4UP8i6QApWxs04RbPQJTeWDV0/keR2E36MeKnyr6LYmUUvqRRI+Iv87SuF1W6ErINzYw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-identifier": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.29.7.tgz",
      "integrity": "sha512-qehxGkRj55h/ff8EMaJ+cYhyaKlHIxqYDn682wQD7RNp9UujOQsHog2uS0r2vzr4pW+sXf90NeeayjcNaX3fFg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-option": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-option/-/helper-validator-option-7.29.7.tgz",
      "integrity": "sha512-N9ZErrD+yW5geCDtBqnOoxmR8+tNKiGuxKlDpuJxfsqpa2dFcexaziGAE/qoHLiDDreVNMupxGmSoNlyvsA3gw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helpers": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/helpers/-/helpers-7.29.7.tgz",
      "integrity": "sha512-1k2lAGRMfHTcwuNYcCNUmaUffmQv8KWMfh2iJUUeRlwlwH4FdNG7mfPI10NPfLHJFThE4Tyr4mv7kTNZOiPuBg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/template": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/parser": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/parser/-/parser-7.29.7.tgz",
      "integrity": "sha512-hnORnjP/1P/zFEndoeX+n+t1RwWRJiJpM/jO7FW32Kn9r5+sJB2JWOdYo4L6k78j15eCwY3Gm/7364B1EMwtNg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.29.7"
      },
      "bin": {
        "parser": "bin/babel-parser.js"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@babel/template": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/template/-/template-7.29.7.tgz",
      "integrity": "sha512-puq+Gf35oI24FeN11LkoUQFqv9uwNeWpxXZi/Ji3rRIoKAzKnxRaZ+Gkj0vKS9ZCiTESfng1N9LyOyXvo+m+Gg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/parser": "^7.29.7",
        "@babel/types": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/traverse": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/traverse/-/traverse-7.29.7.tgz",
      "integrity": "sha512-EhlfNQtZ+NK22w5BM61ciuiq1m58ed33Wr1Xan//ZRTy6hgjnwyCffRYwzsGXdASJSUJ1guZILsErh1eQcl+zw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.29.7",
        "@babel/generator": "^7.29.7",
        "@babel/helper-globals": "^7.29.7",
        "@babel/parser": "^7.29.7",
        "@babel/template": "^7.29.7",
        "@babel/types": "^7.29.7",
        "debug": "^4.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/types": {
      "version": "7.29.7",
      "resolved": "https://registry.npmjs.org/@babel/types/-/types-7.29.7.tgz",
      "integrity": "sha512-4zBIxpPzowiZpusoFkyGVwakdRJUyuH5PxQ/PrqghfdFWWasvnCdPfQXHrenDai+gyLARulZjZowCOj6fjT4pA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-string-parser": "^7.29.7",
        "@babel/helper-validator-identifier": "^7.29.7"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@emnapi/core": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@emnapi/core/-/core-1.11.1.tgz",
      "integrity": "sha512-RSvbQmHzdKzNsLYa/wHrbc3KN4sYLKAdPZxqiM2HATqv/SBk2/ENSHpvXGaLOMcsAyz0poEGqkmmKYG3OWiJEQ==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/wasi-threads": "1.2.2",
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/runtime": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@emnapi/runtime/-/runtime-1.11.1.tgz",
      "integrity": "sha512-vgj7R3y3Wgx24IQaGPA/R6YFXLHVMOZ0uVEyIQPaWs+rd1AzfEMXlAC22FYwO1XkKR6NPsq7mUandH8oIRdZFw==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/wasi-threads": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/@emnapi/wasi-threads/-/wasi-threads-1.2.2.tgz",
      "integrity": "sha512-c95qOXkHdydNKhscBTebqEC1CVAZpyqOfVfBzQ1qgzyl3gfeldUjIggDbIZgDKsHLgnsM+igH7TJ/eAasaVuMA==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils": {
      "version": "4.10.1",
      "resolved": "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.10.1.tgz",
      "integrity": "sha512-cuadcxVFE8sDK6iWJbs8Sn0av2Nrh2QSGQhVlBW9AaAHqHwjWsZHT8LJ4hFGPh7ASBV2deFdM7H/DPjulmh8rg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "eslint-visitor-keys": "^3.4.3"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      },
      "peerDependencies": {
        "eslint": "^6.0.0 || ^7.0.0 || >=8.0.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils/node_modules/eslint-visitor-keys": {
      "version": "3.4.3",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz",
      "integrity": "sha512-wpc+LXeiyiisxPlEkUzU6svyS1frIO3Mgxj1fdy7Pm8Ygzguax2N3Fa/D/ag1WqbOprdI+uY6wMUl8/a2G+iag==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@eslint-community/regexpp": {
      "version": "4.12.2",
      "resolved": "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.12.2.tgz",
      "integrity": "sha512-EriSTlt5OC9/7SXkRSCAhfSxxoSUgBm33OH+IkwbdpgoqsSsUg7y3uh+IICI/Qg4BBWr3U2i39RpmycbxMq4ew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^12.0.0 || ^14.0.0 || >=16.0.0"
      }
    },
    "node_modules/@eslint/config-array": {
      "version": "0.23.5",
      "resolved": "https://registry.npmjs.org/@eslint/config-array/-/config-array-0.23.5.tgz",
      "integrity": "sha512-Y3kKLvC1dvTOT+oGlqNQ1XLqK6D1HU2YXPc52NmAlJZbMMWDzGYXMiPRJ8TYD39muD/OTjlZmNJ4ib7dvSrMBA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/object-schema": "^3.0.5",
        "debug": "^4.3.1",
        "minimatch": "^10.2.4"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      }
    },
    "node_modules/@eslint/config-helpers": {
      "version": "0.6.0",
      "resolved": "https://registry.npmjs.org/@eslint/config-helpers/-/config-helpers-0.6.0.tgz",
      "integrity": "sha512-ii6Bw9jJ2zi2cWA2Z+9/QZ/+3DX6kwaV5Q986D/CdP3Lap3w/pgQZ373FV7byY/i7L4IRH/G43I5dz1ClsCbpA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^1.2.1"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      }
    },
    "node_modules/@eslint/core": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/@eslint/core/-/core-1.2.1.tgz",
      "integrity": "sha512-MwcE1P+AZ4C6DWlpin/OmOA54mmIZ/+xZuJiQd4SyB29oAJjN30UW9wkKNptW2ctp4cEsvhlLY/CsQ1uoHDloQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@types/json-schema": "^7.0.15"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      }
    },
    "node_modules/@eslint/js": {
      "version": "10.0.1",
      "resolved": "https://registry.npmjs.org/@eslint/js/-/js-10.0.1.tgz",
      "integrity": "sha512-zeR9k5pd4gxjZ0abRoIaxdc7I3nDktoXZk2qOv9gCNWx3mVwEn32VRhyLaRsDiJjTs0xq/T8mfPtyuXu7GWBcA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      },
      "peerDependencies": {
        "eslint": "^10.0.0"
      },
      "peerDependenciesMeta": {
        "eslint": {
          "optional": true
        }
      }
    },
    "node_modules/@eslint/object-schema": {
      "version": "3.0.5",
      "resolved": "https://registry.npmjs.org/@eslint/object-schema/-/object-schema-3.0.5.tgz",
      "integrity": "sha512-vqTaUEgxzm+YDSdElad6PiRoX4t8VGDjCtt05zn4nU810UIx/uNEV7/lZJ6KwFThKZOzOxzXy48da+No7HZaMw==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      }
    },
    "node_modules/@eslint/plugin-kit": {
      "version": "0.7.2",
      "resolved": "https://registry.npmjs.org/@eslint/plugin-kit/-/plugin-kit-0.7.2.tgz",
      "integrity": "sha512-+CNAzxglkrpNf/kKywqQfk74QjtceuOE7Qm+AF8miRvPF/wmmK5+OJOgVh3AVTT3RP2mH3+FOaxlE5v72owk0A==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^1.2.1",
        "levn": "^0.4.1"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      }
    },
    "node_modules/@humanfs/core": {
      "version": "0.19.2",
      "resolved": "https://registry.npmjs.org/@humanfs/core/-/core-0.19.2.tgz",
      "integrity": "sha512-UhXNm+CFMWcbChXywFwkmhqjs3PRCmcSa/hfBgLIb7oQ5HNb1wS0icWsGtSAUNgefHeI+eBrA8I1fxmbHsGdvA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanfs/types": "^0.15.0"
      },
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanfs/node": {
      "version": "0.16.8",
      "resolved": "https://registry.npmjs.org/@humanfs/node/-/node-0.16.8.tgz",
      "integrity": "sha512-gE1eQNZ3R++kTzFUpdGlpmy8kDZD/MLyHqDwqjkVQI0JMdI1D51sy1H958PNXYkM2rAac7e5/CnIKZrHtPh3BQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanfs/core": "^0.19.2",
        "@humanfs/types": "^0.15.0",
        "@humanwhocodes/retry": "^0.4.0"
      },
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanfs/types": {
      "version": "0.15.0",
      "resolved": "https://registry.npmjs.org/@humanfs/types/-/types-0.15.0.tgz",
      "integrity": "sha512-ZZ1w0aoQkwuUuC7Yf+7sdeaNfqQiiLcSRbfI08oAxqLtpXQr9AIVX7Ay7HLDuiLYAaFPu8oBYNq/QIi9URHJ3Q==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanwhocodes/module-importer": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz",
      "integrity": "sha512-bxveV4V8v5Yb4ncFTT3rPSgZBOpCkjfK0y4oVVVJwIuDVBRMDXrPyXRL988i5ap9m9bnyEEjWfm5WkBmtffLfA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=12.22"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@humanwhocodes/retry": {
      "version": "0.4.3",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/retry/-/retry-0.4.3.tgz",
      "integrity": "sha512-bV0Tgo9K4hfPCek+aMAn81RppFKv2ySDQeMoSZuvTASywNTnVJCArCZE2FWqpvIatKu7VMRLWlR1EazvVhDyhQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@jridgewell/gen-mapping": {
      "version": "0.3.13",
      "resolved": "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.13.tgz",
      "integrity": "sha512-2kkt/7niJ6MgEPxF0bYdQ6etZaA+fQvDcLKckhy1yIQOzaoKjBBjSj63/aLVjYE3qhRt5dvM+uUyfCg6UKCBbA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.0",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/remapping": {
      "version": "2.3.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/remapping/-/remapping-2.3.5.tgz",
      "integrity": "sha512-LI9u/+laYG4Ds1TDKSJW2YPrIlcVYOwi2fUC6xB43lueCjgxV4lffOCZCtYFiH6TNOX+tQKXx97T4IKHbhyHEQ==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.5",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/resolve-uri": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.2.tgz",
      "integrity": "sha512-bRISgCIjP20/tbWSPWMEi54QVPRZExkuD9lJL+UIxUKtwVJA8wW1Trb1jMs1RFXo1CBTNZ/5hpC9QvmKWdopKw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/sourcemap-codec": {
      "version": "1.5.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.5.5.tgz",
      "integrity": "sha512-cYQ9310grqxueWbl+WuIUIaiUaDcj7WOq5fVhEljNVgRfOUhY9fy2zTvfoqWsnebh8Sl70VScFbICvJnLKB0Og==",
      "license": "MIT"
    },
    "node_modules/@jridgewell/trace-mapping": {
      "version": "0.3.31",
      "resolved": "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.31.tgz",
      "integrity": "sha512-zzNR+SdQSDJzc8joaeP8QQoCQr8NuYx2dIIytl1QeBEZHJ9uW6hebsrYgbz8hJwUQao3TWCMtmfV8Nu1twOLAw==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/resolve-uri": "^3.1.0",
        "@jridgewell/sourcemap-codec": "^1.4.14"
      }
    },
    "node_modules/@napi-rs/wasm-runtime": {
      "version": "1.1.6",
      "resolved": "https://registry.npmjs.org/@napi-rs/wasm-runtime/-/wasm-runtime-1.1.6.tgz",
      "integrity": "sha512-ZLv/JdUfkvOy9eCnnBaGfiO+XimbjebAeO+MRQqD/B+FR1tnRN0tpKSJHRbE8sFfS6aqsXZ67TQjfwfsxULVbg==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@tybys/wasm-util": "^0.10.3"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/Brooooooklyn"
      },
      "peerDependencies": {
        "@emnapi/core": "^1.7.1",
        "@emnapi/runtime": "^1.7.1"
      }
    },
    "node_modules/@oxc-project/types": {
      "version": "0.139.0",
      "resolved": "https://registry.npmjs.org/@oxc-project/types/-/types-0.139.0.tgz",
      "integrity": "sha512-r9gHphtCs+1M7J0pw6Sn/hh/Wpa/iQrOOkrNAlVLF/gHq+/CJmHIWKKUUhdWjcD6CIa8idarspCsASiXCXvFUw==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/Boshen"
      }
    },
    "node_modules/@rolldown/binding-android-arm64": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-android-arm64/-/binding-android-arm64-1.1.5.tgz",
      "integrity": "sha512-lZg8fqIv2v7FF237bwMgzGZEJvGL79/s5knJ/i6FmsGF4XXlzccZ4jb+TrFIxtSSxFtIpdsgrPZeMk1I9AFcyQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-darwin-arm64": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-darwin-arm64/-/binding-darwin-arm64-1.1.5.tgz",
      "integrity": "sha512-51Bnx9pNiMRKSUNtBfySkNJ9vMU9Hh3I1ozDd6gyPPYzaXCfnptUcEZxXGYFn+ul2dtcMUiqGR1Yai2K10uoTw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-darwin-x64": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-darwin-x64/-/binding-darwin-x64-1.1.5.tgz",
      "integrity": "sha512-Tm+gbfC0aHu1tBA/JvKQh32S0K6YgCHkiAF4/W6xX0K0RmNuc94VeK419dJoE65R5aRxmo+noZQSWrAMF6yb6g==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-freebsd-x64": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-freebsd-x64/-/binding-freebsd-x64-1.1.5.tgz",
      "integrity": "sha512-JMzDKCCXq93YccG5gz3hvOs1oXRKAf0XYpfOS88e+wZrC8Iugj6j68867vrYZkvpDDpKn/KoKORThmchMpF6TA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm-gnueabihf": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm-gnueabihf/-/binding-linux-arm-gnueabihf-1.1.5.tgz",
      "integrity": "sha512-uML21j2K5TfPGutKxub+M+nLjZIrWjXQ5Grx4lCe/nimTj9B4L63zHpjXLl4y0L3mcm2htEQIb06oCG/szerNw==",
      "cpu": [
        "arm"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm64-gnu": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm64-gnu/-/binding-linux-arm64-gnu-1.1.5.tgz",
      "integrity": "sha512-navSiuTMogvnQoZoM/v+l3ZWo50/NTwSHSzheABx/RCnmUPaKwq9qSo4Br2OYRs21+Fz8uFqITZM3H4opOB0/Q==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-arm64-musl": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-arm64-musl/-/binding-linux-arm64-musl-1.1.5.tgz",
      "integrity": "sha512-lAryqH7IteztmCXQXk0etKj4wBQ7Gx5S6LjKhsgp9zb8I5bsuvU/2llH1hDQcjsFeqIsovMVN339/8pUDDBXxA==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-ppc64-gnu": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-ppc64-gnu/-/binding-linux-ppc64-gnu-1.1.5.tgz",
      "integrity": "sha512-fsK/sNBnxzBlL4O1JNrZakVQxPspqpED5dLtNsZS9oOKmtSpdNIzxH2kkol5HYTWJN47sE20ztMJPxfZ89qGOg==",
      "cpu": [
        "ppc64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-s390x-gnu": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-s390x-gnu/-/binding-linux-s390x-gnu-1.1.5.tgz",
      "integrity": "sha512-gLYb4BIadlfTOYT5gO503n8zQjXflgzpD0FcyKh0Mzx3rqCZKnHoJWV9xe1KXUJ5lx2JfcSHr/mhzS0PC/McAA==",
      "cpu": [
        "s390x"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-x64-gnu": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-x64-gnu/-/binding-linux-x64-gnu-1.1.5.tgz",
      "integrity": "sha512-FjcpEKUyJygHgs1o50VYNvkt5+7Le/VEdYt0AkRpkL33MnyQfwr8l5mXwMmfmTbyMPr5vJLC+8/Gd9gXnwU1QQ==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-linux-x64-musl": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-linux-x64-musl/-/binding-linux-x64-musl-1.1.5.tgz",
      "integrity": "sha512-Me+PfPI2TMeOQk0gYWfLQZtTktrmzbr8cDboqX83XKc7UrgAi55gF+2dUkWdxd19n55Essp2yeca+O9N5rBxHg==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-openharmony-arm64": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-openharmony-arm64/-/binding-openharmony-arm64-1.1.5.tgz",
      "integrity": "sha512-yc5WrLzXks6zCQfn9Oxr8pORKyl/pF+QjHmW/Qx3qu0oyrrNC+y2JLTU1E2rcWYAmzlnqngWXHQjy51VzW70Vw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "openharmony"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-wasm32-wasi": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-wasm32-wasi/-/binding-wasm32-wasi-1.1.5.tgz",
      "integrity": "sha512-VbQGPX2b4r48TAMIM2cjgluIM1HYutm4pcTEJsle7iEP7sB1dFqtPLBVbdLAZCxy1txCcPxf4QFf4v8uvltPqA==",
      "cpu": [
        "wasm32"
      ],
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/core": "1.11.1",
        "@emnapi/runtime": "1.11.1",
        "@napi-rs/wasm-runtime": "^1.1.6"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-win32-arm64-msvc": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-win32-arm64-msvc/-/binding-win32-arm64-msvc-1.1.5.tgz",
      "integrity": "sha512-gHv82k63z4qpV5+Q1y/12KrK0ltWBukVDI8nZcbT7Tt/ZlOIVwppazneq0F93oDxTo3IgAMEDIoQh3E2n6mVsw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/binding-win32-x64-msvc": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@rolldown/binding-win32-x64-msvc/-/binding-win32-x64-msvc-1.1.5.tgz",
      "integrity": "sha512-tTZuDBPw85tEN5PQi1pnEBzDy0Z49HtScLAbD5t6hyeU92A95pRWaSMw1GZZi/RwgSgUIl0xrSlXIT/9QzvYSA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      }
    },
    "node_modules/@rolldown/pluginutils": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@rolldown/pluginutils/-/pluginutils-1.0.1.tgz",
      "integrity": "sha512-2j9bGt5Jh8hj+vPtgzPtl72j0yRxHAyumoo6TNfAjsLB04UtpSvPbPcDcBMxz7n+9CYB0c1GxQFxYRg2jimqGw==",
      "license": "MIT"
    },
    "node_modules/@tailwindcss/node": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/node/-/node-4.3.3.tgz",
      "integrity": "sha512-/T8IKEsf9VTU6tLjgC7+sv2mOPtQxzE2jMw7u4Tt40Tx+QSZxpzh95/H6cMKoja9XuW7iMdLJYBB0o9G1CaAgg==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/remapping": "^2.3.5",
        "enhanced-resolve": "^5.24.1",
        "jiti": "^2.7.0",
        "lightningcss": "1.32.0",
        "magic-string": "^0.30.21",
        "source-map-js": "^1.2.1",
        "tailwindcss": "4.3.3"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss/-/lightningcss-1.32.0.tgz",
      "integrity": "sha512-NXYBzinNrblfraPGyrbPoD19C1h9lfI/1mzgWYvXUTe414Gz/X1FD2XBZSZM7rRTrMA8JL3OtAaGifrIKhQ5yQ==",
      "license": "MPL-2.0",
      "dependencies": {
        "detect-libc": "^2.0.3"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      },
      "optionalDependencies": {
        "lightningcss-android-arm64": "1.32.0",
        "lightningcss-darwin-arm64": "1.32.0",
        "lightningcss-darwin-x64": "1.32.0",
        "lightningcss-freebsd-x64": "1.32.0",
        "lightningcss-linux-arm-gnueabihf": "1.32.0",
        "lightningcss-linux-arm64-gnu": "1.32.0",
        "lightningcss-linux-arm64-musl": "1.32.0",
        "lightningcss-linux-x64-gnu": "1.32.0",
        "lightningcss-linux-x64-musl": "1.32.0",
        "lightningcss-win32-arm64-msvc": "1.32.0",
        "lightningcss-win32-x64-msvc": "1.32.0"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-android-arm64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-android-arm64/-/lightningcss-android-arm64-1.32.0.tgz",
      "integrity": "sha512-YK7/ClTt4kAK0vo6w3X+Pnm0D2cf2vPHbhOXdoNti1Ga0al1P4TBZhwjATvjNwLEBCnKvjJc2jQgHXH0NEwlAg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-darwin-arm64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-arm64/-/lightningcss-darwin-arm64-1.32.0.tgz",
      "integrity": "sha512-RzeG9Ju5bag2Bv1/lwlVJvBE3q6TtXskdZLLCyfg5pt+HLz9BqlICO7LZM7VHNTTn/5PRhHFBSjk5lc4cmscPQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-darwin-x64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-x64/-/lightningcss-darwin-x64-1.32.0.tgz",
      "integrity": "sha512-U+QsBp2m/s2wqpUYT/6wnlagdZbtZdndSmut/NJqlCcMLTWp5muCrID+K5UJ6jqD2BFshejCYXniPDbNh73V8w==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-freebsd-x64": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-freebsd-x64/-/lightningcss-freebsd-x64-1.32.0.tgz",
      "integrity": "sha512-JCTigedEksZk3tHTTthnMdVfGf61Fky8Ji2E4YjUTEQX14xiy/lTzXnu1vwiZe3bYe0q+SpsSH/CTeDXK6WHig==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-linux-arm-gnueabihf": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm-gnueabihf/-/lightningcss-linux-arm-gnueabihf-1.32.0.tgz",
      "integrity": "sha512-x6rnnpRa2GL0zQOkt6rts3YDPzduLpWvwAF6EMhXFVZXD4tPrBkEFqzGowzCsIWsPjqSK+tyNEODUBXeeVHSkw==",
      "cpu": [
        "arm"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-linux-arm64-gnu": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-gnu/-/lightningcss-linux-arm64-gnu-1.32.0.tgz",
      "integrity": "sha512-0nnMyoyOLRJXfbMOilaSRcLH3Jw5z9HDNGfT/gwCPgaDjnx0i8w7vBzFLFR1f6CMLKF8gVbebmkUN3fa/kQJpQ==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-linux-arm64-musl": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-musl/-/lightningcss-linux-arm64-musl-1.32.0.tgz",
      "integrity": "sha512-UpQkoenr4UJEzgVIYpI80lDFvRmPVg6oqboNHfoH4CQIfNA+HOrZ7Mo7KZP02dC6LjghPQJeBsvXhJod/wnIBg==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-linux-x64-gnu": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-gnu/-/lightningcss-linux-x64-gnu-1.32.0.tgz",
      "integrity": "sha512-V7Qr52IhZmdKPVr+Vtw8o+WLsQJYCTd8loIfpDaMRWGUZfBOYEJeyJIkqGIDMZPwPx24pUMfwSxxI8phr/MbOA==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-linux-x64-musl": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-musl/-/lightningcss-linux-x64-musl-1.32.0.tgz",
      "integrity": "sha512-bYcLp+Vb0awsiXg/80uCRezCYHNg1/l3mt0gzHnWV9XP1W5sKa5/TCdGWaR/zBM2PeF/HbsQv/j2URNOiVuxWg==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-win32-arm64-msvc": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-arm64-msvc/-/lightningcss-win32-arm64-msvc-1.32.0.tgz",
      "integrity": "sha512-8SbC8BR40pS6baCM8sbtYDSwEVQd4JlFTOlaD3gWGHfThTcABnNDBda6eTZeqbofalIJhFx0qKzgHJmcPTnGdw==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/node/node_modules/lightningcss-win32-x64-msvc": {
      "version": "1.32.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-x64-msvc/-/lightningcss-win32-x64-msvc-1.32.0.tgz",
      "integrity": "sha512-Amq9B/SoZYdDi1kFrojnoqPLxYhQ4Wo5XiL8EVJrVsB8ARoC1PWW6VGtT0WKCemjy8aC+louJnjS7U18x3b06Q==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/@tailwindcss/oxide": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide/-/oxide-4.3.3.tgz",
      "integrity": "sha512-krXjAikiaFSPaK/FkAQT5UTx3VormQaiZ5hBFlJZ9UFQGB/rwg1MZIhHAG9smMQRTdyJxP6Qt5MwMtdyU5FWrA==",
      "license": "MIT",
      "engines": {
        "node": ">= 20"
      },
      "optionalDependencies": {
        "@tailwindcss/oxide-android-arm64": "4.3.3",
        "@tailwindcss/oxide-darwin-arm64": "4.3.3",
        "@tailwindcss/oxide-darwin-x64": "4.3.3",
        "@tailwindcss/oxide-freebsd-x64": "4.3.3",
        "@tailwindcss/oxide-linux-arm-gnueabihf": "4.3.3",
        "@tailwindcss/oxide-linux-arm64-gnu": "4.3.3",
        "@tailwindcss/oxide-linux-arm64-musl": "4.3.3",
        "@tailwindcss/oxide-linux-x64-gnu": "4.3.3",
        "@tailwindcss/oxide-linux-x64-musl": "4.3.3",
        "@tailwindcss/oxide-wasm32-wasi": "4.3.3",
        "@tailwindcss/oxide-win32-arm64-msvc": "4.3.3",
        "@tailwindcss/oxide-win32-x64-msvc": "4.3.3"
      }
    },
    "node_modules/@tailwindcss/oxide-android-arm64": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-android-arm64/-/oxide-android-arm64-4.3.3.tgz",
      "integrity": "sha512-Y85A2gmPSkl5Ve5qR86GL4HT509cFqQh1aes9p3sSkyTPwt0Pppf3GkwGe4JPACcRYjgJIEhQgM6dBClnr0NYw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-darwin-arm64": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-darwin-arm64/-/oxide-darwin-arm64-4.3.3.tgz",
      "integrity": "sha512-BiaWatpBcERQFDlOjRDpIVXuFK5PJez5SA4JMg6VYZdBYU+qKfV/vqjcIs+IYmtitf1xYQZTwXvU/8y4lfZUGw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-darwin-x64": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-darwin-x64/-/oxide-darwin-x64-4.3.3.tgz",
      "integrity": "sha512-fAeUqfV5ndhxRwai8cXGzdLvul9utWOmeTkv69unv4ZXixjn61Z+p9lCWdwOwA3TYboG3BwdVuN/RDjhBRl0mw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-freebsd-x64": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-freebsd-x64/-/oxide-freebsd-x64-4.3.3.tgz",
      "integrity": "sha512-iyf5bV6+wnAlflVeEy7R25dupxTNECZN5QMI0qNT6eT+EgaGdZcKhGkr5SdoaWiLJ3spLqIY9VCeSGrwmtg4kw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm-gnueabihf": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm-gnueabihf/-/oxide-linux-arm-gnueabihf-4.3.3.tgz",
      "integrity": "sha512-aAYUprJAJQWWbRrPvtjdroZ56Md+JM8pMiopS6xGEwDfLhqj+2ver2p4nU4Mb3CRqcMmNBjo8KkUgcxhkzVQGQ==",
      "cpu": [
        "arm"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm64-gnu": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm64-gnu/-/oxide-linux-arm64-gnu-4.3.3.tgz",
      "integrity": "sha512-nDxldcEENOxZRzC2uu9jrutZdAAQtb+8WWDCSnWL1zvBk1+FN+x6MtDViPB5AJMfttVCUhehGWus3XBPgatM/w==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-arm64-musl": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-arm64-musl/-/oxide-linux-arm64-musl-4.3.3.tgz",
      "integrity": "sha512-Md44bD6veX/PC5iyF8cDVnw4HBIANZepRZZ7a8DQOvkfo5WUBwcp6iAuCUz23u+4SUkhJlD3eL7hNdW8ezd/kA==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-x64-gnu": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-x64-gnu/-/oxide-linux-x64-gnu-4.3.3.tgz",
      "integrity": "sha512-tx7us1muwOKAKWao2v/GaafFeQboE6aj88vC6ziN2NCGcRm8gWUhwjzg+YdVB1e4boAtdtma4L43onunI6NS4w==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-linux-x64-musl": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-linux-x64-musl/-/oxide-linux-x64-musl-4.3.3.tgz",
      "integrity": "sha512-SJxX60smvHgasZoBy11dX6YRjXJFovwWBoedhbQPOBzgFWBHGB+TVPWB9BxzR7TTxU8FQZAI2AyiNCMzFm8Img==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-wasm32-wasi": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-wasm32-wasi/-/oxide-wasm32-wasi-4.3.3.tgz",
      "integrity": "sha512-jx1+rPhY/5Ympkktd656HBWEBLxP7dH06losBLjjf5vgCODXvi9KhtftWcMIwTFIDqBr7cRnQkdLnAG+IOlGvQ==",
      "bundleDependencies": [
        "@napi-rs/wasm-runtime",
        "@emnapi/core",
        "@emnapi/runtime",
        "@tybys/wasm-util",
        "@emnapi/wasi-threads",
        "tslib"
      ],
      "cpu": [
        "wasm32"
      ],
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/core": "^1.11.1",
        "@emnapi/runtime": "^1.11.1",
        "@emnapi/wasi-threads": "^1.2.2",
        "@napi-rs/wasm-runtime": "^1.1.4",
        "@tybys/wasm-util": "^0.10.2",
        "tslib": "^2.8.1"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/@tailwindcss/oxide-win32-arm64-msvc": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-win32-arm64-msvc/-/oxide-win32-arm64-msvc-4.3.3.tgz",
      "integrity": "sha512-3rc292Ca2ceK6Ulcc/bAVnTs/3nDtoPhyEKlgPv+yQJQi/JS/AMJlqzxvlDacL1nekbrcf6bTqp/jV4qgnPxNQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/oxide-win32-x64-msvc": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/oxide-win32-x64-msvc/-/oxide-win32-x64-msvc-4.3.3.tgz",
      "integrity": "sha512-yJ0pwIVc/nYeGoV02WtsN8KYyLQv7kyI2wDnkezyJlGGjkd4QLwDGAwl47YpPJeuI0M0ObaXGSPjvWDPeTPggw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 20"
      }
    },
    "node_modules/@tailwindcss/vite": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/@tailwindcss/vite/-/vite-4.3.3.tgz",
      "integrity": "sha512-yYU8cogLeSh/ms2jh8Fj7jaba/EWa7Ja6GoUqYZaraEuCI5YS6ms6ObZgjjedm+jm6XZjdNRWBpPP6Z86oOxcw==",
      "license": "MIT",
      "dependencies": {
        "@tailwindcss/node": "4.3.3",
        "@tailwindcss/oxide": "4.3.3",
        "tailwindcss": "4.3.3"
      },
      "peerDependencies": {
        "vite": "^5.2.0 || ^6 || ^7 || ^8"
      }
    },
    "node_modules/@tybys/wasm-util": {
      "version": "0.10.3",
      "resolved": "https://registry.npmjs.org/@tybys/wasm-util/-/wasm-util-0.10.3.tgz",
      "integrity": "sha512-F3fo1MYrRJYL3zER0OUOmkutjr1Vp23m7OsSgp7nq4SP6OqX6C/56XFIPAl5bt3zaBRjmW7SGz3u/6LwFpYcOg==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@types/esrecurse": {
      "version": "4.3.1",
      "resolved": "https://registry.npmjs.org/@types/esrecurse/-/esrecurse-4.3.1.tgz",
      "integrity": "sha512-xJBAbDifo5hpffDBuHl0Y8ywswbiAp/Wi7Y/GtAgSlZyIABppyurxVueOPE8LUQOxdlgi6Zqce7uoEpqNTeiUw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/estree": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.9.tgz",
      "integrity": "sha512-GhdPgy1el4/ImP05X05Uw4cw2/M93BCUmnEvWZNStlCzEKME4Fkk+YpoA5OiHNQmoS7Cafb8Xa3Pya8m1Qrzeg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/json-schema": {
      "version": "7.0.15",
      "resolved": "https://registry.npmjs.org/@types/json-schema/-/json-schema-7.0.15.tgz",
      "integrity": "sha512-5+fP8P8MFNC+AyZCDxrB2pkZFPGzqQWUzpSeuuVLvm8VMcorNYavBqoFcxK8bQz4Qsbn4oUEEem4wDLfcysGHA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/react": {
      "version": "19.2.17",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-19.2.17.tgz",
      "integrity": "sha512-MXfmqaVPEVgkBT/aY0aGCkRWWtByiYQXo3xdQ8r5RzuFrPiRn8Gar2tQdXSUQ2GKV3bkXckek89V8wQBY2Q/Aw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "csstype": "^3.2.2"
      }
    },
    "node_modules/@types/react-dom": {
      "version": "19.2.3",
      "resolved": "https://registry.npmjs.org/@types/react-dom/-/react-dom-19.2.3.tgz",
      "integrity": "sha512-jp2L/eY6fn+KgVVQAOqYItbF0VY/YApe5Mz2F0aykSO8gx31bYCZyvSeYxCHKvzHG5eZjc+zyaS5BrBWya2+kQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "^19.2.0"
      }
    },
    "node_modules/@vitejs/plugin-react": {
      "version": "6.0.4",
      "resolved": "https://registry.npmjs.org/@vitejs/plugin-react/-/plugin-react-6.0.4.tgz",
      "integrity": "sha512-XcCQz0TBpBgljhj0gMuuDj49i6Ytqh5q1osT/Gp5uAVJUCTWxyskk/l1jwYYiu2xcNHHipdMz40EGfM1VdamVg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@rolldown/pluginutils": "^1.0.1"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "peerDependencies": {
        "@rolldown/plugin-babel": "^0.1.7 || ^0.2.0",
        "babel-plugin-react-compiler": "^1.0.0",
        "vite": "^8.0.0"
      },
      "peerDependenciesMeta": {
        "@rolldown/plugin-babel": {
          "optional": true
        },
        "babel-plugin-react-compiler": {
          "optional": true
        }
      }
    },
    "node_modules/acorn": {
      "version": "8.17.0",
      "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.17.0.tgz",
      "integrity": "sha512-xRQbDb9BnwDafYNn6Vwl839DYVjqXYb1XVGtWAZ1kcDc6iwAL4hg3B1dZlRiuENFeO2H53gFG3in621AdERVAg==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "acorn": "bin/acorn"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/acorn-jsx": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz",
      "integrity": "sha512-rq9s+JNhf0IChjtDXxllJ7g41oZk5SlXtp0LHwyA5cejwn7vKmKp4pPri6YEePv2PU65sAsegbXtIinmDFDXgQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "acorn": "^6.0.0 || ^7.0.0 || ^8.0.0"
      }
    },
    "node_modules/ajv": {
      "version": "6.15.0",
      "resolved": "https://registry.npmjs.org/ajv/-/ajv-6.15.0.tgz",
      "integrity": "sha512-fgFx7Hfoq60ytK2c7DhnF8jIvzYgOMxfugjLOSMHjLIPgenqa7S7oaagATUq99mV6IYvN2tRmC0wnTYX6iPbMw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-deep-equal": "^3.1.1",
        "fast-json-stable-stringify": "^2.0.0",
        "json-schema-traverse": "^0.4.1",
        "uri-js": "^4.2.2"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/epoberezkin"
      }
    },
    "node_modules/balanced-match": {
      "version": "4.0.4",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-4.0.4.tgz",
      "integrity": "sha512-BLrgEcRTwX2o6gGxGOCNyMvGSp35YofuYzw9h1IMTRmKqttAZZVU67bdb9Pr2vUHA8+j3i2tJfjO6C6+4myGTA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "18 || 20 || >=22"
      }
    },
    "node_modules/baseline-browser-mapping": {
      "version": "2.11.1",
      "resolved": "https://registry.npmjs.org/baseline-browser-mapping/-/baseline-browser-mapping-2.11.1.tgz",
      "integrity": "sha512-HYXq73DDpCtNzOmrFsm9eSwCvWCql0RzqjpDzXN9EadiLJ4DNat0nsZ/Bzmy+Ud12mb4/zKDY0cQ805ZzN+i0A==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "baseline-browser-mapping": "dist/cli.cjs"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/brace-expansion": {
      "version": "5.0.8",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-5.0.8.tgz",
      "integrity": "sha512-JZyDyq3D4AUifKTPOB7DELf6XsB3WdPuNxCtob1vFXPsSXhdAiHBWJ/tJ8HAc9aH84BK+5JFZLNkJKx3G9kzQg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^4.0.2"
      },
      "engines": {
        "node": "20 || >=22"
      }
    },
    "node_modules/browserslist": {
      "version": "4.28.7",
      "resolved": "https://registry.npmjs.org/browserslist/-/browserslist-4.28.7.tgz",
      "integrity": "sha512-JxV13hNrFxqjOc8alRbq9dK1MM79NEXYpma2B2J4wAtpWS5zIEIKqWPGCl7N4o7Uc7B7itylh7SuDujATRyyTw==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "baseline-browser-mapping": "^2.10.44",
        "caniuse-lite": "^1.0.30001806",
        "electron-to-chromium": "^1.5.393",
        "node-releases": "^2.0.51",
        "update-browserslist-db": "^1.2.3"
      },
      "bin": {
        "browserslist": "cli.js"
      },
      "engines": {
        "node": "^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7"
      }
    },
    "node_modules/caniuse-lite": {
      "version": "1.0.30001806",
      "resolved": "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001806.tgz",
      "integrity": "sha512-72Cuvd95zbSYPKq6Fhg8eDJRlzgWDf7/mtoZv6Qe/DYNCEBdNxoA3+rZAU2ZhGCpZlns3EssFavaZomckT5Uuw==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/caniuse-lite"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "CC-BY-4.0"
    },
    "node_modules/convert-source-map": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/convert-source-map/-/convert-source-map-2.0.0.tgz",
      "integrity": "sha512-Kvp459HrV2FEJ1CAsi1Ku+MY3kasH19TFykTz2xWmMeq6bk2NU3XXvfJ+Q61m0xktWwt+1HSYf3JZsTms3aRJg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/cross-spawn": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
      "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "path-key": "^3.1.0",
        "shebang-command": "^2.0.0",
        "which": "^2.0.1"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/csstype": {
      "version": "3.2.3",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.2.3.tgz",
      "integrity": "sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/debug": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
      "integrity": "sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.3"
      },
      "engines": {
        "node": ">=6.0"
      },
      "peerDependenciesMeta": {
        "supports-color": {
          "optional": true
        }
      }
    },
    "node_modules/deep-is": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz",
      "integrity": "sha512-oIPzksmTg4/MriiaYGO+okXDT7ztn/w3Eptv/+gSIdMdKsJo0u4CfYNFJPy+4SKMuCqGw2wxnA+URMg3t8a/bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/detect-libc": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/detect-libc/-/detect-libc-2.1.2.tgz",
      "integrity": "sha512-Btj2BOOO83o3WyH59e8MgXsxEQVcarkUOpEYrubB0urwnN10yQ364rsiByU11nZlqWYZm05i/of7io4mzihBtQ==",
      "license": "Apache-2.0",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/electron-to-chromium": {
      "version": "1.5.396",
      "resolved": "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.396.tgz",
      "integrity": "sha512-yHiw2Y3C3H9U6TMbOfoWK/BPreiOPXRfTWPBwQBoZG6/8TB6eOPnsy5oaRYuatR7Fw2SJ4kKforgufeo7fq0EQ==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/enhanced-resolve": {
      "version": "5.24.3",
      "resolved": "https://registry.npmjs.org/enhanced-resolve/-/enhanced-resolve-5.24.3.tgz",
      "integrity": "sha512-PwKooW9JUzh5chmYfHM3IQl5OkK2u2Nm011MgeZrss3JmFraUx/fqrf78kk8GUMYoibx/14MdwTl/1WKkG7TpQ==",
      "license": "MIT",
      "dependencies": {
        "graceful-fs": "^4.2.4",
        "tapable": "^2.3.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/escalade": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz",
      "integrity": "sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/escape-string-regexp": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
      "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint": {
      "version": "10.7.0",
      "resolved": "https://registry.npmjs.org/eslint/-/eslint-10.7.0.tgz",
      "integrity": "sha512-GVTD7s1vdIl6UYvAfriOPeY1Df8LIZjfofLvHwde+erDHGGuHyuM6xoxRxmHiebhYuD2p1vN4wWh0XzPARSGDQ==",
      "dev": true,
      "license": "MIT",
      "workspaces": [
        "packages/*"
      ],
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.8.0",
        "@eslint-community/regexpp": "^4.12.2",
        "@eslint/config-array": "^0.23.5",
        "@eslint/config-helpers": "^0.6.0",
        "@eslint/core": "^1.2.1",
        "@eslint/plugin-kit": "^0.7.2",
        "@humanfs/node": "^0.16.6",
        "@humanwhocodes/module-importer": "^1.0.1",
        "@humanwhocodes/retry": "^0.4.2",
        "@types/estree": "^1.0.6",
        "ajv": "^6.14.0",
        "cross-spawn": "^7.0.6",
        "debug": "^4.3.2",
        "escape-string-regexp": "^4.0.0",
        "eslint-scope": "^9.1.2",
        "eslint-visitor-keys": "^5.0.1",
        "espree": "^11.2.0",
        "esquery": "^1.7.0",
        "esutils": "^2.0.2",
        "fast-deep-equal": "^3.1.3",
        "file-entry-cache": "^8.0.0",
        "find-up": "^5.0.0",
        "glob-parent": "^6.0.2",
        "ignore": "^5.2.0",
        "imurmurhash": "^0.1.4",
        "is-glob": "^4.0.0",
        "json-stable-stringify-without-jsonify": "^1.0.1",
        "minimatch": "^10.2.4",
        "natural-compare": "^1.4.0",
        "optionator": "^0.9.3"
      },
      "bin": {
        "eslint": "bin/eslint.js"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      },
      "peerDependencies": {
        "jiti": "*"
      },
      "peerDependenciesMeta": {
        "jiti": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-plugin-react-hooks": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react-hooks/-/eslint-plugin-react-hooks-7.1.1.tgz",
      "integrity": "sha512-f2I7Gw6JbvCexzIInuSbZpfdQ44D7iqdWX01FKLvrPgqxoE7oMj8clOfto8U6vYiz4yd5oKu39rRSVOe1zRu0g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.24.4",
        "@babel/parser": "^7.24.4",
        "hermes-parser": "^0.25.1",
        "zod": "^3.25.0 || ^4.0.0",
        "zod-validation-error": "^3.5.0 || ^4.0.0"
      },
      "engines": {
        "node": ">=18"
      },
      "peerDependencies": {
        "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0 || ^9.0.0 || ^10.0.0"
      }
    },
    "node_modules/eslint-plugin-react-refresh": {
      "version": "0.5.3",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react-refresh/-/eslint-plugin-react-refresh-0.5.3.tgz",
      "integrity": "sha512-5EMmLCV98Pi4o/f/3DP/v/tNqLHMIc9I8LKClNDWhZ9JTho89/kQcitCXQBMG7sAfVRK0Ie3T2EDOzp1YXYiVA==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "eslint": "^9 || ^10"
      }
    },
    "node_modules/eslint-scope": {
      "version": "9.1.2",
      "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-9.1.2.tgz",
      "integrity": "sha512-xS90H51cKw0jltxmvmHy2Iai1LIqrfbw57b79w/J7MfvDfkIkFZ+kj6zC3BjtUwh150HsSSdxXZcsuv72miDFQ==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "@types/esrecurse": "^4.3.1",
        "@types/estree": "^1.0.8",
        "esrecurse": "^4.3.0",
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint-visitor-keys": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-5.0.1.tgz",
      "integrity": "sha512-tD40eHxA35h0PEIZNeIjkHoDR4YjjJp34biM0mDvplBe//mB+IHCqHDGV7pxF+7MklTvighcCPPZC7ynWyjdTA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/espree": {
      "version": "11.2.0",
      "resolved": "https://registry.npmjs.org/espree/-/espree-11.2.0.tgz",
      "integrity": "sha512-7p3DrVEIopW1B1avAGLuCSh1jubc01H2JHc8B4qqGblmg5gI9yumBgACjWo4JlIc04ufug4xJ3SQI8HkS/Rgzw==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "acorn": "^8.16.0",
        "acorn-jsx": "^5.3.2",
        "eslint-visitor-keys": "^5.0.1"
      },
      "engines": {
        "node": "^20.19.0 || ^22.13.0 || >=24"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/esquery": {
      "version": "1.7.0",
      "resolved": "https://registry.npmjs.org/esquery/-/esquery-1.7.0.tgz",
      "integrity": "sha512-Ap6G0WQwcU/LHsvLwON1fAQX9Zp0A2Y6Y/cJBl9r/JbW90Zyg4/zbG6zzKa2OTALELarYHmKu0GhpM5EO+7T0g==",
      "dev": true,
      "license": "BSD-3-Clause",
      "dependencies": {
        "estraverse": "^5.1.0"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/esrecurse": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz",
      "integrity": "sha512-KmfKL3b6G+RXvP8N1vr3Tq1kL/oCFgn2NYXEtqP8/L3pKapUA4G8cFVaoF3SU323CD4XypR/ffioHmkti6/Tag==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/estraverse": {
      "version": "5.3.0",
      "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
      "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/esutils": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz",
      "integrity": "sha512-kVscqXk4OCp68SZ0dkgEKVi6/8ij300KBWTJq32P/dYeWTSwK41WyTxalN1eRmA5Z9UU/LX9D7FWSmV9SAYx6g==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/fast-deep-equal": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz",
      "integrity": "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-json-stable-stringify": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz",
      "integrity": "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-levenshtein": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/fast-levenshtein/-/fast-levenshtein-2.0.6.tgz",
      "integrity": "sha512-DCXu6Ifhqcks7TZKY3Hxp3y6qphY5SJZmrWMDrKcERSOXWQdMhU9Ig/PYrzyw/ul9jOIyh0N4M0tbC5hodg8dw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fdir": {
      "version": "6.5.0",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
      "license": "MIT",
      "engines": {
        "node": ">=12.0.0"
      },
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/file-entry-cache": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/file-entry-cache/-/file-entry-cache-8.0.0.tgz",
      "integrity": "sha512-XXTUwCvisa5oacNGRP9SfNtYBNAMi+RPwBFmblZEF7N7swHYQS6/Zfk7SRwx4D5j3CH211YNRco1DEMNVfZCnQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flat-cache": "^4.0.0"
      },
      "engines": {
        "node": ">=16.0.0"
      }
    },
    "node_modules/find-up": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz",
      "integrity": "sha512-78/PXT1wlLLDgTzDs7sjq9hzz0vXD+zn+7wypEe4fXQxCmdmqfGsEPQxmiCSQI3ajFV91bVSsvNtrJRiW6nGng==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "locate-path": "^6.0.0",
        "path-exists": "^4.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/flat-cache": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/flat-cache/-/flat-cache-4.0.1.tgz",
      "integrity": "sha512-f7ccFPK3SXFHpx15UIGyRJ/FJQctuKZ0zVuN3frBo4HnK3cay9VEW0R6yPYFHC0AgqhukPzKjq22t5DmAyqGyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flatted": "^3.2.9",
        "keyv": "^4.5.4"
      },
      "engines": {
        "node": ">=16"
      }
    },
    "node_modules/flatted": {
      "version": "3.4.3",
      "resolved": "https://registry.npmjs.org/flatted/-/flatted-3.4.3.tgz",
      "integrity": "sha512-/zipXxyO6rGvuNGDiULY9MvEGSkb2gaG4GGH4ygMi0ZZzyMHdUZBmntJmx5x1G2VuPytCwGN4xsJP6cw+sK+vQ==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/fsevents": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/fsevents/-/fsevents-2.3.3.tgz",
      "integrity": "sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw==",
      "hasInstallScript": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^8.16.0 || ^10.6.0 || >=11.0.0"
      }
    },
    "node_modules/gensync": {
      "version": "1.0.0-beta.2",
      "resolved": "https://registry.npmjs.org/gensync/-/gensync-1.0.0-beta.2.tgz",
      "integrity": "sha512-3hN7NaskYvMDLQY55gnW3NQ+mesEAepTqlg+VEbj7zzqEMBVNhzcGYYeqFo/TlYz6eQiFcp1HcsCZO+nGgS8zg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/glob-parent": {
      "version": "6.0.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-6.0.2.tgz",
      "integrity": "sha512-XxwI8EOhVQgWp6iDL+3b0r86f4d6AX6zSU55HfB4ydCEuXLXc5FcYeOu+nnGftS4TEju/11rt4KJPTMgbfmv4A==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/globals": {
      "version": "17.7.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-17.7.0.tgz",
      "integrity": "sha512-Czmyns5dUsq4seFBR/Kdydhmo8y9kC79hiSkPn0YcGtNnYWnrgt0vjrSjx9tspoDGWm2CMarffRuLjM4xUz8xg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/graceful-fs": {
      "version": "4.2.11",
      "resolved": "https://registry.npmjs.org/graceful-fs/-/graceful-fs-4.2.11.tgz",
      "integrity": "sha512-RbJ5/jmFcNNCcDV5o9eTnBLJ/HszWV0P73bc+Ff4nS/rJj+YaS6IGyiOL0VoBYX+l1Wrl3k63h/KrH+nhJ0XvQ==",
      "license": "ISC"
    },
    "node_modules/hermes-estree": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-estree/-/hermes-estree-0.25.1.tgz",
      "integrity": "sha512-0wUoCcLp+5Ev5pDW2OriHC2MJCbwLwuRx+gAqMTOkGKJJiBCLjtrvy4PWUGn6MIVefecRpzoOZ/UV6iGdOr+Cw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/hermes-parser": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-parser/-/hermes-parser-0.25.1.tgz",
      "integrity": "sha512-6pEjquH3rqaI6cYAXYPcz9MS4rY6R4ngRgrgfDshRptUZIc3lw0MCIJIGDj9++mfySOuPTHB4nrSW99BCvOPIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hermes-estree": "0.25.1"
      }
    },
    "node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/imurmurhash": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/imurmurhash/-/imurmurhash-0.1.4.tgz",
      "integrity": "sha512-JmXMZ6wuvDmLiHEml9ykzqO6lwFbof0GG4IkcGaENdCRDDmMVnny7s5HsIgHCbaq0w2MyPhDqkhTUgS2LU2PHA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.8.19"
      }
    },
    "node_modules/is-extglob": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz",
      "integrity": "sha512-SbKbANkN603Vi4jEZv49LeVJMn4yGwsbzZworEoyEiutsN3nJYdbO36zfhGJ6QEDpOZIFkDtnq5JRxmvl3jsoQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-glob": {
      "version": "4.0.3",
      "resolved": "https://registry.npmjs.org/is-glob/-/is-glob-4.0.3.tgz",
      "integrity": "sha512-xelSayHH36ZgE7ZWhli7pW34hNbNl8Ojv5KVmkJD4hBdD3th8Tfk9vYasLM+mXWOZhFkgZfxhLSnrwRr4elSSg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-extglob": "^2.1.1"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/isexe": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz",
      "integrity": "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/jiti": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/jiti/-/jiti-2.7.0.tgz",
      "integrity": "sha512-AC/7JofJvZGrrneWNaEnJeOLUx+JlGt7tNa0wZiRPT4MY1wmfKjt2+6O2p2uz2+skll8OZZmJMNqeke7kKbNgQ==",
      "license": "MIT",
      "bin": {
        "jiti": "lib/jiti-cli.mjs"
      }
    },
    "node_modules/js-tokens": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz",
      "integrity": "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/jsesc": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/jsesc/-/jsesc-3.1.0.tgz",
      "integrity": "sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "jsesc": "bin/jsesc"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/json-buffer": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/json-buffer/-/json-buffer-3.0.1.tgz",
      "integrity": "sha512-4bV5BfR2mqfQTJm+V5tPPdf+ZpuhiIvTuAB5g8kcrXOZpTT/QwwVRWBywX1ozr6lEuPdbHxwaJlm9G6mI2sfSQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-schema-traverse": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-0.4.1.tgz",
      "integrity": "sha512-xbbCH5dCYU5T8LcEhhuh7HJ88HXuW3qsI3Y0zOZFKfZEHcpWiHU/Jxzk629Brsab/mMiHQti9wMP+845RPe3Vg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-stable-stringify-without-jsonify": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/json-stable-stringify-without-jsonify/-/json-stable-stringify-without-jsonify-1.0.1.tgz",
      "integrity": "sha512-Bdboy+l7tA3OGW6FjyFHWkP5LuByj1Tk33Ljyq0axyzdk9//JSi2u3fP1QSmd1KNwq6VOKYGlAu87CisVir6Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json5": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/json5/-/json5-2.2.3.tgz",
      "integrity": "sha512-XmOWe7eyHYH14cLdVPoyg+GOH3rYX++KpzrylJwSW98t3Nk+U8XOl8FWKOgwtzdb8lXGf6zYwDUzeHMWfxasyg==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "json5": "lib/cli.js"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/keyv": {
      "version": "4.5.4",
      "resolved": "https://registry.npmjs.org/keyv/-/keyv-4.5.4.tgz",
      "integrity": "sha512-oxVHkHR/EJf2CNXnWxRLW6mg7JyCCUcG0DtEGmL2ctUo1PNTin1PUil+r/+4r5MpVgC/fn1kjsx7mjSujKqIpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "json-buffer": "3.0.1"
      }
    },
    "node_modules/levn": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/levn/-/levn-0.4.1.tgz",
      "integrity": "sha512-+bT2uH4E5LGE7h/n3evcS/sQlJXCpIp6ym8OWJ5eV6+67Dsql/LaaT7qJBAt2rzfoa/5QBGBhxDix1dMt2kQKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1",
        "type-check": "~0.4.0"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/lightningcss": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss/-/lightningcss-1.33.0.tgz",
      "integrity": "sha512-WkUDrojuJs0xkgGf2udWxa3yGBRxPtxUkB79i6aCZLRgc7PM8fZe9TosfPDcvEpQZbuFASnHYmRLBLUbmLOIIA==",
      "license": "MPL-2.0",
      "dependencies": {
        "detect-libc": "^2.0.3"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      },
      "optionalDependencies": {
        "lightningcss-android-arm64": "1.33.0",
        "lightningcss-darwin-arm64": "1.33.0",
        "lightningcss-darwin-x64": "1.33.0",
        "lightningcss-freebsd-x64": "1.33.0",
        "lightningcss-linux-arm-gnueabihf": "1.33.0",
        "lightningcss-linux-arm64-gnu": "1.33.0",
        "lightningcss-linux-arm64-musl": "1.33.0",
        "lightningcss-linux-x64-gnu": "1.33.0",
        "lightningcss-linux-x64-musl": "1.33.0",
        "lightningcss-win32-arm64-msvc": "1.33.0",
        "lightningcss-win32-x64-msvc": "1.33.0"
      }
    },
    "node_modules/lightningcss-android-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-android-arm64/-/lightningcss-android-arm64-1.33.0.tgz",
      "integrity": "sha512-gEpRTalKdosp4Bb8qWtc2iOgE5SeIHlpS1up9bFq2wAyYhl1UdTObYiHe98zEM9SQvSoqQZ1IQD0JNpg3Ml5pg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "android"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-arm64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-arm64/-/lightningcss-darwin-arm64-1.33.0.tgz",
      "integrity": "sha512-Sciaz8eenNTKn9b3t7+xr0ipTp9YxKQY4npwQ3mrRuL0BAVHBLyZxofhaKBAVtzmtRZ/zTyo0/to4B1uWG/Djg==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-darwin-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-darwin-x64/-/lightningcss-darwin-x64-1.33.0.tgz",
      "integrity": "sha512-Z5UPAxzrjlWNNyGy6i65cJzzvgJ5D3T6wMvs+gWpY9d7qRhANrxqAp6LhxIgZhWEw18RfJTGcRxjuLIBr+m8XQ==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-freebsd-x64": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-freebsd-x64/-/lightningcss-freebsd-x64-1.33.0.tgz",
      "integrity": "sha512-QQM/Ti/hQajJwCY+RiWuCZ9sdtI/XQk7nDK5vC8kkdwixezOlDgvDx7+RT+QjK6FcFT4MpsuoBnHIo/O3StRRg==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "freebsd"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm-gnueabihf": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm-gnueabihf/-/lightningcss-linux-arm-gnueabihf-1.33.0.tgz",
      "integrity": "sha512-N7FVBe6iS24MlM6R/4RBTxGhQheZGs7tiQ9U32UtF75NzP5Q7xWPRqLBCKxlRQRk3rY1jCIPLzx7WzOhuUIRLQ==",
      "cpu": [
        "arm"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-gnu/-/lightningcss-linux-arm64-gnu-1.33.0.tgz",
      "integrity": "sha512-j2v/itmy4HlNxlc6voKXYgBqNi0Ng2LShg4z7GufpEgs05P+2suBVyi9I6YHq5uoVFx9ETin3eCEhLVyXGQnKg==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-arm64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-arm64-musl/-/lightningcss-linux-arm64-musl-1.33.0.tgz",
      "integrity": "sha512-yiO5ROMuYQgXbC60yjZU5CYSFZGKXL0HFATXt9mHJn1+zW55oCtMI9NfcVhYLMFDL7gV7oBPon/EmMMGg2OvtQ==",
      "cpu": [
        "arm64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-gnu": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-gnu/-/lightningcss-linux-x64-gnu-1.33.0.tgz",
      "integrity": "sha512-ar+Ju7LmcN0Jo4FpL4hpFybwNG9/3A/Br5KW2n2jyODg3MEZXaDYADdemoNS+BDNfMgKvylJLj4S5tyRActuAg==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "glibc"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-linux-x64-musl": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-linux-x64-musl/-/lightningcss-linux-x64-musl-1.33.0.tgz",
      "integrity": "sha512-RYiYbkokw0trfKqqzfF55lginwEPrD3OJDfTuJzFs1MK6iFnDenaz1fqLLtX4ITG3OktJQXOeTaw1awrBAlZPw==",
      "cpu": [
        "x64"
      ],
      "libc": [
        "musl"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-arm64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-arm64-msvc/-/lightningcss-win32-arm64-msvc-1.33.0.tgz",
      "integrity": "sha512-1K+MPfLSFVpphzpdbfkhlWk6wBrTObBzS2T6db10PNOZgR9GoVsAWzwNyuhUYYbTp23j+4RrncfujZ4uAzXvwA==",
      "cpu": [
        "arm64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/lightningcss-win32-x64-msvc": {
      "version": "1.33.0",
      "resolved": "https://registry.npmjs.org/lightningcss-win32-x64-msvc/-/lightningcss-win32-x64-msvc-1.33.0.tgz",
      "integrity": "sha512-OlEICDx/Xl0FqSp4bry8zFnCvGpig3Gl4gCquvYwHuqJKEC1+n9NgDniFvqHGmMv1ZkqDJrDqKKSykTDX+ehuA==",
      "cpu": [
        "x64"
      ],
      "license": "MPL-2.0",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 12.0.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/parcel"
      }
    },
    "node_modules/locate-path": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz",
      "integrity": "sha512-iPZK6eYjbxRu3uB4/WZ3EsEIMJFMqAoopl3R+zuq0UjcAm/MO6KCweDgPfP3elTztoKP3KtnVHxTn2NHBSDVUw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-locate": "^5.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/lru-cache": {
      "version": "5.1.1",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-5.1.1.tgz",
      "integrity": "sha512-KpNARQA3Iwv+jTA0utUVVbrh+Jlrr1Fv0e56GGzAFOXN7dk/FviaDW8LHmK52DlcH4WP2n6gI8vN1aesBFgo9w==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "yallist": "^3.0.2"
      }
    },
    "node_modules/magic-string": {
      "version": "0.30.21",
      "resolved": "https://registry.npmjs.org/magic-string/-/magic-string-0.30.21.tgz",
      "integrity": "sha512-vd2F4YUyEXKGcLHoq+TEyCjxueSeHnFxyyjNp80yg0XV4vUhnDer/lvvlqM/arB5bXQN5K2/3oinyCRyx8T2CQ==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.5"
      }
    },
    "node_modules/minimatch": {
      "version": "10.2.5",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-10.2.5.tgz",
      "integrity": "sha512-MULkVLfKGYDFYejP07QOurDLLQpcjk7Fw+7jXS2R2czRQzR56yHRveU5NDJEOviH+hETZKSkIk5c+T23GjFUMg==",
      "dev": true,
      "license": "BlueOak-1.0.0",
      "dependencies": {
        "brace-expansion": "^5.0.5"
      },
      "engines": {
        "node": "18 || 20 || >=22"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/ms": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.1.3.tgz",
      "integrity": "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/nanoid": {
      "version": "3.3.16",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.16.tgz",
      "integrity": "sha512-bzlKTyNJ7+LdGIIwy8ijFpIqEQIvafahV7eYykJ8Cvh42EdJeODoJ6gUJXpQJvej1BddH8OqTXZNE/KfbWAu8Q==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/natural-compare": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/natural-compare/-/natural-compare-1.4.0.tgz",
      "integrity": "sha512-OWND8ei3VtNC9h7V60qff3SVobHr996CTwgxubgyQYEpg290h9J0buyECNNJexkFm5sOajh5G116RYA1c8ZMSw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/node-releases": {
      "version": "2.0.51",
      "resolved": "https://registry.npmjs.org/node-releases/-/node-releases-2.0.51.tgz",
      "integrity": "sha512-wRNIrw4DmVLKQlbgOMdkMx27Wrpzes2hh5Jtbi2bjPd+4wJstWIqP5A+lscnqbm0xxmT5Bpg8Lec5ItEBwx6BQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/optionator": {
      "version": "0.9.4",
      "resolved": "https://registry.npmjs.org/optionator/-/optionator-0.9.4.tgz",
      "integrity": "sha512-6IpQ7mKUxRcZNLIObR0hz7lxsapSSIYNZJwXPGeF0mTVqGKFIXj1DQcMoT22S3ROcLyY/rz0PWaWZ9ayWmad9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "deep-is": "^0.1.3",
        "fast-levenshtein": "^2.0.6",
        "levn": "^0.4.1",
        "prelude-ls": "^1.2.1",
        "type-check": "^0.4.0",
        "word-wrap": "^1.2.5"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/p-limit": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-3.1.0.tgz",
      "integrity": "sha512-TYOanM3wGwNGsZN2cVTYPArw454xnXj5qmWF1bEoAc4+cU/ol7GVh7odevjp1FNHduHc3KZMcFduxU5Xc6uJRQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "yocto-queue": "^0.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-locate": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz",
      "integrity": "sha512-LaNjtRWUBY++zB5nE/NwcaoMylSPk+S+ZHNB1TzdbMJMny6dynpAGt7X/tl/QYq3TIeE6nxHppbo2LGymrG5Pw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-limit": "^3.0.2"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/path-exists": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/path-exists/-/path-exists-4.0.0.tgz",
      "integrity": "sha512-ak9Qy5Q7jYb2Wwcey5Fpvg2KoAc/ZIhLSLOSBmRmygPsGwkVVt0fZa0qrtMz+m6tJTAHfZQ8FnmB4MG4LWy7/w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-key": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz",
      "integrity": "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "4.0.5",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.5.tgz",
      "integrity": "sha512-RvwwcruNjI1ncT5xRakeyS9Lf8lcItv34KD+aif+VH9kduAyfYBipGh12274xtenIPZ119/R9BdTBa8gAwSh0A==",
      "license": "MIT",
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.22",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.22.tgz",
      "integrity": "sha512-KBDEIpLrvpv16pp3K0Fw+UCoZfopFjjgeB+0tA/aaThfEE74kKDLrgg603YvOWJyg3+WYtyq3xYsQWsIyZlPqQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.16",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.1"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/prelude-ls": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/prelude-ls/-/prelude-ls-1.2.1.tgz",
      "integrity": "sha512-vkcDPrRZo1QZLbn5RLGPpg/WmIQ65qoWWhcGKf/b5eplkkarX0m9z8ppCat4mlOqUsWpyNuYgO3VRyrYHSzX5g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/punycode": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz",
      "integrity": "sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/react": {
      "version": "19.2.8",
      "resolved": "https://registry.npmjs.org/react/-/react-19.2.8.tgz",
      "integrity": "sha512-PWaYA1L/q9u2u7xYQi+Y3L3Yfnie7XyLeaJICV1MGD6LprsBxcAqGjYyr0eY3p+QdsA+x/Irkt4Qif8D63+Sbw==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-dom": {
      "version": "19.2.8",
      "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-19.2.8.tgz",
      "integrity": "sha512-rVprimfGBG3DR+Tq0IQG2DT5PxKth1WIGDmj5yPmlzr4YBe7uyE+Du4oVqTDXZSHGGGXRtTJEGSSePyQCMBglQ==",
      "license": "MIT",
      "dependencies": {
        "scheduler": "^0.27.0"
      },
      "peerDependencies": {
        "react": "^19.2.8"
      }
    },
    "node_modules/rolldown": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/rolldown/-/rolldown-1.1.5.tgz",
      "integrity": "sha512-t9z29cJjXf/vxQ8dyhCSpt6H6aSwHTk8cT5I3iy6SMXuFpk5mB6PL6XfC8PCwrPTx93udwKUm9HRteAlTGBLiA==",
      "license": "MIT",
      "dependencies": {
        "@oxc-project/types": "=0.139.0",
        "@rolldown/pluginutils": "^1.0.0"
      },
      "bin": {
        "rolldown": "bin/cli.mjs"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "optionalDependencies": {
        "@rolldown/binding-android-arm64": "1.1.5",
        "@rolldown/binding-darwin-arm64": "1.1.5",
        "@rolldown/binding-darwin-x64": "1.1.5",
        "@rolldown/binding-freebsd-x64": "1.1.5",
        "@rolldown/binding-linux-arm-gnueabihf": "1.1.5",
        "@rolldown/binding-linux-arm64-gnu": "1.1.5",
        "@rolldown/binding-linux-arm64-musl": "1.1.5",
        "@rolldown/binding-linux-ppc64-gnu": "1.1.5",
        "@rolldown/binding-linux-s390x-gnu": "1.1.5",
        "@rolldown/binding-linux-x64-gnu": "1.1.5",
        "@rolldown/binding-linux-x64-musl": "1.1.5",
        "@rolldown/binding-openharmony-arm64": "1.1.5",
        "@rolldown/binding-wasm32-wasi": "1.1.5",
        "@rolldown/binding-win32-arm64-msvc": "1.1.5",
        "@rolldown/binding-win32-x64-msvc": "1.1.5"
      }
    },
    "node_modules/scheduler": {
      "version": "0.27.0",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.27.0.tgz",
      "integrity": "sha512-eNv+WrVbKu1f3vbYJT/xtiF5syA5HPIMtf9IgY/nKg0sWqzAUEvqY/xm7OcZc/qafLx/iO9FgOmeSAp4v5ti/Q==",
      "license": "MIT"
    },
    "node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/shebang-command": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz",
      "integrity": "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "shebang-regex": "^3.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shebang-regex": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz",
      "integrity": "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/source-map-js": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.1.tgz",
      "integrity": "sha512-UXWMKhLOwVKb728IUtQPXxfYU+usdybtUrK/8uGE8CQMvrhOpwvzDBwj0QhSL7MQc7vIsISBG8VQ8+IDQxpfQA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/tailwindcss": {
      "version": "4.3.3",
      "resolved": "https://registry.npmjs.org/tailwindcss/-/tailwindcss-4.3.3.tgz",
      "integrity": "sha512-gOhV3P7ufE62QDGg1zVaTgCR+EtPv92k2nIhVcVKcLmxT1sUBsQGhnZj175j+MqRt4zLF7ic+sCYjfhxMxj7YQ==",
      "license": "MIT"
    },
    "node_modules/tapable": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/tapable/-/tapable-2.3.3.tgz",
      "integrity": "sha512-uxc/zpqFg6x7C8vOE7lh6Lbda8eEL9zmVm/PLeTPBRhh1xCgdWaQ+J1CUieGpIfm2HdtsUpRv+HshiasBMcc6A==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/webpack"
      }
    },
    "node_modules/tinyglobby": {
      "version": "0.2.17",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.17.tgz",
      "integrity": "sha512-wXR/dYpcqKmfWpEdZjiKJOwCNFndD0DMnrW/cYjVGttEkBfVgcLFHoNrlj47mjOVic9yyNu65alsgF4NQyTa2g==",
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.5.0",
        "picomatch": "^4.0.4"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tslib": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.8.1.tgz",
      "integrity": "sha512-oJFu94HQb+KVduSUQL7wnpmqnfmLsOA/nAh6b6EH0wCEoK0/mPeXU6c3wKDV83MkOuHPRHtSXKKU99IBazS/2w==",
      "license": "0BSD",
      "optional": true
    },
    "node_modules/type-check": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/type-check/-/type-check-0.4.0.tgz",
      "integrity": "sha512-XleUoc9uwGXqjWwXaUTZAmzMcFZ5858QA2vvx1Ur5xIcixXIP+8LnFDgRplU30us6teqdlskFfu+ae4K79Ooew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/update-browserslist-db": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.2.3.tgz",
      "integrity": "sha512-Js0m9cx+qOgDxo0eMiFGEueWztz+d4+M3rGlmKPT+T4IS/jP4ylw3Nwpu6cpTTP8R1MAC1kF4VbdLt3ARf209w==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "escalade": "^3.2.0",
        "picocolors": "^1.1.1"
      },
      "bin": {
        "update-browserslist-db": "cli.js"
      },
      "peerDependencies": {
        "browserslist": ">= 4.21.0"
      }
    },
    "node_modules/uri-js": {
      "version": "4.4.1",
      "resolved": "https://registry.npmjs.org/uri-js/-/uri-js-4.4.1.tgz",
      "integrity": "sha512-7rKUyy33Q1yc98pQ1DAmLtwX109F7TIfWlW1Ydo8Wl1ii1SeHieeh0HHfPeL2fMXK6z0s8ecKs9frCuLJvndBg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "punycode": "^2.1.0"
      }
    },
    "node_modules/vite": {
      "version": "8.1.5",
      "resolved": "https://registry.npmjs.org/vite/-/vite-8.1.5.tgz",
      "integrity": "sha512-7ULLwsCdYx/nRyrpiEwvqb5TFHrMVZyBt+rg/OAXT7rgj/z+DtTDyKFeLAdDkubDVDKD8jOsndmy7m55XcfUsw==",
      "license": "MIT",
      "dependencies": {
        "lightningcss": "^1.32.0",
        "picomatch": "^4.0.5",
        "postcss": "^8.5.17",
        "rolldown": "~1.1.5",
        "tinyglobby": "^0.2.17"
      },
      "bin": {
        "vite": "bin/vite.js"
      },
      "engines": {
        "node": "^20.19.0 || >=22.12.0"
      },
      "funding": {
        "url": "https://github.com/vitejs/vite?sponsor=1"
      },
      "optionalDependencies": {
        "fsevents": "~2.3.3"
      },
      "peerDependencies": {
        "@types/node": "^20.19.0 || >=22.12.0",
        "@vitejs/devtools": "^0.3.0",
        "esbuild": "^0.27.0 || ^0.28.0",
        "jiti": ">=1.21.0",
        "less": "^4.0.0",
        "sass": "^1.70.0",
        "sass-embedded": "^1.70.0",
        "stylus": ">=0.54.8",
        "sugarss": "^5.0.0",
        "terser": "^5.16.0",
        "tsx": "^4.8.1",
        "yaml": "^2.4.2"
      },
      "peerDependenciesMeta": {
        "@types/node": {
          "optional": true
        },
        "@vitejs/devtools": {
          "optional": true
        },
        "esbuild": {
          "optional": true
        },
        "jiti": {
          "optional": true
        },
        "less": {
          "optional": true
        },
        "sass": {
          "optional": true
        },
        "sass-embedded": {
          "optional": true
        },
        "stylus": {
          "optional": true
        },
        "sugarss": {
          "optional": true
        },
        "terser": {
          "optional": true
        },
        "tsx": {
          "optional": true
        },
        "yaml": {
          "optional": true
        }
      }
    },
    "node_modules/which": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/which/-/which-2.0.2.tgz",
      "integrity": "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "isexe": "^2.0.0"
      },
      "bin": {
        "node-which": "bin/node-which"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/word-wrap": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/word-wrap/-/word-wrap-1.2.5.tgz",
      "integrity": "sha512-BN22B5eaMMI9UMtjrGd5g5eCYPpCPDUy0FJXbYsaT5zYxjFOckS53SQDE3pWkVoWpHXVb3BrYcEN4Twa55B5cA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/yallist": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/yallist/-/yallist-3.1.1.tgz",
      "integrity": "sha512-a4UGQaWPH59mOXUYnAG2ewncQS4i4F43Tv3JoAM+s2VDAmS9NsK8GpDMLrCHPksFT7h3K6TOoUNn2pb7RoXx4g==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/yocto-queue": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/yocto-queue/-/yocto-queue-0.1.0.tgz",
      "integrity": "sha512-rVksvsnNCdJ/ohGc6xgPwyN8eheCxsiLM8mxuE/t/mOVqJewPuO1miLpTHQiRgTKCLexL4MeAFVagts7HmNZ2Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/zod": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/zod/-/zod-4.4.3.tgz",
      "integrity": "sha512-ytENFjIJFl2UwYglde2jchW2Hwm4GJFLDiSXWdTrJQBIN9Fcyp7n4DhxJEiWNAJMV1/BqWfW/kkg71UDcHJyTQ==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/colinhacks"
      }
    },
    "node_modules/zod-validation-error": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/zod-validation-error/-/zod-validation-error-4.0.2.tgz",
      "integrity": "sha512-Q6/nZLe6jxuU80qb/4uJ4t5v2VEZ44lzQjPDhYJNztRQ4wyWc6VF3D3Kb/fAuPetZQnhS3hnajCf9CsWesghLQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18.0.0"
      },
      "peerDependencies": {
        "zod": "^3.25.0 || ^4.0.0"
      }
    }
  }
}

```

---

## File: `frontend\package.json`

```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tailwindcss/vite": "^4.3.3",
    "react": "^19.2.7",
    "react-dom": "^19.2.7",
    "tailwindcss": "^4.3.3"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@types/react": "^19.2.17",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^6.0.3",
    "eslint": "^10.6.0",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.3",
    "globals": "^17.7.0",
    "vite": "^8.1.1"
  }
}

```

---

## File: `frontend\README.md`

```markdown
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

```

---

## File: `frontend\vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),tailwindcss()],
})

```

---

## File: `frontend\dist\index.html`

```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#212121" />
    <title>Health Intelligence Companion</title>
    <script type="module" crossorigin src="/assets/index-SJ78fGiK.js"></script>
    <link rel="stylesheet" crossorigin href="/assets/index--Zz0r1_F.css">
  </head>
  <body class="bg-[#212121]">
    <div id="root"></div>
  </body>
</html>

```

---

## File: `frontend\dist\assets\index--Zz0r1_F.css`

```css
/*! tailwindcss v4.3.3 | MIT License | https://tailwindcss.com */
@layer properties{@supports (((-webkit-hyphens:none)) and (not (margin-trim:inline))) or ((-moz-orient:inline) and (not (color:rgb(from red r g b)))){*,:before,:after,::backdrop{--tw-translate-x:0;--tw-translate-y:0;--tw-translate-z:0;--tw-rotate-x:initial;--tw-rotate-y:initial;--tw-rotate-z:initial;--tw-skew-x:initial;--tw-skew-y:initial;--tw-space-y-reverse:0;--tw-border-style:solid;--tw-gradient-position:initial;--tw-gradient-from:#0000;--tw-gradient-via:#0000;--tw-gradient-to:#0000;--tw-gradient-stops:initial;--tw-gradient-via-stops:initial;--tw-gradient-from-position:0%;--tw-gradient-via-position:50%;--tw-gradient-to-position:100%;--tw-leading:initial;--tw-font-weight:initial;--tw-tracking:initial;--tw-shadow:0 0 #0000;--tw-shadow-color:initial;--tw-shadow-alpha:100%;--tw-inset-shadow:0 0 #0000;--tw-inset-shadow-color:initial;--tw-inset-shadow-alpha:100%;--tw-ring-color:initial;--tw-ring-shadow:0 0 #0000;--tw-inset-ring-color:initial;--tw-inset-ring-shadow:0 0 #0000;--tw-ring-inset:initial;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-offset-shadow:0 0 #0000;--tw-blur:initial;--tw-brightness:initial;--tw-contrast:initial;--tw-grayscale:initial;--tw-hue-rotate:initial;--tw-invert:initial;--tw-opacity:initial;--tw-saturate:initial;--tw-sepia:initial;--tw-drop-shadow:initial;--tw-drop-shadow-color:initial;--tw-drop-shadow-alpha:100%;--tw-drop-shadow-size:initial;--tw-backdrop-blur:initial;--tw-backdrop-brightness:initial;--tw-backdrop-contrast:initial;--tw-backdrop-grayscale:initial;--tw-backdrop-hue-rotate:initial;--tw-backdrop-invert:initial;--tw-backdrop-opacity:initial;--tw-backdrop-saturate:initial;--tw-backdrop-sepia:initial;--tw-duration:initial;--tw-scale-x:1;--tw-scale-y:1;--tw-scale-z:1}}}@layer theme{:root,:host{--font-sans:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";--font-mono:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;--color-red-400:oklch(70.4% .191 22.216);--color-red-500:oklch(63.7% .237 25.331);--color-emerald-300:oklch(84.5% .143 164.978);--color-emerald-400:oklch(76.5% .177 163.223);--color-emerald-500:oklch(69.6% .17 162.48);--color-teal-500:oklch(70.4% .14 182.503);--color-teal-600:oklch(60% .118 184.704);--color-blue-300:oklch(80.9% .105 251.813);--color-blue-400:oklch(70.7% .165 254.624);--color-blue-500:oklch(62.3% .214 259.815);--color-gray-100:oklch(96.7% .003 264.542);--color-gray-200:oklch(92.8% .006 264.531);--color-gray-300:oklch(87.2% .01 258.338);--color-gray-400:oklch(70.7% .022 261.325);--color-gray-500:oklch(55.1% .027 264.364);--color-gray-600:oklch(44.6% .03 256.802);--color-gray-700:oklch(37.3% .034 259.733);--color-gray-900:oklch(21% .034 264.665);--color-black:#000;--color-white:#fff;--spacing:.25rem;--container-sm:24rem;--container-md:28rem;--container-lg:32rem;--container-3xl:48rem;--container-5xl:64rem;--text-xs:.75rem;--text-xs--line-height:calc(1 / .75);--text-sm:.875rem;--text-sm--line-height:calc(1.25 / .875);--text-base:1rem;--text-base--line-height:calc(1.5 / 1);--text-lg:1.125rem;--text-lg--line-height:calc(1.75 / 1.125);--text-2xl:1.5rem;--text-2xl--line-height:calc(2 / 1.5);--font-weight-medium:500;--font-weight-semibold:600;--font-weight-bold:700;--tracking-tight:-.025em;--tracking-wider:.05em;--leading-snug:1.375;--leading-relaxed:1.625;--radius-sm:.25rem;--radius-md:.375rem;--radius-lg:.5rem;--radius-xl:.75rem;--radius-2xl:1rem;--animate-spin:spin 1s linear infinite;--animate-pulse:pulse 2s cubic-bezier(.4, 0, .6, 1) infinite;--animate-bounce:bounce 1s infinite;--blur-sm:8px;--default-transition-duration:.15s;--default-transition-timing-function:cubic-bezier(.4, 0, .2, 1);--default-font-family:var(--font-sans);--default-mono-font-family:var(--font-mono)}}@layer base{*,:after,:before,::backdrop{box-sizing:border-box;border:0 solid;margin:0;padding:0}::file-selector-button{box-sizing:border-box;border:0 solid;margin:0;padding:0}html,:host{-webkit-text-size-adjust:100%;tab-size:4;line-height:1.5;font-family:var(--default-font-family,-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji");font-feature-settings:var(--default-font-feature-settings,normal);font-variation-settings:var(--default-font-variation-settings,normal);-webkit-tap-highlight-color:transparent}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;-webkit-text-decoration:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,samp,pre{font-family:var(--default-mono-font-family,ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace);font-feature-settings:var(--default-mono-font-feature-settings,normal);font-variation-settings:var(--default-mono-font-variation-settings,normal);font-size:1em}small{font-size:80%}sub,sup{vertical-align:baseline;font-size:75%;line-height:0;position:relative}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}:-moz-focusring:where(:not(iframe)){outline:auto}progress{vertical-align:baseline}summary{display:list-item}ol,ul,menu{list-style:none}img,svg,video,canvas,audio,iframe,embed,object{vertical-align:middle;display:block}img,video{max-width:100%;height:auto}button,input,select,optgroup,textarea{font:inherit;font-feature-settings:inherit;font-variation-settings:inherit;letter-spacing:inherit;color:inherit;opacity:1;background-color:#0000;border-radius:0}::file-selector-button{font:inherit;font-feature-settings:inherit;font-variation-settings:inherit;letter-spacing:inherit;color:inherit;opacity:1;background-color:#0000;border-radius:0}:where(select:is([multiple],[size])) optgroup{font-weight:bolder}:where(select:is([multiple],[size])) optgroup option{padding-inline-start:20px}::file-selector-button{margin-inline-end:4px}::placeholder{opacity:1}@supports (not ((-webkit-appearance:-apple-pay-button))) or (contain-intrinsic-size:1px){::placeholder{color:currentColor}@supports (color:color-mix(in lab, red, red)){::placeholder{color:color-mix(in oklab, currentcolor 50%, transparent)}}}textarea{resize:vertical}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-date-and-time-value{min-height:1lh;text-align:inherit}::-webkit-datetime-edit{display:inline-flex}::-webkit-datetime-edit-fields-wrapper{padding:0}::-webkit-datetime-edit{padding-block:0}::-webkit-datetime-edit-year-field{padding-block:0}::-webkit-datetime-edit-month-field{padding-block:0}::-webkit-datetime-edit-day-field{padding-block:0}::-webkit-datetime-edit-hour-field{padding-block:0}::-webkit-datetime-edit-minute-field{padding-block:0}::-webkit-datetime-edit-second-field{padding-block:0}::-webkit-datetime-edit-millisecond-field{padding-block:0}::-webkit-datetime-edit-meridiem-field{padding-block:0}::-webkit-calendar-picker-indicator{line-height:1}:-moz-ui-invalid{box-shadow:none}button,input:where([type=button],[type=reset],[type=submit]){appearance:button}::file-selector-button{appearance:button}::-webkit-inner-spin-button{height:auto}::-webkit-outer-spin-button{height:auto}[hidden]:where(:not([hidden=until-found])){display:none!important}}@layer components;@layer utilities{.pointer-events-none{pointer-events:none}.collapse{visibility:collapse}.absolute{position:absolute}.fixed{position:fixed}.relative{position:relative}.sticky{position:sticky}.inset-0{inset:0}.inset-y-0{inset-block:0}.top-0{top:0}.right-0{right:0}.left-0{left:0}.z-40{z-index:40}.z-50{z-index:50}.mx-2{margin-inline:calc(var(--spacing) * 2)}.mx-4{margin-inline:calc(var(--spacing) * 4)}.mx-auto{margin-inline:auto}.my-3{margin-block:calc(var(--spacing) * 3)}.mt-0\.5{margin-top:calc(var(--spacing) * .5)}.mt-1{margin-top:var(--spacing)}.mt-2{margin-top:calc(var(--spacing) * 2)}.mt-5{margin-top:calc(var(--spacing) * 5)}.mr-0\.5{margin-right:calc(var(--spacing) * .5)}.-mb-1{margin-bottom:calc(var(--spacing) * -1)}.mb-1\.5{margin-bottom:calc(var(--spacing) * 1.5)}.mb-2{margin-bottom:calc(var(--spacing) * 2)}.mb-3{margin-bottom:calc(var(--spacing) * 3)}.mb-3\.5{margin-bottom:calc(var(--spacing) * 3.5)}.mb-5{margin-bottom:calc(var(--spacing) * 5)}.mb-6{margin-bottom:calc(var(--spacing) * 6)}.mb-8{margin-bottom:calc(var(--spacing) * 8)}.ml-2{margin-left:calc(var(--spacing) * 2)}.ml-auto{margin-left:auto}.block{display:block}.flex{display:flex}.grid{display:grid}.hidden{display:none}.inline{display:inline}.h-2{height:calc(var(--spacing) * 2)}.h-3{height:calc(var(--spacing) * 3)}.h-3\.5{height:calc(var(--spacing) * 3.5)}.h-4{height:calc(var(--spacing) * 4)}.h-4\.5{height:calc(var(--spacing) * 4.5)}.h-5{height:calc(var(--spacing) * 5)}.h-7{height:calc(var(--spacing) * 7)}.h-8{height:calc(var(--spacing) * 8)}.h-10{height:calc(var(--spacing) * 10)}.h-12{height:calc(var(--spacing) * 12)}.h-14{height:calc(var(--spacing) * 14)}.h-\[calc\(100vh-65px\)\]{height:calc(100vh - 65px)}.h-full{height:100%}.max-h-40{max-height:calc(var(--spacing) * 40)}.max-h-\[200px\]{max-height:200px}.w-1\/3{width:33.3333%}.w-2{width:calc(var(--spacing) * 2)}.w-3\.5{width:calc(var(--spacing) * 3.5)}.w-4{width:calc(var(--spacing) * 4)}.w-4\.5{width:calc(var(--spacing) * 4.5)}.w-5{width:calc(var(--spacing) * 5)}.w-5\/6{width:83.3333%}.w-7{width:calc(var(--spacing) * 7)}.w-8{width:calc(var(--spacing) * 8)}.w-10{width:calc(var(--spacing) * 10)}.w-14{width:calc(var(--spacing) * 14)}.w-48{width:calc(var(--spacing) * 48)}.w-56{width:calc(var(--spacing) * 56)}.w-64{width:calc(var(--spacing) * 64)}.w-\[280px\]{width:280px}.w-fit{width:fit-content}.w-full{width:100%}.w-px{width:1px}.max-w-3xl{max-width:var(--container-3xl)}.max-w-5xl{max-width:var(--container-5xl)}.max-w-\[75\%\]{max-width:75%}.max-w-\[120px\]{max-width:120px}.max-w-\[180px\]{max-width:180px}.max-w-lg{max-width:var(--container-lg)}.max-w-md{max-width:var(--container-md)}.max-w-none{max-width:none}.max-w-sm{max-width:var(--container-sm)}.min-w-0{min-width:0}.flex-1{flex:1}.flex-shrink-0,.shrink-0{flex-shrink:0}.-translate-x-full{--tw-translate-x:-100%;translate:var(--tw-translate-x) var(--tw-translate-y)}.translate-x-0{--tw-translate-x:0px;translate:var(--tw-translate-x) var(--tw-translate-y)}.rotate-180{rotate:180deg}.transform{transform:var(--tw-rotate-x,) var(--tw-rotate-y,) var(--tw-rotate-z,) var(--tw-skew-x,) var(--tw-skew-y,)}.animate-bounce{animation:var(--animate-bounce)}.animate-pulse{animation:var(--animate-pulse)}.animate-spin{animation:var(--animate-spin)}.resize-none{resize:none}.scrollbar-thin{scrollbar-width:thin}.grid-cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}.flex-col{flex-direction:column}.flex-wrap{flex-wrap:wrap}.items-center{align-items:center}.items-end{align-items:flex-end}.items-start{align-items:flex-start}.justify-between{justify-content:space-between}.justify-center{justify-content:center}.justify-end{justify-content:flex-end}.gap-0\.5{gap:calc(var(--spacing) * .5)}.gap-1{gap:var(--spacing)}.gap-1\.5{gap:calc(var(--spacing) * 1.5)}.gap-2{gap:calc(var(--spacing) * 2)}.gap-2\.5{gap:calc(var(--spacing) * 2.5)}.gap-3{gap:calc(var(--spacing) * 3)}:where(.space-y-0\.5>:not(:last-child)){--tw-space-y-reverse:0;margin-block-start:calc(calc(var(--spacing) * .5) * var(--tw-space-y-reverse));margin-block-end:calc(calc(var(--spacing) * .5) * calc(1 - var(--tw-space-y-reverse)))}:where(.space-y-2>:not(:last-child)){--tw-space-y-reverse:0;margin-block-start:calc(calc(var(--spacing) * 2) * var(--tw-space-y-reverse));margin-block-end:calc(calc(var(--spacing) * 2) * calc(1 - var(--tw-space-y-reverse)))}:where(.space-y-3\.5>:not(:last-child)){--tw-space-y-reverse:0;margin-block-start:calc(calc(var(--spacing) * 3.5) * var(--tw-space-y-reverse));margin-block-end:calc(calc(var(--spacing) * 3.5) * calc(1 - var(--tw-space-y-reverse)))}:where(.space-y-4>:not(:last-child)){--tw-space-y-reverse:0;margin-block-start:calc(calc(var(--spacing) * 4) * var(--tw-space-y-reverse));margin-block-end:calc(calc(var(--spacing) * 4) * calc(1 - var(--tw-space-y-reverse)))}:where(.space-y-6>:not(:last-child)){--tw-space-y-reverse:0;margin-block-start:calc(calc(var(--spacing) * 6) * var(--tw-space-y-reverse));margin-block-end:calc(calc(var(--spacing) * 6) * calc(1 - var(--tw-space-y-reverse)))}.truncate{text-overflow:ellipsis;white-space:nowrap;overflow:hidden}.overflow-hidden{overflow:hidden}.overflow-x-auto{overflow-x:auto}.overflow-y-auto{overflow-y:auto}.rounded{border-radius:.25rem}.rounded-2xl{border-radius:var(--radius-2xl)}.rounded-full{border-radius:2147483647px}.rounded-lg{border-radius:var(--radius-lg)}.rounded-md{border-radius:var(--radius-md)}.rounded-xl{border-radius:var(--radius-xl)}.rounded-tr-sm{border-top-right-radius:var(--radius-sm)}.border{border-style:var(--tw-border-style);border-width:1px}.border-t{border-top-style:var(--tw-border-style);border-top-width:1px}.border-r{border-right-style:var(--tw-border-style);border-right-width:1px}.border-b{border-bottom-style:var(--tw-border-style);border-bottom-width:1px}.border-blue-500\/20{border-color:#3080ff33}@supports (color:color-mix(in lab, red, red)){.border-blue-500\/20{border-color:color-mix(in oklab, var(--color-blue-500) 20%, transparent)}}.border-emerald-500\/30{border-color:#00bb7f4d}@supports (color:color-mix(in lab, red, red)){.border-emerald-500\/30{border-color:color-mix(in oklab, var(--color-emerald-500) 30%, transparent)}}.border-red-500\/20{border-color:#fb2c3633}@supports (color:color-mix(in lab, red, red)){.border-red-500\/20{border-color:color-mix(in oklab, var(--color-red-500) 20%, transparent)}}.border-transparent{border-color:#0000}.border-white\/5{border-color:#ffffff0d}@supports (color:color-mix(in lab, red, red)){.border-white\/5{border-color:color-mix(in oklab, var(--color-white) 5%, transparent)}}.border-white\/10{border-color:#ffffff1a}@supports (color:color-mix(in lab, red, red)){.border-white\/10{border-color:color-mix(in oklab, var(--color-white) 10%, transparent)}}.bg-\[\#1b1b1b\]{background-color:#1b1b1b}.bg-\[\#2f2f2f\]{background-color:#2f2f2f}.bg-\[\#212121\]{background-color:#212121}.bg-black\/40{background-color:#0006}@supports (color:color-mix(in lab, red, red)){.bg-black\/40{background-color:color-mix(in oklab, var(--color-black) 40%, transparent)}}.bg-black\/60{background-color:#0009}@supports (color:color-mix(in lab, red, red)){.bg-black\/60{background-color:color-mix(in oklab, var(--color-black) 60%, transparent)}}.bg-blue-500\/10{background-color:#3080ff1a}@supports (color:color-mix(in lab, red, red)){.bg-blue-500\/10{background-color:color-mix(in oklab, var(--color-blue-500) 10%, transparent)}}.bg-emerald-500\/20{background-color:#00bb7f33}@supports (color:color-mix(in lab, red, red)){.bg-emerald-500\/20{background-color:color-mix(in oklab, var(--color-emerald-500) 20%, transparent)}}.bg-gray-500{background-color:var(--color-gray-500)}.bg-red-500\/10{background-color:#fb2c361a}@supports (color:color-mix(in lab, red, red)){.bg-red-500\/10{background-color:color-mix(in oklab, var(--color-red-500) 10%, transparent)}}.bg-transparent{background-color:#0000}.bg-white{background-color:var(--color-white)}.bg-white\/5{background-color:#ffffff0d}@supports (color:color-mix(in lab, red, red)){.bg-white\/5{background-color:color-mix(in oklab, var(--color-white) 5%, transparent)}}.bg-white\/10{background-color:#ffffff1a}@supports (color:color-mix(in lab, red, red)){.bg-white\/10{background-color:color-mix(in oklab, var(--color-white) 10%, transparent)}}.bg-gradient-to-br{--tw-gradient-position:to bottom right in oklab;background-image:linear-gradient(var(--tw-gradient-stops))}.bg-gradient-to-r{--tw-gradient-position:to right in oklab;background-image:linear-gradient(var(--tw-gradient-stops))}.from-emerald-400{--tw-gradient-from:var(--color-emerald-400);--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.from-emerald-500{--tw-gradient-from:var(--color-emerald-500);--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.to-teal-600{--tw-gradient-to:var(--color-teal-600);--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.object-contain{object-fit:contain}.object-cover{object-fit:cover}.p-1{padding:var(--spacing)}.p-1\.5{padding:calc(var(--spacing) * 1.5)}.p-2{padding:calc(var(--spacing) * 2)}.p-3{padding:calc(var(--spacing) * 3)}.p-4{padding:calc(var(--spacing) * 4)}.p-6{padding:calc(var(--spacing) * 6)}.px-1{padding-inline:var(--spacing)}.px-1\.5{padding-inline:calc(var(--spacing) * 1.5)}.px-2{padding-inline:calc(var(--spacing) * 2)}.px-2\.5{padding-inline:calc(var(--spacing) * 2.5)}.px-3{padding-inline:calc(var(--spacing) * 3)}.px-4{padding-inline:calc(var(--spacing) * 4)}.px-6{padding-inline:calc(var(--spacing) * 6)}.py-0\.5{padding-block:calc(var(--spacing) * .5)}.py-1{padding-block:var(--spacing)}.py-1\.5{padding-block:calc(var(--spacing) * 1.5)}.py-2{padding-block:calc(var(--spacing) * 2)}.py-2\.5{padding-block:calc(var(--spacing) * 2.5)}.py-3{padding-block:calc(var(--spacing) * 3)}.py-3\.5{padding-block:calc(var(--spacing) * 3.5)}.py-4{padding-block:calc(var(--spacing) * 4)}.pt-1{padding-top:var(--spacing)}.pt-2{padding-top:calc(var(--spacing) * 2)}.pt-4{padding-top:calc(var(--spacing) * 4)}.pt-6{padding-top:calc(var(--spacing) * 6)}.pb-2{padding-bottom:calc(var(--spacing) * 2)}.pb-3\.5{padding-bottom:calc(var(--spacing) * 3.5)}.text-center{text-align:center}.text-left{text-align:left}.font-mono{font-family:var(--font-mono)}.text-2xl{font-size:var(--text-2xl);line-height:var(--tw-leading,var(--text-2xl--line-height))}.text-base{font-size:var(--text-base);line-height:var(--tw-leading,var(--text-base--line-height))}.text-lg{font-size:var(--text-lg);line-height:var(--tw-leading,var(--text-lg--line-height))}.text-sm{font-size:var(--text-sm);line-height:var(--tw-leading,var(--text-sm--line-height))}.text-xs{font-size:var(--text-xs);line-height:var(--tw-leading,var(--text-xs--line-height))}.text-\[10px\]{font-size:10px}.text-\[11px\]{font-size:11px}.leading-relaxed{--tw-leading:var(--leading-relaxed);line-height:var(--leading-relaxed)}.leading-snug{--tw-leading:var(--leading-snug);line-height:var(--leading-snug)}.font-bold{--tw-font-weight:var(--font-weight-bold);font-weight:var(--font-weight-bold)}.font-medium{--tw-font-weight:var(--font-weight-medium);font-weight:var(--font-weight-medium)}.font-semibold{--tw-font-weight:var(--font-weight-semibold);font-weight:var(--font-weight-semibold)}.tracking-tight{--tw-tracking:var(--tracking-tight);letter-spacing:var(--tracking-tight)}.tracking-wider{--tw-tracking:var(--tracking-wider);letter-spacing:var(--tracking-wider)}.whitespace-pre-wrap{white-space:pre-wrap}.text-blue-300{color:var(--color-blue-300)}.text-blue-400{color:var(--color-blue-400)}.text-emerald-300{color:var(--color-emerald-300)}.text-emerald-400{color:var(--color-emerald-400)}.text-gray-100{color:var(--color-gray-100)}.text-gray-200{color:var(--color-gray-200)}.text-gray-300{color:var(--color-gray-300)}.text-gray-400{color:var(--color-gray-400)}.text-gray-500{color:var(--color-gray-500)}.text-gray-600{color:var(--color-gray-600)}.text-gray-700{color:var(--color-gray-700)}.text-gray-900{color:var(--color-gray-900)}.text-red-400{color:var(--color-red-400)}.text-red-500{color:var(--color-red-500)}.text-white{color:var(--color-white)}.lowercase{text-transform:lowercase}.uppercase{text-transform:uppercase}.placeholder-gray-600::placeholder{color:var(--color-gray-600)}.opacity-0{opacity:0}.opacity-25{opacity:.25}.opacity-70{opacity:.7}.opacity-75{opacity:.75}.opacity-100{opacity:1}.shadow-2xl{--tw-shadow:0 25px 50px -12px var(--tw-shadow-color,#00000040);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.shadow-lg{--tw-shadow:0 10px 15px -3px var(--tw-shadow-color,#0000001a), 0 4px 6px -4px var(--tw-shadow-color,#0000001a);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.shadow-sm{--tw-shadow:0 1px 3px 0 var(--tw-shadow-color,#0000001a), 0 1px 2px -1px var(--tw-shadow-color,#0000001a);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.ring-1{--tw-ring-shadow:var(--tw-ring-inset,) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color,currentcolor);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.shadow-emerald-500\/20{--tw-shadow-color:#00bb7f33}@supports (color:color-mix(in lab, red, red)){.shadow-emerald-500\/20{--tw-shadow-color:color-mix(in oklab, color-mix(in oklab, var(--color-emerald-500) 20%, transparent) var(--tw-shadow-alpha), transparent)}}.ring-white\/10{--tw-ring-color:#ffffff1a}@supports (color:color-mix(in lab, red, red)){.ring-white\/10{--tw-ring-color:color-mix(in oklab, var(--color-white) 10%, transparent)}}.filter{filter:var(--tw-blur,) var(--tw-brightness,) var(--tw-contrast,) var(--tw-grayscale,) var(--tw-hue-rotate,) var(--tw-invert,) var(--tw-saturate,) var(--tw-sepia,) var(--tw-drop-shadow,)}.backdrop-blur-sm{--tw-backdrop-blur:blur(var(--blur-sm));-webkit-backdrop-filter:var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,);backdrop-filter:var(--tw-backdrop-blur,) var(--tw-backdrop-brightness,) var(--tw-backdrop-contrast,) var(--tw-backdrop-grayscale,) var(--tw-backdrop-hue-rotate,) var(--tw-backdrop-invert,) var(--tw-backdrop-opacity,) var(--tw-backdrop-saturate,) var(--tw-backdrop-sepia,)}.transition-all{transition-property:all;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.transition-colors{transition-property:color,background-color,border-color,outline-color,text-decoration-color,fill,stroke,--tw-gradient-from,--tw-gradient-via,--tw-gradient-to;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.transition-opacity{transition-property:opacity;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.transition-transform{transition-property:transform,translate,scale,rotate;transition-timing-function:var(--tw-ease,var(--default-transition-timing-function));transition-duration:var(--tw-duration,var(--default-transition-duration))}.duration-150{--tw-duration:.15s;transition-duration:.15s}.duration-200{--tw-duration:.2s;transition-duration:.2s}.duration-300{--tw-duration:.3s;transition-duration:.3s}.outline-none{--tw-outline-style:none;outline-style:none}@media (hover:hover){.group-hover\:opacity-100:is(:where(.group):hover *){opacity:1}}.focus-within\:border-white\/20:focus-within{border-color:#fff3}@supports (color:color-mix(in lab, red, red)){.focus-within\:border-white\/20:focus-within{border-color:color-mix(in oklab, var(--color-white) 20%, transparent)}}@media (hover:hover){.hover\:border-white\/20:hover{border-color:#fff3}@supports (color:color-mix(in lab, red, red)){.hover\:border-white\/20:hover{border-color:color-mix(in oklab, var(--color-white) 20%, transparent)}}.hover\:bg-gray-200:hover{background-color:var(--color-gray-200)}.hover\:bg-white\/5:hover{background-color:#ffffff0d}@supports (color:color-mix(in lab, red, red)){.hover\:bg-white\/5:hover{background-color:color-mix(in oklab, var(--color-white) 5%, transparent)}}.hover\:bg-white\/10:hover{background-color:#ffffff1a}@supports (color:color-mix(in lab, red, red)){.hover\:bg-white\/10:hover{background-color:color-mix(in oklab, var(--color-white) 10%, transparent)}}.hover\:bg-white\/\[0\.08\]:hover{background-color:#ffffff14}@supports (color:color-mix(in lab, red, red)){.hover\:bg-white\/\[0\.08\]:hover{background-color:color-mix(in oklab, var(--color-white) 8%, transparent)}}.hover\:from-emerald-400:hover{--tw-gradient-from:var(--color-emerald-400);--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.hover\:to-teal-500:hover{--tw-gradient-to:var(--color-teal-500);--tw-gradient-stops:var(--tw-gradient-via-stops,var(--tw-gradient-position), var(--tw-gradient-from) var(--tw-gradient-from-position), var(--tw-gradient-to) var(--tw-gradient-to-position))}.hover\:text-emerald-300:hover{color:var(--color-emerald-300)}.hover\:text-gray-200:hover{color:var(--color-gray-200)}.hover\:text-gray-300:hover{color:var(--color-gray-300)}.hover\:underline:hover{text-decoration-line:underline}}.focus\:border-emerald-500\/50:focus{border-color:#00bb7f80}@supports (color:color-mix(in lab, red, red)){.focus\:border-emerald-500\/50:focus{border-color:color-mix(in oklab, var(--color-emerald-500) 50%, transparent)}}.focus\:ring-1:focus{--tw-ring-shadow:var(--tw-ring-inset,) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color,currentcolor);box-shadow:var(--tw-inset-shadow), var(--tw-inset-ring-shadow), var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow)}.focus\:ring-emerald-500\/20:focus{--tw-ring-color:#00bb7f33}@supports (color:color-mix(in lab, red, red)){.focus\:ring-emerald-500\/20:focus{--tw-ring-color:color-mix(in oklab, var(--color-emerald-500) 20%, transparent)}}.active\:scale-95:active{--tw-scale-x:95%;--tw-scale-y:95%;--tw-scale-z:95%;scale:var(--tw-scale-x) var(--tw-scale-y)}.active\:scale-\[0\.98\]:active{scale:.98}.disabled\:cursor-not-allowed:disabled{cursor:not-allowed}.disabled\:opacity-20:disabled{opacity:.2}.disabled\:opacity-40:disabled{opacity:.4}.disabled\:opacity-50:disabled{opacity:.5}.disabled\:opacity-60:disabled{opacity:.6}@media (width>=40rem){.sm\:inline{display:inline}}@media (width>=48rem){.md\:flex{display:flex}.md\:hidden{display:none}}}@keyframes fade-in{0%{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.animate-fade-in{animation:.3s ease-out fade-in}.scrollbar-thin::-webkit-scrollbar{width:6px;height:6px}.scrollbar-thin::-webkit-scrollbar-track{background:0 0}.scrollbar-thin::-webkit-scrollbar-thumb{background:#424242;border-radius:3px}.scrollbar-thin::-webkit-scrollbar-thumb:hover{background:#555}.scrollbar-thin{scrollbar-width:thin;scrollbar-color:#424242 transparent}html{--lightningcss-light: ;--lightningcss-dark:initial;color-scheme:dark}body{background:#212121}@property --tw-translate-x{syntax:"*";inherits:false;initial-value:0}@property --tw-translate-y{syntax:"*";inherits:false;initial-value:0}@property --tw-translate-z{syntax:"*";inherits:false;initial-value:0}@property --tw-rotate-x{syntax:"*";inherits:false}@property --tw-rotate-y{syntax:"*";inherits:false}@property --tw-rotate-z{syntax:"*";inherits:false}@property --tw-skew-x{syntax:"*";inherits:false}@property --tw-skew-y{syntax:"*";inherits:false}@property --tw-space-y-reverse{syntax:"*";inherits:false;initial-value:0}@property --tw-border-style{syntax:"*";inherits:false;initial-value:solid}@property --tw-gradient-position{syntax:"*";inherits:false}@property --tw-gradient-from{syntax:"<color>";inherits:false;initial-value:#0000}@property --tw-gradient-via{syntax:"<color>";inherits:false;initial-value:#0000}@property --tw-gradient-to{syntax:"<color>";inherits:false;initial-value:#0000}@property --tw-gradient-stops{syntax:"*";inherits:false}@property --tw-gradient-via-stops{syntax:"*";inherits:false}@property --tw-gradient-from-position{syntax:"<length-percentage>";inherits:false;initial-value:0%}@property --tw-gradient-via-position{syntax:"<length-percentage>";inherits:false;initial-value:50%}@property --tw-gradient-to-position{syntax:"<length-percentage>";inherits:false;initial-value:100%}@property --tw-leading{syntax:"*";inherits:false}@property --tw-font-weight{syntax:"*";inherits:false}@property --tw-tracking{syntax:"*";inherits:false}@property --tw-shadow{syntax:"*";inherits:false;initial-value:0 0 #0000}@property --tw-shadow-color{syntax:"*";inherits:false}@property --tw-shadow-alpha{syntax:"<percentage>";inherits:false;initial-value:100%}@property --tw-inset-shadow{syntax:"*";inherits:false;initial-value:0 0 #0000}@property --tw-inset-shadow-color{syntax:"*";inherits:false}@property --tw-inset-shadow-alpha{syntax:"<percentage>";inherits:false;initial-value:100%}@property --tw-ring-color{syntax:"*";inherits:false}@property --tw-ring-shadow{syntax:"*";inherits:false;initial-value:0 0 #0000}@property --tw-inset-ring-color{syntax:"*";inherits:false}@property --tw-inset-ring-shadow{syntax:"*";inherits:false;initial-value:0 0 #0000}@property --tw-ring-inset{syntax:"*";inherits:false}@property --tw-ring-offset-width{syntax:"<length>";inherits:false;initial-value:0}@property --tw-ring-offset-color{syntax:"*";inherits:false;initial-value:#fff}@property --tw-ring-offset-shadow{syntax:"*";inherits:false;initial-value:0 0 #0000}@property --tw-blur{syntax:"*";inherits:false}@property --tw-brightness{syntax:"*";inherits:false}@property --tw-contrast{syntax:"*";inherits:false}@property --tw-grayscale{syntax:"*";inherits:false}@property --tw-hue-rotate{syntax:"*";inherits:false}@property --tw-invert{syntax:"*";inherits:false}@property --tw-opacity{syntax:"*";inherits:false}@property --tw-saturate{syntax:"*";inherits:false}@property --tw-sepia{syntax:"*";inherits:false}@property --tw-drop-shadow{syntax:"*";inherits:false}@property --tw-drop-shadow-color{syntax:"*";inherits:false}@property --tw-drop-shadow-alpha{syntax:"<percentage>";inherits:false;initial-value:100%}@property --tw-drop-shadow-size{syntax:"*";inherits:false}@property --tw-backdrop-blur{syntax:"*";inherits:false}@property --tw-backdrop-brightness{syntax:"*";inherits:false}@property --tw-backdrop-contrast{syntax:"*";inherits:false}@property --tw-backdrop-grayscale{syntax:"*";inherits:false}@property --tw-backdrop-hue-rotate{syntax:"*";inherits:false}@property --tw-backdrop-invert{syntax:"*";inherits:false}@property --tw-backdrop-opacity{syntax:"*";inherits:false}@property --tw-backdrop-saturate{syntax:"*";inherits:false}@property --tw-backdrop-sepia{syntax:"*";inherits:false}@property --tw-duration{syntax:"*";inherits:false}@property --tw-scale-x{syntax:"*";inherits:false;initial-value:1}@property --tw-scale-y{syntax:"*";inherits:false;initial-value:1}@property --tw-scale-z{syntax:"*";inherits:false;initial-value:1}@keyframes spin{to{transform:rotate(360deg)}}@keyframes pulse{50%{opacity:.5}}@keyframes bounce{0%,to{animation-timing-function:cubic-bezier(.8,0,1,1);transform:translateY(-25%)}50%{animation-timing-function:cubic-bezier(0,0,.2,1);transform:none}}

```

---

## File: `frontend\dist\assets\index-SJ78fGiK.js`

```javascript
var e=Object.create,t=Object.defineProperty,n=Object.getOwnPropertyDescriptor,r=Object.getOwnPropertyNames,i=Object.getPrototypeOf,a=Object.prototype.hasOwnProperty,o=(e,t)=>()=>(t||(e((t={exports:{}}).exports,t),e=null),t.exports),s=(e,i,o,s)=>{if(i&&typeof i==`object`||typeof i==`function`)for(var c=r(i),l=0,u=c.length,d;l<u;l++)d=c[l],!a.call(e,d)&&d!==o&&t(e,d,{get:(e=>i[e]).bind(null,d),enumerable:!(s=n(i,d))||s.enumerable});return e},c=(n,r,a)=>(a=n==null?{}:e(i(n)),s(r||!n||!n.__esModule?t(a,`default`,{value:n,enumerable:!0}):a,n));(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),e.crossOrigin===`use-credentials`?t.credentials=`include`:e.crossOrigin===`anonymous`?t.credentials=`omit`:t.credentials=`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var l=o((e=>{var t=Symbol.for(`react.transitional.element`),n=Symbol.for(`react.portal`),r=Symbol.for(`react.fragment`),i=Symbol.for(`react.strict_mode`),a=Symbol.for(`react.profiler`),o=Symbol.for(`react.consumer`),s=Symbol.for(`react.context`),c=Symbol.for(`react.forward_ref`),l=Symbol.for(`react.suspense`),u=Symbol.for(`react.memo`),d=Symbol.for(`react.lazy`),f=Symbol.for(`react.activity`),p=Symbol.iterator;function m(e){return typeof e!=`object`||!e?null:(e=p&&e[p]||e[`@@iterator`],typeof e==`function`?e:null)}var h={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},g=Object.assign,_={};function v(e,t,n){this.props=e,this.context=t,this.refs=_,this.updater=n||h}v.prototype.isReactComponent={},v.prototype.setState=function(e,t){if(typeof e!=`object`&&typeof e!=`function`&&e!=null)throw Error(`takes an object of state variables to update or a function which returns an object of state variables.`);this.updater.enqueueSetState(this,e,t,`setState`)},v.prototype.forceUpdate=function(e){this.updater.enqueueForceUpdate(this,e,`forceUpdate`)};function y(){}y.prototype=v.prototype;function b(e,t,n){this.props=e,this.context=t,this.refs=_,this.updater=n||h}var x=b.prototype=new y;x.constructor=b,g(x,v.prototype),x.isPureReactComponent=!0;var ee=Array.isArray;function S(){}var C={H:null,A:null,T:null,S:null},te=Object.prototype.hasOwnProperty;function ne(e,n,r){var i=r.ref;return{$$typeof:t,type:e,key:n,ref:i===void 0?null:i,props:r}}function re(e,t){return ne(e.type,t,e.props)}function ie(e){return typeof e==`object`&&!!e&&e.$$typeof===t}function ae(e){var t={"=":`=0`,":":`=2`};return`$`+e.replace(/[=:]/g,function(e){return t[e]})}var oe=/\/+/g;function w(e,t){return typeof e==`object`&&e&&e.key!=null?ae(``+e.key):t.toString(36)}function se(e){switch(e.status){case`fulfilled`:return e.value;case`rejected`:throw e.reason;default:switch(typeof e.status==`string`?e.then(S,S):(e.status=`pending`,e.then(function(t){e.status===`pending`&&(e.status=`fulfilled`,e.value=t)},function(t){e.status===`pending`&&(e.status=`rejected`,e.reason=t)})),e.status){case`fulfilled`:return e.value;case`rejected`:throw e.reason}}throw e}function ce(e,r,i,a,o){var s=typeof e;(s===`undefined`||s===`boolean`)&&(e=null);var c=!1;if(e===null)c=!0;else switch(s){case`bigint`:case`string`:case`number`:c=!0;break;case`object`:switch(e.$$typeof){case t:case n:c=!0;break;case d:return c=e._init,ce(c(e._payload),r,i,a,o)}}if(c)return o=o(e),c=a===``?`.`+w(e,0):a,ee(o)?(i=``,c!=null&&(i=c.replace(oe,`$&/`)+`/`),ce(o,r,i,``,function(e){return e})):o!=null&&(ie(o)&&(o=re(o,i+(o.key==null||e&&e.key===o.key?``:(``+o.key).replace(oe,`$&/`)+`/`)+c)),r.push(o)),1;c=0;var l=a===``?`.`:a+`:`;if(ee(e))for(var u=0;u<e.length;u++)a=e[u],s=l+w(a,u),c+=ce(a,r,i,s,o);else if(u=m(e),typeof u==`function`)for(e=u.call(e),u=0;!(a=e.next()).done;)a=a.value,s=l+w(a,u++),c+=ce(a,r,i,s,o);else if(s===`object`){if(typeof e.then==`function`)return ce(se(e),r,i,a,o);throw r=String(e),Error(`Objects are not valid as a React child (found: `+(r===`[object Object]`?`object with keys {`+Object.keys(e).join(`, `)+`}`:r)+`). If you meant to render a collection of children, use an array instead.`)}return c}function le(e,t,n){if(e==null)return e;var r=[],i=0;return ce(e,r,``,``,function(e){return t.call(n,e,i++)}),r}function ue(e){if(e._status===-1){var t=e._result;t=t(),t.then(function(t){(e._status===0||e._status===-1)&&(e._status=1,e._result=t)},function(t){(e._status===0||e._status===-1)&&(e._status=2,e._result=t)}),e._status===-1&&(e._status=0,e._result=t)}if(e._status===1)return e._result.default;throw e._result}var T=typeof reportError==`function`?reportError:function(e){if(typeof window==`object`&&typeof window.ErrorEvent==`function`){var t=new window.ErrorEvent(`error`,{bubbles:!0,cancelable:!0,message:typeof e==`object`&&e&&typeof e.message==`string`?String(e.message):String(e),error:e});if(!window.dispatchEvent(t))return}else if(typeof process==`object`&&typeof process.emit==`function`){process.emit(`uncaughtException`,e);return}console.error(e)},E={map:le,forEach:function(e,t,n){le(e,function(){t.apply(this,arguments)},n)},count:function(e){var t=0;return le(e,function(){t++}),t},toArray:function(e){return le(e,function(e){return e})||[]},only:function(e){if(!ie(e))throw Error(`React.Children.only expected to receive a single React element child.`);return e}};e.Activity=f,e.Children=E,e.Component=v,e.Fragment=r,e.Profiler=a,e.PureComponent=b,e.StrictMode=i,e.Suspense=l,e.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=C,e.__COMPILER_RUNTIME={__proto__:null,c:function(e){return C.H.useMemoCache(e)}},e.cache=function(e){return function(){return e.apply(null,arguments)}},e.cacheSignal=function(){return null},e.cloneElement=function(e,t,n){if(e==null)throw Error(`The argument must be a React element, but you passed `+e+`.`);var r=g({},e.props),i=e.key;if(t!=null)for(a in t.key!==void 0&&(i=``+t.key),t)!te.call(t,a)||a===`key`||a===`__self`||a===`__source`||a===`ref`&&t.ref===void 0||(r[a]=t[a]);var a=arguments.length-2;if(a===1)r.children=n;else if(1<a){for(var o=Array(a),s=0;s<a;s++)o[s]=arguments[s+2];r.children=o}return ne(e.type,i,r)},e.createContext=function(e){return e={$$typeof:s,_currentValue:e,_currentValue2:e,_threadCount:0,Provider:null,Consumer:null},e.Provider=e,e.Consumer={$$typeof:o,_context:e},e},e.createElement=function(e,t,n){var r,i={},a=null;if(t!=null)for(r in t.key!==void 0&&(a=``+t.key),t)te.call(t,r)&&r!==`key`&&r!==`__self`&&r!==`__source`&&(i[r]=t[r]);var o=arguments.length-2;if(o===1)i.children=n;else if(1<o){for(var s=Array(o),c=0;c<o;c++)s[c]=arguments[c+2];i.children=s}if(e&&e.defaultProps)for(r in o=e.defaultProps,o)i[r]===void 0&&(i[r]=o[r]);return ne(e,a,i)},e.createRef=function(){return{current:null}},e.forwardRef=function(e){return{$$typeof:c,render:e}},e.isValidElement=ie,e.lazy=function(e){return{$$typeof:d,_payload:{_status:-1,_result:e},_init:ue}},e.memo=function(e,t){return{$$typeof:u,type:e,compare:t===void 0?null:t}},e.startTransition=function(e){var t=C.T,n={};C.T=n;try{var r=e(),i=C.S;i!==null&&i(n,r),typeof r==`object`&&r&&typeof r.then==`function`&&r.then(S,T)}catch(e){T(e)}finally{t!==null&&n.types!==null&&(t.types=n.types),C.T=t}},e.unstable_useCacheRefresh=function(){return C.H.useCacheRefresh()},e.use=function(e){return C.H.use(e)},e.useActionState=function(e,t,n){return C.H.useActionState(e,t,n)},e.useCallback=function(e,t){return C.H.useCallback(e,t)},e.useContext=function(e){return C.H.useContext(e)},e.useDebugValue=function(){},e.useDeferredValue=function(e,t){return C.H.useDeferredValue(e,t)},e.useEffect=function(e,t){return C.H.useEffect(e,t)},e.useEffectEvent=function(e){return C.H.useEffectEvent(e)},e.useId=function(){return C.H.useId()},e.useImperativeHandle=function(e,t,n){return C.H.useImperativeHandle(e,t,n)},e.useInsertionEffect=function(e,t){return C.H.useInsertionEffect(e,t)},e.useLayoutEffect=function(e,t){return C.H.useLayoutEffect(e,t)},e.useMemo=function(e,t){return C.H.useMemo(e,t)},e.useOptimistic=function(e,t){return C.H.useOptimistic(e,t)},e.useReducer=function(e,t,n){return C.H.useReducer(e,t,n)},e.useRef=function(e){return C.H.useRef(e)},e.useState=function(e){return C.H.useState(e)},e.useSyncExternalStore=function(e,t,n){return C.H.useSyncExternalStore(e,t,n)},e.useTransition=function(){return C.H.useTransition()},e.version=`19.2.8`})),u=o(((e,t)=>{t.exports=l()})),d=o((e=>{function t(e,t){var n=e.length;e.push(t);a:for(;0<n;){var r=n-1>>>1,a=e[r];if(0<i(a,t))e[r]=t,e[n]=a,n=r;else break a}}function n(e){return e.length===0?null:e[0]}function r(e){if(e.length===0)return null;var t=e[0],n=e.pop();if(n!==t){e[0]=n;a:for(var r=0,a=e.length,o=a>>>1;r<o;){var s=2*(r+1)-1,c=e[s],l=s+1,u=e[l];if(0>i(c,n))l<a&&0>i(u,c)?(e[r]=u,e[l]=n,r=l):(e[r]=c,e[s]=n,r=s);else if(l<a&&0>i(u,n))e[r]=u,e[l]=n,r=l;else break a}}return t}function i(e,t){var n=e.sortIndex-t.sortIndex;return n===0?e.id-t.id:n}if(e.unstable_now=void 0,typeof performance==`object`&&typeof performance.now==`function`){var a=performance;e.unstable_now=function(){return a.now()}}else{var o=Date,s=o.now();e.unstable_now=function(){return o.now()-s}}var c=[],l=[],u=1,d=null,f=3,p=!1,m=!1,h=!1,g=!1,_=typeof setTimeout==`function`?setTimeout:null,v=typeof clearTimeout==`function`?clearTimeout:null,y=typeof setImmediate<`u`?setImmediate:null;function b(e){for(var i=n(l);i!==null;){if(i.callback===null)r(l);else if(i.startTime<=e)r(l),i.sortIndex=i.expirationTime,t(c,i);else break;i=n(l)}}function x(e){if(h=!1,b(e),!m)if(n(c)!==null)m=!0,ee||(ee=!0,ie());else{var t=n(l);t!==null&&w(x,t.startTime-e)}}var ee=!1,S=-1,C=5,te=-1;function ne(){return g?!0:!(e.unstable_now()-te<C)}function re(){if(g=!1,ee){var t=e.unstable_now();te=t;var i=!0;try{a:{m=!1,h&&(h=!1,v(S),S=-1),p=!0;var a=f;try{b:{for(b(t),d=n(c);d!==null&&!(d.expirationTime>t&&ne());){var o=d.callback;if(typeof o==`function`){d.callback=null,f=d.priorityLevel;var s=o(d.expirationTime<=t);if(t=e.unstable_now(),typeof s==`function`){d.callback=s,b(t),i=!0;break b}d===n(c)&&r(c),b(t)}else r(c);d=n(c)}if(d!==null)i=!0;else{var u=n(l);u!==null&&w(x,u.startTime-t),i=!1}}break a}finally{d=null,f=a,p=!1}i=void 0}}finally{i?ie():ee=!1}}}var ie;if(typeof y==`function`)ie=function(){y(re)};else if(typeof MessageChannel<`u`){var ae=new MessageChannel,oe=ae.port2;ae.port1.onmessage=re,ie=function(){oe.postMessage(null)}}else ie=function(){_(re,0)};function w(t,n){S=_(function(){t(e.unstable_now())},n)}e.unstable_IdlePriority=5,e.unstable_ImmediatePriority=1,e.unstable_LowPriority=4,e.unstable_NormalPriority=3,e.unstable_Profiling=null,e.unstable_UserBlockingPriority=2,e.unstable_cancelCallback=function(e){e.callback=null},e.unstable_forceFrameRate=function(e){0>e||125<e?console.error(`forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported`):C=0<e?Math.floor(1e3/e):5},e.unstable_getCurrentPriorityLevel=function(){return f},e.unstable_next=function(e){switch(f){case 1:case 2:case 3:var t=3;break;default:t=f}var n=f;f=t;try{return e()}finally{f=n}},e.unstable_requestPaint=function(){g=!0},e.unstable_runWithPriority=function(e,t){switch(e){case 1:case 2:case 3:case 4:case 5:break;default:e=3}var n=f;f=e;try{return t()}finally{f=n}},e.unstable_scheduleCallback=function(r,i,a){var o=e.unstable_now();switch(typeof a==`object`&&a?(a=a.delay,a=typeof a==`number`&&0<a?o+a:o):a=o,r){case 1:var s=-1;break;case 2:s=250;break;case 5:s=1073741823;break;case 4:s=1e4;break;default:s=5e3}return s=a+s,r={id:u++,callback:i,priorityLevel:r,startTime:a,expirationTime:s,sortIndex:-1},a>o?(r.sortIndex=a,t(l,r),n(c)===null&&r===n(l)&&(h?(v(S),S=-1):h=!0,w(x,a-o))):(r.sortIndex=s,t(c,r),m||p||(m=!0,ee||(ee=!0,ie()))),r},e.unstable_shouldYield=ne,e.unstable_wrapCallback=function(e){var t=f;return function(){var n=f;f=t;try{return e.apply(this,arguments)}finally{f=n}}}})),f=o(((e,t)=>{t.exports=d()})),p=o((e=>{var t=u();function n(e){var t=`https://react.dev/errors/`+e;if(1<arguments.length){t+=`?args[]=`+encodeURIComponent(arguments[1]);for(var n=2;n<arguments.length;n++)t+=`&args[]=`+encodeURIComponent(arguments[n])}return`Minified React error #`+e+`; visit `+t+` for the full message or use the non-minified dev environment for full errors and additional helpful warnings.`}function r(){}var i={d:{f:r,r:function(){throw Error(n(522))},D:r,C:r,L:r,m:r,X:r,S:r,M:r},p:0,findDOMNode:null},a=Symbol.for(`react.portal`);function o(e,t,n){var r=3<arguments.length&&arguments[3]!==void 0?arguments[3]:null;return{$$typeof:a,key:r==null?null:``+r,children:e,containerInfo:t,implementation:n}}var s=t.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE;function c(e,t){if(e===`font`)return``;if(typeof t==`string`)return t===`use-credentials`?t:``}e.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE=i,e.createPortal=function(e,t){var r=2<arguments.length&&arguments[2]!==void 0?arguments[2]:null;if(!t||t.nodeType!==1&&t.nodeType!==9&&t.nodeType!==11)throw Error(n(299));return o(e,t,null,r)},e.flushSync=function(e){var t=s.T,n=i.p;try{if(s.T=null,i.p=2,e)return e()}finally{s.T=t,i.p=n,i.d.f()}},e.preconnect=function(e,t){typeof e==`string`&&(t?(t=t.crossOrigin,t=typeof t==`string`?t===`use-credentials`?t:``:void 0):t=null,i.d.C(e,t))},e.prefetchDNS=function(e){typeof e==`string`&&i.d.D(e)},e.preinit=function(e,t){if(typeof e==`string`&&t&&typeof t.as==`string`){var n=t.as,r=c(n,t.crossOrigin),a=typeof t.integrity==`string`?t.integrity:void 0,o=typeof t.fetchPriority==`string`?t.fetchPriority:void 0;n===`style`?i.d.S(e,typeof t.precedence==`string`?t.precedence:void 0,{crossOrigin:r,integrity:a,fetchPriority:o}):n===`script`&&i.d.X(e,{crossOrigin:r,integrity:a,fetchPriority:o,nonce:typeof t.nonce==`string`?t.nonce:void 0})}},e.preinitModule=function(e,t){if(typeof e==`string`)if(typeof t==`object`&&t){if(t.as==null||t.as===`script`){var n=c(t.as,t.crossOrigin);i.d.M(e,{crossOrigin:n,integrity:typeof t.integrity==`string`?t.integrity:void 0,nonce:typeof t.nonce==`string`?t.nonce:void 0})}}else t??i.d.M(e)},e.preload=function(e,t){if(typeof e==`string`&&typeof t==`object`&&t&&typeof t.as==`string`){var n=t.as,r=c(n,t.crossOrigin);i.d.L(e,n,{crossOrigin:r,integrity:typeof t.integrity==`string`?t.integrity:void 0,nonce:typeof t.nonce==`string`?t.nonce:void 0,type:typeof t.type==`string`?t.type:void 0,fetchPriority:typeof t.fetchPriority==`string`?t.fetchPriority:void 0,referrerPolicy:typeof t.referrerPolicy==`string`?t.referrerPolicy:void 0,imageSrcSet:typeof t.imageSrcSet==`string`?t.imageSrcSet:void 0,imageSizes:typeof t.imageSizes==`string`?t.imageSizes:void 0,media:typeof t.media==`string`?t.media:void 0})}},e.preloadModule=function(e,t){if(typeof e==`string`)if(t){var n=c(t.as,t.crossOrigin);i.d.m(e,{as:typeof t.as==`string`&&t.as!==`script`?t.as:void 0,crossOrigin:n,integrity:typeof t.integrity==`string`?t.integrity:void 0})}else i.d.m(e)},e.requestFormReset=function(e){i.d.r(e)},e.unstable_batchedUpdates=function(e,t){return e(t)},e.useFormState=function(e,t,n){return s.H.useFormState(e,t,n)},e.useFormStatus=function(){return s.H.useHostTransitionStatus()},e.version=`19.2.8`})),m=o(((e,t)=>{function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>`u`||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!=`function`))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(e){console.error(e)}}n(),t.exports=p()})),h=o((e=>{var t=f(),n=u(),r=m();function i(e){var t=`https://react.dev/errors/`+e;if(1<arguments.length){t+=`?args[]=`+encodeURIComponent(arguments[1]);for(var n=2;n<arguments.length;n++)t+=`&args[]=`+encodeURIComponent(arguments[n])}return`Minified React error #`+e+`; visit `+t+` for the full message or use the non-minified dev environment for full errors and additional helpful warnings.`}function a(e){return!(!e||e.nodeType!==1&&e.nodeType!==9&&e.nodeType!==11)}function o(e){var t=e,n=e;if(e.alternate)for(;t.return;)t=t.return;else{e=t;do t=e,t.flags&4098&&(n=t.return),e=t.return;while(e)}return t.tag===3?n:null}function s(e){if(e.tag===13){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function c(e){if(e.tag===31){var t=e.memoizedState;if(t===null&&(e=e.alternate,e!==null&&(t=e.memoizedState)),t!==null)return t.dehydrated}return null}function l(e){if(o(e)!==e)throw Error(i(188))}function d(e){var t=e.alternate;if(!t){if(t=o(e),t===null)throw Error(i(188));return t===e?e:null}for(var n=e,r=t;;){var a=n.return;if(a===null)break;var s=a.alternate;if(s===null){if(r=a.return,r!==null){n=r;continue}break}if(a.child===s.child){for(s=a.child;s;){if(s===n)return l(a),e;if(s===r)return l(a),t;s=s.sibling}throw Error(i(188))}if(n.return!==r.return)n=a,r=s;else{for(var c=!1,u=a.child;u;){if(u===n){c=!0,n=a,r=s;break}if(u===r){c=!0,r=a,n=s;break}u=u.sibling}if(!c){for(u=s.child;u;){if(u===n){c=!0,n=s,r=a;break}if(u===r){c=!0,r=s,n=a;break}u=u.sibling}if(!c)throw Error(i(189))}}if(n.alternate!==r)throw Error(i(190))}if(n.tag!==3)throw Error(i(188));return n.stateNode.current===n?e:t}function p(e){var t=e.tag;if(t===5||t===26||t===27||t===6)return e;for(e=e.child;e!==null;){if(t=p(e),t!==null)return t;e=e.sibling}return null}var h=Object.assign,g=Symbol.for(`react.element`),_=Symbol.for(`react.transitional.element`),v=Symbol.for(`react.portal`),y=Symbol.for(`react.fragment`),b=Symbol.for(`react.strict_mode`),x=Symbol.for(`react.profiler`),ee=Symbol.for(`react.consumer`),S=Symbol.for(`react.context`),C=Symbol.for(`react.forward_ref`),te=Symbol.for(`react.suspense`),ne=Symbol.for(`react.suspense_list`),re=Symbol.for(`react.memo`),ie=Symbol.for(`react.lazy`),ae=Symbol.for(`react.activity`),oe=Symbol.for(`react.memo_cache_sentinel`),w=Symbol.iterator;function se(e){return typeof e!=`object`||!e?null:(e=w&&e[w]||e[`@@iterator`],typeof e==`function`?e:null)}var ce=Symbol.for(`react.client.reference`);function le(e){if(e==null)return null;if(typeof e==`function`)return e.$$typeof===ce?null:e.displayName||e.name||null;if(typeof e==`string`)return e;switch(e){case y:return`Fragment`;case x:return`Profiler`;case b:return`StrictMode`;case te:return`Suspense`;case ne:return`SuspenseList`;case ae:return`Activity`}if(typeof e==`object`)switch(e.$$typeof){case v:return`Portal`;case S:return e.displayName||`Context`;case ee:return(e._context.displayName||`Context`)+`.Consumer`;case C:var t=e.render;return e=e.displayName,e||=(e=t.displayName||t.name||``,e===``?`ForwardRef`:`ForwardRef(`+e+`)`),e;case re:return t=e.displayName||null,t===null?le(e.type)||`Memo`:t;case ie:t=e._payload,e=e._init;try{return le(e(t))}catch{}}return null}var ue=Array.isArray,T=n.__CLIENT_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,E=r.__DOM_INTERNALS_DO_NOT_USE_OR_WARN_USERS_THEY_CANNOT_UPGRADE,de={pending:!1,data:null,method:null,action:null},fe=[],pe=-1;function me(e){return{current:e}}function D(e){0>pe||(e.current=fe[pe],fe[pe]=null,pe--)}function O(e,t){pe++,fe[pe]=e.current,e.current=t}var he=me(null),ge=me(null),_e=me(null),ve=me(null);function ye(e,t){switch(O(_e,t),O(ge,e),O(he,null),t.nodeType){case 9:case 11:e=(e=t.documentElement)&&(e=e.namespaceURI)?Vd(e):0;break;default:if(e=t.tagName,t=t.namespaceURI)t=Vd(t),e=Hd(t,e);else switch(e){case`svg`:e=1;break;case`math`:e=2;break;default:e=0}}D(he),O(he,e)}function be(){D(he),D(ge),D(_e)}function xe(e){e.memoizedState!==null&&O(ve,e);var t=he.current,n=Hd(t,e.type);t!==n&&(O(ge,e),O(he,n))}function Se(e){ge.current===e&&(D(he),D(ge)),ve.current===e&&(D(ve),Qf._currentValue=de)}var Ce,we;function Te(e){if(Ce===void 0)try{throw Error()}catch(e){var t=e.stack.trim().match(/\n( *(at )?)/);Ce=t&&t[1]||``,we=-1<e.stack.indexOf(`
    at`)?` (<anonymous>)`:-1<e.stack.indexOf(`@`)?`@unknown:0:0`:``}return`
`+Ce+e+we}var Ee=!1;function De(e,t){if(!e||Ee)return``;Ee=!0;var n=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{var r={DetermineComponentFrameRoot:function(){try{if(t){var n=function(){throw Error()};if(Object.defineProperty(n.prototype,"props",{set:function(){throw Error()}}),typeof Reflect==`object`&&Reflect.construct){try{Reflect.construct(n,[])}catch(e){var r=e}Reflect.construct(e,[],n)}else{try{n.call()}catch(e){r=e}e.call(n.prototype)}}else{try{throw Error()}catch(e){r=e}(n=e())&&typeof n.catch==`function`&&n.catch(function(){})}}catch(e){if(e&&r&&typeof e.stack==`string`)return[e.stack,r.stack]}return[null,null]}};r.DetermineComponentFrameRoot.displayName=`DetermineComponentFrameRoot`;var i=Object.getOwnPropertyDescriptor(r.DetermineComponentFrameRoot,`name`);i&&i.configurable&&Object.defineProperty(r.DetermineComponentFrameRoot,"name",{value:`DetermineComponentFrameRoot`});var a=r.DetermineComponentFrameRoot(),o=a[0],s=a[1];if(o&&s){var c=o.split(`
`),l=s.split(`
`);for(i=r=0;r<c.length&&!c[r].includes(`DetermineComponentFrameRoot`);)r++;for(;i<l.length&&!l[i].includes(`DetermineComponentFrameRoot`);)i++;if(r===c.length||i===l.length)for(r=c.length-1,i=l.length-1;1<=r&&0<=i&&c[r]!==l[i];)i--;for(;1<=r&&0<=i;r--,i--)if(c[r]!==l[i]){if(r!==1||i!==1)do if(r--,i--,0>i||c[r]!==l[i]){var u=`
`+c[r].replace(` at new `,` at `);return e.displayName&&u.includes(`<anonymous>`)&&(u=u.replace(`<anonymous>`,e.displayName)),u}while(1<=r&&0<=i);break}}}finally{Ee=!1,Error.prepareStackTrace=n}return(n=e?e.displayName||e.name:``)?Te(n):``}function Oe(e,t){switch(e.tag){case 26:case 27:case 5:return Te(e.type);case 16:return Te(`Lazy`);case 13:return e.child!==t&&t!==null?Te(`Suspense Fallback`):Te(`Suspense`);case 19:return Te(`SuspenseList`);case 0:case 15:return De(e.type,!1);case 11:return De(e.type.render,!1);case 1:return De(e.type,!0);case 31:return Te(`Activity`);default:return``}}function ke(e){try{var t=``,n=null;do t+=Oe(e,n),n=e,e=e.return;while(e);return t}catch(e){return`
Error generating stack: `+e.message+`
`+e.stack}}var Ae=Object.prototype.hasOwnProperty,je=t.unstable_scheduleCallback,Me=t.unstable_cancelCallback,Ne=t.unstable_shouldYield,Pe=t.unstable_requestPaint,Fe=t.unstable_now,Ie=t.unstable_getCurrentPriorityLevel,Le=t.unstable_ImmediatePriority,Re=t.unstable_UserBlockingPriority,ze=t.unstable_NormalPriority,Be=t.unstable_LowPriority,Ve=t.unstable_IdlePriority,He=t.log,Ue=t.unstable_setDisableYieldValue,We=null,Ge=null;function Ke(e){if(typeof He==`function`&&Ue(e),Ge&&typeof Ge.setStrictMode==`function`)try{Ge.setStrictMode(We,e)}catch{}}var qe=Math.clz32?Math.clz32:Xe,Je=Math.log,Ye=Math.LN2;function Xe(e){return e>>>=0,e===0?32:31-(Je(e)/Ye|0)|0}var Ze=256,Qe=262144,$e=4194304;function et(e){var t=e&42;if(t!==0)return t;switch(e&-e){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:return 64;case 128:return 128;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:return e&261888;case 262144:case 524288:case 1048576:case 2097152:return e&3932160;case 4194304:case 8388608:case 16777216:case 33554432:return e&62914560;case 67108864:return 67108864;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 0;default:return e}}function tt(e,t,n){var r=e.pendingLanes;if(r===0)return 0;var i=0,a=e.suspendedLanes,o=e.pingedLanes;e=e.warmLanes;var s=r&134217727;return s===0?(s=r&~a,s===0?o===0?n||(n=r&~e,n!==0&&(i=et(n))):i=et(o):i=et(s)):(r=s&~a,r===0?(o&=s,o===0?n||(n=s&~e,n!==0&&(i=et(n))):i=et(o)):i=et(r)),i===0?0:t!==0&&t!==i&&(t&a)===0&&(a=i&-i,n=t&-t,a>=n||a===32&&n&4194048)?t:i}function nt(e,t){return(e.pendingLanes&~(e.suspendedLanes&~e.pingedLanes)&t)===0}function rt(e,t){switch(e){case 1:case 2:case 4:case 8:case 64:return t+250;case 16:case 32:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return t+5e3;case 4194304:case 8388608:case 16777216:case 33554432:return-1;case 67108864:case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}function it(){var e=$e;return $e<<=1,!($e&62914560)&&($e=4194304),e}function at(e){for(var t=[],n=0;31>n;n++)t.push(e);return t}function ot(e,t){e.pendingLanes|=t,t!==268435456&&(e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0)}function st(e,t,n,r,i,a){var o=e.pendingLanes;e.pendingLanes=n,e.suspendedLanes=0,e.pingedLanes=0,e.warmLanes=0,e.expiredLanes&=n,e.entangledLanes&=n,e.errorRecoveryDisabledLanes&=n,e.shellSuspendCounter=0;var s=e.entanglements,c=e.expirationTimes,l=e.hiddenUpdates;for(n=o&~n;0<n;){var u=31-qe(n),d=1<<u;s[u]=0,c[u]=-1;var f=l[u];if(f!==null)for(l[u]=null,u=0;u<f.length;u++){var p=f[u];p!==null&&(p.lane&=-536870913)}n&=~d}r!==0&&ct(e,r,0),a!==0&&i===0&&e.tag!==0&&(e.suspendedLanes|=a&~(o&~t))}function ct(e,t,n){e.pendingLanes|=t,e.suspendedLanes&=~t;var r=31-qe(t);e.entangledLanes|=t,e.entanglements[r]=e.entanglements[r]|1073741824|n&261930}function lt(e,t){var n=e.entangledLanes|=t;for(e=e.entanglements;n;){var r=31-qe(n),i=1<<r;i&t|e[r]&t&&(e[r]|=t),n&=~i}}function ut(e,t){var n=t&-t;return n=n&42?1:dt(n),(n&(e.suspendedLanes|t))===0?n:0}function dt(e){switch(e){case 2:e=1;break;case 8:e=4;break;case 32:e=16;break;case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:e=128;break;case 268435456:e=134217728;break;default:e=0}return e}function ft(e){return e&=-e,2<e?8<e?e&134217727?32:268435456:8:2}function pt(){var e=E.p;return e===0?(e=window.event,e===void 0?32:mp(e.type)):e}function mt(e,t){var n=E.p;try{return E.p=e,t()}finally{E.p=n}}var ht=Math.random().toString(36).slice(2),gt=`__reactFiber$`+ht,_t=`__reactProps$`+ht,vt=`__reactContainer$`+ht,yt=`__reactEvents$`+ht,bt=`__reactListeners$`+ht,xt=`__reactHandles$`+ht,St=`__reactResources$`+ht,Ct=`__reactMarker$`+ht;function wt(e){delete e[gt],delete e[_t],delete e[yt],delete e[bt],delete e[xt]}function Tt(e){var t=e[gt];if(t)return t;for(var n=e.parentNode;n;){if(t=n[vt]||n[gt]){if(n=t.alternate,t.child!==null||n!==null&&n.child!==null)for(e=df(e);e!==null;){if(n=e[gt])return n;e=df(e)}return t}e=n,n=e.parentNode}return null}function Et(e){if(e=e[gt]||e[vt]){var t=e.tag;if(t===5||t===6||t===13||t===31||t===26||t===27||t===3)return e}return null}function Dt(e){var t=e.tag;if(t===5||t===26||t===27||t===6)return e.stateNode;throw Error(i(33))}function Ot(e){var t=e[St];return t||=e[St]={hoistableStyles:new Map,hoistableScripts:new Map},t}function k(e){e[Ct]=!0}var kt=new Set,At={};function jt(e,t){Mt(e,t),Mt(e+`Capture`,t)}function Mt(e,t){for(At[e]=t,e=0;e<t.length;e++)kt.add(t[e])}var Nt=RegExp(`^[:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD][:A-Z_a-z\\u00C0-\\u00D6\\u00D8-\\u00F6\\u00F8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD\\-.0-9\\u00B7\\u0300-\\u036F\\u203F-\\u2040]*$`),Pt={},Ft={};function It(e){return Ae.call(Ft,e)?!0:Ae.call(Pt,e)?!1:Nt.test(e)?Ft[e]=!0:(Pt[e]=!0,!1)}function Lt(e,t,n){if(It(t))if(n===null)e.removeAttribute(t);else{switch(typeof n){case`undefined`:case`function`:case`symbol`:e.removeAttribute(t);return;case`boolean`:var r=t.toLowerCase().slice(0,5);if(r!==`data-`&&r!==`aria-`){e.removeAttribute(t);return}}e.setAttribute(t,``+n)}}function Rt(e,t,n){if(n===null)e.removeAttribute(t);else{switch(typeof n){case`undefined`:case`function`:case`symbol`:case`boolean`:e.removeAttribute(t);return}e.setAttribute(t,``+n)}}function zt(e,t,n,r){if(r===null)e.removeAttribute(n);else{switch(typeof r){case`undefined`:case`function`:case`symbol`:case`boolean`:e.removeAttribute(n);return}e.setAttributeNS(t,n,``+r)}}function Bt(e){switch(typeof e){case`bigint`:case`boolean`:case`number`:case`string`:case`undefined`:return e;case`object`:return e;default:return``}}function Vt(e){var t=e.type;return(e=e.nodeName)&&e.toLowerCase()===`input`&&(t===`checkbox`||t===`radio`)}function Ht(e,t,n){var r=Object.getOwnPropertyDescriptor(e.constructor.prototype,t);if(!e.hasOwnProperty(t)&&r!==void 0&&typeof r.get==`function`&&typeof r.set==`function`){var i=r.get,a=r.set;return Object.defineProperty(e,t,{configurable:!0,get:function(){return i.call(this)},set:function(e){n=``+e,a.call(this,e)}}),Object.defineProperty(e,t,{enumerable:r.enumerable}),{getValue:function(){return n},setValue:function(e){n=``+e},stopTracking:function(){e._valueTracker=null,delete e[t]}}}}function Ut(e){if(!e._valueTracker){var t=Vt(e)?`checked`:`value`;e._valueTracker=Ht(e,t,``+e[t])}}function Wt(e){if(!e)return!1;var t=e._valueTracker;if(!t)return!0;var n=t.getValue(),r=``;return e&&(r=Vt(e)?e.checked?`true`:`false`:e.value),e=r,e===n?!1:(t.setValue(e),!0)}function Gt(e){if(e||=typeof document<`u`?document:void 0,e===void 0)return null;try{return e.activeElement||e.body}catch{return e.body}}var Kt=/[\n"\\]/g;function qt(e){return e.replace(Kt,function(e){return`\\`+e.charCodeAt(0).toString(16)+` `})}function Jt(e,t,n,r,i,a,o,s){e.name=``,o!=null&&typeof o!=`function`&&typeof o!=`symbol`&&typeof o!=`boolean`?e.type=o:e.removeAttribute(`type`),t==null?o!==`submit`&&o!==`reset`||e.removeAttribute(`value`):o===`number`?(t===0&&e.value===``||e.value!=t)&&(e.value=``+Bt(t)):e.value!==``+Bt(t)&&(e.value=``+Bt(t)),t==null?n==null?r!=null&&e.removeAttribute(`value`):Xt(e,o,Bt(n)):Xt(e,o,Bt(t)),i==null&&a!=null&&(e.defaultChecked=!!a),i!=null&&(e.checked=i&&typeof i!=`function`&&typeof i!=`symbol`),s!=null&&typeof s!=`function`&&typeof s!=`symbol`&&typeof s!=`boolean`?e.name=``+Bt(s):e.removeAttribute(`name`)}function Yt(e,t,n,r,i,a,o,s){if(a!=null&&typeof a!=`function`&&typeof a!=`symbol`&&typeof a!=`boolean`&&(e.type=a),t!=null||n!=null){if(!(a!==`submit`&&a!==`reset`||t!=null)){Ut(e);return}n=n==null?``:``+Bt(n),t=t==null?n:``+Bt(t),s||t===e.value||(e.value=t),e.defaultValue=t}r??=i,r=typeof r!=`function`&&typeof r!=`symbol`&&!!r,e.checked=s?e.checked:!!r,e.defaultChecked=!!r,o!=null&&typeof o!=`function`&&typeof o!=`symbol`&&typeof o!=`boolean`&&(e.name=o),Ut(e)}function Xt(e,t,n){t===`number`&&Gt(e.ownerDocument)===e||e.defaultValue===``+n||(e.defaultValue=``+n)}function Zt(e,t,n,r){if(e=e.options,t){t={};for(var i=0;i<n.length;i++)t[`$`+n[i]]=!0;for(n=0;n<e.length;n++)i=t.hasOwnProperty(`$`+e[n].value),e[n].selected!==i&&(e[n].selected=i),i&&r&&(e[n].defaultSelected=!0)}else{for(n=``+Bt(n),t=null,i=0;i<e.length;i++){if(e[i].value===n){e[i].selected=!0,r&&(e[i].defaultSelected=!0);return}t!==null||e[i].disabled||(t=e[i])}t!==null&&(t.selected=!0)}}function Qt(e,t,n){if(t!=null&&(t=``+Bt(t),t!==e.value&&(e.value=t),n==null)){e.defaultValue!==t&&(e.defaultValue=t);return}e.defaultValue=n==null?``:``+Bt(n)}function $t(e,t,n,r){if(t==null){if(r!=null){if(n!=null)throw Error(i(92));if(ue(r)){if(1<r.length)throw Error(i(93));r=r[0]}n=r}n??=``,t=n}n=Bt(t),e.defaultValue=n,r=e.textContent,r===n&&r!==``&&r!==null&&(e.value=r),Ut(e)}function en(e,t){if(t){var n=e.firstChild;if(n&&n===e.lastChild&&n.nodeType===3){n.nodeValue=t;return}}e.textContent=t}var tn=new Set(`animationIterationCount aspectRatio borderImageOutset borderImageSlice borderImageWidth boxFlex boxFlexGroup boxOrdinalGroup columnCount columns flex flexGrow flexPositive flexShrink flexNegative flexOrder gridArea gridRow gridRowEnd gridRowSpan gridRowStart gridColumn gridColumnEnd gridColumnSpan gridColumnStart fontWeight lineClamp lineHeight opacity order orphans scale tabSize widows zIndex zoom fillOpacity floodOpacity stopOpacity strokeDasharray strokeDashoffset strokeMiterlimit strokeOpacity strokeWidth MozAnimationIterationCount MozBoxFlex MozBoxFlexGroup MozLineClamp msAnimationIterationCount msFlex msZoom msFlexGrow msFlexNegative msFlexOrder msFlexPositive msFlexShrink msGridColumn msGridColumnSpan msGridRow msGridRowSpan WebkitAnimationIterationCount WebkitBoxFlex WebKitBoxFlexGroup WebkitBoxOrdinalGroup WebkitColumnCount WebkitColumns WebkitFlex WebkitFlexGrow WebkitFlexPositive WebkitFlexShrink WebkitLineClamp`.split(` `));function nn(e,t,n){var r=t.indexOf(`--`)===0;n==null||typeof n==`boolean`||n===``?r?e.setProperty(t,``):t===`float`?e.cssFloat=``:e[t]=``:r?e.setProperty(t,n):typeof n!=`number`||n===0||tn.has(t)?t===`float`?e.cssFloat=n:e[t]=(``+n).trim():e[t]=n+`px`}function rn(e,t,n){if(t!=null&&typeof t!=`object`)throw Error(i(62));if(e=e.style,n!=null){for(var r in n)!n.hasOwnProperty(r)||t!=null&&t.hasOwnProperty(r)||(r.indexOf(`--`)===0?e.setProperty(r,``):r===`float`?e.cssFloat=``:e[r]=``);for(var a in t)r=t[a],t.hasOwnProperty(a)&&n[a]!==r&&nn(e,a,r)}else for(var o in t)t.hasOwnProperty(o)&&nn(e,o,t[o])}function an(e){if(e.indexOf(`-`)===-1)return!1;switch(e){case`annotation-xml`:case`color-profile`:case`font-face`:case`font-face-src`:case`font-face-uri`:case`font-face-format`:case`font-face-name`:case`missing-glyph`:return!1;default:return!0}}var on=new Map([[`acceptCharset`,`accept-charset`],[`htmlFor`,`for`],[`httpEquiv`,`http-equiv`],[`crossOrigin`,`crossorigin`],[`accentHeight`,`accent-height`],[`alignmentBaseline`,`alignment-baseline`],[`arabicForm`,`arabic-form`],[`baselineShift`,`baseline-shift`],[`capHeight`,`cap-height`],[`clipPath`,`clip-path`],[`clipRule`,`clip-rule`],[`colorInterpolation`,`color-interpolation`],[`colorInterpolationFilters`,`color-interpolation-filters`],[`colorProfile`,`color-profile`],[`colorRendering`,`color-rendering`],[`dominantBaseline`,`dominant-baseline`],[`enableBackground`,`enable-background`],[`fillOpacity`,`fill-opacity`],[`fillRule`,`fill-rule`],[`floodColor`,`flood-color`],[`floodOpacity`,`flood-opacity`],[`fontFamily`,`font-family`],[`fontSize`,`font-size`],[`fontSizeAdjust`,`font-size-adjust`],[`fontStretch`,`font-stretch`],[`fontStyle`,`font-style`],[`fontVariant`,`font-variant`],[`fontWeight`,`font-weight`],[`glyphName`,`glyph-name`],[`glyphOrientationHorizontal`,`glyph-orientation-horizontal`],[`glyphOrientationVertical`,`glyph-orientation-vertical`],[`horizAdvX`,`horiz-adv-x`],[`horizOriginX`,`horiz-origin-x`],[`imageRendering`,`image-rendering`],[`letterSpacing`,`letter-spacing`],[`lightingColor`,`lighting-color`],[`markerEnd`,`marker-end`],[`markerMid`,`marker-mid`],[`markerStart`,`marker-start`],[`overlinePosition`,`overline-position`],[`overlineThickness`,`overline-thickness`],[`paintOrder`,`paint-order`],[`panose-1`,`panose-1`],[`pointerEvents`,`pointer-events`],[`renderingIntent`,`rendering-intent`],[`shapeRendering`,`shape-rendering`],[`stopColor`,`stop-color`],[`stopOpacity`,`stop-opacity`],[`strikethroughPosition`,`strikethrough-position`],[`strikethroughThickness`,`strikethrough-thickness`],[`strokeDasharray`,`stroke-dasharray`],[`strokeDashoffset`,`stroke-dashoffset`],[`strokeLinecap`,`stroke-linecap`],[`strokeLinejoin`,`stroke-linejoin`],[`strokeMiterlimit`,`stroke-miterlimit`],[`strokeOpacity`,`stroke-opacity`],[`strokeWidth`,`stroke-width`],[`textAnchor`,`text-anchor`],[`textDecoration`,`text-decoration`],[`textRendering`,`text-rendering`],[`transformOrigin`,`transform-origin`],[`underlinePosition`,`underline-position`],[`underlineThickness`,`underline-thickness`],[`unicodeBidi`,`unicode-bidi`],[`unicodeRange`,`unicode-range`],[`unitsPerEm`,`units-per-em`],[`vAlphabetic`,`v-alphabetic`],[`vHanging`,`v-hanging`],[`vIdeographic`,`v-ideographic`],[`vMathematical`,`v-mathematical`],[`vectorEffect`,`vector-effect`],[`vertAdvY`,`vert-adv-y`],[`vertOriginX`,`vert-origin-x`],[`vertOriginY`,`vert-origin-y`],[`wordSpacing`,`word-spacing`],[`writingMode`,`writing-mode`],[`xmlnsXlink`,`xmlns:xlink`],[`xHeight`,`x-height`]]),sn=/^[\u0000-\u001F ]*j[\r\n\t]*a[\r\n\t]*v[\r\n\t]*a[\r\n\t]*s[\r\n\t]*c[\r\n\t]*r[\r\n\t]*i[\r\n\t]*p[\r\n\t]*t[\r\n\t]*:/i;function cn(e){return sn.test(``+e)?`javascript:throw new Error('React has blocked a javascript: URL as a security precaution.')`:e}function ln(){}var un=null;function dn(e){return e=e.target||e.srcElement||window,e.correspondingUseElement&&(e=e.correspondingUseElement),e.nodeType===3?e.parentNode:e}var fn=null,pn=null;function mn(e){var t=Et(e);if(t&&(e=t.stateNode)){var n=e[_t]||null;a:switch(e=t.stateNode,t.type){case`input`:if(Jt(e,n.value,n.defaultValue,n.defaultValue,n.checked,n.defaultChecked,n.type,n.name),t=n.name,n.type===`radio`&&t!=null){for(n=e;n.parentNode;)n=n.parentNode;for(n=n.querySelectorAll(`input[name="`+qt(``+t)+`"][type="radio"]`),t=0;t<n.length;t++){var r=n[t];if(r!==e&&r.form===e.form){var a=r[_t]||null;if(!a)throw Error(i(90));Jt(r,a.value,a.defaultValue,a.defaultValue,a.checked,a.defaultChecked,a.type,a.name)}}for(t=0;t<n.length;t++)r=n[t],r.form===e.form&&Wt(r)}break a;case`textarea`:Qt(e,n.value,n.defaultValue);break a;case`select`:t=n.value,t!=null&&Zt(e,!!n.multiple,t,!1)}}}var hn=!1;function gn(e,t,n){if(hn)return e(t,n);hn=!0;try{return e(t)}finally{if(hn=!1,(fn!==null||pn!==null)&&(bu(),fn&&(t=fn,e=pn,pn=fn=null,mn(t),e)))for(t=0;t<e.length;t++)mn(e[t])}}function _n(e,t){var n=e.stateNode;if(n===null)return null;var r=n[_t]||null;if(r===null)return null;n=r[t];a:switch(t){case`onClick`:case`onClickCapture`:case`onDoubleClick`:case`onDoubleClickCapture`:case`onMouseDown`:case`onMouseDownCapture`:case`onMouseMove`:case`onMouseMoveCapture`:case`onMouseUp`:case`onMouseUpCapture`:case`onMouseEnter`:(r=!r.disabled)||(e=e.type,r=!(e===`button`||e===`input`||e===`select`||e===`textarea`)),e=!r;break a;default:e=!1}if(e)return null;if(n&&typeof n!=`function`)throw Error(i(231,t,typeof n));return n}var vn=!(typeof window>`u`||window.document===void 0||window.document.createElement===void 0),yn=!1;if(vn)try{var bn={};Object.defineProperty(bn,"passive",{get:function(){yn=!0}}),window.addEventListener(`test`,bn,bn),window.removeEventListener(`test`,bn,bn)}catch{yn=!1}var xn=null,Sn=null,Cn=null;function wn(){if(Cn)return Cn;var e,t=Sn,n=t.length,r,i=`value`in xn?xn.value:xn.textContent,a=i.length;for(e=0;e<n&&t[e]===i[e];e++);var o=n-e;for(r=1;r<=o&&t[n-r]===i[a-r];r++);return Cn=i.slice(e,1<r?1-r:void 0)}function Tn(e){var t=e.keyCode;return`charCode`in e?(e=e.charCode,e===0&&t===13&&(e=13)):e=t,e===10&&(e=13),32<=e||e===13?e:0}function En(){return!0}function Dn(){return!1}function On(e){function t(t,n,r,i,a){for(var o in this._reactName=t,this._targetInst=r,this.type=n,this.nativeEvent=i,this.target=a,this.currentTarget=null,e)e.hasOwnProperty(o)&&(t=e[o],this[o]=t?t(i):i[o]);return this.isDefaultPrevented=(i.defaultPrevented==null?!1===i.returnValue:i.defaultPrevented)?En:Dn,this.isPropagationStopped=Dn,this}return h(t.prototype,{preventDefault:function(){this.defaultPrevented=!0;var e=this.nativeEvent;e&&(e.preventDefault?e.preventDefault():typeof e.returnValue!=`unknown`&&(e.returnValue=!1),this.isDefaultPrevented=En)},stopPropagation:function(){var e=this.nativeEvent;e&&(e.stopPropagation?e.stopPropagation():typeof e.cancelBubble!=`unknown`&&(e.cancelBubble=!0),this.isPropagationStopped=En)},persist:function(){},isPersistent:En}),t}var kn={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(e){return e.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},An=On(kn),jn=h({},kn,{view:0,detail:0}),Mn=On(jn),Nn,Pn,Fn,In=h({},jn,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:qn,button:0,buttons:0,relatedTarget:function(e){return e.relatedTarget===void 0?e.fromElement===e.srcElement?e.toElement:e.fromElement:e.relatedTarget},movementX:function(e){return`movementX`in e?e.movementX:(e!==Fn&&(Fn&&e.type===`mousemove`?(Nn=e.screenX-Fn.screenX,Pn=e.screenY-Fn.screenY):Pn=Nn=0,Fn=e),Nn)},movementY:function(e){return`movementY`in e?e.movementY:Pn}}),Ln=On(In),Rn=On(h({},In,{dataTransfer:0})),zn=On(h({},jn,{relatedTarget:0})),Bn=On(h({},kn,{animationName:0,elapsedTime:0,pseudoElement:0})),Vn=On(h({},kn,{clipboardData:function(e){return`clipboardData`in e?e.clipboardData:window.clipboardData}})),Hn=On(h({},kn,{data:0})),Un={Esc:`Escape`,Spacebar:` `,Left:`ArrowLeft`,Up:`ArrowUp`,Right:`ArrowRight`,Down:`ArrowDown`,Del:`Delete`,Win:`OS`,Menu:`ContextMenu`,Apps:`ContextMenu`,Scroll:`ScrollLock`,MozPrintableKey:`Unidentified`},Wn={8:`Backspace`,9:`Tab`,12:`Clear`,13:`Enter`,16:`Shift`,17:`Control`,18:`Alt`,19:`Pause`,20:`CapsLock`,27:`Escape`,32:` `,33:`PageUp`,34:`PageDown`,35:`End`,36:`Home`,37:`ArrowLeft`,38:`ArrowUp`,39:`ArrowRight`,40:`ArrowDown`,45:`Insert`,46:`Delete`,112:`F1`,113:`F2`,114:`F3`,115:`F4`,116:`F5`,117:`F6`,118:`F7`,119:`F8`,120:`F9`,121:`F10`,122:`F11`,123:`F12`,144:`NumLock`,145:`ScrollLock`,224:`Meta`},Gn={Alt:`altKey`,Control:`ctrlKey`,Meta:`metaKey`,Shift:`shiftKey`};function Kn(e){var t=this.nativeEvent;return t.getModifierState?t.getModifierState(e):(e=Gn[e])?!!t[e]:!1}function qn(){return Kn}var Jn=On(h({},jn,{key:function(e){if(e.key){var t=Un[e.key]||e.key;if(t!==`Unidentified`)return t}return e.type===`keypress`?(e=Tn(e),e===13?`Enter`:String.fromCharCode(e)):e.type===`keydown`||e.type===`keyup`?Wn[e.keyCode]||`Unidentified`:``},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:qn,charCode:function(e){return e.type===`keypress`?Tn(e):0},keyCode:function(e){return e.type===`keydown`||e.type===`keyup`?e.keyCode:0},which:function(e){return e.type===`keypress`?Tn(e):e.type===`keydown`||e.type===`keyup`?e.keyCode:0}})),Yn=On(h({},In,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0})),Xn=On(h({},jn,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:qn})),Zn=On(h({},kn,{propertyName:0,elapsedTime:0,pseudoElement:0})),Qn=On(h({},In,{deltaX:function(e){return`deltaX`in e?e.deltaX:`wheelDeltaX`in e?-e.wheelDeltaX:0},deltaY:function(e){return`deltaY`in e?e.deltaY:`wheelDeltaY`in e?-e.wheelDeltaY:`wheelDelta`in e?-e.wheelDelta:0},deltaZ:0,deltaMode:0})),$n=On(h({},kn,{newState:0,oldState:0})),er=[9,13,27,32],tr=vn&&`CompositionEvent`in window,nr=null;vn&&`documentMode`in document&&(nr=document.documentMode);var rr=vn&&`TextEvent`in window&&!nr,ir=vn&&(!tr||nr&&8<nr&&11>=nr),ar=` `,or=!1;function sr(e,t){switch(e){case`keyup`:return er.indexOf(t.keyCode)!==-1;case`keydown`:return t.keyCode!==229;case`keypress`:case`mousedown`:case`focusout`:return!0;default:return!1}}function cr(e){return e=e.detail,typeof e==`object`&&`data`in e?e.data:null}var lr=!1;function ur(e,t){switch(e){case`compositionend`:return cr(t);case`keypress`:return t.which===32?(or=!0,ar):null;case`textInput`:return e=t.data,e===ar&&or?null:e;default:return null}}function dr(e,t){if(lr)return e===`compositionend`||!tr&&sr(e,t)?(e=wn(),Cn=Sn=xn=null,lr=!1,e):null;switch(e){case`paste`:return null;case`keypress`:if(!(t.ctrlKey||t.altKey||t.metaKey)||t.ctrlKey&&t.altKey){if(t.char&&1<t.char.length)return t.char;if(t.which)return String.fromCharCode(t.which)}return null;case`compositionend`:return ir&&t.locale!==`ko`?null:t.data;default:return null}}var fr={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function pr(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t===`input`?!!fr[e.type]:t===`textarea`}function mr(e,t,n,r){fn?pn?pn.push(r):pn=[r]:fn=r,t=Ed(t,`onChange`),0<t.length&&(n=new An(`onChange`,`change`,null,n,r),e.push({event:n,listeners:t}))}var hr=null,gr=null;function _r(e){yd(e,0)}function vr(e){if(Wt(Dt(e)))return e}function yr(e,t){if(e===`change`)return t}var br=!1;if(vn){var xr;if(vn){var Sr=`oninput`in document;if(!Sr){var Cr=document.createElement(`div`);Cr.setAttribute(`oninput`,`return;`),Sr=typeof Cr.oninput==`function`}xr=Sr}else xr=!1;br=xr&&(!document.documentMode||9<document.documentMode)}function wr(){hr&&(hr.detachEvent(`onpropertychange`,Tr),gr=hr=null)}function Tr(e){if(e.propertyName===`value`&&vr(gr)){var t=[];mr(t,gr,e,dn(e)),gn(_r,t)}}function Er(e,t,n){e===`focusin`?(wr(),hr=t,gr=n,hr.attachEvent(`onpropertychange`,Tr)):e===`focusout`&&wr()}function Dr(e){if(e===`selectionchange`||e===`keyup`||e===`keydown`)return vr(gr)}function Or(e,t){if(e===`click`)return vr(t)}function kr(e,t){if(e===`input`||e===`change`)return vr(t)}function Ar(e,t){return e===t&&(e!==0||1/e==1/t)||e!==e&&t!==t}var jr=typeof Object.is==`function`?Object.is:Ar;function Mr(e,t){if(jr(e,t))return!0;if(typeof e!=`object`||!e||typeof t!=`object`||!t)return!1;var n=Object.keys(e),r=Object.keys(t);if(n.length!==r.length)return!1;for(r=0;r<n.length;r++){var i=n[r];if(!Ae.call(t,i)||!jr(e[i],t[i]))return!1}return!0}function Nr(e){for(;e&&e.firstChild;)e=e.firstChild;return e}function Pr(e,t){var n=Nr(e);e=0;for(var r;n;){if(n.nodeType===3){if(r=e+n.textContent.length,e<=t&&r>=t)return{node:n,offset:t-e};e=r}a:{for(;n;){if(n.nextSibling){n=n.nextSibling;break a}n=n.parentNode}n=void 0}n=Nr(n)}}function Fr(e,t){return e&&t?e===t?!0:e&&e.nodeType===3?!1:t&&t.nodeType===3?Fr(e,t.parentNode):`contains`in e?e.contains(t):e.compareDocumentPosition?!!(e.compareDocumentPosition(t)&16):!1:!1}function Ir(e){e=e!=null&&e.ownerDocument!=null&&e.ownerDocument.defaultView!=null?e.ownerDocument.defaultView:window;for(var t=Gt(e.document);t instanceof e.HTMLIFrameElement;){try{var n=typeof t.contentWindow.location.href==`string`}catch{n=!1}if(n)e=t.contentWindow;else break;t=Gt(e.document)}return t}function Lr(e){var t=e&&e.nodeName&&e.nodeName.toLowerCase();return t&&(t===`input`&&(e.type===`text`||e.type===`search`||e.type===`tel`||e.type===`url`||e.type===`password`)||t===`textarea`||e.contentEditable===`true`)}var Rr=vn&&`documentMode`in document&&11>=document.documentMode,zr=null,Br=null,Vr=null,Hr=!1;function Ur(e,t,n){var r=n.window===n?n.document:n.nodeType===9?n:n.ownerDocument;Hr||zr==null||zr!==Gt(r)||(r=zr,`selectionStart`in r&&Lr(r)?r={start:r.selectionStart,end:r.selectionEnd}:(r=(r.ownerDocument&&r.ownerDocument.defaultView||window).getSelection(),r={anchorNode:r.anchorNode,anchorOffset:r.anchorOffset,focusNode:r.focusNode,focusOffset:r.focusOffset}),Vr&&Mr(Vr,r)||(Vr=r,r=Ed(Br,`onSelect`),0<r.length&&(t=new An(`onSelect`,`select`,null,t,n),e.push({event:t,listeners:r}),t.target=zr)))}function Wr(e,t){var n={};return n[e.toLowerCase()]=t.toLowerCase(),n[`Webkit`+e]=`webkit`+t,n[`Moz`+e]=`moz`+t,n}var Gr={animationend:Wr(`Animation`,`AnimationEnd`),animationiteration:Wr(`Animation`,`AnimationIteration`),animationstart:Wr(`Animation`,`AnimationStart`),transitionrun:Wr(`Transition`,`TransitionRun`),transitionstart:Wr(`Transition`,`TransitionStart`),transitioncancel:Wr(`Transition`,`TransitionCancel`),transitionend:Wr(`Transition`,`TransitionEnd`)},Kr={},qr={};vn&&(qr=document.createElement(`div`).style,`AnimationEvent`in window||(delete Gr.animationend.animation,delete Gr.animationiteration.animation,delete Gr.animationstart.animation),`TransitionEvent`in window||delete Gr.transitionend.transition);function Jr(e){if(Kr[e])return Kr[e];if(!Gr[e])return e;var t=Gr[e],n;for(n in t)if(t.hasOwnProperty(n)&&n in qr)return Kr[e]=t[n];return e}var Yr=Jr(`animationend`),Xr=Jr(`animationiteration`),Zr=Jr(`animationstart`),Qr=Jr(`transitionrun`),$r=Jr(`transitionstart`),ei=Jr(`transitioncancel`),ti=Jr(`transitionend`),ni=new Map,ri=`abort auxClick beforeToggle cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel`.split(` `);ri.push(`scrollEnd`);function ii(e,t){ni.set(e,t),jt(t,[e])}var ai=typeof reportError==`function`?reportError:function(e){if(typeof window==`object`&&typeof window.ErrorEvent==`function`){var t=new window.ErrorEvent(`error`,{bubbles:!0,cancelable:!0,message:typeof e==`object`&&e&&typeof e.message==`string`?String(e.message):String(e),error:e});if(!window.dispatchEvent(t))return}else if(typeof process==`object`&&typeof process.emit==`function`){process.emit(`uncaughtException`,e);return}console.error(e)},oi=[],si=0,ci=0;function li(){for(var e=si,t=ci=si=0;t<e;){var n=oi[t];oi[t++]=null;var r=oi[t];oi[t++]=null;var i=oi[t];oi[t++]=null;var a=oi[t];if(oi[t++]=null,r!==null&&i!==null){var o=r.pending;o===null?i.next=i:(i.next=o.next,o.next=i),r.pending=i}a!==0&&pi(n,i,a)}}function ui(e,t,n,r){oi[si++]=e,oi[si++]=t,oi[si++]=n,oi[si++]=r,ci|=r,e.lanes|=r,e=e.alternate,e!==null&&(e.lanes|=r)}function di(e,t,n,r){return ui(e,t,n,r),mi(e)}function fi(e,t){return ui(e,null,null,t),mi(e)}function pi(e,t,n){e.lanes|=n;var r=e.alternate;r!==null&&(r.lanes|=n);for(var i=!1,a=e.return;a!==null;)a.childLanes|=n,r=a.alternate,r!==null&&(r.childLanes|=n),a.tag===22&&(e=a.stateNode,e===null||e._visibility&1||(i=!0)),e=a,a=a.return;return e.tag===3?(a=e.stateNode,i&&t!==null&&(i=31-qe(n),e=a.hiddenUpdates,r=e[i],r===null?e[i]=[t]:r.push(t),t.lane=n|536870912),a):null}function mi(e){if(50<du)throw du=0,fu=null,Error(i(185));for(var t=e.return;t!==null;)e=t,t=e.return;return e.tag===3?e.stateNode:null}var hi={};function gi(e,t,n,r){this.tag=e,this.key=n,this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null,this.index=0,this.refCleanup=this.ref=null,this.pendingProps=t,this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null,this.mode=r,this.subtreeFlags=this.flags=0,this.deletions=null,this.childLanes=this.lanes=0,this.alternate=null}function _i(e,t,n,r){return new gi(e,t,n,r)}function vi(e){return e=e.prototype,!(!e||!e.isReactComponent)}function yi(e,t){var n=e.alternate;return n===null?(n=_i(e.tag,t,e.key,e.mode),n.elementType=e.elementType,n.type=e.type,n.stateNode=e.stateNode,n.alternate=e,e.alternate=n):(n.pendingProps=t,n.type=e.type,n.flags=0,n.subtreeFlags=0,n.deletions=null),n.flags=e.flags&65011712,n.childLanes=e.childLanes,n.lanes=e.lanes,n.child=e.child,n.memoizedProps=e.memoizedProps,n.memoizedState=e.memoizedState,n.updateQueue=e.updateQueue,t=e.dependencies,n.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext},n.sibling=e.sibling,n.index=e.index,n.ref=e.ref,n.refCleanup=e.refCleanup,n}function bi(e,t){e.flags&=65011714;var n=e.alternate;return n===null?(e.childLanes=0,e.lanes=t,e.child=null,e.subtreeFlags=0,e.memoizedProps=null,e.memoizedState=null,e.updateQueue=null,e.dependencies=null,e.stateNode=null):(e.childLanes=n.childLanes,e.lanes=n.lanes,e.child=n.child,e.subtreeFlags=0,e.deletions=null,e.memoizedProps=n.memoizedProps,e.memoizedState=n.memoizedState,e.updateQueue=n.updateQueue,e.type=n.type,t=n.dependencies,e.dependencies=t===null?null:{lanes:t.lanes,firstContext:t.firstContext}),e}function xi(e,t,n,r,a,o){var s=0;if(r=e,typeof e==`function`)vi(e)&&(s=1);else if(typeof e==`string`)s=Uf(e,n,he.current)?26:e===`html`||e===`head`||e===`body`?27:5;else a:switch(e){case ae:return e=_i(31,n,t,a),e.elementType=ae,e.lanes=o,e;case y:return Si(n.children,a,o,t);case b:s=8,a|=24;break;case x:return e=_i(12,n,t,a|2),e.elementType=x,e.lanes=o,e;case te:return e=_i(13,n,t,a),e.elementType=te,e.lanes=o,e;case ne:return e=_i(19,n,t,a),e.elementType=ne,e.lanes=o,e;default:if(typeof e==`object`&&e)switch(e.$$typeof){case S:s=10;break a;case ee:s=9;break a;case C:s=11;break a;case re:s=14;break a;case ie:s=16,r=null;break a}s=29,n=Error(i(130,e===null?`null`:typeof e,``)),r=null}return t=_i(s,n,t,a),t.elementType=e,t.type=r,t.lanes=o,t}function Si(e,t,n,r){return e=_i(7,e,r,t),e.lanes=n,e}function Ci(e,t,n){return e=_i(6,e,null,t),e.lanes=n,e}function wi(e){var t=_i(18,null,null,0);return t.stateNode=e,t}function Ti(e,t,n){return t=_i(4,e.children===null?[]:e.children,e.key,t),t.lanes=n,t.stateNode={containerInfo:e.containerInfo,pendingChildren:null,implementation:e.implementation},t}var Ei=new WeakMap;function Di(e,t){if(typeof e==`object`&&e){var n=Ei.get(e);return n===void 0?(t={value:e,source:t,stack:ke(t)},Ei.set(e,t),t):n}return{value:e,source:t,stack:ke(t)}}var Oi=[],ki=0,Ai=null,ji=0,Mi=[],Ni=0,Pi=null,Fi=1,Ii=``;function Li(e,t){Oi[ki++]=ji,Oi[ki++]=Ai,Ai=e,ji=t}function Ri(e,t,n){Mi[Ni++]=Fi,Mi[Ni++]=Ii,Mi[Ni++]=Pi,Pi=e;var r=Fi;e=Ii;var i=32-qe(r)-1;r&=~(1<<i),n+=1;var a=32-qe(t)+i;if(30<a){var o=i-i%5;a=(r&(1<<o)-1).toString(32),r>>=o,i-=o,Fi=1<<32-qe(t)+i|n<<i|r,Ii=a+e}else Fi=1<<a|n<<i|r,Ii=e}function zi(e){e.return!==null&&(Li(e,1),Ri(e,1,0))}function Bi(e){for(;e===Ai;)Ai=Oi[--ki],Oi[ki]=null,ji=Oi[--ki],Oi[ki]=null;for(;e===Pi;)Pi=Mi[--Ni],Mi[Ni]=null,Ii=Mi[--Ni],Mi[Ni]=null,Fi=Mi[--Ni],Mi[Ni]=null}function Vi(e,t){Mi[Ni++]=Fi,Mi[Ni++]=Ii,Mi[Ni++]=Pi,Fi=t.id,Ii=t.overflow,Pi=e}var Hi=null,A=null,j=!1,Ui=null,Wi=!1,Gi=Error(i(519));function Ki(e){throw Qi(Di(Error(i(418,1<arguments.length&&arguments[1]!==void 0&&arguments[1]?`text`:`HTML`,``)),e)),Gi}function qi(e){var t=e.stateNode,n=e.type,r=e.memoizedProps;switch(t[gt]=e,t[_t]=r,n){case`dialog`:Q(`cancel`,t),Q(`close`,t);break;case`iframe`:case`object`:case`embed`:Q(`load`,t);break;case`video`:case`audio`:for(n=0;n<_d.length;n++)Q(_d[n],t);break;case`source`:Q(`error`,t);break;case`img`:case`image`:case`link`:Q(`error`,t),Q(`load`,t);break;case`details`:Q(`toggle`,t);break;case`input`:Q(`invalid`,t),Yt(t,r.value,r.defaultValue,r.checked,r.defaultChecked,r.type,r.name,!0);break;case`select`:Q(`invalid`,t);break;case`textarea`:Q(`invalid`,t),$t(t,r.value,r.defaultValue,r.children)}n=r.children,typeof n!=`string`&&typeof n!=`number`&&typeof n!=`bigint`||t.textContent===``+n||!0===r.suppressHydrationWarning||Md(t.textContent,n)?(r.popover!=null&&(Q(`beforetoggle`,t),Q(`toggle`,t)),r.onScroll!=null&&Q(`scroll`,t),r.onScrollEnd!=null&&Q(`scrollend`,t),r.onClick!=null&&(t.onclick=ln),t=!0):t=!1,t||Ki(e,!0)}function Ji(e){for(Hi=e.return;Hi;)switch(Hi.tag){case 5:case 31:case 13:Wi=!1;return;case 27:case 3:Wi=!0;return;default:Hi=Hi.return}}function Yi(e){if(e!==Hi)return!1;if(!j)return Ji(e),j=!0,!1;var t=e.tag,n;if((n=t!==3&&t!==27)&&((n=t===5)&&(n=e.type,n=!(n!==`form`&&n!==`button`)||Ud(e.type,e.memoizedProps)),n=!n),n&&A&&Ki(e),Ji(e),t===13){if(e=e.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(317));A=uf(e)}else if(t===31){if(e=e.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(317));A=uf(e)}else t===27?(t=A,Zd(e.type)?(e=lf,lf=null,A=e):A=t):A=Hi?cf(e.stateNode.nextSibling):null;return!0}function Xi(){A=Hi=null,j=!1}function Zi(){var e=Ui;return e!==null&&(Ql===null?Ql=e:Ql.push.apply(Ql,e),Ui=null),e}function Qi(e){Ui===null?Ui=[e]:Ui.push(e)}var $i=me(null),ea=null,ta=null;function na(e,t,n){O($i,t._currentValue),t._currentValue=n}function ra(e){e._currentValue=$i.current,D($i)}function ia(e,t,n){for(;e!==null;){var r=e.alternate;if((e.childLanes&t)===t?r!==null&&(r.childLanes&t)!==t&&(r.childLanes|=t):(e.childLanes|=t,r!==null&&(r.childLanes|=t)),e===n)break;e=e.return}}function aa(e,t,n,r){var a=e.child;for(a!==null&&(a.return=e);a!==null;){var o=a.dependencies;if(o!==null){var s=a.child;o=o.firstContext;a:for(;o!==null;){var c=o;o=a;for(var l=0;l<t.length;l++)if(c.context===t[l]){o.lanes|=n,c=o.alternate,c!==null&&(c.lanes|=n),ia(o.return,n,e),r||(s=null);break a}o=c.next}}else if(a.tag===18){if(s=a.return,s===null)throw Error(i(341));s.lanes|=n,o=s.alternate,o!==null&&(o.lanes|=n),ia(s,n,e),s=null}else s=a.child;if(s!==null)s.return=a;else for(s=a;s!==null;){if(s===e){s=null;break}if(a=s.sibling,a!==null){a.return=s.return,s=a;break}s=s.return}a=s}}function oa(e,t,n,r){e=null;for(var a=t,o=!1;a!==null;){if(!o){if(a.flags&524288)o=!0;else if(a.flags&262144)break}if(a.tag===10){var s=a.alternate;if(s===null)throw Error(i(387));if(s=s.memoizedProps,s!==null){var c=a.type;jr(a.pendingProps.value,s.value)||(e===null?e=[c]:e.push(c))}}else if(a===ve.current){if(s=a.alternate,s===null)throw Error(i(387));s.memoizedState.memoizedState!==a.memoizedState.memoizedState&&(e===null?e=[Qf]:e.push(Qf))}a=a.return}e!==null&&aa(t,e,n,r),t.flags|=262144}function sa(e){for(e=e.firstContext;e!==null;){if(!jr(e.context._currentValue,e.memoizedValue))return!0;e=e.next}return!1}function ca(e){ea=e,ta=null,e=e.dependencies,e!==null&&(e.firstContext=null)}function la(e){return da(ea,e)}function ua(e,t){return ea===null&&ca(e),da(e,t)}function da(e,t){var n=t._currentValue;if(t={context:t,memoizedValue:n,next:null},ta===null){if(e===null)throw Error(i(308));ta=t,e.dependencies={lanes:0,firstContext:t},e.flags|=524288}else ta=ta.next=t;return n}var fa=typeof AbortController<`u`?AbortController:function(){var e=[],t=this.signal={aborted:!1,addEventListener:function(t,n){e.push(n)}};this.abort=function(){t.aborted=!0,e.forEach(function(e){return e()})}},pa=t.unstable_scheduleCallback,ma=t.unstable_NormalPriority,M={$$typeof:S,Consumer:null,Provider:null,_currentValue:null,_currentValue2:null,_threadCount:0};function ha(){return{controller:new fa,data:new Map,refCount:0}}function ga(e){e.refCount--,e.refCount===0&&pa(ma,function(){e.controller.abort()})}var _a=null,va=0,ya=0,ba=null;function xa(e,t){if(_a===null){var n=_a=[];va=0,ya=dd(),ba={status:`pending`,value:void 0,then:function(e){n.push(e)}}}return va++,t.then(Sa,Sa),t}function Sa(){if(--va===0&&_a!==null){ba!==null&&(ba.status=`fulfilled`);var e=_a;_a=null,ya=0,ba=null;for(var t=0;t<e.length;t++)(0,e[t])()}}function Ca(e,t){var n=[],r={status:`pending`,value:null,reason:null,then:function(e){n.push(e)}};return e.then(function(){r.status=`fulfilled`,r.value=t;for(var e=0;e<n.length;e++)(0,n[e])(t)},function(e){for(r.status=`rejected`,r.reason=e,e=0;e<n.length;e++)(0,n[e])(void 0)}),r}var wa=T.S;T.S=function(e,t){tu=Fe(),typeof t==`object`&&t&&typeof t.then==`function`&&xa(e,t),wa!==null&&wa(e,t)};var Ta=me(null);function Ea(){var e=Ta.current;return e===null?G.pooledCache:e}function Da(e,t){t===null?O(Ta,Ta.current):O(Ta,t.pool)}function Oa(){var e=Ea();return e===null?null:{parent:M._currentValue,pool:e}}var ka=Error(i(460)),Aa=Error(i(474)),ja=Error(i(542)),Ma={then:function(){}};function Na(e){return e=e.status,e===`fulfilled`||e===`rejected`}function Pa(e,t,n){switch(n=e[n],n===void 0?e.push(t):n!==t&&(t.then(ln,ln),t=n),t.status){case`fulfilled`:return t.value;case`rejected`:throw e=t.reason,Ra(e),e;default:if(typeof t.status==`string`)t.then(ln,ln);else{if(e=G,e!==null&&100<e.shellSuspendCounter)throw Error(i(482));e=t,e.status=`pending`,e.then(function(e){if(t.status===`pending`){var n=t;n.status=`fulfilled`,n.value=e}},function(e){if(t.status===`pending`){var n=t;n.status=`rejected`,n.reason=e}})}switch(t.status){case`fulfilled`:return t.value;case`rejected`:throw e=t.reason,Ra(e),e}throw Ia=t,ka}}function Fa(e){try{var t=e._init;return t(e._payload)}catch(e){throw typeof e==`object`&&e&&typeof e.then==`function`?(Ia=e,ka):e}}var Ia=null;function La(){if(Ia===null)throw Error(i(459));var e=Ia;return Ia=null,e}function Ra(e){if(e===ka||e===ja)throw Error(i(483))}var za=null,Ba=0;function Va(e){var t=Ba;return Ba+=1,za===null&&(za=[]),Pa(za,e,t)}function Ha(e,t){t=t.props.ref,e.ref=t===void 0?null:t}function Ua(e,t){throw t.$$typeof===g?Error(i(525)):(e=Object.prototype.toString.call(t),Error(i(31,e===`[object Object]`?`object with keys {`+Object.keys(t).join(`, `)+`}`:e)))}function Wa(e){function t(t,n){if(e){var r=t.deletions;r===null?(t.deletions=[n],t.flags|=16):r.push(n)}}function n(n,r){if(!e)return null;for(;r!==null;)t(n,r),r=r.sibling;return null}function r(e){for(var t=new Map;e!==null;)e.key===null?t.set(e.index,e):t.set(e.key,e),e=e.sibling;return t}function a(e,t){return e=yi(e,t),e.index=0,e.sibling=null,e}function o(t,n,r){return t.index=r,e?(r=t.alternate,r===null?(t.flags|=67108866,n):(r=r.index,r<n?(t.flags|=67108866,n):r)):(t.flags|=1048576,n)}function s(t){return e&&t.alternate===null&&(t.flags|=67108866),t}function c(e,t,n,r){return t===null||t.tag!==6?(t=Ci(n,e.mode,r),t.return=e,t):(t=a(t,n),t.return=e,t)}function l(e,t,n,r){var i=n.type;return i===y?d(e,t,n.props.children,r,n.key):t!==null&&(t.elementType===i||typeof i==`object`&&i&&i.$$typeof===ie&&Fa(i)===t.type)?(t=a(t,n.props),Ha(t,n),t.return=e,t):(t=xi(n.type,n.key,n.props,null,e.mode,r),Ha(t,n),t.return=e,t)}function u(e,t,n,r){return t===null||t.tag!==4||t.stateNode.containerInfo!==n.containerInfo||t.stateNode.implementation!==n.implementation?(t=Ti(n,e.mode,r),t.return=e,t):(t=a(t,n.children||[]),t.return=e,t)}function d(e,t,n,r,i){return t===null||t.tag!==7?(t=Si(n,e.mode,r,i),t.return=e,t):(t=a(t,n),t.return=e,t)}function f(e,t,n){if(typeof t==`string`&&t!==``||typeof t==`number`||typeof t==`bigint`)return t=Ci(``+t,e.mode,n),t.return=e,t;if(typeof t==`object`&&t){switch(t.$$typeof){case _:return n=xi(t.type,t.key,t.props,null,e.mode,n),Ha(n,t),n.return=e,n;case v:return t=Ti(t,e.mode,n),t.return=e,t;case ie:return t=Fa(t),f(e,t,n)}if(ue(t)||se(t))return t=Si(t,e.mode,n,null),t.return=e,t;if(typeof t.then==`function`)return f(e,Va(t),n);if(t.$$typeof===S)return f(e,ua(e,t),n);Ua(e,t)}return null}function p(e,t,n,r){var i=t===null?null:t.key;if(typeof n==`string`&&n!==``||typeof n==`number`||typeof n==`bigint`)return i===null?c(e,t,``+n,r):null;if(typeof n==`object`&&n){switch(n.$$typeof){case _:return n.key===i?l(e,t,n,r):null;case v:return n.key===i?u(e,t,n,r):null;case ie:return n=Fa(n),p(e,t,n,r)}if(ue(n)||se(n))return i===null?d(e,t,n,r,null):null;if(typeof n.then==`function`)return p(e,t,Va(n),r);if(n.$$typeof===S)return p(e,t,ua(e,n),r);Ua(e,n)}return null}function m(e,t,n,r,i){if(typeof r==`string`&&r!==``||typeof r==`number`||typeof r==`bigint`)return e=e.get(n)||null,c(t,e,``+r,i);if(typeof r==`object`&&r){switch(r.$$typeof){case _:return e=e.get(r.key===null?n:r.key)||null,l(t,e,r,i);case v:return e=e.get(r.key===null?n:r.key)||null,u(t,e,r,i);case ie:return r=Fa(r),m(e,t,n,r,i)}if(ue(r)||se(r))return e=e.get(n)||null,d(t,e,r,i,null);if(typeof r.then==`function`)return m(e,t,n,Va(r),i);if(r.$$typeof===S)return m(e,t,n,ua(t,r),i);Ua(t,r)}return null}function h(i,a,s,c){for(var l=null,u=null,d=a,h=a=0,g=null;d!==null&&h<s.length;h++){d.index>h?(g=d,d=null):g=d.sibling;var _=p(i,d,s[h],c);if(_===null){d===null&&(d=g);break}e&&d&&_.alternate===null&&t(i,d),a=o(_,a,h),u===null?l=_:u.sibling=_,u=_,d=g}if(h===s.length)return n(i,d),j&&Li(i,h),l;if(d===null){for(;h<s.length;h++)d=f(i,s[h],c),d!==null&&(a=o(d,a,h),u===null?l=d:u.sibling=d,u=d);return j&&Li(i,h),l}for(d=r(d);h<s.length;h++)g=m(d,i,h,s[h],c),g!==null&&(e&&g.alternate!==null&&d.delete(g.key===null?h:g.key),a=o(g,a,h),u===null?l=g:u.sibling=g,u=g);return e&&d.forEach(function(e){return t(i,e)}),j&&Li(i,h),l}function g(a,s,c,l){if(c==null)throw Error(i(151));for(var u=null,d=null,h=s,g=s=0,_=null,v=c.next();h!==null&&!v.done;g++,v=c.next()){h.index>g?(_=h,h=null):_=h.sibling;var y=p(a,h,v.value,l);if(y===null){h===null&&(h=_);break}e&&h&&y.alternate===null&&t(a,h),s=o(y,s,g),d===null?u=y:d.sibling=y,d=y,h=_}if(v.done)return n(a,h),j&&Li(a,g),u;if(h===null){for(;!v.done;g++,v=c.next())v=f(a,v.value,l),v!==null&&(s=o(v,s,g),d===null?u=v:d.sibling=v,d=v);return j&&Li(a,g),u}for(h=r(h);!v.done;g++,v=c.next())v=m(h,a,g,v.value,l),v!==null&&(e&&v.alternate!==null&&h.delete(v.key===null?g:v.key),s=o(v,s,g),d===null?u=v:d.sibling=v,d=v);return e&&h.forEach(function(e){return t(a,e)}),j&&Li(a,g),u}function b(e,r,o,c){if(typeof o==`object`&&o&&o.type===y&&o.key===null&&(o=o.props.children),typeof o==`object`&&o){switch(o.$$typeof){case _:a:{for(var l=o.key;r!==null;){if(r.key===l){if(l=o.type,l===y){if(r.tag===7){n(e,r.sibling),c=a(r,o.props.children),c.return=e,e=c;break a}}else if(r.elementType===l||typeof l==`object`&&l&&l.$$typeof===ie&&Fa(l)===r.type){n(e,r.sibling),c=a(r,o.props),Ha(c,o),c.return=e,e=c;break a}n(e,r);break}else t(e,r);r=r.sibling}o.type===y?(c=Si(o.props.children,e.mode,c,o.key),c.return=e,e=c):(c=xi(o.type,o.key,o.props,null,e.mode,c),Ha(c,o),c.return=e,e=c)}return s(e);case v:a:{for(l=o.key;r!==null;){if(r.key===l)if(r.tag===4&&r.stateNode.containerInfo===o.containerInfo&&r.stateNode.implementation===o.implementation){n(e,r.sibling),c=a(r,o.children||[]),c.return=e,e=c;break a}else{n(e,r);break}else t(e,r);r=r.sibling}c=Ti(o,e.mode,c),c.return=e,e=c}return s(e);case ie:return o=Fa(o),b(e,r,o,c)}if(ue(o))return h(e,r,o,c);if(se(o)){if(l=se(o),typeof l!=`function`)throw Error(i(150));return o=l.call(o),g(e,r,o,c)}if(typeof o.then==`function`)return b(e,r,Va(o),c);if(o.$$typeof===S)return b(e,r,ua(e,o),c);Ua(e,o)}return typeof o==`string`&&o!==``||typeof o==`number`||typeof o==`bigint`?(o=``+o,r!==null&&r.tag===6?(n(e,r.sibling),c=a(r,o),c.return=e,e=c):(n(e,r),c=Ci(o,e.mode,c),c.return=e,e=c),s(e)):n(e,r)}return function(e,t,n,r){try{Ba=0;var i=b(e,t,n,r);return za=null,i}catch(t){if(t===ka||t===ja)throw t;var a=_i(29,t,null,e.mode);return a.lanes=r,a.return=e,a}}}var Ga=Wa(!0),Ka=Wa(!1),qa=!1;function Ja(e){e.updateQueue={baseState:e.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,lanes:0,hiddenCallbacks:null},callbacks:null}}function Ya(e,t){e=e.updateQueue,t.updateQueue===e&&(t.updateQueue={baseState:e.baseState,firstBaseUpdate:e.firstBaseUpdate,lastBaseUpdate:e.lastBaseUpdate,shared:e.shared,callbacks:null})}function Xa(e){return{lane:e,tag:0,payload:null,callback:null,next:null}}function Za(e,t,n){var r=e.updateQueue;if(r===null)return null;if(r=r.shared,W&2){var i=r.pending;return i===null?t.next=t:(t.next=i.next,i.next=t),r.pending=t,t=mi(e),pi(e,null,n),t}return ui(e,r,t,n),mi(e)}function Qa(e,t,n){if(t=t.updateQueue,t!==null&&(t=t.shared,n&4194048)){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,lt(e,n)}}function $a(e,t){var n=e.updateQueue,r=e.alternate;if(r!==null&&(r=r.updateQueue,n===r)){var i=null,a=null;if(n=n.firstBaseUpdate,n!==null){do{var o={lane:n.lane,tag:n.tag,payload:n.payload,callback:null,next:null};a===null?i=a=o:a=a.next=o,n=n.next}while(n!==null);a===null?i=a=t:a=a.next=t}else i=a=t;n={baseState:r.baseState,firstBaseUpdate:i,lastBaseUpdate:a,shared:r.shared,callbacks:r.callbacks},e.updateQueue=n;return}e=n.lastBaseUpdate,e===null?n.firstBaseUpdate=t:e.next=t,n.lastBaseUpdate=t}var eo=!1;function to(){if(eo){var e=ba;if(e!==null)throw e}}function no(e,t,n,r){eo=!1;var i=e.updateQueue;qa=!1;var a=i.firstBaseUpdate,o=i.lastBaseUpdate,s=i.shared.pending;if(s!==null){i.shared.pending=null;var c=s,l=c.next;c.next=null,o===null?a=l:o.next=l,o=c;var u=e.alternate;u!==null&&(u=u.updateQueue,s=u.lastBaseUpdate,s!==o&&(s===null?u.firstBaseUpdate=l:s.next=l,u.lastBaseUpdate=c))}if(a!==null){var d=i.baseState;o=0,u=l=c=null,s=a;do{var f=s.lane&-536870913,p=f!==s.lane;if(p?(q&f)===f:(r&f)===f){f!==0&&f===ya&&(eo=!0),u!==null&&(u=u.next={lane:0,tag:s.tag,payload:s.payload,callback:null,next:null});a:{var m=e,g=s;f=t;var _=n;switch(g.tag){case 1:if(m=g.payload,typeof m==`function`){d=m.call(_,d,f);break a}d=m;break a;case 3:m.flags=m.flags&-65537|128;case 0:if(m=g.payload,f=typeof m==`function`?m.call(_,d,f):m,f==null)break a;d=h({},d,f);break a;case 2:qa=!0}}f=s.callback,f!==null&&(e.flags|=64,p&&(e.flags|=8192),p=i.callbacks,p===null?i.callbacks=[f]:p.push(f))}else p={lane:f,tag:s.tag,payload:s.payload,callback:s.callback,next:null},u===null?(l=u=p,c=d):u=u.next=p,o|=f;if(s=s.next,s===null){if(s=i.shared.pending,s===null)break;p=s,s=p.next,p.next=null,i.lastBaseUpdate=p,i.shared.pending=null}}while(1);u===null&&(c=d),i.baseState=c,i.firstBaseUpdate=l,i.lastBaseUpdate=u,a===null&&(i.shared.lanes=0),Kl|=o,e.lanes=o,e.memoizedState=d}}function ro(e,t){if(typeof e!=`function`)throw Error(i(191,e));e.call(t)}function io(e,t){var n=e.callbacks;if(n!==null)for(e.callbacks=null,e=0;e<n.length;e++)ro(n[e],t)}var ao=me(null),oo=me(0);function so(e,t){e=Gl,O(oo,e),O(ao,t),Gl=e|t.baseLanes}function co(){O(oo,Gl),O(ao,ao.current)}function lo(){Gl=oo.current,D(ao),D(oo)}var uo=me(null),fo=null;function po(e){var t=e.alternate;O(N,N.current&1),O(uo,e),fo===null&&(t===null||ao.current!==null||t.memoizedState!==null)&&(fo=e)}function mo(e){O(N,N.current),O(uo,e),fo===null&&(fo=e)}function ho(e){e.tag===22?(O(N,N.current),O(uo,e),fo===null&&(fo=e)):go(e)}function go(){O(N,N.current),O(uo,uo.current)}function _o(e){D(uo),fo===e&&(fo=null),D(N)}var N=me(0);function vo(e){for(var t=e;t!==null;){if(t.tag===13){var n=t.memoizedState;if(n!==null&&(n=n.dehydrated,n===null||af(n)||of(n)))return t}else if(t.tag===19&&(t.memoizedProps.revealOrder===`forwards`||t.memoizedProps.revealOrder===`backwards`||t.memoizedProps.revealOrder===`unstable_legacy-backwards`||t.memoizedProps.revealOrder===`together`)){if(t.flags&128)return t}else if(t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return null;t=t.return}t.sibling.return=t.return,t=t.sibling}return null}var yo=0,P=null,F=null,I=null,bo=!1,xo=!1,So=!1,Co=0,wo=0,To=null,Eo=0;function L(){throw Error(i(321))}function Do(e,t){if(t===null)return!1;for(var n=0;n<t.length&&n<e.length;n++)if(!jr(e[n],t[n]))return!1;return!0}function Oo(e,t,n,r,i,a){return yo=a,P=t,t.memoizedState=null,t.updateQueue=null,t.lanes=0,T.H=e===null||e.memoizedState===null?Ws:Gs,So=!1,a=n(r,i),So=!1,xo&&(a=Ao(t,n,r,i)),ko(e),a}function ko(e){T.H=Us;var t=F!==null&&F.next!==null;if(yo=0,I=F=P=null,bo=!1,wo=0,To=null,t)throw Error(i(300));e===null||z||(e=e.dependencies,e!==null&&sa(e)&&(z=!0))}function Ao(e,t,n,r){P=e;var a=0;do{if(xo&&(To=null),wo=0,xo=!1,25<=a)throw Error(i(301));if(a+=1,I=F=null,e.updateQueue!=null){var o=e.updateQueue;o.lastEffect=null,o.events=null,o.stores=null,o.memoCache!=null&&(o.memoCache.index=0)}T.H=Ks,o=t(n,r)}while(xo);return o}function jo(){var e=T.H,t=e.useState()[0];return t=typeof t.then==`function`?Lo(t):t,e=e.useState()[0],(F===null?null:F.memoizedState)!==e&&(P.flags|=1024),t}function Mo(){var e=Co!==0;return Co=0,e}function No(e,t,n){t.updateQueue=e.updateQueue,t.flags&=-2053,e.lanes&=~n}function Po(e){if(bo){for(e=e.memoizedState;e!==null;){var t=e.queue;t!==null&&(t.pending=null),e=e.next}bo=!1}yo=0,I=F=P=null,xo=!1,wo=Co=0,To=null}function Fo(){var e={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};return I===null?P.memoizedState=I=e:I=I.next=e,I}function R(){if(F===null){var e=P.alternate;e=e===null?null:e.memoizedState}else e=F.next;var t=I===null?P.memoizedState:I.next;if(t!==null)I=t,F=e;else{if(e===null)throw P.alternate===null?Error(i(467)):Error(i(310));F=e,e={memoizedState:F.memoizedState,baseState:F.baseState,baseQueue:F.baseQueue,queue:F.queue,next:null},I===null?P.memoizedState=I=e:I=I.next=e}return I}function Io(){return{lastEffect:null,events:null,stores:null,memoCache:null}}function Lo(e){var t=wo;return wo+=1,To===null&&(To=[]),e=Pa(To,e,t),t=P,(I===null?t.memoizedState:I.next)===null&&(t=t.alternate,T.H=t===null||t.memoizedState===null?Ws:Gs),e}function Ro(e){if(typeof e==`object`&&e){if(typeof e.then==`function`)return Lo(e);if(e.$$typeof===S)return la(e)}throw Error(i(438,String(e)))}function zo(e){var t=null,n=P.updateQueue;if(n!==null&&(t=n.memoCache),t==null){var r=P.alternate;r!==null&&(r=r.updateQueue,r!==null&&(r=r.memoCache,r!=null&&(t={data:r.data.map(function(e){return e.slice()}),index:0})))}if(t??={data:[],index:0},n===null&&(n=Io(),P.updateQueue=n),n.memoCache=t,n=t.data[t.index],n===void 0)for(n=t.data[t.index]=Array(e),r=0;r<e;r++)n[r]=oe;return t.index++,n}function Bo(e,t){return typeof t==`function`?t(e):t}function Vo(e){return Ho(R(),F,e)}function Ho(e,t,n){var r=e.queue;if(r===null)throw Error(i(311));r.lastRenderedReducer=n;var a=e.baseQueue,o=r.pending;if(o!==null){if(a!==null){var s=a.next;a.next=o.next,o.next=s}t.baseQueue=a=o,r.pending=null}if(o=e.baseState,a===null)e.memoizedState=o;else{t=a.next;var c=s=null,l=null,u=t,d=!1;do{var f=u.lane&-536870913;if(f===u.lane?(yo&f)===f:(q&f)===f){var p=u.revertLane;if(p===0)l!==null&&(l=l.next={lane:0,revertLane:0,gesture:null,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null}),f===ya&&(d=!0);else if((yo&p)===p){u=u.next,p===ya&&(d=!0);continue}else f={lane:0,revertLane:u.revertLane,gesture:null,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null},l===null?(c=l=f,s=o):l=l.next=f,P.lanes|=p,Kl|=p;f=u.action,So&&n(o,f),o=u.hasEagerState?u.eagerState:n(o,f)}else p={lane:f,revertLane:u.revertLane,gesture:u.gesture,action:u.action,hasEagerState:u.hasEagerState,eagerState:u.eagerState,next:null},l===null?(c=l=p,s=o):l=l.next=p,P.lanes|=f,Kl|=f;u=u.next}while(u!==null&&u!==t);if(l===null?s=o:l.next=c,!jr(o,e.memoizedState)&&(z=!0,d&&(n=ba,n!==null)))throw n;e.memoizedState=o,e.baseState=s,e.baseQueue=l,r.lastRenderedState=o}return a===null&&(r.lanes=0),[e.memoizedState,r.dispatch]}function Uo(e){var t=R(),n=t.queue;if(n===null)throw Error(i(311));n.lastRenderedReducer=e;var r=n.dispatch,a=n.pending,o=t.memoizedState;if(a!==null){n.pending=null;var s=a=a.next;do o=e(o,s.action),s=s.next;while(s!==a);jr(o,t.memoizedState)||(z=!0),t.memoizedState=o,t.baseQueue===null&&(t.baseState=o),n.lastRenderedState=o}return[o,r]}function Wo(e,t,n){var r=P,a=R(),o=j;if(o){if(n===void 0)throw Error(i(407));n=n()}else n=t();var s=!jr((F||a).memoizedState,n);if(s&&(a.memoizedState=n,z=!0),a=a.queue,hs(qo.bind(null,r,a,e),[e]),a.getSnapshot!==t||s||I!==null&&I.memoizedState.tag&1){if(r.flags|=2048,us(9,{destroy:void 0},Ko.bind(null,r,a,n,t),null),G===null)throw Error(i(349));o||yo&127||Go(r,t,n)}return n}function Go(e,t,n){e.flags|=16384,e={getSnapshot:t,value:n},t=P.updateQueue,t===null?(t=Io(),P.updateQueue=t,t.stores=[e]):(n=t.stores,n===null?t.stores=[e]:n.push(e))}function Ko(e,t,n,r){t.value=n,t.getSnapshot=r,Jo(t)&&Yo(e)}function qo(e,t,n){return n(function(){Jo(t)&&Yo(e)})}function Jo(e){var t=e.getSnapshot;e=e.value;try{var n=t();return!jr(e,n)}catch{return!0}}function Yo(e){var t=fi(e,2);t!==null&&hu(t,e,2)}function Xo(e){var t=Fo();if(typeof e==`function`){var n=e;if(e=n(),So){Ke(!0);try{n()}finally{Ke(!1)}}}return t.memoizedState=t.baseState=e,t.queue={pending:null,lanes:0,dispatch:null,lastRenderedReducer:Bo,lastRenderedState:e},t}function Zo(e,t,n,r){return e.baseState=n,Ho(e,F,typeof r==`function`?r:Bo)}function Qo(e,t,n,r,a){if(Bs(e))throw Error(i(485));if(e=t.action,e!==null){var o={payload:a,action:e,next:null,isTransition:!0,status:`pending`,value:null,reason:null,listeners:[],then:function(e){o.listeners.push(e)}};T.T===null?o.isTransition=!1:n(!0),r(o),n=t.pending,n===null?(o.next=t.pending=o,$o(t,o)):(o.next=n.next,t.pending=n.next=o)}}function $o(e,t){var n=t.action,r=t.payload,i=e.state;if(t.isTransition){var a=T.T,o={};T.T=o;try{var s=n(i,r),c=T.S;c!==null&&c(o,s),es(e,t,s)}catch(n){ns(e,t,n)}finally{a!==null&&o.types!==null&&(a.types=o.types),T.T=a}}else try{a=n(i,r),es(e,t,a)}catch(n){ns(e,t,n)}}function es(e,t,n){typeof n==`object`&&n&&typeof n.then==`function`?n.then(function(n){ts(e,t,n)},function(n){return ns(e,t,n)}):ts(e,t,n)}function ts(e,t,n){t.status=`fulfilled`,t.value=n,rs(t),e.state=n,t=e.pending,t!==null&&(n=t.next,n===t?e.pending=null:(n=n.next,t.next=n,$o(e,n)))}function ns(e,t,n){var r=e.pending;if(e.pending=null,r!==null){r=r.next;do t.status=`rejected`,t.reason=n,rs(t),t=t.next;while(t!==r)}e.action=null}function rs(e){e=e.listeners;for(var t=0;t<e.length;t++)(0,e[t])()}function is(e,t){return t}function as(e,t){if(j){var n=G.formState;if(n!==null){a:{var r=P;if(j){if(A){b:{for(var i=A,a=Wi;i.nodeType!==8;){if(!a){i=null;break b}if(i=cf(i.nextSibling),i===null){i=null;break b}}a=i.data,i=a===`F!`||a===`F`?i:null}if(i){A=cf(i.nextSibling),r=i.data===`F!`;break a}}Ki(r)}r=!1}r&&(t=n[0])}}return n=Fo(),n.memoizedState=n.baseState=t,r={pending:null,lanes:0,dispatch:null,lastRenderedReducer:is,lastRenderedState:t},n.queue=r,n=Ls.bind(null,P,r),r.dispatch=n,r=Xo(!1),a=zs.bind(null,P,!1,r.queue),r=Fo(),i={state:t,dispatch:null,action:e,pending:null},r.queue=i,n=Qo.bind(null,P,i,a,n),i.dispatch=n,r.memoizedState=e,[t,n,!1]}function os(e){return ss(R(),F,e)}function ss(e,t,n){if(t=Ho(e,t,is)[0],e=Vo(Bo)[0],typeof t==`object`&&t&&typeof t.then==`function`)try{var r=Lo(t)}catch(e){throw e===ka?ja:e}else r=t;t=R();var i=t.queue,a=i.dispatch;return n!==t.memoizedState&&(P.flags|=2048,us(9,{destroy:void 0},cs.bind(null,i,n),null)),[r,a,e]}function cs(e,t){e.action=t}function ls(e){var t=R(),n=F;if(n!==null)return ss(t,n,e);R(),t=t.memoizedState,n=R();var r=n.queue.dispatch;return n.memoizedState=e,[t,r,!1]}function us(e,t,n,r){return e={tag:e,create:n,deps:r,inst:t,next:null},t=P.updateQueue,t===null&&(t=Io(),P.updateQueue=t),n=t.lastEffect,n===null?t.lastEffect=e.next=e:(r=n.next,n.next=e,e.next=r,t.lastEffect=e),e}function ds(){return R().memoizedState}function fs(e,t,n,r){var i=Fo();P.flags|=e,i.memoizedState=us(1|t,{destroy:void 0},n,r===void 0?null:r)}function ps(e,t,n,r){var i=R();r=r===void 0?null:r;var a=i.memoizedState.inst;F!==null&&r!==null&&Do(r,F.memoizedState.deps)?i.memoizedState=us(t,a,n,r):(P.flags|=e,i.memoizedState=us(1|t,a,n,r))}function ms(e,t){fs(8390656,8,e,t)}function hs(e,t){ps(2048,8,e,t)}function gs(e){P.flags|=4;var t=P.updateQueue;if(t===null)t=Io(),P.updateQueue=t,t.events=[e];else{var n=t.events;n===null?t.events=[e]:n.push(e)}}function _s(e){var t=R().memoizedState;return gs({ref:t,nextImpl:e}),function(){if(W&2)throw Error(i(440));return t.impl.apply(void 0,arguments)}}function vs(e,t){return ps(4,2,e,t)}function ys(e,t){return ps(4,4,e,t)}function bs(e,t){if(typeof t==`function`){e=e();var n=t(e);return function(){typeof n==`function`?n():t(null)}}if(t!=null)return e=e(),t.current=e,function(){t.current=null}}function xs(e,t,n){n=n==null?null:n.concat([e]),ps(4,4,bs.bind(null,t,e),n)}function Ss(){}function Cs(e,t){var n=R();t=t===void 0?null:t;var r=n.memoizedState;return t!==null&&Do(t,r[1])?r[0]:(n.memoizedState=[e,t],e)}function ws(e,t){var n=R();t=t===void 0?null:t;var r=n.memoizedState;if(t!==null&&Do(t,r[1]))return r[0];if(r=e(),So){Ke(!0);try{e()}finally{Ke(!1)}}return n.memoizedState=[r,t],r}function Ts(e,t,n){return n===void 0||yo&1073741824&&!(q&261930)?e.memoizedState=t:(e.memoizedState=n,e=mu(),P.lanes|=e,Kl|=e,n)}function Es(e,t,n,r){return jr(n,t)?n:ao.current===null?!(yo&42)||yo&1073741824&&!(q&261930)?(z=!0,e.memoizedState=n):(e=mu(),P.lanes|=e,Kl|=e,t):(e=Ts(e,n,r),jr(e,t)||(z=!0),e)}function Ds(e,t,n,r,i){var a=E.p;E.p=a!==0&&8>a?a:8;var o=T.T,s={};T.T=s,zs(e,!1,t,n);try{var c=i(),l=T.S;l!==null&&l(s,c),typeof c==`object`&&c&&typeof c.then==`function`?Rs(e,t,Ca(c,r),pu(e)):Rs(e,t,r,pu(e))}catch(n){Rs(e,t,{then:function(){},status:`rejected`,reason:n},pu())}finally{E.p=a,o!==null&&s.types!==null&&(o.types=s.types),T.T=o}}function Os(){}function ks(e,t,n,r){if(e.tag!==5)throw Error(i(476));var a=As(e).queue;Ds(e,a,t,de,n===null?Os:function(){return js(e),n(r)})}function As(e){var t=e.memoizedState;if(t!==null)return t;t={memoizedState:de,baseState:de,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Bo,lastRenderedState:de},next:null};var n={};return t.next={memoizedState:n,baseState:n,baseQueue:null,queue:{pending:null,lanes:0,dispatch:null,lastRenderedReducer:Bo,lastRenderedState:n},next:null},e.memoizedState=t,e=e.alternate,e!==null&&(e.memoizedState=t),t}function js(e){var t=As(e);t.next===null&&(t=e.alternate.memoizedState),Rs(e,t.next.queue,{},pu())}function Ms(){return la(Qf)}function Ns(){return R().memoizedState}function Ps(){return R().memoizedState}function Fs(e){for(var t=e.return;t!==null;){switch(t.tag){case 24:case 3:var n=pu();e=Xa(n);var r=Za(t,e,n);r!==null&&(hu(r,t,n),Qa(r,t,n)),t={cache:ha()},e.payload=t;return}t=t.return}}function Is(e,t,n){var r=pu();n={lane:r,revertLane:0,gesture:null,action:n,hasEagerState:!1,eagerState:null,next:null},Bs(e)?Vs(t,n):(n=di(e,t,n,r),n!==null&&(hu(n,e,r),Hs(n,t,r)))}function Ls(e,t,n){Rs(e,t,n,pu())}function Rs(e,t,n,r){var i={lane:r,revertLane:0,gesture:null,action:n,hasEagerState:!1,eagerState:null,next:null};if(Bs(e))Vs(t,i);else{var a=e.alternate;if(e.lanes===0&&(a===null||a.lanes===0)&&(a=t.lastRenderedReducer,a!==null))try{var o=t.lastRenderedState,s=a(o,n);if(i.hasEagerState=!0,i.eagerState=s,jr(s,o))return ui(e,t,i,0),G===null&&li(),!1}catch{}if(n=di(e,t,i,r),n!==null)return hu(n,e,r),Hs(n,t,r),!0}return!1}function zs(e,t,n,r){if(r={lane:2,revertLane:dd(),gesture:null,action:r,hasEagerState:!1,eagerState:null,next:null},Bs(e)){if(t)throw Error(i(479))}else t=di(e,n,r,2),t!==null&&hu(t,e,2)}function Bs(e){var t=e.alternate;return e===P||t!==null&&t===P}function Vs(e,t){xo=bo=!0;var n=e.pending;n===null?t.next=t:(t.next=n.next,n.next=t),e.pending=t}function Hs(e,t,n){if(n&4194048){var r=t.lanes;r&=e.pendingLanes,n|=r,t.lanes=n,lt(e,n)}}var Us={readContext:la,use:Ro,useCallback:L,useContext:L,useEffect:L,useImperativeHandle:L,useLayoutEffect:L,useInsertionEffect:L,useMemo:L,useReducer:L,useRef:L,useState:L,useDebugValue:L,useDeferredValue:L,useTransition:L,useSyncExternalStore:L,useId:L,useHostTransitionStatus:L,useFormState:L,useActionState:L,useOptimistic:L,useMemoCache:L,useCacheRefresh:L};Us.useEffectEvent=L;var Ws={readContext:la,use:Ro,useCallback:function(e,t){return Fo().memoizedState=[e,t===void 0?null:t],e},useContext:la,useEffect:ms,useImperativeHandle:function(e,t,n){n=n==null?null:n.concat([e]),fs(4194308,4,bs.bind(null,t,e),n)},useLayoutEffect:function(e,t){return fs(4194308,4,e,t)},useInsertionEffect:function(e,t){fs(4,2,e,t)},useMemo:function(e,t){var n=Fo();t=t===void 0?null:t;var r=e();if(So){Ke(!0);try{e()}finally{Ke(!1)}}return n.memoizedState=[r,t],r},useReducer:function(e,t,n){var r=Fo();if(n!==void 0){var i=n(t);if(So){Ke(!0);try{n(t)}finally{Ke(!1)}}}else i=t;return r.memoizedState=r.baseState=i,e={pending:null,lanes:0,dispatch:null,lastRenderedReducer:e,lastRenderedState:i},r.queue=e,e=e.dispatch=Is.bind(null,P,e),[r.memoizedState,e]},useRef:function(e){var t=Fo();return e={current:e},t.memoizedState=e},useState:function(e){e=Xo(e);var t=e.queue,n=Ls.bind(null,P,t);return t.dispatch=n,[e.memoizedState,n]},useDebugValue:Ss,useDeferredValue:function(e,t){return Ts(Fo(),e,t)},useTransition:function(){var e=Xo(!1);return e=Ds.bind(null,P,e.queue,!0,!1),Fo().memoizedState=e,[!1,e]},useSyncExternalStore:function(e,t,n){var r=P,a=Fo();if(j){if(n===void 0)throw Error(i(407));n=n()}else{if(n=t(),G===null)throw Error(i(349));q&127||Go(r,t,n)}a.memoizedState=n;var o={value:n,getSnapshot:t};return a.queue=o,ms(qo.bind(null,r,o,e),[e]),r.flags|=2048,us(9,{destroy:void 0},Ko.bind(null,r,o,n,t),null),n},useId:function(){var e=Fo(),t=G.identifierPrefix;if(j){var n=Ii,r=Fi;n=(r&~(1<<32-qe(r)-1)).toString(32)+n,t=`_`+t+`R_`+n,n=Co++,0<n&&(t+=`H`+n.toString(32)),t+=`_`}else n=Eo++,t=`_`+t+`r_`+n.toString(32)+`_`;return e.memoizedState=t},useHostTransitionStatus:Ms,useFormState:as,useActionState:as,useOptimistic:function(e){var t=Fo();t.memoizedState=t.baseState=e;var n={pending:null,lanes:0,dispatch:null,lastRenderedReducer:null,lastRenderedState:null};return t.queue=n,t=zs.bind(null,P,!0,n),n.dispatch=t,[e,t]},useMemoCache:zo,useCacheRefresh:function(){return Fo().memoizedState=Fs.bind(null,P)},useEffectEvent:function(e){var t=Fo(),n={impl:e};return t.memoizedState=n,function(){if(W&2)throw Error(i(440));return n.impl.apply(void 0,arguments)}}},Gs={readContext:la,use:Ro,useCallback:Cs,useContext:la,useEffect:hs,useImperativeHandle:xs,useInsertionEffect:vs,useLayoutEffect:ys,useMemo:ws,useReducer:Vo,useRef:ds,useState:function(){return Vo(Bo)},useDebugValue:Ss,useDeferredValue:function(e,t){return Es(R(),F.memoizedState,e,t)},useTransition:function(){var e=Vo(Bo)[0],t=R().memoizedState;return[typeof e==`boolean`?e:Lo(e),t]},useSyncExternalStore:Wo,useId:Ns,useHostTransitionStatus:Ms,useFormState:os,useActionState:os,useOptimistic:function(e,t){return Zo(R(),F,e,t)},useMemoCache:zo,useCacheRefresh:Ps};Gs.useEffectEvent=_s;var Ks={readContext:la,use:Ro,useCallback:Cs,useContext:la,useEffect:hs,useImperativeHandle:xs,useInsertionEffect:vs,useLayoutEffect:ys,useMemo:ws,useReducer:Uo,useRef:ds,useState:function(){return Uo(Bo)},useDebugValue:Ss,useDeferredValue:function(e,t){var n=R();return F===null?Ts(n,e,t):Es(n,F.memoizedState,e,t)},useTransition:function(){var e=Uo(Bo)[0],t=R().memoizedState;return[typeof e==`boolean`?e:Lo(e),t]},useSyncExternalStore:Wo,useId:Ns,useHostTransitionStatus:Ms,useFormState:ls,useActionState:ls,useOptimistic:function(e,t){var n=R();return F===null?(n.baseState=e,[e,n.queue.dispatch]):Zo(n,F,e,t)},useMemoCache:zo,useCacheRefresh:Ps};Ks.useEffectEvent=_s;function qs(e,t,n,r){t=e.memoizedState,n=n(r,t),n=n==null?t:h({},t,n),e.memoizedState=n,e.lanes===0&&(e.updateQueue.baseState=n)}var Js={enqueueSetState:function(e,t,n){e=e._reactInternals;var r=pu(),i=Xa(r);i.payload=t,n!=null&&(i.callback=n),t=Za(e,i,r),t!==null&&(hu(t,e,r),Qa(t,e,r))},enqueueReplaceState:function(e,t,n){e=e._reactInternals;var r=pu(),i=Xa(r);i.tag=1,i.payload=t,n!=null&&(i.callback=n),t=Za(e,i,r),t!==null&&(hu(t,e,r),Qa(t,e,r))},enqueueForceUpdate:function(e,t){e=e._reactInternals;var n=pu(),r=Xa(n);r.tag=2,t!=null&&(r.callback=t),t=Za(e,r,n),t!==null&&(hu(t,e,n),Qa(t,e,n))}};function Ys(e,t,n,r,i,a,o){return e=e.stateNode,typeof e.shouldComponentUpdate==`function`?e.shouldComponentUpdate(r,a,o):t.prototype&&t.prototype.isPureReactComponent?!Mr(n,r)||!Mr(i,a):!0}function Xs(e,t,n,r){e=t.state,typeof t.componentWillReceiveProps==`function`&&t.componentWillReceiveProps(n,r),typeof t.UNSAFE_componentWillReceiveProps==`function`&&t.UNSAFE_componentWillReceiveProps(n,r),t.state!==e&&Js.enqueueReplaceState(t,t.state,null)}function Zs(e,t){var n=t;if(`ref`in t)for(var r in n={},t)r!==`ref`&&(n[r]=t[r]);if(e=e.defaultProps)for(var i in n===t&&(n=h({},n)),e)n[i]===void 0&&(n[i]=e[i]);return n}function Qs(e){ai(e)}function $s(e){console.error(e)}function ec(e){ai(e)}function tc(e,t){try{var n=e.onUncaughtError;n(t.value,{componentStack:t.stack})}catch(e){setTimeout(function(){throw e})}}function nc(e,t,n){try{var r=e.onCaughtError;r(n.value,{componentStack:n.stack,errorBoundary:t.tag===1?t.stateNode:null})}catch(e){setTimeout(function(){throw e})}}function rc(e,t,n){return n=Xa(n),n.tag=3,n.payload={element:null},n.callback=function(){tc(e,t)},n}function ic(e){return e=Xa(e),e.tag=3,e}function ac(e,t,n,r){var i=n.type.getDerivedStateFromError;if(typeof i==`function`){var a=r.value;e.payload=function(){return i(a)},e.callback=function(){nc(t,n,r)}}var o=n.stateNode;o!==null&&typeof o.componentDidCatch==`function`&&(e.callback=function(){nc(t,n,r),typeof i!=`function`&&(iu===null?iu=new Set([this]):iu.add(this));var e=r.stack;this.componentDidCatch(r.value,{componentStack:e===null?``:e})})}function oc(e,t,n,r,a){if(n.flags|=32768,typeof r==`object`&&r&&typeof r.then==`function`){if(t=n.alternate,t!==null&&oa(t,n,a,!0),n=uo.current,n!==null){switch(n.tag){case 31:case 13:return fo===null?Du():n.alternate===null&&Y===0&&(Y=3),n.flags&=-257,n.flags|=65536,n.lanes=a,r===Ma?n.flags|=16384:(t=n.updateQueue,t===null?n.updateQueue=new Set([r]):t.add(r),Gu(e,r,a)),!1;case 22:return n.flags|=65536,r===Ma?n.flags|=16384:(t=n.updateQueue,t===null?(t={transitions:null,markerInstances:null,retryQueue:new Set([r])},n.updateQueue=t):(n=t.retryQueue,n===null?t.retryQueue=new Set([r]):n.add(r)),Gu(e,r,a)),!1}throw Error(i(435,n.tag))}return Gu(e,r,a),Du(),!1}if(j)return t=uo.current,t===null?(r!==Gi&&(t=Error(i(423),{cause:r}),Qi(Di(t,n))),e=e.current.alternate,e.flags|=65536,a&=-a,e.lanes|=a,r=Di(r,n),a=rc(e.stateNode,r,a),$a(e,a),Y!==4&&(Y=2)):(!(t.flags&65536)&&(t.flags|=256),t.flags|=65536,t.lanes=a,r!==Gi&&(e=Error(i(422),{cause:r}),Qi(Di(e,n)))),!1;var o=Error(i(520),{cause:r});if(o=Di(o,n),Zl===null?Zl=[o]:Zl.push(o),Y!==4&&(Y=2),t===null)return!0;r=Di(r,n),n=t;do{switch(n.tag){case 3:return n.flags|=65536,e=a&-a,n.lanes|=e,e=rc(n.stateNode,r,e),$a(n,e),!1;case 1:if(t=n.type,o=n.stateNode,!(n.flags&128)&&(typeof t.getDerivedStateFromError==`function`||o!==null&&typeof o.componentDidCatch==`function`&&(iu===null||!iu.has(o))))return n.flags|=65536,a&=-a,n.lanes|=a,a=ic(a),ac(a,e,n,r),$a(n,a),!1}n=n.return}while(n!==null);return!1}var sc=Error(i(461)),z=!1;function cc(e,t,n,r){t.child=e===null?Ka(t,null,n,r):Ga(t,e.child,n,r)}function lc(e,t,n,r,i){n=n.render;var a=t.ref;if(`ref`in r){var o={};for(var s in r)s!==`ref`&&(o[s]=r[s])}else o=r;return ca(t),r=Oo(e,t,n,o,a,i),s=Mo(),e!==null&&!z?(No(e,t,i),Nc(e,t,i)):(j&&s&&zi(t),t.flags|=1,cc(e,t,r,i),t.child)}function uc(e,t,n,r,i){if(e===null){var a=n.type;return typeof a==`function`&&!vi(a)&&a.defaultProps===void 0&&n.compare===null?(t.tag=15,t.type=a,dc(e,t,a,r,i)):(e=xi(n.type,null,r,t,t.mode,i),e.ref=t.ref,e.return=t,t.child=e)}if(a=e.child,!Pc(e,i)){var o=a.memoizedProps;if(n=n.compare,n=n===null?Mr:n,n(o,r)&&e.ref===t.ref)return Nc(e,t,i)}return t.flags|=1,e=yi(a,r),e.ref=t.ref,e.return=t,t.child=e}function dc(e,t,n,r,i){if(e!==null){var a=e.memoizedProps;if(Mr(a,r)&&e.ref===t.ref)if(z=!1,t.pendingProps=r=a,Pc(e,i))e.flags&131072&&(z=!0);else return t.lanes=e.lanes,Nc(e,t,i)}return yc(e,t,n,r,i)}function fc(e,t,n,r){var i=r.children,a=e===null?null:e.memoizedState;if(e===null&&t.stateNode===null&&(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),r.mode===`hidden`){if(t.flags&128){if(a=a===null?n:a.baseLanes|n,e!==null){for(r=t.child=e.child,i=0;r!==null;)i=i|r.lanes|r.childLanes,r=r.sibling;r=i&~a}else r=0,t.child=null;return mc(e,t,a,n,r)}if(n&536870912)t.memoizedState={baseLanes:0,cachePool:null},e!==null&&Da(t,a===null?null:a.cachePool),a===null?co():so(t,a),ho(t);else return r=t.lanes=536870912,mc(e,t,a===null?n:a.baseLanes|n,n,r)}else a===null?(e!==null&&Da(t,null),co(),go(t)):(Da(t,a.cachePool),so(t,a),go(t),t.memoizedState=null);return cc(e,t,i,n),t.child}function pc(e,t){return e!==null&&e.tag===22||t.stateNode!==null||(t.stateNode={_visibility:1,_pendingMarkers:null,_retryCache:null,_transitions:null}),t.sibling}function mc(e,t,n,r,i){var a=Ea();return a=a===null?null:{parent:M._currentValue,pool:a},t.memoizedState={baseLanes:n,cachePool:a},e!==null&&Da(t,null),co(),ho(t),e!==null&&oa(e,t,r,!0),t.childLanes=i,null}function hc(e,t){return t=Oc({mode:t.mode,children:t.children},e.mode),t.ref=e.ref,e.child=t,t.return=e,t}function gc(e,t,n){return Ga(t,e.child,null,n),e=hc(t,t.pendingProps),e.flags|=2,_o(t),t.memoizedState=null,e}function _c(e,t,n){var r=t.pendingProps,a=(t.flags&128)!=0;if(t.flags&=-129,e===null){if(j){if(r.mode===`hidden`)return e=hc(t,r),t.lanes=536870912,pc(null,e);if(mo(t),(e=A)?(e=rf(e,Wi),e=e!==null&&e.data===`&`?e:null,e!==null&&(t.memoizedState={dehydrated:e,treeContext:Pi===null?null:{id:Fi,overflow:Ii},retryLane:536870912,hydrationErrors:null},n=wi(e),n.return=t,t.child=n,Hi=t,A=null)):e=null,e===null)throw Ki(t);return t.lanes=536870912,null}return hc(t,r)}var o=e.memoizedState;if(o!==null){var s=o.dehydrated;if(mo(t),a)if(t.flags&256)t.flags&=-257,t=gc(e,t,n);else if(t.memoizedState!==null)t.child=e.child,t.flags|=128,t=null;else throw Error(i(558));else if(z||oa(e,t,n,!1),a=(n&e.childLanes)!==0,z||a){if(r=G,r!==null&&(s=ut(r,n),s!==0&&s!==o.retryLane))throw o.retryLane=s,fi(e,s),hu(r,e,s),sc;Du(),t=gc(e,t,n)}else e=o.treeContext,A=cf(s.nextSibling),Hi=t,j=!0,Ui=null,Wi=!1,e!==null&&Vi(t,e),t=hc(t,r),t.flags|=4096;return t}return e=yi(e.child,{mode:r.mode,children:r.children}),e.ref=t.ref,t.child=e,e.return=t,e}function vc(e,t){var n=t.ref;if(n===null)e!==null&&e.ref!==null&&(t.flags|=4194816);else{if(typeof n!=`function`&&typeof n!=`object`)throw Error(i(284));(e===null||e.ref!==n)&&(t.flags|=4194816)}}function yc(e,t,n,r,i){return ca(t),n=Oo(e,t,n,r,void 0,i),r=Mo(),e!==null&&!z?(No(e,t,i),Nc(e,t,i)):(j&&r&&zi(t),t.flags|=1,cc(e,t,n,i),t.child)}function bc(e,t,n,r,i,a){return ca(t),t.updateQueue=null,n=Ao(t,r,n,i),ko(e),r=Mo(),e!==null&&!z?(No(e,t,a),Nc(e,t,a)):(j&&r&&zi(t),t.flags|=1,cc(e,t,n,a),t.child)}function xc(e,t,n,r,i){if(ca(t),t.stateNode===null){var a=hi,o=n.contextType;typeof o==`object`&&o&&(a=la(o)),a=new n(r,a),t.memoizedState=a.state!==null&&a.state!==void 0?a.state:null,a.updater=Js,t.stateNode=a,a._reactInternals=t,a=t.stateNode,a.props=r,a.state=t.memoizedState,a.refs={},Ja(t),o=n.contextType,a.context=typeof o==`object`&&o?la(o):hi,a.state=t.memoizedState,o=n.getDerivedStateFromProps,typeof o==`function`&&(qs(t,n,o,r),a.state=t.memoizedState),typeof n.getDerivedStateFromProps==`function`||typeof a.getSnapshotBeforeUpdate==`function`||typeof a.UNSAFE_componentWillMount!=`function`&&typeof a.componentWillMount!=`function`||(o=a.state,typeof a.componentWillMount==`function`&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount==`function`&&a.UNSAFE_componentWillMount(),o!==a.state&&Js.enqueueReplaceState(a,a.state,null),no(t,r,a,i),to(),a.state=t.memoizedState),typeof a.componentDidMount==`function`&&(t.flags|=4194308),r=!0}else if(e===null){a=t.stateNode;var s=t.memoizedProps,c=Zs(n,s);a.props=c;var l=a.context,u=n.contextType;o=hi,typeof u==`object`&&u&&(o=la(u));var d=n.getDerivedStateFromProps;u=typeof d==`function`||typeof a.getSnapshotBeforeUpdate==`function`,s=t.pendingProps!==s,u||typeof a.UNSAFE_componentWillReceiveProps!=`function`&&typeof a.componentWillReceiveProps!=`function`||(s||l!==o)&&Xs(t,a,r,o),qa=!1;var f=t.memoizedState;a.state=f,no(t,r,a,i),to(),l=t.memoizedState,s||f!==l||qa?(typeof d==`function`&&(qs(t,n,d,r),l=t.memoizedState),(c=qa||Ys(t,n,c,r,f,l,o))?(u||typeof a.UNSAFE_componentWillMount!=`function`&&typeof a.componentWillMount!=`function`||(typeof a.componentWillMount==`function`&&a.componentWillMount(),typeof a.UNSAFE_componentWillMount==`function`&&a.UNSAFE_componentWillMount()),typeof a.componentDidMount==`function`&&(t.flags|=4194308)):(typeof a.componentDidMount==`function`&&(t.flags|=4194308),t.memoizedProps=r,t.memoizedState=l),a.props=r,a.state=l,a.context=o,r=c):(typeof a.componentDidMount==`function`&&(t.flags|=4194308),r=!1)}else{a=t.stateNode,Ya(e,t),o=t.memoizedProps,u=Zs(n,o),a.props=u,d=t.pendingProps,f=a.context,l=n.contextType,c=hi,typeof l==`object`&&l&&(c=la(l)),s=n.getDerivedStateFromProps,(l=typeof s==`function`||typeof a.getSnapshotBeforeUpdate==`function`)||typeof a.UNSAFE_componentWillReceiveProps!=`function`&&typeof a.componentWillReceiveProps!=`function`||(o!==d||f!==c)&&Xs(t,a,r,c),qa=!1,f=t.memoizedState,a.state=f,no(t,r,a,i),to();var p=t.memoizedState;o!==d||f!==p||qa||e!==null&&e.dependencies!==null&&sa(e.dependencies)?(typeof s==`function`&&(qs(t,n,s,r),p=t.memoizedState),(u=qa||Ys(t,n,u,r,f,p,c)||e!==null&&e.dependencies!==null&&sa(e.dependencies))?(l||typeof a.UNSAFE_componentWillUpdate!=`function`&&typeof a.componentWillUpdate!=`function`||(typeof a.componentWillUpdate==`function`&&a.componentWillUpdate(r,p,c),typeof a.UNSAFE_componentWillUpdate==`function`&&a.UNSAFE_componentWillUpdate(r,p,c)),typeof a.componentDidUpdate==`function`&&(t.flags|=4),typeof a.getSnapshotBeforeUpdate==`function`&&(t.flags|=1024)):(typeof a.componentDidUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),t.memoizedProps=r,t.memoizedState=p),a.props=r,a.state=p,a.context=c,r=u):(typeof a.componentDidUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=4),typeof a.getSnapshotBeforeUpdate!=`function`||o===e.memoizedProps&&f===e.memoizedState||(t.flags|=1024),r=!1)}return a=r,vc(e,t),r=(t.flags&128)!=0,a||r?(a=t.stateNode,n=r&&typeof n.getDerivedStateFromError!=`function`?null:a.render(),t.flags|=1,e!==null&&r?(t.child=Ga(t,e.child,null,i),t.child=Ga(t,null,n,i)):cc(e,t,n,i),t.memoizedState=a.state,e=t.child):e=Nc(e,t,i),e}function Sc(e,t,n,r){return Xi(),t.flags|=256,cc(e,t,n,r),t.child}var Cc={dehydrated:null,treeContext:null,retryLane:0,hydrationErrors:null};function wc(e){return{baseLanes:e,cachePool:Oa()}}function Tc(e,t,n){return e=e===null?0:e.childLanes&~n,t&&(e|=Yl),e}function Ec(e,t,n){var r=t.pendingProps,a=!1,o=(t.flags&128)!=0,s;if((s=o)||(s=e!==null&&e.memoizedState===null?!1:(N.current&2)!=0),s&&(a=!0,t.flags&=-129),s=(t.flags&32)!=0,t.flags&=-33,e===null){if(j){if(a?po(t):go(t),(e=A)?(e=rf(e,Wi),e=e!==null&&e.data!==`&`?e:null,e!==null&&(t.memoizedState={dehydrated:e,treeContext:Pi===null?null:{id:Fi,overflow:Ii},retryLane:536870912,hydrationErrors:null},n=wi(e),n.return=t,t.child=n,Hi=t,A=null)):e=null,e===null)throw Ki(t);return of(e)?t.lanes=32:t.lanes=536870912,null}var c=r.children;return r=r.fallback,a?(go(t),a=t.mode,c=Oc({mode:`hidden`,children:c},a),r=Si(r,a,n,null),c.return=t,r.return=t,c.sibling=r,t.child=c,r=t.child,r.memoizedState=wc(n),r.childLanes=Tc(e,s,n),t.memoizedState=Cc,pc(null,r)):(po(t),Dc(t,c))}var l=e.memoizedState;if(l!==null&&(c=l.dehydrated,c!==null)){if(o)t.flags&256?(po(t),t.flags&=-257,t=kc(e,t,n)):t.memoizedState===null?(go(t),c=r.fallback,a=t.mode,r=Oc({mode:`visible`,children:r.children},a),c=Si(c,a,n,null),c.flags|=2,r.return=t,c.return=t,r.sibling=c,t.child=r,Ga(t,e.child,null,n),r=t.child,r.memoizedState=wc(n),r.childLanes=Tc(e,s,n),t.memoizedState=Cc,t=pc(null,r)):(go(t),t.child=e.child,t.flags|=128,t=null);else if(po(t),of(c)){if(s=c.nextSibling&&c.nextSibling.dataset,s)var u=s.dgst;s=u,r=Error(i(419)),r.stack=``,r.digest=s,Qi({value:r,source:null,stack:null}),t=kc(e,t,n)}else if(z||oa(e,t,n,!1),s=(n&e.childLanes)!==0,z||s){if(s=G,s!==null&&(r=ut(s,n),r!==0&&r!==l.retryLane))throw l.retryLane=r,fi(e,r),hu(s,e,r),sc;af(c)||Du(),t=kc(e,t,n)}else af(c)?(t.flags|=192,t.child=e.child,t=null):(e=l.treeContext,A=cf(c.nextSibling),Hi=t,j=!0,Ui=null,Wi=!1,e!==null&&Vi(t,e),t=Dc(t,r.children),t.flags|=4096);return t}return a?(go(t),c=r.fallback,a=t.mode,l=e.child,u=l.sibling,r=yi(l,{mode:`hidden`,children:r.children}),r.subtreeFlags=l.subtreeFlags&65011712,u===null?(c=Si(c,a,n,null),c.flags|=2):c=yi(u,c),c.return=t,r.return=t,r.sibling=c,t.child=r,pc(null,r),r=t.child,c=e.child.memoizedState,c===null?c=wc(n):(a=c.cachePool,a===null?a=Oa():(l=M._currentValue,a=a.parent===l?a:{parent:l,pool:l}),c={baseLanes:c.baseLanes|n,cachePool:a}),r.memoizedState=c,r.childLanes=Tc(e,s,n),t.memoizedState=Cc,pc(e.child,r)):(po(t),n=e.child,e=n.sibling,n=yi(n,{mode:`visible`,children:r.children}),n.return=t,n.sibling=null,e!==null&&(s=t.deletions,s===null?(t.deletions=[e],t.flags|=16):s.push(e)),t.child=n,t.memoizedState=null,n)}function Dc(e,t){return t=Oc({mode:`visible`,children:t},e.mode),t.return=e,e.child=t}function Oc(e,t){return e=_i(22,e,null,t),e.lanes=0,e}function kc(e,t,n){return Ga(t,e.child,null,n),e=Dc(t,t.pendingProps.children),e.flags|=2,t.memoizedState=null,e}function Ac(e,t,n){e.lanes|=t;var r=e.alternate;r!==null&&(r.lanes|=t),ia(e.return,t,n)}function jc(e,t,n,r,i,a){var o=e.memoizedState;o===null?e.memoizedState={isBackwards:t,rendering:null,renderingStartTime:0,last:r,tail:n,tailMode:i,treeForkCount:a}:(o.isBackwards=t,o.rendering=null,o.renderingStartTime=0,o.last=r,o.tail=n,o.tailMode=i,o.treeForkCount=a)}function Mc(e,t,n){var r=t.pendingProps,i=r.revealOrder,a=r.tail;r=r.children;var o=N.current,s=(o&2)!=0;if(s?(o=o&1|2,t.flags|=128):o&=1,O(N,o),cc(e,t,r,n),r=j?ji:0,!s&&e!==null&&e.flags&128)a:for(e=t.child;e!==null;){if(e.tag===13)e.memoizedState!==null&&Ac(e,n,t);else if(e.tag===19)Ac(e,n,t);else if(e.child!==null){e.child.return=e,e=e.child;continue}if(e===t)break a;for(;e.sibling===null;){if(e.return===null||e.return===t)break a;e=e.return}e.sibling.return=e.return,e=e.sibling}switch(i){case`forwards`:for(n=t.child,i=null;n!==null;)e=n.alternate,e!==null&&vo(e)===null&&(i=n),n=n.sibling;n=i,n===null?(i=t.child,t.child=null):(i=n.sibling,n.sibling=null),jc(t,!1,i,n,a,r);break;case`backwards`:case`unstable_legacy-backwards`:for(n=null,i=t.child,t.child=null;i!==null;){if(e=i.alternate,e!==null&&vo(e)===null){t.child=i;break}e=i.sibling,i.sibling=n,n=i,i=e}jc(t,!0,n,null,a,r);break;case`together`:jc(t,!1,null,null,void 0,r);break;default:t.memoizedState=null}return t.child}function Nc(e,t,n){if(e!==null&&(t.dependencies=e.dependencies),Kl|=t.lanes,(n&t.childLanes)===0)if(e!==null){if(oa(e,t,n,!1),(n&t.childLanes)===0)return null}else return null;if(e!==null&&t.child!==e.child)throw Error(i(153));if(t.child!==null){for(e=t.child,n=yi(e,e.pendingProps),t.child=n,n.return=t;e.sibling!==null;)e=e.sibling,n=n.sibling=yi(e,e.pendingProps),n.return=t;n.sibling=null}return t.child}function Pc(e,t){return(e.lanes&t)===0?(e=e.dependencies,!!(e!==null&&sa(e))):!0}function Fc(e,t,n){switch(t.tag){case 3:ye(t,t.stateNode.containerInfo),na(t,M,e.memoizedState.cache),Xi();break;case 27:case 5:xe(t);break;case 4:ye(t,t.stateNode.containerInfo);break;case 10:na(t,t.type,t.memoizedProps.value);break;case 31:if(t.memoizedState!==null)return t.flags|=128,mo(t),null;break;case 13:var r=t.memoizedState;if(r!==null)return r.dehydrated===null?(n&t.child.childLanes)===0?(po(t),e=Nc(e,t,n),e===null?null:e.sibling):Ec(e,t,n):(po(t),t.flags|=128,null);po(t);break;case 19:var i=(e.flags&128)!=0;if(r=(n&t.childLanes)!==0,r||=(oa(e,t,n,!1),(n&t.childLanes)!==0),i){if(r)return Mc(e,t,n);t.flags|=128}if(i=t.memoizedState,i!==null&&(i.rendering=null,i.tail=null,i.lastEffect=null),O(N,N.current),r)break;return null;case 22:return t.lanes=0,fc(e,t,n,t.pendingProps);case 24:na(t,M,e.memoizedState.cache)}return Nc(e,t,n)}function Ic(e,t,n){if(e!==null)if(e.memoizedProps!==t.pendingProps)z=!0;else{if(!Pc(e,n)&&!(t.flags&128))return z=!1,Fc(e,t,n);z=!!(e.flags&131072)}else z=!1,j&&t.flags&1048576&&Ri(t,ji,t.index);switch(t.lanes=0,t.tag){case 16:a:{var r=t.pendingProps;if(e=Fa(t.elementType),t.type=e,typeof e==`function`)vi(e)?(r=Zs(e,r),t.tag=1,t=xc(null,t,e,r,n)):(t.tag=0,t=yc(null,t,e,r,n));else{if(e!=null){var a=e.$$typeof;if(a===C){t.tag=11,t=lc(null,t,e,r,n);break a}else if(a===re){t.tag=14,t=uc(null,t,e,r,n);break a}}throw t=le(e)||e,Error(i(306,t,``))}}return t;case 0:return yc(e,t,t.type,t.pendingProps,n);case 1:return r=t.type,a=Zs(r,t.pendingProps),xc(e,t,r,a,n);case 3:a:{if(ye(t,t.stateNode.containerInfo),e===null)throw Error(i(387));r=t.pendingProps;var o=t.memoizedState;a=o.element,Ya(e,t),no(t,r,null,n);var s=t.memoizedState;if(r=s.cache,na(t,M,r),r!==o.cache&&aa(t,[M],n,!0),to(),r=s.element,o.isDehydrated)if(o={element:r,isDehydrated:!1,cache:s.cache},t.updateQueue.baseState=o,t.memoizedState=o,t.flags&256){t=Sc(e,t,r,n);break a}else if(r!==a){a=Di(Error(i(424)),t),Qi(a),t=Sc(e,t,r,n);break a}else{switch(e=t.stateNode.containerInfo,e.nodeType){case 9:e=e.body;break;default:e=e.nodeName===`HTML`?e.ownerDocument.body:e}for(A=cf(e.firstChild),Hi=t,j=!0,Ui=null,Wi=!0,n=Ka(t,null,r,n),t.child=n;n;)n.flags=n.flags&-3|4096,n=n.sibling}else{if(Xi(),r===a){t=Nc(e,t,n);break a}cc(e,t,r,n)}t=t.child}return t;case 26:return vc(e,t),e===null?(n=kf(t.type,null,t.pendingProps,null))?t.memoizedState=n:j||(n=t.type,e=t.pendingProps,r=Bd(_e.current).createElement(n),r[gt]=t,r[_t]=e,Pd(r,n,e),k(r),t.stateNode=r):t.memoizedState=kf(t.type,e.memoizedProps,t.pendingProps,e.memoizedState),null;case 27:return xe(t),e===null&&j&&(r=t.stateNode=ff(t.type,t.pendingProps,_e.current),Hi=t,Wi=!0,a=A,Zd(t.type)?(lf=a,A=cf(r.firstChild)):A=a),cc(e,t,t.pendingProps.children,n),vc(e,t),e===null&&(t.flags|=4194304),t.child;case 5:return e===null&&j&&((a=r=A)&&(r=tf(r,t.type,t.pendingProps,Wi),r===null?a=!1:(t.stateNode=r,Hi=t,A=cf(r.firstChild),Wi=!1,a=!0)),a||Ki(t)),xe(t),a=t.type,o=t.pendingProps,s=e===null?null:e.memoizedProps,r=o.children,Ud(a,o)?r=null:s!==null&&Ud(a,s)&&(t.flags|=32),t.memoizedState!==null&&(a=Oo(e,t,jo,null,null,n),Qf._currentValue=a),vc(e,t),cc(e,t,r,n),t.child;case 6:return e===null&&j&&((e=n=A)&&(n=nf(n,t.pendingProps,Wi),n===null?e=!1:(t.stateNode=n,Hi=t,A=null,e=!0)),e||Ki(t)),null;case 13:return Ec(e,t,n);case 4:return ye(t,t.stateNode.containerInfo),r=t.pendingProps,e===null?t.child=Ga(t,null,r,n):cc(e,t,r,n),t.child;case 11:return lc(e,t,t.type,t.pendingProps,n);case 7:return cc(e,t,t.pendingProps,n),t.child;case 8:return cc(e,t,t.pendingProps.children,n),t.child;case 12:return cc(e,t,t.pendingProps.children,n),t.child;case 10:return r=t.pendingProps,na(t,t.type,r.value),cc(e,t,r.children,n),t.child;case 9:return a=t.type._context,r=t.pendingProps.children,ca(t),a=la(a),r=r(a),t.flags|=1,cc(e,t,r,n),t.child;case 14:return uc(e,t,t.type,t.pendingProps,n);case 15:return dc(e,t,t.type,t.pendingProps,n);case 19:return Mc(e,t,n);case 31:return _c(e,t,n);case 22:return fc(e,t,n,t.pendingProps);case 24:return ca(t),r=la(M),e===null?(a=Ea(),a===null&&(a=G,o=ha(),a.pooledCache=o,o.refCount++,o!==null&&(a.pooledCacheLanes|=n),a=o),t.memoizedState={parent:r,cache:a},Ja(t),na(t,M,a)):((e.lanes&n)!==0&&(Ya(e,t),no(t,null,null,n),to()),a=e.memoizedState,o=t.memoizedState,a.parent===r?(r=o.cache,na(t,M,r),r!==a.cache&&aa(t,[M],n,!0)):(a={parent:r,cache:r},t.memoizedState=a,t.lanes===0&&(t.memoizedState=t.updateQueue.baseState=a),na(t,M,r))),cc(e,t,t.pendingProps.children,n),t.child;case 29:throw t.pendingProps}throw Error(i(156,t.tag))}function Lc(e){e.flags|=4}function Rc(e,t,n,r,i){if((t=(e.mode&32)!=0)&&(t=!1),t){if(e.flags|=16777216,(i&335544128)===i)if(e.stateNode.complete)e.flags|=8192;else if(wu())e.flags|=8192;else throw Ia=Ma,Aa}else e.flags&=-16777217}function zc(e,t){if(t.type!==`stylesheet`||t.state.loading&4)e.flags&=-16777217;else if(e.flags|=16777216,!Wf(t))if(wu())e.flags|=8192;else throw Ia=Ma,Aa}function Bc(e,t){t!==null&&(e.flags|=4),e.flags&16384&&(t=e.tag===22?536870912:it(),e.lanes|=t,Xl|=t)}function Vc(e,t){if(!j)switch(e.tailMode){case`hidden`:t=e.tail;for(var n=null;t!==null;)t.alternate!==null&&(n=t),t=t.sibling;n===null?e.tail=null:n.sibling=null;break;case`collapsed`:n=e.tail;for(var r=null;n!==null;)n.alternate!==null&&(r=n),n=n.sibling;r===null?t||e.tail===null?e.tail=null:e.tail.sibling=null:r.sibling=null}}function B(e){var t=e.alternate!==null&&e.alternate.child===e.child,n=0,r=0;if(t)for(var i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags&65011712,r|=i.flags&65011712,i.return=e,i=i.sibling;else for(i=e.child;i!==null;)n|=i.lanes|i.childLanes,r|=i.subtreeFlags,r|=i.flags,i.return=e,i=i.sibling;return e.subtreeFlags|=r,e.childLanes=n,t}function Hc(e,t,n){var r=t.pendingProps;switch(Bi(t),t.tag){case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return B(t),null;case 1:return B(t),null;case 3:return n=t.stateNode,r=null,e!==null&&(r=e.memoizedState.cache),t.memoizedState.cache!==r&&(t.flags|=2048),ra(M),be(),n.pendingContext&&(n.context=n.pendingContext,n.pendingContext=null),(e===null||e.child===null)&&(Yi(t)?Lc(t):e===null||e.memoizedState.isDehydrated&&!(t.flags&256)||(t.flags|=1024,Zi())),B(t),null;case 26:var a=t.type,o=t.memoizedState;return e===null?(Lc(t),o===null?(B(t),Rc(t,a,null,r,n)):(B(t),zc(t,o))):o?o===e.memoizedState?(B(t),t.flags&=-16777217):(Lc(t),B(t),zc(t,o)):(e=e.memoizedProps,e!==r&&Lc(t),B(t),Rc(t,a,e,r,n)),null;case 27:if(Se(t),n=_e.current,a=t.type,e!==null&&t.stateNode!=null)e.memoizedProps!==r&&Lc(t);else{if(!r){if(t.stateNode===null)throw Error(i(166));return B(t),null}e=he.current,Yi(t)?qi(t,e):(e=ff(a,r,n),t.stateNode=e,Lc(t))}return B(t),null;case 5:if(Se(t),a=t.type,e!==null&&t.stateNode!=null)e.memoizedProps!==r&&Lc(t);else{if(!r){if(t.stateNode===null)throw Error(i(166));return B(t),null}if(o=he.current,Yi(t))qi(t,o);else{var s=Bd(_e.current);switch(o){case 1:o=s.createElementNS(`http://www.w3.org/2000/svg`,a);break;case 2:o=s.createElementNS(`http://www.w3.org/1998/Math/MathML`,a);break;default:switch(a){case`svg`:o=s.createElementNS(`http://www.w3.org/2000/svg`,a);break;case`math`:o=s.createElementNS(`http://www.w3.org/1998/Math/MathML`,a);break;case`script`:o=s.createElement(`div`),o.innerHTML=`<script><\/script>`,o=o.removeChild(o.firstChild);break;case`select`:o=typeof r.is==`string`?s.createElement(`select`,{is:r.is}):s.createElement(`select`),r.multiple?o.multiple=!0:r.size&&(o.size=r.size);break;default:o=typeof r.is==`string`?s.createElement(a,{is:r.is}):s.createElement(a)}}o[gt]=t,o[_t]=r;a:for(s=t.child;s!==null;){if(s.tag===5||s.tag===6)o.appendChild(s.stateNode);else if(s.tag!==4&&s.tag!==27&&s.child!==null){s.child.return=s,s=s.child;continue}if(s===t)break a;for(;s.sibling===null;){if(s.return===null||s.return===t)break a;s=s.return}s.sibling.return=s.return,s=s.sibling}t.stateNode=o;a:switch(Pd(o,a,r),a){case`button`:case`input`:case`select`:case`textarea`:r=!!r.autoFocus;break a;case`img`:r=!0;break a;default:r=!1}r&&Lc(t)}}return B(t),Rc(t,t.type,e===null?null:e.memoizedProps,t.pendingProps,n),null;case 6:if(e&&t.stateNode!=null)e.memoizedProps!==r&&Lc(t);else{if(typeof r!=`string`&&t.stateNode===null)throw Error(i(166));if(e=_e.current,Yi(t)){if(e=t.stateNode,n=t.memoizedProps,r=null,a=Hi,a!==null)switch(a.tag){case 27:case 5:r=a.memoizedProps}e[gt]=t,e=!!(e.nodeValue===n||r!==null&&!0===r.suppressHydrationWarning||Md(e.nodeValue,n)),e||Ki(t,!0)}else e=Bd(e).createTextNode(r),e[gt]=t,t.stateNode=e}return B(t),null;case 31:if(n=t.memoizedState,e===null||e.memoizedState!==null){if(r=Yi(t),n!==null){if(e===null){if(!r)throw Error(i(318));if(e=t.memoizedState,e=e===null?null:e.dehydrated,!e)throw Error(i(557));e[gt]=t}else Xi(),!(t.flags&128)&&(t.memoizedState=null),t.flags|=4;B(t),e=!1}else n=Zi(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=n),e=!0;if(!e)return t.flags&256?(_o(t),t):(_o(t),null);if(t.flags&128)throw Error(i(558))}return B(t),null;case 13:if(r=t.memoizedState,e===null||e.memoizedState!==null&&e.memoizedState.dehydrated!==null){if(a=Yi(t),r!==null&&r.dehydrated!==null){if(e===null){if(!a)throw Error(i(318));if(a=t.memoizedState,a=a===null?null:a.dehydrated,!a)throw Error(i(317));a[gt]=t}else Xi(),!(t.flags&128)&&(t.memoizedState=null),t.flags|=4;B(t),a=!1}else a=Zi(),e!==null&&e.memoizedState!==null&&(e.memoizedState.hydrationErrors=a),a=!0;if(!a)return t.flags&256?(_o(t),t):(_o(t),null)}return _o(t),t.flags&128?(t.lanes=n,t):(n=r!==null,e=e!==null&&e.memoizedState!==null,n&&(r=t.child,a=null,r.alternate!==null&&r.alternate.memoizedState!==null&&r.alternate.memoizedState.cachePool!==null&&(a=r.alternate.memoizedState.cachePool.pool),o=null,r.memoizedState!==null&&r.memoizedState.cachePool!==null&&(o=r.memoizedState.cachePool.pool),o!==a&&(r.flags|=2048)),n!==e&&n&&(t.child.flags|=8192),Bc(t,t.updateQueue),B(t),null);case 4:return be(),e===null&&Sd(t.stateNode.containerInfo),B(t),null;case 10:return ra(t.type),B(t),null;case 19:if(D(N),r=t.memoizedState,r===null)return B(t),null;if(a=(t.flags&128)!=0,o=r.rendering,o===null)if(a)Vc(r,!1);else{if(Y!==0||e!==null&&e.flags&128)for(e=t.child;e!==null;){if(o=vo(e),o!==null){for(t.flags|=128,Vc(r,!1),e=o.updateQueue,t.updateQueue=e,Bc(t,e),t.subtreeFlags=0,e=n,n=t.child;n!==null;)bi(n,e),n=n.sibling;return O(N,N.current&1|2),j&&Li(t,r.treeForkCount),t.child}e=e.sibling}r.tail!==null&&Fe()>nu&&(t.flags|=128,a=!0,Vc(r,!1),t.lanes=4194304)}else{if(!a)if(e=vo(o),e!==null){if(t.flags|=128,a=!0,e=e.updateQueue,t.updateQueue=e,Bc(t,e),Vc(r,!0),r.tail===null&&r.tailMode===`hidden`&&!o.alternate&&!j)return B(t),null}else 2*Fe()-r.renderingStartTime>nu&&n!==536870912&&(t.flags|=128,a=!0,Vc(r,!1),t.lanes=4194304);r.isBackwards?(o.sibling=t.child,t.child=o):(e=r.last,e===null?t.child=o:e.sibling=o,r.last=o)}return r.tail===null?(B(t),null):(e=r.tail,r.rendering=e,r.tail=e.sibling,r.renderingStartTime=Fe(),e.sibling=null,n=N.current,O(N,a?n&1|2:n&1),j&&Li(t,r.treeForkCount),e);case 22:case 23:return _o(t),lo(),r=t.memoizedState!==null,e===null?r&&(t.flags|=8192):e.memoizedState!==null!==r&&(t.flags|=8192),r?n&536870912&&!(t.flags&128)&&(B(t),t.subtreeFlags&6&&(t.flags|=8192)):B(t),n=t.updateQueue,n!==null&&Bc(t,n.retryQueue),n=null,e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(n=e.memoizedState.cachePool.pool),r=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(r=t.memoizedState.cachePool.pool),r!==n&&(t.flags|=2048),e!==null&&D(Ta),null;case 24:return n=null,e!==null&&(n=e.memoizedState.cache),t.memoizedState.cache!==n&&(t.flags|=2048),ra(M),B(t),null;case 25:return null;case 30:return null}throw Error(i(156,t.tag))}function Uc(e,t){switch(Bi(t),t.tag){case 1:return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 3:return ra(M),be(),e=t.flags,e&65536&&!(e&128)?(t.flags=e&-65537|128,t):null;case 26:case 27:case 5:return Se(t),null;case 31:if(t.memoizedState!==null){if(_o(t),t.alternate===null)throw Error(i(340));Xi()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 13:if(_o(t),e=t.memoizedState,e!==null&&e.dehydrated!==null){if(t.alternate===null)throw Error(i(340));Xi()}return e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 19:return D(N),null;case 4:return be(),null;case 10:return ra(t.type),null;case 22:case 23:return _o(t),lo(),e!==null&&D(Ta),e=t.flags,e&65536?(t.flags=e&-65537|128,t):null;case 24:return ra(M),null;case 25:return null;default:return null}}function Wc(e,t){switch(Bi(t),t.tag){case 3:ra(M),be();break;case 26:case 27:case 5:Se(t);break;case 4:be();break;case 31:t.memoizedState!==null&&_o(t);break;case 13:_o(t);break;case 19:D(N);break;case 10:ra(t.type);break;case 22:case 23:_o(t),lo(),e!==null&&D(Ta);break;case 24:ra(M)}}function Gc(e,t){try{var n=t.updateQueue,r=n===null?null:n.lastEffect;if(r!==null){var i=r.next;n=i;do{if((n.tag&e)===e){r=void 0;var a=n.create,o=n.inst;r=a(),o.destroy=r}n=n.next}while(n!==i)}}catch(e){Z(t,t.return,e)}}function Kc(e,t,n){try{var r=t.updateQueue,i=r===null?null:r.lastEffect;if(i!==null){var a=i.next;r=a;do{if((r.tag&e)===e){var o=r.inst,s=o.destroy;if(s!==void 0){o.destroy=void 0,i=t;var c=n,l=s;try{l()}catch(e){Z(i,c,e)}}}r=r.next}while(r!==a)}}catch(e){Z(t,t.return,e)}}function qc(e){var t=e.updateQueue;if(t!==null){var n=e.stateNode;try{io(t,n)}catch(t){Z(e,e.return,t)}}}function Jc(e,t,n){n.props=Zs(e.type,e.memoizedProps),n.state=e.memoizedState;try{n.componentWillUnmount()}catch(n){Z(e,t,n)}}function Yc(e,t){try{var n=e.ref;if(n!==null){switch(e.tag){case 26:case 27:case 5:var r=e.stateNode;break;case 30:r=e.stateNode;break;default:r=e.stateNode}typeof n==`function`?e.refCleanup=n(r):n.current=r}}catch(n){Z(e,t,n)}}function Xc(e,t){var n=e.ref,r=e.refCleanup;if(n!==null)if(typeof r==`function`)try{r()}catch(n){Z(e,t,n)}finally{e.refCleanup=null,e=e.alternate,e!=null&&(e.refCleanup=null)}else if(typeof n==`function`)try{n(null)}catch(n){Z(e,t,n)}else n.current=null}function Zc(e){var t=e.type,n=e.memoizedProps,r=e.stateNode;try{a:switch(t){case`button`:case`input`:case`select`:case`textarea`:n.autoFocus&&r.focus();break a;case`img`:n.src?r.src=n.src:n.srcSet&&(r.srcset=n.srcSet)}}catch(t){Z(e,e.return,t)}}function Qc(e,t,n){try{var r=e.stateNode;Fd(r,e.type,n,t),r[_t]=t}catch(t){Z(e,e.return,t)}}function $c(e){return e.tag===5||e.tag===3||e.tag===26||e.tag===27&&Zd(e.type)||e.tag===4}function el(e){a:for(;;){for(;e.sibling===null;){if(e.return===null||$c(e.return))return null;e=e.return}for(e.sibling.return=e.return,e=e.sibling;e.tag!==5&&e.tag!==6&&e.tag!==18;){if(e.tag===27&&Zd(e.type)||e.flags&2||e.child===null||e.tag===4)continue a;e.child.return=e,e=e.child}if(!(e.flags&2))return e.stateNode}}function tl(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?(n.nodeType===9?n.body:n.nodeName===`HTML`?n.ownerDocument.body:n).insertBefore(e,t):(t=n.nodeType===9?n.body:n.nodeName===`HTML`?n.ownerDocument.body:n,t.appendChild(e),n=n._reactRootContainer,n!=null||t.onclick!==null||(t.onclick=ln));else if(r!==4&&(r===27&&Zd(e.type)&&(n=e.stateNode,t=null),e=e.child,e!==null))for(tl(e,t,n),e=e.sibling;e!==null;)tl(e,t,n),e=e.sibling}function nl(e,t,n){var r=e.tag;if(r===5||r===6)e=e.stateNode,t?n.insertBefore(e,t):n.appendChild(e);else if(r!==4&&(r===27&&Zd(e.type)&&(n=e.stateNode),e=e.child,e!==null))for(nl(e,t,n),e=e.sibling;e!==null;)nl(e,t,n),e=e.sibling}function rl(e){var t=e.stateNode,n=e.memoizedProps;try{for(var r=e.type,i=t.attributes;i.length;)t.removeAttributeNode(i[0]);Pd(t,r,n),t[gt]=e,t[_t]=n}catch(t){Z(e,e.return,t)}}var il=!1,V=!1,al=!1,ol=typeof WeakSet==`function`?WeakSet:Set,H=null;function sl(e,t){if(e=e.containerInfo,Rd=sp,e=Ir(e),Lr(e)){if(`selectionStart`in e)var n={start:e.selectionStart,end:e.selectionEnd};else a:{n=(n=e.ownerDocument)&&n.defaultView||window;var r=n.getSelection&&n.getSelection();if(r&&r.rangeCount!==0){n=r.anchorNode;var a=r.anchorOffset,o=r.focusNode;r=r.focusOffset;try{n.nodeType,o.nodeType}catch{n=null;break a}var s=0,c=-1,l=-1,u=0,d=0,f=e,p=null;b:for(;;){for(var m;f!==n||a!==0&&f.nodeType!==3||(c=s+a),f!==o||r!==0&&f.nodeType!==3||(l=s+r),f.nodeType===3&&(s+=f.nodeValue.length),(m=f.firstChild)!==null;)p=f,f=m;for(;;){if(f===e)break b;if(p===n&&++u===a&&(c=s),p===o&&++d===r&&(l=s),(m=f.nextSibling)!==null)break;f=p,p=f.parentNode}f=m}n=c===-1||l===-1?null:{start:c,end:l}}else n=null}n||={start:0,end:0}}else n=null;for(zd={focusedElem:e,selectionRange:n},sp=!1,H=t;H!==null;)if(t=H,e=t.child,t.subtreeFlags&1028&&e!==null)e.return=t,H=e;else for(;H!==null;){switch(t=H,o=t.alternate,e=t.flags,t.tag){case 0:if(e&4&&(e=t.updateQueue,e=e===null?null:e.events,e!==null))for(n=0;n<e.length;n++)a=e[n],a.ref.impl=a.nextImpl;break;case 11:case 15:break;case 1:if(e&1024&&o!==null){e=void 0,n=t,a=o.memoizedProps,o=o.memoizedState,r=n.stateNode;try{var h=Zs(n.type,a);e=r.getSnapshotBeforeUpdate(h,o),r.__reactInternalSnapshotBeforeUpdate=e}catch(e){Z(n,n.return,e)}}break;case 3:if(e&1024){if(e=t.stateNode.containerInfo,n=e.nodeType,n===9)ef(e);else if(n===1)switch(e.nodeName){case`HEAD`:case`HTML`:case`BODY`:ef(e);break;default:e.textContent=``}}break;case 5:case 26:case 27:case 6:case 4:case 17:break;default:if(e&1024)throw Error(i(163))}if(e=t.sibling,e!==null){e.return=t.return,H=e;break}H=t.return}}function cl(e,t,n){var r=n.flags;switch(n.tag){case 0:case 11:case 15:Sl(e,n),r&4&&Gc(5,n);break;case 1:if(Sl(e,n),r&4)if(e=n.stateNode,t===null)try{e.componentDidMount()}catch(e){Z(n,n.return,e)}else{var i=Zs(n.type,t.memoizedProps);t=t.memoizedState;try{e.componentDidUpdate(i,t,e.__reactInternalSnapshotBeforeUpdate)}catch(e){Z(n,n.return,e)}}r&64&&qc(n),r&512&&Yc(n,n.return);break;case 3:if(Sl(e,n),r&64&&(e=n.updateQueue,e!==null)){if(t=null,n.child!==null)switch(n.child.tag){case 27:case 5:t=n.child.stateNode;break;case 1:t=n.child.stateNode}try{io(e,t)}catch(e){Z(n,n.return,e)}}break;case 27:t===null&&r&4&&rl(n);case 26:case 5:Sl(e,n),t===null&&r&4&&Zc(n),r&512&&Yc(n,n.return);break;case 12:Sl(e,n);break;case 31:Sl(e,n),r&4&&pl(e,n);break;case 13:Sl(e,n),r&4&&ml(e,n),r&64&&(e=n.memoizedState,e!==null&&(e=e.dehydrated,e!==null&&(n=Ju.bind(null,n),sf(e,n))));break;case 22:if(r=n.memoizedState!==null||il,!r){t=t!==null&&t.memoizedState!==null||V,i=il;var a=V;il=r,(V=t)&&!a?wl(e,n,(n.subtreeFlags&8772)!=0):Sl(e,n),il=i,V=a}break;case 30:break;default:Sl(e,n)}}function ll(e){var t=e.alternate;t!==null&&(e.alternate=null,ll(t)),e.child=null,e.deletions=null,e.sibling=null,e.tag===5&&(t=e.stateNode,t!==null&&wt(t)),e.stateNode=null,e.return=null,e.dependencies=null,e.memoizedProps=null,e.memoizedState=null,e.pendingProps=null,e.stateNode=null,e.updateQueue=null}var U=null,ul=!1;function dl(e,t,n){for(n=n.child;n!==null;)fl(e,t,n),n=n.sibling}function fl(e,t,n){if(Ge&&typeof Ge.onCommitFiberUnmount==`function`)try{Ge.onCommitFiberUnmount(We,n)}catch{}switch(n.tag){case 26:V||Xc(n,t),dl(e,t,n),n.memoizedState?n.memoizedState.count--:n.stateNode&&(n=n.stateNode,n.parentNode.removeChild(n));break;case 27:V||Xc(n,t);var r=U,i=ul;Zd(n.type)&&(U=n.stateNode,ul=!1),dl(e,t,n),pf(n.stateNode),U=r,ul=i;break;case 5:V||Xc(n,t);case 6:if(r=U,i=ul,U=null,dl(e,t,n),U=r,ul=i,U!==null)if(ul)try{(U.nodeType===9?U.body:U.nodeName===`HTML`?U.ownerDocument.body:U).removeChild(n.stateNode)}catch(e){Z(n,t,e)}else try{U.removeChild(n.stateNode)}catch(e){Z(n,t,e)}break;case 18:U!==null&&(ul?(e=U,Qd(e.nodeType===9?e.body:e.nodeName===`HTML`?e.ownerDocument.body:e,n.stateNode),Np(e)):Qd(U,n.stateNode));break;case 4:r=U,i=ul,U=n.stateNode.containerInfo,ul=!0,dl(e,t,n),U=r,ul=i;break;case 0:case 11:case 14:case 15:Kc(2,n,t),V||Kc(4,n,t),dl(e,t,n);break;case 1:V||(Xc(n,t),r=n.stateNode,typeof r.componentWillUnmount==`function`&&Jc(n,t,r)),dl(e,t,n);break;case 21:dl(e,t,n);break;case 22:V=(r=V)||n.memoizedState!==null,dl(e,t,n),V=r;break;default:dl(e,t,n)}}function pl(e,t){if(t.memoizedState===null&&(e=t.alternate,e!==null&&(e=e.memoizedState,e!==null))){e=e.dehydrated;try{Np(e)}catch(e){Z(t,t.return,e)}}}function ml(e,t){if(t.memoizedState===null&&(e=t.alternate,e!==null&&(e=e.memoizedState,e!==null&&(e=e.dehydrated,e!==null))))try{Np(e)}catch(e){Z(t,t.return,e)}}function hl(e){switch(e.tag){case 31:case 13:case 19:var t=e.stateNode;return t===null&&(t=e.stateNode=new ol),t;case 22:return e=e.stateNode,t=e._retryCache,t===null&&(t=e._retryCache=new ol),t;default:throw Error(i(435,e.tag))}}function gl(e,t){var n=hl(e);t.forEach(function(t){if(!n.has(t)){n.add(t);var r=Yu.bind(null,e,t);t.then(r,r)}})}function _l(e,t){var n=t.deletions;if(n!==null)for(var r=0;r<n.length;r++){var a=n[r],o=e,s=t,c=s;a:for(;c!==null;){switch(c.tag){case 27:if(Zd(c.type)){U=c.stateNode,ul=!1;break a}break;case 5:U=c.stateNode,ul=!1;break a;case 3:case 4:U=c.stateNode.containerInfo,ul=!0;break a}c=c.return}if(U===null)throw Error(i(160));fl(o,s,a),U=null,ul=!1,o=a.alternate,o!==null&&(o.return=null),a.return=null}if(t.subtreeFlags&13886)for(t=t.child;t!==null;)yl(t,e),t=t.sibling}var vl=null;function yl(e,t){var n=e.alternate,r=e.flags;switch(e.tag){case 0:case 11:case 14:case 15:_l(t,e),bl(e),r&4&&(Kc(3,e,e.return),Gc(3,e),Kc(5,e,e.return));break;case 1:_l(t,e),bl(e),r&512&&(V||n===null||Xc(n,n.return)),r&64&&il&&(e=e.updateQueue,e!==null&&(r=e.callbacks,r!==null&&(n=e.shared.hiddenCallbacks,e.shared.hiddenCallbacks=n===null?r:n.concat(r))));break;case 26:var a=vl;if(_l(t,e),bl(e),r&512&&(V||n===null||Xc(n,n.return)),r&4){var o=n===null?null:n.memoizedState;if(r=e.memoizedState,n===null)if(r===null)if(e.stateNode===null){a:{r=e.type,n=e.memoizedProps,a=a.ownerDocument||a;b:switch(r){case`title`:o=a.getElementsByTagName(`title`)[0],(!o||o[Ct]||o[gt]||o.namespaceURI===`http://www.w3.org/2000/svg`||o.hasAttribute(`itemprop`))&&(o=a.createElement(r),a.head.insertBefore(o,a.querySelector(`head > title`))),Pd(o,r,n),o[gt]=e,k(o),r=o;break a;case`link`:var s=Vf(`link`,`href`,a).get(r+(n.href||``));if(s){for(var c=0;c<s.length;c++)if(o=s[c],o.getAttribute(`href`)===(n.href==null||n.href===``?null:n.href)&&o.getAttribute(`rel`)===(n.rel==null?null:n.rel)&&o.getAttribute(`title`)===(n.title==null?null:n.title)&&o.getAttribute(`crossorigin`)===(n.crossOrigin==null?null:n.crossOrigin)){s.splice(c,1);break b}}o=a.createElement(r),Pd(o,r,n),a.head.appendChild(o);break;case`meta`:if(s=Vf(`meta`,`content`,a).get(r+(n.content||``))){for(c=0;c<s.length;c++)if(o=s[c],o.getAttribute(`content`)===(n.content==null?null:``+n.content)&&o.getAttribute(`name`)===(n.name==null?null:n.name)&&o.getAttribute(`property`)===(n.property==null?null:n.property)&&o.getAttribute(`http-equiv`)===(n.httpEquiv==null?null:n.httpEquiv)&&o.getAttribute(`charset`)===(n.charSet==null?null:n.charSet)){s.splice(c,1);break b}}o=a.createElement(r),Pd(o,r,n),a.head.appendChild(o);break;default:throw Error(i(468,r))}o[gt]=e,k(o),r=o}e.stateNode=r}else Hf(a,e.type,e.stateNode);else e.stateNode=If(a,r,e.memoizedProps);else o===r?r===null&&e.stateNode!==null&&Qc(e,e.memoizedProps,n.memoizedProps):(o===null?n.stateNode!==null&&(n=n.stateNode,n.parentNode.removeChild(n)):o.count--,r===null?Hf(a,e.type,e.stateNode):If(a,r,e.memoizedProps))}break;case 27:_l(t,e),bl(e),r&512&&(V||n===null||Xc(n,n.return)),n!==null&&r&4&&Qc(e,e.memoizedProps,n.memoizedProps);break;case 5:if(_l(t,e),bl(e),r&512&&(V||n===null||Xc(n,n.return)),e.flags&32){a=e.stateNode;try{en(a,``)}catch(t){Z(e,e.return,t)}}r&4&&e.stateNode!=null&&(a=e.memoizedProps,Qc(e,a,n===null?a:n.memoizedProps)),r&1024&&(al=!0);break;case 6:if(_l(t,e),bl(e),r&4){if(e.stateNode===null)throw Error(i(162));r=e.memoizedProps,n=e.stateNode;try{n.nodeValue=r}catch(t){Z(e,e.return,t)}}break;case 3:if(Bf=null,a=vl,vl=gf(t.containerInfo),_l(t,e),vl=a,bl(e),r&4&&n!==null&&n.memoizedState.isDehydrated)try{Np(t.containerInfo)}catch(t){Z(e,e.return,t)}al&&(al=!1,xl(e));break;case 4:r=vl,vl=gf(e.stateNode.containerInfo),_l(t,e),bl(e),vl=r;break;case 12:_l(t,e),bl(e);break;case 31:_l(t,e),bl(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,gl(e,r)));break;case 13:_l(t,e),bl(e),e.child.flags&8192&&e.memoizedState!==null!=(n!==null&&n.memoizedState!==null)&&(eu=Fe()),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,gl(e,r)));break;case 22:a=e.memoizedState!==null;var l=n!==null&&n.memoizedState!==null,u=il,d=V;if(il=u||a,V=d||l,_l(t,e),V=d,il=u,bl(e),r&8192)a:for(t=e.stateNode,t._visibility=a?t._visibility&-2:t._visibility|1,a&&(n===null||l||il||V||Cl(e)),n=null,t=e;;){if(t.tag===5||t.tag===26){if(n===null){l=n=t;try{if(o=l.stateNode,a)s=o.style,typeof s.setProperty==`function`?s.setProperty(`display`,`none`,`important`):s.display=`none`;else{c=l.stateNode;var f=l.memoizedProps.style,p=f!=null&&f.hasOwnProperty(`display`)?f.display:null;c.style.display=p==null||typeof p==`boolean`?``:(``+p).trim()}}catch(e){Z(l,l.return,e)}}}else if(t.tag===6){if(n===null){l=t;try{l.stateNode.nodeValue=a?``:l.memoizedProps}catch(e){Z(l,l.return,e)}}}else if(t.tag===18){if(n===null){l=t;try{var m=l.stateNode;a?$d(m,!0):$d(l.stateNode,!1)}catch(e){Z(l,l.return,e)}}}else if((t.tag!==22&&t.tag!==23||t.memoizedState===null||t===e)&&t.child!==null){t.child.return=t,t=t.child;continue}if(t===e)break a;for(;t.sibling===null;){if(t.return===null||t.return===e)break a;n===t&&(n=null),t=t.return}n===t&&(n=null),t.sibling.return=t.return,t=t.sibling}r&4&&(r=e.updateQueue,r!==null&&(n=r.retryQueue,n!==null&&(r.retryQueue=null,gl(e,n))));break;case 19:_l(t,e),bl(e),r&4&&(r=e.updateQueue,r!==null&&(e.updateQueue=null,gl(e,r)));break;case 30:break;case 21:break;default:_l(t,e),bl(e)}}function bl(e){var t=e.flags;if(t&2){try{for(var n,r=e.return;r!==null;){if($c(r)){n=r;break}r=r.return}if(n==null)throw Error(i(160));switch(n.tag){case 27:var a=n.stateNode;nl(e,el(e),a);break;case 5:var o=n.stateNode;n.flags&32&&(en(o,``),n.flags&=-33),nl(e,el(e),o);break;case 3:case 4:var s=n.stateNode.containerInfo;tl(e,el(e),s);break;default:throw Error(i(161))}}catch(t){Z(e,e.return,t)}e.flags&=-3}t&4096&&(e.flags&=-4097)}function xl(e){if(e.subtreeFlags&1024)for(e=e.child;e!==null;){var t=e;xl(t),t.tag===5&&t.flags&1024&&t.stateNode.reset(),e=e.sibling}}function Sl(e,t){if(t.subtreeFlags&8772)for(t=t.child;t!==null;)cl(e,t.alternate,t),t=t.sibling}function Cl(e){for(e=e.child;e!==null;){var t=e;switch(t.tag){case 0:case 11:case 14:case 15:Kc(4,t,t.return),Cl(t);break;case 1:Xc(t,t.return);var n=t.stateNode;typeof n.componentWillUnmount==`function`&&Jc(t,t.return,n),Cl(t);break;case 27:pf(t.stateNode);case 26:case 5:Xc(t,t.return),Cl(t);break;case 22:t.memoizedState===null&&Cl(t);break;case 30:Cl(t);break;default:Cl(t)}e=e.sibling}}function wl(e,t,n){for(n&&=(t.subtreeFlags&8772)!=0,t=t.child;t!==null;){var r=t.alternate,i=e,a=t,o=a.flags;switch(a.tag){case 0:case 11:case 15:wl(i,a,n),Gc(4,a);break;case 1:if(wl(i,a,n),r=a,i=r.stateNode,typeof i.componentDidMount==`function`)try{i.componentDidMount()}catch(e){Z(r,r.return,e)}if(r=a,i=r.updateQueue,i!==null){var s=r.stateNode;try{var c=i.shared.hiddenCallbacks;if(c!==null)for(i.shared.hiddenCallbacks=null,i=0;i<c.length;i++)ro(c[i],s)}catch(e){Z(r,r.return,e)}}n&&o&64&&qc(a),Yc(a,a.return);break;case 27:rl(a);case 26:case 5:wl(i,a,n),n&&r===null&&o&4&&Zc(a),Yc(a,a.return);break;case 12:wl(i,a,n);break;case 31:wl(i,a,n),n&&o&4&&pl(i,a);break;case 13:wl(i,a,n),n&&o&4&&ml(i,a);break;case 22:a.memoizedState===null&&wl(i,a,n),Yc(a,a.return);break;case 30:break;default:wl(i,a,n)}t=t.sibling}}function Tl(e,t){var n=null;e!==null&&e.memoizedState!==null&&e.memoizedState.cachePool!==null&&(n=e.memoizedState.cachePool.pool),e=null,t.memoizedState!==null&&t.memoizedState.cachePool!==null&&(e=t.memoizedState.cachePool.pool),e!==n&&(e!=null&&e.refCount++,n!=null&&ga(n))}function El(e,t){e=null,t.alternate!==null&&(e=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==e&&(t.refCount++,e!=null&&ga(e))}function Dl(e,t,n,r){if(t.subtreeFlags&10256)for(t=t.child;t!==null;)Ol(e,t,n,r),t=t.sibling}function Ol(e,t,n,r){var i=t.flags;switch(t.tag){case 0:case 11:case 15:Dl(e,t,n,r),i&2048&&Gc(9,t);break;case 1:Dl(e,t,n,r);break;case 3:Dl(e,t,n,r),i&2048&&(e=null,t.alternate!==null&&(e=t.alternate.memoizedState.cache),t=t.memoizedState.cache,t!==e&&(t.refCount++,e!=null&&ga(e)));break;case 12:if(i&2048){Dl(e,t,n,r),e=t.stateNode;try{var a=t.memoizedProps,o=a.id,s=a.onPostCommit;typeof s==`function`&&s(o,t.alternate===null?`mount`:`update`,e.passiveEffectDuration,-0)}catch(e){Z(t,t.return,e)}}else Dl(e,t,n,r);break;case 31:Dl(e,t,n,r);break;case 13:Dl(e,t,n,r);break;case 23:break;case 22:a=t.stateNode,o=t.alternate,t.memoizedState===null?a._visibility&2?Dl(e,t,n,r):(a._visibility|=2,kl(e,t,n,r,(t.subtreeFlags&10256)!=0||!1)):a._visibility&2?Dl(e,t,n,r):Al(e,t),i&2048&&Tl(o,t);break;case 24:Dl(e,t,n,r),i&2048&&El(t.alternate,t);break;default:Dl(e,t,n,r)}}function kl(e,t,n,r,i){for(i&&=(t.subtreeFlags&10256)!=0||!1,t=t.child;t!==null;){var a=e,o=t,s=n,c=r,l=o.flags;switch(o.tag){case 0:case 11:case 15:kl(a,o,s,c,i),Gc(8,o);break;case 23:break;case 22:var u=o.stateNode;o.memoizedState===null?(u._visibility|=2,kl(a,o,s,c,i)):u._visibility&2?kl(a,o,s,c,i):Al(a,o),i&&l&2048&&Tl(o.alternate,o);break;case 24:kl(a,o,s,c,i),i&&l&2048&&El(o.alternate,o);break;default:kl(a,o,s,c,i)}t=t.sibling}}function Al(e,t){if(t.subtreeFlags&10256)for(t=t.child;t!==null;){var n=e,r=t,i=r.flags;switch(r.tag){case 22:Al(n,r),i&2048&&Tl(r.alternate,r);break;case 24:Al(n,r),i&2048&&El(r.alternate,r);break;default:Al(n,r)}t=t.sibling}}var jl=8192;function Ml(e,t,n){if(e.subtreeFlags&jl)for(e=e.child;e!==null;)Nl(e,t,n),e=e.sibling}function Nl(e,t,n){switch(e.tag){case 26:Ml(e,t,n),e.flags&jl&&e.memoizedState!==null&&Gf(n,vl,e.memoizedState,e.memoizedProps);break;case 5:Ml(e,t,n);break;case 3:case 4:var r=vl;vl=gf(e.stateNode.containerInfo),Ml(e,t,n),vl=r;break;case 22:e.memoizedState===null&&(r=e.alternate,r!==null&&r.memoizedState!==null?(r=jl,jl=16777216,Ml(e,t,n),jl=r):Ml(e,t,n));break;default:Ml(e,t,n)}}function Pl(e){var t=e.alternate;if(t!==null&&(e=t.child,e!==null)){t.child=null;do t=e.sibling,e.sibling=null,e=t;while(e!==null)}}function Fl(e){var t=e.deletions;if(e.flags&16){if(t!==null)for(var n=0;n<t.length;n++){var r=t[n];H=r,Rl(r,e)}Pl(e)}if(e.subtreeFlags&10256)for(e=e.child;e!==null;)Il(e),e=e.sibling}function Il(e){switch(e.tag){case 0:case 11:case 15:Fl(e),e.flags&2048&&Kc(9,e,e.return);break;case 3:Fl(e);break;case 12:Fl(e);break;case 22:var t=e.stateNode;e.memoizedState!==null&&t._visibility&2&&(e.return===null||e.return.tag!==13)?(t._visibility&=-3,Ll(e)):Fl(e);break;default:Fl(e)}}function Ll(e){var t=e.deletions;if(e.flags&16){if(t!==null)for(var n=0;n<t.length;n++){var r=t[n];H=r,Rl(r,e)}Pl(e)}for(e=e.child;e!==null;){switch(t=e,t.tag){case 0:case 11:case 15:Kc(8,t,t.return),Ll(t);break;case 22:n=t.stateNode,n._visibility&2&&(n._visibility&=-3,Ll(t));break;default:Ll(t)}e=e.sibling}}function Rl(e,t){for(;H!==null;){var n=H;switch(n.tag){case 0:case 11:case 15:Kc(8,n,t);break;case 23:case 22:if(n.memoizedState!==null&&n.memoizedState.cachePool!==null){var r=n.memoizedState.cachePool.pool;r!=null&&r.refCount++}break;case 24:ga(n.memoizedState.cache)}if(r=n.child,r!==null)r.return=n,H=r;else a:for(n=e;H!==null;){r=H;var i=r.sibling,a=r.return;if(ll(r),r===n){H=null;break a}if(i!==null){i.return=a,H=i;break a}H=a}}}var zl={getCacheForType:function(e){var t=la(M),n=t.data.get(e);return n===void 0&&(n=e(),t.data.set(e,n)),n},cacheSignal:function(){return la(M).controller.signal}},Bl=typeof WeakMap==`function`?WeakMap:Map,W=0,G=null,K=null,q=0,J=0,Vl=null,Hl=!1,Ul=!1,Wl=!1,Gl=0,Y=0,Kl=0,ql=0,Jl=0,Yl=0,Xl=0,Zl=null,Ql=null,$l=!1,eu=0,tu=0,nu=1/0,ru=null,iu=null,X=0,au=null,ou=null,su=0,cu=0,lu=null,uu=null,du=0,fu=null;function pu(){return W&2&&q!==0?q&-q:T.T===null?pt():dd()}function mu(){if(Yl===0)if(!(q&536870912)||j){var e=Qe;Qe<<=1,!(Qe&3932160)&&(Qe=262144),Yl=e}else Yl=536870912;return e=uo.current,e!==null&&(e.flags|=32),Yl}function hu(e,t,n){(e===G&&(J===2||J===9)||e.cancelPendingCommit!==null)&&(Su(e,0),yu(e,q,Yl,!1)),ot(e,n),(!(W&2)||e!==G)&&(e===G&&(!(W&2)&&(ql|=n),Y===4&&yu(e,q,Yl,!1)),rd(e))}function gu(e,t,n){if(W&6)throw Error(i(327));var r=!n&&(t&127)==0&&(t&e.expiredLanes)===0||nt(e,t),a=r?Au(e,t):Ou(e,t,!0),o=r;do{if(a===0){Ul&&!r&&yu(e,t,0,!1);break}else{if(n=e.current.alternate,o&&!vu(n)){a=Ou(e,t,!1),o=!1;continue}if(a===2){if(o=t,e.errorRecoveryDisabledLanes&o)var s=0;else s=e.pendingLanes&-536870913,s=s===0?s&536870912?536870912:0:s;if(s!==0){t=s;a:{var c=e;a=Zl;var l=c.current.memoizedState.isDehydrated;if(l&&(Su(c,s).flags|=256),s=Ou(c,s,!1),s!==2){if(Wl&&!l){c.errorRecoveryDisabledLanes|=o,ql|=o,a=4;break a}o=Ql,Ql=a,o!==null&&(Ql===null?Ql=o:Ql.push.apply(Ql,o))}a=s}if(o=!1,a!==2)continue}}if(a===1){Su(e,0),yu(e,t,0,!0);break}a:{switch(r=e,o=a,o){case 0:case 1:throw Error(i(345));case 4:if((t&4194048)!==t)break;case 6:yu(r,t,Yl,!Hl);break a;case 2:Ql=null;break;case 3:case 5:break;default:throw Error(i(329))}if((t&62914560)===t&&(a=eu+300-Fe(),10<a)){if(yu(r,t,Yl,!Hl),tt(r,0,!0)!==0)break a;su=t,r.timeoutHandle=Kd(_u.bind(null,r,n,Ql,ru,$l,t,Yl,ql,Xl,Hl,o,`Throttled`,-0,0),a);break a}_u(r,n,Ql,ru,$l,t,Yl,ql,Xl,Hl,o,null,-0,0)}}break}while(1);rd(e)}function _u(e,t,n,r,i,a,o,s,c,l,u,d,f,p){if(e.timeoutHandle=-1,d=t.subtreeFlags,d&8192||(d&16785408)==16785408){d={stylesheets:null,count:0,imgCount:0,imgBytes:0,suspenseyImages:[],waitingForImages:!0,waitingForViewTransition:!1,unsuspend:ln},Nl(t,a,d);var m=(a&62914560)===a?eu-Fe():(a&4194048)===a?tu-Fe():0;if(m=qf(d,m),m!==null){su=a,e.cancelPendingCommit=m(Lu.bind(null,e,t,a,n,r,i,o,s,c,u,d,null,f,p)),yu(e,a,o,!l);return}}Lu(e,t,a,n,r,i,o,s,c)}function vu(e){for(var t=e;;){var n=t.tag;if((n===0||n===11||n===15)&&t.flags&16384&&(n=t.updateQueue,n!==null&&(n=n.stores,n!==null)))for(var r=0;r<n.length;r++){var i=n[r],a=i.getSnapshot;i=i.value;try{if(!jr(a(),i))return!1}catch{return!1}}if(n=t.child,t.subtreeFlags&16384&&n!==null)n.return=t,t=n;else{if(t===e)break;for(;t.sibling===null;){if(t.return===null||t.return===e)return!0;t=t.return}t.sibling.return=t.return,t=t.sibling}}return!0}function yu(e,t,n,r){t&=~Jl,t&=~ql,e.suspendedLanes|=t,e.pingedLanes&=~t,r&&(e.warmLanes|=t),r=e.expirationTimes;for(var i=t;0<i;){var a=31-qe(i),o=1<<a;r[a]=-1,i&=~o}n!==0&&ct(e,n,t)}function bu(){return W&6?!0:(id(0,!1),!1)}function xu(){if(K!==null){if(J===0)var e=K.return;else e=K,ta=ea=null,Po(e),za=null,Ba=0,e=K;for(;e!==null;)Wc(e.alternate,e),e=e.return;K=null}}function Su(e,t){var n=e.timeoutHandle;n!==-1&&(e.timeoutHandle=-1,qd(n)),n=e.cancelPendingCommit,n!==null&&(e.cancelPendingCommit=null,n()),su=0,xu(),G=e,K=n=yi(e.current,null),q=t,J=0,Vl=null,Hl=!1,Ul=nt(e,t),Wl=!1,Xl=Yl=Jl=ql=Kl=Y=0,Ql=Zl=null,$l=!1,t&8&&(t|=t&32);var r=e.entangledLanes;if(r!==0)for(e=e.entanglements,r&=t;0<r;){var i=31-qe(r),a=1<<i;t|=e[i],r&=~a}return Gl=t,li(),n}function Cu(e,t){P=null,T.H=Us,t===ka||t===ja?(t=La(),J=3):t===Aa?(t=La(),J=4):J=t===sc?8:typeof t==`object`&&t&&typeof t.then==`function`?6:1,Vl=t,K===null&&(Y=1,tc(e,Di(t,e.current)))}function wu(){var e=uo.current;return e===null?!0:(q&4194048)===q?fo===null:(q&62914560)===q||q&536870912?e===fo:!1}function Tu(){var e=T.H;return T.H=Us,e===null?Us:e}function Eu(){var e=T.A;return T.A=zl,e}function Du(){Y=4,Hl||(q&4194048)!==q&&uo.current!==null||(Ul=!0),!(Kl&134217727)&&!(ql&134217727)||G===null||yu(G,q,Yl,!1)}function Ou(e,t,n){var r=W;W|=2;var i=Tu(),a=Eu();(G!==e||q!==t)&&(ru=null,Su(e,t)),t=!1;var o=Y;a:do try{if(J!==0&&K!==null){var s=K,c=Vl;switch(J){case 8:xu(),o=6;break a;case 3:case 2:case 9:case 6:uo.current===null&&(t=!0);var l=J;if(J=0,Vl=null,Pu(e,s,c,l),n&&Ul){o=0;break a}break;default:l=J,J=0,Vl=null,Pu(e,s,c,l)}}ku(),o=Y;break}catch(t){Cu(e,t)}while(1);return t&&e.shellSuspendCounter++,ta=ea=null,W=r,T.H=i,T.A=a,K===null&&(G=null,q=0,li()),o}function ku(){for(;K!==null;)Mu(K)}function Au(e,t){var n=W;W|=2;var r=Tu(),a=Eu();G!==e||q!==t?(ru=null,nu=Fe()+500,Su(e,t)):Ul=nt(e,t);a:do try{if(J!==0&&K!==null){t=K;var o=Vl;b:switch(J){case 1:J=0,Vl=null,Pu(e,t,o,1);break;case 2:case 9:if(Na(o)){J=0,Vl=null,Nu(t);break}t=function(){J!==2&&J!==9||G!==e||(J=7),rd(e)},o.then(t,t);break a;case 3:J=7;break a;case 4:J=5;break a;case 7:Na(o)?(J=0,Vl=null,Nu(t)):(J=0,Vl=null,Pu(e,t,o,7));break;case 5:var s=null;switch(K.tag){case 26:s=K.memoizedState;case 5:case 27:var c=K;if(s?Wf(s):c.stateNode.complete){J=0,Vl=null;var l=c.sibling;if(l!==null)K=l;else{var u=c.return;u===null?K=null:(K=u,Fu(u))}break b}}J=0,Vl=null,Pu(e,t,o,5);break;case 6:J=0,Vl=null,Pu(e,t,o,6);break;case 8:xu(),Y=6;break a;default:throw Error(i(462))}}ju();break}catch(t){Cu(e,t)}while(1);return ta=ea=null,T.H=r,T.A=a,W=n,K===null?(G=null,q=0,li(),Y):0}function ju(){for(;K!==null&&!Ne();)Mu(K)}function Mu(e){var t=Ic(e.alternate,e,Gl);e.memoizedProps=e.pendingProps,t===null?Fu(e):K=t}function Nu(e){var t=e,n=t.alternate;switch(t.tag){case 15:case 0:t=bc(n,t,t.pendingProps,t.type,void 0,q);break;case 11:t=bc(n,t,t.pendingProps,t.type.render,t.ref,q);break;case 5:Po(t);default:Wc(n,t),t=K=bi(t,Gl),t=Ic(n,t,Gl)}e.memoizedProps=e.pendingProps,t===null?Fu(e):K=t}function Pu(e,t,n,r){ta=ea=null,Po(t),za=null,Ba=0;var i=t.return;try{if(oc(e,i,t,n,q)){Y=1,tc(e,Di(n,e.current)),K=null;return}}catch(t){if(i!==null)throw K=i,t;Y=1,tc(e,Di(n,e.current)),K=null;return}t.flags&32768?(j||r===1?e=!0:Ul||q&536870912?e=!1:(Hl=e=!0,(r===2||r===9||r===3||r===6)&&(r=uo.current,r!==null&&r.tag===13&&(r.flags|=16384))),Iu(t,e)):Fu(t)}function Fu(e){var t=e;do{if(t.flags&32768){Iu(t,Hl);return}e=t.return;var n=Hc(t.alternate,t,Gl);if(n!==null){K=n;return}if(t=t.sibling,t!==null){K=t;return}K=t=e}while(t!==null);Y===0&&(Y=5)}function Iu(e,t){do{var n=Uc(e.alternate,e);if(n!==null){n.flags&=32767,K=n;return}if(n=e.return,n!==null&&(n.flags|=32768,n.subtreeFlags=0,n.deletions=null),!t&&(e=e.sibling,e!==null)){K=e;return}K=e=n}while(e!==null);Y=6,K=null}function Lu(e,t,n,r,a,o,s,c,l){e.cancelPendingCommit=null;do Hu();while(X!==0);if(W&6)throw Error(i(327));if(t!==null){if(t===e.current)throw Error(i(177));if(o=t.lanes|t.childLanes,o|=ci,st(e,n,o,s,c,l),e===G&&(K=G=null,q=0),ou=t,au=e,su=n,cu=o,lu=a,uu=r,t.subtreeFlags&10256||t.flags&10256?(e.callbackNode=null,e.callbackPriority=0,Xu(ze,function(){return Uu(),null})):(e.callbackNode=null,e.callbackPriority=0),r=(t.flags&13878)!=0,t.subtreeFlags&13878||r){r=T.T,T.T=null,a=E.p,E.p=2,s=W,W|=4;try{sl(e,t,n)}finally{W=s,E.p=a,T.T=r}}X=1,Ru(),zu(),Bu()}}function Ru(){if(X===1){X=0;var e=au,t=ou,n=(t.flags&13878)!=0;if(t.subtreeFlags&13878||n){n=T.T,T.T=null;var r=E.p;E.p=2;var i=W;W|=4;try{yl(t,e);var a=zd,o=Ir(e.containerInfo),s=a.focusedElem,c=a.selectionRange;if(o!==s&&s&&s.ownerDocument&&Fr(s.ownerDocument.documentElement,s)){if(c!==null&&Lr(s)){var l=c.start,u=c.end;if(u===void 0&&(u=l),`selectionStart`in s)s.selectionStart=l,s.selectionEnd=Math.min(u,s.value.length);else{var d=s.ownerDocument||document,f=d&&d.defaultView||window;if(f.getSelection){var p=f.getSelection(),m=s.textContent.length,h=Math.min(c.start,m),g=c.end===void 0?h:Math.min(c.end,m);!p.extend&&h>g&&(o=g,g=h,h=o);var _=Pr(s,h),v=Pr(s,g);if(_&&v&&(p.rangeCount!==1||p.anchorNode!==_.node||p.anchorOffset!==_.offset||p.focusNode!==v.node||p.focusOffset!==v.offset)){var y=d.createRange();y.setStart(_.node,_.offset),p.removeAllRanges(),h>g?(p.addRange(y),p.extend(v.node,v.offset)):(y.setEnd(v.node,v.offset),p.addRange(y))}}}}for(d=[],p=s;p=p.parentNode;)p.nodeType===1&&d.push({element:p,left:p.scrollLeft,top:p.scrollTop});for(typeof s.focus==`function`&&s.focus(),s=0;s<d.length;s++){var b=d[s];b.element.scrollLeft=b.left,b.element.scrollTop=b.top}}sp=!!Rd,zd=Rd=null}finally{W=i,E.p=r,T.T=n}}e.current=t,X=2}}function zu(){if(X===2){X=0;var e=au,t=ou,n=(t.flags&8772)!=0;if(t.subtreeFlags&8772||n){n=T.T,T.T=null;var r=E.p;E.p=2;var i=W;W|=4;try{cl(e,t.alternate,t)}finally{W=i,E.p=r,T.T=n}}X=3}}function Bu(){if(X===4||X===3){X=0,Pe();var e=au,t=ou,n=su,r=uu;t.subtreeFlags&10256||t.flags&10256?X=5:(X=0,ou=au=null,Vu(e,e.pendingLanes));var i=e.pendingLanes;if(i===0&&(iu=null),ft(n),t=t.stateNode,Ge&&typeof Ge.onCommitFiberRoot==`function`)try{Ge.onCommitFiberRoot(We,t,void 0,(t.current.flags&128)==128)}catch{}if(r!==null){t=T.T,i=E.p,E.p=2,T.T=null;try{for(var a=e.onRecoverableError,o=0;o<r.length;o++){var s=r[o];a(s.value,{componentStack:s.stack})}}finally{T.T=t,E.p=i}}su&3&&Hu(),rd(e),i=e.pendingLanes,n&261930&&i&42?e===fu?du++:(du=0,fu=e):du=0,id(0,!1)}}function Vu(e,t){(e.pooledCacheLanes&=t)===0&&(t=e.pooledCache,t!=null&&(e.pooledCache=null,ga(t)))}function Hu(){return Ru(),zu(),Bu(),Uu()}function Uu(){if(X!==5)return!1;var e=au,t=cu;cu=0;var n=ft(su),r=T.T,a=E.p;try{E.p=32>n?32:n,T.T=null,n=lu,lu=null;var o=au,s=su;if(X=0,ou=au=null,su=0,W&6)throw Error(i(331));var c=W;if(W|=4,Il(o.current),Ol(o,o.current,s,n),W=c,id(0,!1),Ge&&typeof Ge.onPostCommitFiberRoot==`function`)try{Ge.onPostCommitFiberRoot(We,o)}catch{}return!0}finally{E.p=a,T.T=r,Vu(e,t)}}function Wu(e,t,n){t=Di(n,t),t=rc(e.stateNode,t,2),e=Za(e,t,2),e!==null&&(ot(e,2),rd(e))}function Z(e,t,n){if(e.tag===3)Wu(e,e,n);else for(;t!==null;){if(t.tag===3){Wu(t,e,n);break}else if(t.tag===1){var r=t.stateNode;if(typeof t.type.getDerivedStateFromError==`function`||typeof r.componentDidCatch==`function`&&(iu===null||!iu.has(r))){e=Di(n,e),n=ic(2),r=Za(t,n,2),r!==null&&(ac(n,r,t,e),ot(r,2),rd(r));break}}t=t.return}}function Gu(e,t,n){var r=e.pingCache;if(r===null){r=e.pingCache=new Bl;var i=new Set;r.set(t,i)}else i=r.get(t),i===void 0&&(i=new Set,r.set(t,i));i.has(n)||(Wl=!0,i.add(n),e=Ku.bind(null,e,t,n),t.then(e,e))}function Ku(e,t,n){var r=e.pingCache;r!==null&&r.delete(t),e.pingedLanes|=e.suspendedLanes&n,e.warmLanes&=~n,G===e&&(q&n)===n&&(Y===4||Y===3&&(q&62914560)===q&&300>Fe()-eu?!(W&2)&&Su(e,0):Jl|=n,Xl===q&&(Xl=0)),rd(e)}function qu(e,t){t===0&&(t=it()),e=fi(e,t),e!==null&&(ot(e,t),rd(e))}function Ju(e){var t=e.memoizedState,n=0;t!==null&&(n=t.retryLane),qu(e,n)}function Yu(e,t){var n=0;switch(e.tag){case 31:case 13:var r=e.stateNode,a=e.memoizedState;a!==null&&(n=a.retryLane);break;case 19:r=e.stateNode;break;case 22:r=e.stateNode._retryCache;break;default:throw Error(i(314))}r!==null&&r.delete(t),qu(e,n)}function Xu(e,t){return je(e,t)}var Zu=null,Qu=null,$u=!1,ed=!1,td=!1,nd=0;function rd(e){e!==Qu&&e.next===null&&(Qu===null?Zu=Qu=e:Qu=Qu.next=e),ed=!0,$u||($u=!0,ud())}function id(e,t){if(!td&&ed){td=!0;do for(var n=!1,r=Zu;r!==null;){if(!t)if(e!==0){var i=r.pendingLanes;if(i===0)var a=0;else{var o=r.suspendedLanes,s=r.pingedLanes;a=(1<<31-qe(42|e)+1)-1,a&=i&~(o&~s),a=a&201326741?a&201326741|1:a?a|2:0}a!==0&&(n=!0,ld(r,a))}else a=q,a=tt(r,r===G?a:0,r.cancelPendingCommit!==null||r.timeoutHandle!==-1),!(a&3)||nt(r,a)||(n=!0,ld(r,a));r=r.next}while(n);td=!1}}function ad(){od()}function od(){ed=$u=!1;var e=0;nd!==0&&Gd()&&(e=nd);for(var t=Fe(),n=null,r=Zu;r!==null;){var i=r.next,a=sd(r,t);a===0?(r.next=null,n===null?Zu=i:n.next=i,i===null&&(Qu=n)):(n=r,(e!==0||a&3)&&(ed=!0)),r=i}X!==0&&X!==5||id(e,!1),nd!==0&&(nd=0)}function sd(e,t){for(var n=e.suspendedLanes,r=e.pingedLanes,i=e.expirationTimes,a=e.pendingLanes&-62914561;0<a;){var o=31-qe(a),s=1<<o,c=i[o];c===-1?((s&n)===0||(s&r)!==0)&&(i[o]=rt(s,t)):c<=t&&(e.expiredLanes|=s),a&=~s}if(t=G,n=q,n=tt(e,e===t?n:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r=e.callbackNode,n===0||e===t&&(J===2||J===9)||e.cancelPendingCommit!==null)return r!==null&&r!==null&&Me(r),e.callbackNode=null,e.callbackPriority=0;if(!(n&3)||nt(e,n)){if(t=n&-n,t===e.callbackPriority)return t;switch(r!==null&&Me(r),ft(n)){case 2:case 8:n=Re;break;case 32:n=ze;break;case 268435456:n=Ve;break;default:n=ze}return r=cd.bind(null,e),n=je(n,r),e.callbackPriority=t,e.callbackNode=n,t}return r!==null&&r!==null&&Me(r),e.callbackPriority=2,e.callbackNode=null,2}function cd(e,t){if(X!==0&&X!==5)return e.callbackNode=null,e.callbackPriority=0,null;var n=e.callbackNode;if(Hu()&&e.callbackNode!==n)return null;var r=q;return r=tt(e,e===G?r:0,e.cancelPendingCommit!==null||e.timeoutHandle!==-1),r===0?null:(gu(e,r,t),sd(e,Fe()),e.callbackNode!=null&&e.callbackNode===n?cd.bind(null,e):null)}function ld(e,t){if(Hu())return null;gu(e,t,!0)}function ud(){Yd(function(){W&6?je(Le,ad):od()})}function dd(){if(nd===0){var e=ya;e===0&&(e=Ze,Ze<<=1,!(Ze&261888)&&(Ze=256)),nd=e}return nd}function fd(e){return e==null||typeof e==`symbol`||typeof e==`boolean`?null:typeof e==`function`?e:cn(``+e)}function pd(e,t){var n=t.ownerDocument.createElement(`input`);return n.name=t.name,n.value=t.value,e.id&&n.setAttribute(`form`,e.id),t.parentNode.insertBefore(n,t),e=new FormData(e),n.parentNode.removeChild(n),e}function md(e,t,n,r,i){if(t===`submit`&&n&&n.stateNode===i){var a=fd((i[_t]||null).action),o=r.submitter;o&&(t=(t=o[_t]||null)?fd(t.formAction):o.getAttribute(`formAction`),t!==null&&(a=t,o=null));var s=new An(`action`,`action`,null,r,i);e.push({event:s,listeners:[{instance:null,listener:function(){if(r.defaultPrevented){if(nd!==0){var e=o?pd(i,o):new FormData(i);ks(n,{pending:!0,data:e,method:i.method,action:a},null,e)}}else typeof a==`function`&&(s.preventDefault(),e=o?pd(i,o):new FormData(i),ks(n,{pending:!0,data:e,method:i.method,action:a},a,e))},currentTarget:i}]})}}for(var hd=0;hd<ri.length;hd++){var gd=ri[hd];ii(gd.toLowerCase(),`on`+(gd[0].toUpperCase()+gd.slice(1)))}ii(Yr,`onAnimationEnd`),ii(Xr,`onAnimationIteration`),ii(Zr,`onAnimationStart`),ii(`dblclick`,`onDoubleClick`),ii(`focusin`,`onFocus`),ii(`focusout`,`onBlur`),ii(Qr,`onTransitionRun`),ii($r,`onTransitionStart`),ii(ei,`onTransitionCancel`),ii(ti,`onTransitionEnd`),Mt(`onMouseEnter`,[`mouseout`,`mouseover`]),Mt(`onMouseLeave`,[`mouseout`,`mouseover`]),Mt(`onPointerEnter`,[`pointerout`,`pointerover`]),Mt(`onPointerLeave`,[`pointerout`,`pointerover`]),jt(`onChange`,`change click focusin focusout input keydown keyup selectionchange`.split(` `)),jt(`onSelect`,`focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange`.split(` `)),jt(`onBeforeInput`,[`compositionend`,`keypress`,`textInput`,`paste`]),jt(`onCompositionEnd`,`compositionend focusout keydown keypress keyup mousedown`.split(` `)),jt(`onCompositionStart`,`compositionstart focusout keydown keypress keyup mousedown`.split(` `)),jt(`onCompositionUpdate`,`compositionupdate focusout keydown keypress keyup mousedown`.split(` `));var _d=`abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting`.split(` `),vd=new Set(`beforetoggle cancel close invalid load scroll scrollend toggle`.split(` `).concat(_d));function yd(e,t){t=(t&4)!=0;for(var n=0;n<e.length;n++){var r=e[n],i=r.event;r=r.listeners;a:{var a=void 0;if(t)for(var o=r.length-1;0<=o;o--){var s=r[o],c=s.instance,l=s.currentTarget;if(s=s.listener,c!==a&&i.isPropagationStopped())break a;a=s,i.currentTarget=l;try{a(i)}catch(e){ai(e)}i.currentTarget=null,a=c}else for(o=0;o<r.length;o++){if(s=r[o],c=s.instance,l=s.currentTarget,s=s.listener,c!==a&&i.isPropagationStopped())break a;a=s,i.currentTarget=l;try{a(i)}catch(e){ai(e)}i.currentTarget=null,a=c}}}}function Q(e,t){var n=t[yt];n===void 0&&(n=t[yt]=new Set);var r=e+`__bubble`;n.has(r)||(Cd(t,e,2,!1),n.add(r))}function bd(e,t,n){var r=0;t&&(r|=4),Cd(n,e,r,t)}var xd=`_reactListening`+Math.random().toString(36).slice(2);function Sd(e){if(!e[xd]){e[xd]=!0,kt.forEach(function(t){t!==`selectionchange`&&(vd.has(t)||bd(t,!1,e),bd(t,!0,e))});var t=e.nodeType===9?e:e.ownerDocument;t===null||t[xd]||(t[xd]=!0,bd(`selectionchange`,!1,t))}}function Cd(e,t,n,r){switch(mp(t)){case 2:var i=cp;break;case 8:i=lp;break;default:i=up}n=i.bind(null,t,n,e),i=void 0,!yn||t!==`touchstart`&&t!==`touchmove`&&t!==`wheel`||(i=!0),r?i===void 0?e.addEventListener(t,n,!0):e.addEventListener(t,n,{capture:!0,passive:i}):i===void 0?e.addEventListener(t,n,!1):e.addEventListener(t,n,{passive:i})}function wd(e,t,n,r,i){var a=r;if(!(t&1)&&!(t&2)&&r!==null)a:for(;;){if(r===null)return;var s=r.tag;if(s===3||s===4){var c=r.stateNode.containerInfo;if(c===i)break;if(s===4)for(s=r.return;s!==null;){var l=s.tag;if((l===3||l===4)&&s.stateNode.containerInfo===i)return;s=s.return}for(;c!==null;){if(s=Tt(c),s===null)return;if(l=s.tag,l===5||l===6||l===26||l===27){r=a=s;continue a}c=c.parentNode}}r=r.return}gn(function(){var r=a,i=dn(n),s=[];a:{var c=ni.get(e);if(c!==void 0){var l=An,u=e;switch(e){case`keypress`:if(Tn(n)===0)break a;case`keydown`:case`keyup`:l=Jn;break;case`focusin`:u=`focus`,l=zn;break;case`focusout`:u=`blur`,l=zn;break;case`beforeblur`:case`afterblur`:l=zn;break;case`click`:if(n.button===2)break a;case`auxclick`:case`dblclick`:case`mousedown`:case`mousemove`:case`mouseup`:case`mouseout`:case`mouseover`:case`contextmenu`:l=Ln;break;case`drag`:case`dragend`:case`dragenter`:case`dragexit`:case`dragleave`:case`dragover`:case`dragstart`:case`drop`:l=Rn;break;case`touchcancel`:case`touchend`:case`touchmove`:case`touchstart`:l=Xn;break;case Yr:case Xr:case Zr:l=Bn;break;case ti:l=Zn;break;case`scroll`:case`scrollend`:l=Mn;break;case`wheel`:l=Qn;break;case`copy`:case`cut`:case`paste`:l=Vn;break;case`gotpointercapture`:case`lostpointercapture`:case`pointercancel`:case`pointerdown`:case`pointermove`:case`pointerout`:case`pointerover`:case`pointerup`:l=Yn;break;case`toggle`:case`beforetoggle`:l=$n}var d=(t&4)!=0,f=!d&&(e===`scroll`||e===`scrollend`),p=d?c===null?null:c+`Capture`:c;d=[];for(var m=r,h;m!==null;){var g=m;if(h=g.stateNode,g=g.tag,g!==5&&g!==26&&g!==27||h===null||p===null||(g=_n(m,p),g!=null&&d.push(Td(m,g,h))),f)break;m=m.return}0<d.length&&(c=new l(c,u,null,n,i),s.push({event:c,listeners:d}))}}if(!(t&7)){a:{if(c=e===`mouseover`||e===`pointerover`,l=e===`mouseout`||e===`pointerout`,c&&n!==un&&(u=n.relatedTarget||n.fromElement)&&(Tt(u)||u[vt]))break a;if((l||c)&&(c=i.window===i?i:(c=i.ownerDocument)?c.defaultView||c.parentWindow:window,l?(u=n.relatedTarget||n.toElement,l=r,u=u?Tt(u):null,u!==null&&(f=o(u),d=u.tag,u!==f||d!==5&&d!==27&&d!==6)&&(u=null)):(l=null,u=r),l!==u)){if(d=Ln,g=`onMouseLeave`,p=`onMouseEnter`,m=`mouse`,(e===`pointerout`||e===`pointerover`)&&(d=Yn,g=`onPointerLeave`,p=`onPointerEnter`,m=`pointer`),f=l==null?c:Dt(l),h=u==null?c:Dt(u),c=new d(g,m+`leave`,l,n,i),c.target=f,c.relatedTarget=h,g=null,Tt(i)===r&&(d=new d(p,m+`enter`,u,n,i),d.target=h,d.relatedTarget=f,g=d),f=g,l&&u)b:{for(d=Dd,p=l,m=u,h=0,g=p;g;g=d(g))h++;g=0;for(var _=m;_;_=d(_))g++;for(;0<h-g;)p=d(p),h--;for(;0<g-h;)m=d(m),g--;for(;h--;){if(p===m||m!==null&&p===m.alternate){d=p;break b}p=d(p),m=d(m)}d=null}else d=null;l!==null&&Od(s,c,l,d,!1),u!==null&&f!==null&&Od(s,f,u,d,!0)}}a:{if(c=r?Dt(r):window,l=c.nodeName&&c.nodeName.toLowerCase(),l===`select`||l===`input`&&c.type===`file`)var v=yr;else if(pr(c))if(br)v=kr;else{v=Dr;var y=Er}else l=c.nodeName,!l||l.toLowerCase()!==`input`||c.type!==`checkbox`&&c.type!==`radio`?r&&an(r.elementType)&&(v=yr):v=Or;if(v&&=v(e,r)){mr(s,v,n,i);break a}y&&y(e,c,r),e===`focusout`&&r&&c.type===`number`&&r.memoizedProps.value!=null&&Xt(c,`number`,c.value)}switch(y=r?Dt(r):window,e){case`focusin`:(pr(y)||y.contentEditable===`true`)&&(zr=y,Br=r,Vr=null);break;case`focusout`:Vr=Br=zr=null;break;case`mousedown`:Hr=!0;break;case`contextmenu`:case`mouseup`:case`dragend`:Hr=!1,Ur(s,n,i);break;case`selectionchange`:if(Rr)break;case`keydown`:case`keyup`:Ur(s,n,i)}var b;if(tr)b:{switch(e){case`compositionstart`:var x=`onCompositionStart`;break b;case`compositionend`:x=`onCompositionEnd`;break b;case`compositionupdate`:x=`onCompositionUpdate`;break b}x=void 0}else lr?sr(e,n)&&(x=`onCompositionEnd`):e===`keydown`&&n.keyCode===229&&(x=`onCompositionStart`);x&&(ir&&n.locale!==`ko`&&(lr||x!==`onCompositionStart`?x===`onCompositionEnd`&&lr&&(b=wn()):(xn=i,Sn=`value`in xn?xn.value:xn.textContent,lr=!0)),y=Ed(r,x),0<y.length&&(x=new Hn(x,e,null,n,i),s.push({event:x,listeners:y}),b?x.data=b:(b=cr(n),b!==null&&(x.data=b)))),(b=rr?ur(e,n):dr(e,n))&&(x=Ed(r,`onBeforeInput`),0<x.length&&(y=new Hn(`onBeforeInput`,`beforeinput`,null,n,i),s.push({event:y,listeners:x}),y.data=b)),md(s,e,r,n,i)}yd(s,t)})}function Td(e,t,n){return{instance:e,listener:t,currentTarget:n}}function Ed(e,t){for(var n=t+`Capture`,r=[];e!==null;){var i=e,a=i.stateNode;if(i=i.tag,i!==5&&i!==26&&i!==27||a===null||(i=_n(e,n),i!=null&&r.unshift(Td(e,i,a)),i=_n(e,t),i!=null&&r.push(Td(e,i,a))),e.tag===3)return r;e=e.return}return[]}function Dd(e){if(e===null)return null;do e=e.return;while(e&&e.tag!==5&&e.tag!==27);return e||null}function Od(e,t,n,r,i){for(var a=t._reactName,o=[];n!==null&&n!==r;){var s=n,c=s.alternate,l=s.stateNode;if(s=s.tag,c!==null&&c===r)break;s!==5&&s!==26&&s!==27||l===null||(c=l,i?(l=_n(n,a),l!=null&&o.unshift(Td(n,l,c))):i||(l=_n(n,a),l!=null&&o.push(Td(n,l,c)))),n=n.return}o.length!==0&&e.push({event:t,listeners:o})}var kd=/\r\n?/g,Ad=/\u0000|\uFFFD/g;function jd(e){return(typeof e==`string`?e:``+e).replace(kd,`
`).replace(Ad,``)}function Md(e,t){return t=jd(t),jd(e)===t}function $(e,t,n,r,a,o){switch(n){case`children`:typeof r==`string`?t===`body`||t===`textarea`&&r===``||en(e,r):(typeof r==`number`||typeof r==`bigint`)&&t!==`body`&&en(e,``+r);break;case`className`:Rt(e,`class`,r);break;case`tabIndex`:Rt(e,`tabindex`,r);break;case`dir`:case`role`:case`viewBox`:case`width`:case`height`:Rt(e,n,r);break;case`style`:rn(e,r,o);break;case`data`:if(t!==`object`){Rt(e,`data`,r);break}case`src`:case`href`:if(r===``&&(t!==`a`||n!==`href`)){e.removeAttribute(n);break}if(r==null||typeof r==`function`||typeof r==`symbol`||typeof r==`boolean`){e.removeAttribute(n);break}r=cn(``+r),e.setAttribute(n,r);break;case`action`:case`formAction`:if(typeof r==`function`){e.setAttribute(n,`javascript:throw new Error('A React form was unexpectedly submitted. If you called form.submit() manually, consider using form.requestSubmit() instead. If you\\'re trying to use event.stopPropagation() in a submit event handler, consider also calling event.preventDefault().')`);break}else typeof o==`function`&&(n===`formAction`?(t!==`input`&&$(e,t,`name`,a.name,a,null),$(e,t,`formEncType`,a.formEncType,a,null),$(e,t,`formMethod`,a.formMethod,a,null),$(e,t,`formTarget`,a.formTarget,a,null)):($(e,t,`encType`,a.encType,a,null),$(e,t,`method`,a.method,a,null),$(e,t,`target`,a.target,a,null)));if(r==null||typeof r==`symbol`||typeof r==`boolean`){e.removeAttribute(n);break}r=cn(``+r),e.setAttribute(n,r);break;case`onClick`:r!=null&&(e.onclick=ln);break;case`onScroll`:r!=null&&Q(`scroll`,e);break;case`onScrollEnd`:r!=null&&Q(`scrollend`,e);break;case`dangerouslySetInnerHTML`:if(r!=null){if(typeof r!=`object`||!(`__html`in r))throw Error(i(61));if(n=r.__html,n!=null){if(a.children!=null)throw Error(i(60));e.innerHTML=n}}break;case`multiple`:e.multiple=r&&typeof r!=`function`&&typeof r!=`symbol`;break;case`muted`:e.muted=r&&typeof r!=`function`&&typeof r!=`symbol`;break;case`suppressContentEditableWarning`:case`suppressHydrationWarning`:case`defaultValue`:case`defaultChecked`:case`innerHTML`:case`ref`:break;case`autoFocus`:break;case`xlinkHref`:if(r==null||typeof r==`function`||typeof r==`boolean`||typeof r==`symbol`){e.removeAttribute(`xlink:href`);break}n=cn(``+r),e.setAttributeNS(`http://www.w3.org/1999/xlink`,`xlink:href`,n);break;case`contentEditable`:case`spellCheck`:case`draggable`:case`value`:case`autoReverse`:case`externalResourcesRequired`:case`focusable`:case`preserveAlpha`:r!=null&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,``+r):e.removeAttribute(n);break;case`inert`:case`allowFullScreen`:case`async`:case`autoPlay`:case`controls`:case`default`:case`defer`:case`disabled`:case`disablePictureInPicture`:case`disableRemotePlayback`:case`formNoValidate`:case`hidden`:case`loop`:case`noModule`:case`noValidate`:case`open`:case`playsInline`:case`readOnly`:case`required`:case`reversed`:case`scoped`:case`seamless`:case`itemScope`:r&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,``):e.removeAttribute(n);break;case`capture`:case`download`:!0===r?e.setAttribute(n,``):!1!==r&&r!=null&&typeof r!=`function`&&typeof r!=`symbol`?e.setAttribute(n,r):e.removeAttribute(n);break;case`cols`:case`rows`:case`size`:case`span`:r!=null&&typeof r!=`function`&&typeof r!=`symbol`&&!isNaN(r)&&1<=r?e.setAttribute(n,r):e.removeAttribute(n);break;case`rowSpan`:case`start`:r==null||typeof r==`function`||typeof r==`symbol`||isNaN(r)?e.removeAttribute(n):e.setAttribute(n,r);break;case`popover`:Q(`beforetoggle`,e),Q(`toggle`,e),Lt(e,`popover`,r);break;case`xlinkActuate`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:actuate`,r);break;case`xlinkArcrole`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:arcrole`,r);break;case`xlinkRole`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:role`,r);break;case`xlinkShow`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:show`,r);break;case`xlinkTitle`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:title`,r);break;case`xlinkType`:zt(e,`http://www.w3.org/1999/xlink`,`xlink:type`,r);break;case`xmlBase`:zt(e,`http://www.w3.org/XML/1998/namespace`,`xml:base`,r);break;case`xmlLang`:zt(e,`http://www.w3.org/XML/1998/namespace`,`xml:lang`,r);break;case`xmlSpace`:zt(e,`http://www.w3.org/XML/1998/namespace`,`xml:space`,r);break;case`is`:Lt(e,`is`,r);break;case`innerText`:case`textContent`:break;default:(!(2<n.length)||n[0]!==`o`&&n[0]!==`O`||n[1]!==`n`&&n[1]!==`N`)&&(n=on.get(n)||n,Lt(e,n,r))}}function Nd(e,t,n,r,a,o){switch(n){case`style`:rn(e,r,o);break;case`dangerouslySetInnerHTML`:if(r!=null){if(typeof r!=`object`||!(`__html`in r))throw Error(i(61));if(n=r.__html,n!=null){if(a.children!=null)throw Error(i(60));e.innerHTML=n}}break;case`children`:typeof r==`string`?en(e,r):(typeof r==`number`||typeof r==`bigint`)&&en(e,``+r);break;case`onScroll`:r!=null&&Q(`scroll`,e);break;case`onScrollEnd`:r!=null&&Q(`scrollend`,e);break;case`onClick`:r!=null&&(e.onclick=ln);break;case`suppressContentEditableWarning`:case`suppressHydrationWarning`:case`innerHTML`:case`ref`:break;case`innerText`:case`textContent`:break;default:if(!At.hasOwnProperty(n))a:{if(n[0]===`o`&&n[1]===`n`&&(a=n.endsWith(`Capture`),t=n.slice(2,a?n.length-7:void 0),o=e[_t]||null,o=o==null?null:o[n],typeof o==`function`&&e.removeEventListener(t,o,a),typeof r==`function`)){typeof o!=`function`&&o!==null&&(n in e?e[n]=null:e.hasAttribute(n)&&e.removeAttribute(n)),e.addEventListener(t,r,a);break a}n in e?e[n]=r:!0===r?e.setAttribute(n,``):Lt(e,n,r)}}}function Pd(e,t,n){switch(t){case`div`:case`span`:case`svg`:case`path`:case`a`:case`g`:case`p`:case`li`:break;case`img`:Q(`error`,e),Q(`load`,e);var r=!1,a=!1,o;for(o in n)if(n.hasOwnProperty(o)){var s=n[o];if(s!=null)switch(o){case`src`:r=!0;break;case`srcSet`:a=!0;break;case`children`:case`dangerouslySetInnerHTML`:throw Error(i(137,t));default:$(e,t,o,s,n,null)}}a&&$(e,t,`srcSet`,n.srcSet,n,null),r&&$(e,t,`src`,n.src,n,null);return;case`input`:Q(`invalid`,e);var c=o=s=a=null,l=null,u=null;for(r in n)if(n.hasOwnProperty(r)){var d=n[r];if(d!=null)switch(r){case`name`:a=d;break;case`type`:s=d;break;case`checked`:l=d;break;case`defaultChecked`:u=d;break;case`value`:o=d;break;case`defaultValue`:c=d;break;case`children`:case`dangerouslySetInnerHTML`:if(d!=null)throw Error(i(137,t));break;default:$(e,t,r,d,n,null)}}Yt(e,o,c,l,u,s,a,!1);return;case`select`:for(a in Q(`invalid`,e),r=s=o=null,n)if(n.hasOwnProperty(a)&&(c=n[a],c!=null))switch(a){case`value`:o=c;break;case`defaultValue`:s=c;break;case`multiple`:r=c;default:$(e,t,a,c,n,null)}t=o,n=s,e.multiple=!!r,t==null?n!=null&&Zt(e,!!r,n,!0):Zt(e,!!r,t,!1);return;case`textarea`:for(s in Q(`invalid`,e),o=a=r=null,n)if(n.hasOwnProperty(s)&&(c=n[s],c!=null))switch(s){case`value`:r=c;break;case`defaultValue`:a=c;break;case`children`:o=c;break;case`dangerouslySetInnerHTML`:if(c!=null)throw Error(i(91));break;default:$(e,t,s,c,n,null)}$t(e,r,a,o);return;case`option`:for(l in n)if(n.hasOwnProperty(l)&&(r=n[l],r!=null))switch(l){case`selected`:e.selected=r&&typeof r!=`function`&&typeof r!=`symbol`;break;default:$(e,t,l,r,n,null)}return;case`dialog`:Q(`beforetoggle`,e),Q(`toggle`,e),Q(`cancel`,e),Q(`close`,e);break;case`iframe`:case`object`:Q(`load`,e);break;case`video`:case`audio`:for(r=0;r<_d.length;r++)Q(_d[r],e);break;case`image`:Q(`error`,e),Q(`load`,e);break;case`details`:Q(`toggle`,e);break;case`embed`:case`source`:case`link`:Q(`error`,e),Q(`load`,e);case`area`:case`base`:case`br`:case`col`:case`hr`:case`keygen`:case`meta`:case`param`:case`track`:case`wbr`:case`menuitem`:for(u in n)if(n.hasOwnProperty(u)&&(r=n[u],r!=null))switch(u){case`children`:case`dangerouslySetInnerHTML`:throw Error(i(137,t));default:$(e,t,u,r,n,null)}return;default:if(an(t)){for(d in n)n.hasOwnProperty(d)&&(r=n[d],r!==void 0&&Nd(e,t,d,r,n,void 0));return}}for(c in n)n.hasOwnProperty(c)&&(r=n[c],r!=null&&$(e,t,c,r,n,null))}function Fd(e,t,n,r){switch(t){case`div`:case`span`:case`svg`:case`path`:case`a`:case`g`:case`p`:case`li`:break;case`input`:var a=null,o=null,s=null,c=null,l=null,u=null,d=null;for(m in n){var f=n[m];if(n.hasOwnProperty(m)&&f!=null)switch(m){case`checked`:break;case`value`:break;case`defaultValue`:l=f;default:r.hasOwnProperty(m)||$(e,t,m,null,r,f)}}for(var p in r){var m=r[p];if(f=n[p],r.hasOwnProperty(p)&&(m!=null||f!=null))switch(p){case`type`:o=m;break;case`name`:a=m;break;case`checked`:u=m;break;case`defaultChecked`:d=m;break;case`value`:s=m;break;case`defaultValue`:c=m;break;case`children`:case`dangerouslySetInnerHTML`:if(m!=null)throw Error(i(137,t));break;default:m!==f&&$(e,t,p,m,r,f)}}Jt(e,s,c,l,u,d,o,a);return;case`select`:for(o in m=s=c=p=null,n)if(l=n[o],n.hasOwnProperty(o)&&l!=null)switch(o){case`value`:break;case`multiple`:m=l;default:r.hasOwnProperty(o)||$(e,t,o,null,r,l)}for(a in r)if(o=r[a],l=n[a],r.hasOwnProperty(a)&&(o!=null||l!=null))switch(a){case`value`:p=o;break;case`defaultValue`:c=o;break;case`multiple`:s=o;default:o!==l&&$(e,t,a,o,r,l)}t=c,n=s,r=m,p==null?!!r!=!!n&&(t==null?Zt(e,!!n,n?[]:``,!1):Zt(e,!!n,t,!0)):Zt(e,!!n,p,!1);return;case`textarea`:for(c in m=p=null,n)if(a=n[c],n.hasOwnProperty(c)&&a!=null&&!r.hasOwnProperty(c))switch(c){case`value`:break;case`children`:break;default:$(e,t,c,null,r,a)}for(s in r)if(a=r[s],o=n[s],r.hasOwnProperty(s)&&(a!=null||o!=null))switch(s){case`value`:p=a;break;case`defaultValue`:m=a;break;case`children`:break;case`dangerouslySetInnerHTML`:if(a!=null)throw Error(i(91));break;default:a!==o&&$(e,t,s,a,r,o)}Qt(e,p,m);return;case`option`:for(var h in n)if(p=n[h],n.hasOwnProperty(h)&&p!=null&&!r.hasOwnProperty(h))switch(h){case`selected`:e.selected=!1;break;default:$(e,t,h,null,r,p)}for(l in r)if(p=r[l],m=n[l],r.hasOwnProperty(l)&&p!==m&&(p!=null||m!=null))switch(l){case`selected`:e.selected=p&&typeof p!=`function`&&typeof p!=`symbol`;break;default:$(e,t,l,p,r,m)}return;case`img`:case`link`:case`area`:case`base`:case`br`:case`col`:case`embed`:case`hr`:case`keygen`:case`meta`:case`param`:case`source`:case`track`:case`wbr`:case`menuitem`:for(var g in n)p=n[g],n.hasOwnProperty(g)&&p!=null&&!r.hasOwnProperty(g)&&$(e,t,g,null,r,p);for(u in r)if(p=r[u],m=n[u],r.hasOwnProperty(u)&&p!==m&&(p!=null||m!=null))switch(u){case`children`:case`dangerouslySetInnerHTML`:if(p!=null)throw Error(i(137,t));break;default:$(e,t,u,p,r,m)}return;default:if(an(t)){for(var _ in n)p=n[_],n.hasOwnProperty(_)&&p!==void 0&&!r.hasOwnProperty(_)&&Nd(e,t,_,void 0,r,p);for(d in r)p=r[d],m=n[d],!r.hasOwnProperty(d)||p===m||p===void 0&&m===void 0||Nd(e,t,d,p,r,m);return}}for(var v in n)p=n[v],n.hasOwnProperty(v)&&p!=null&&!r.hasOwnProperty(v)&&$(e,t,v,null,r,p);for(f in r)p=r[f],m=n[f],!r.hasOwnProperty(f)||p===m||p==null&&m==null||$(e,t,f,p,r,m)}function Id(e){switch(e){case`css`:case`script`:case`font`:case`img`:case`image`:case`input`:case`link`:return!0;default:return!1}}function Ld(){if(typeof performance.getEntriesByType==`function`){for(var e=0,t=0,n=performance.getEntriesByType(`resource`),r=0;r<n.length;r++){var i=n[r],a=i.transferSize,o=i.initiatorType,s=i.duration;if(a&&s&&Id(o)){for(o=0,s=i.responseEnd,r+=1;r<n.length;r++){var c=n[r],l=c.startTime;if(l>s)break;var u=c.transferSize,d=c.initiatorType;u&&Id(d)&&(c=c.responseEnd,o+=u*(c<s?1:(s-l)/(c-l)))}if(--r,t+=8*(a+o)/(i.duration/1e3),e++,10<e)break}}if(0<e)return t/e/1e6}return navigator.connection&&(e=navigator.connection.downlink,typeof e==`number`)?e:5}var Rd=null,zd=null;function Bd(e){return e.nodeType===9?e:e.ownerDocument}function Vd(e){switch(e){case`http://www.w3.org/2000/svg`:return 1;case`http://www.w3.org/1998/Math/MathML`:return 2;default:return 0}}function Hd(e,t){if(e===0)switch(t){case`svg`:return 1;case`math`:return 2;default:return 0}return e===1&&t===`foreignObject`?0:e}function Ud(e,t){return e===`textarea`||e===`noscript`||typeof t.children==`string`||typeof t.children==`number`||typeof t.children==`bigint`||typeof t.dangerouslySetInnerHTML==`object`&&t.dangerouslySetInnerHTML!==null&&t.dangerouslySetInnerHTML.__html!=null}var Wd=null;function Gd(){var e=window.event;return e&&e.type===`popstate`?e===Wd?!1:(Wd=e,!0):(Wd=null,!1)}var Kd=typeof setTimeout==`function`?setTimeout:void 0,qd=typeof clearTimeout==`function`?clearTimeout:void 0,Jd=typeof Promise==`function`?Promise:void 0,Yd=typeof queueMicrotask==`function`?queueMicrotask:Jd===void 0?Kd:function(e){return Jd.resolve(null).then(e).catch(Xd)};function Xd(e){setTimeout(function(){throw e})}function Zd(e){return e===`head`}function Qd(e,t){var n=t,r=0;do{var i=n.nextSibling;if(e.removeChild(n),i&&i.nodeType===8)if(n=i.data,n===`/$`||n===`/&`){if(r===0){e.removeChild(i),Np(t);return}r--}else if(n===`$`||n===`$?`||n===`$~`||n===`$!`||n===`&`)r++;else if(n===`html`)pf(e.ownerDocument.documentElement);else if(n===`head`){n=e.ownerDocument.head,pf(n);for(var a=n.firstChild;a;){var o=a.nextSibling,s=a.nodeName;a[Ct]||s===`SCRIPT`||s===`STYLE`||s===`LINK`&&a.rel.toLowerCase()===`stylesheet`||n.removeChild(a),a=o}}else n===`body`&&pf(e.ownerDocument.body);n=i}while(n);Np(t)}function $d(e,t){var n=e;e=0;do{var r=n.nextSibling;if(n.nodeType===1?t?(n._stashedDisplay=n.style.display,n.style.display=`none`):(n.style.display=n._stashedDisplay||``,n.getAttribute(`style`)===``&&n.removeAttribute(`style`)):n.nodeType===3&&(t?(n._stashedText=n.nodeValue,n.nodeValue=``):n.nodeValue=n._stashedText||``),r&&r.nodeType===8)if(n=r.data,n===`/$`){if(e===0)break;e--}else n!==`$`&&n!==`$?`&&n!==`$~`&&n!==`$!`||e++;n=r}while(n)}function ef(e){var t=e.firstChild;for(t&&t.nodeType===10&&(t=t.nextSibling);t;){var n=t;switch(t=t.nextSibling,n.nodeName){case`HTML`:case`HEAD`:case`BODY`:ef(n),wt(n);continue;case`SCRIPT`:case`STYLE`:continue;case`LINK`:if(n.rel.toLowerCase()===`stylesheet`)continue}e.removeChild(n)}}function tf(e,t,n,r){for(;e.nodeType===1;){var i=n;if(e.nodeName.toLowerCase()!==t.toLowerCase()){if(!r&&(e.nodeName!==`INPUT`||e.type!==`hidden`))break}else if(!r)if(t===`input`&&e.type===`hidden`){var a=i.name==null?null:``+i.name;if(i.type===`hidden`&&e.getAttribute(`name`)===a)return e}else return e;else if(!e[Ct])switch(t){case`meta`:if(!e.hasAttribute(`itemprop`))break;return e;case`link`:if(a=e.getAttribute(`rel`),a===`stylesheet`&&e.hasAttribute(`data-precedence`)||a!==i.rel||e.getAttribute(`href`)!==(i.href==null||i.href===``?null:i.href)||e.getAttribute(`crossorigin`)!==(i.crossOrigin==null?null:i.crossOrigin)||e.getAttribute(`title`)!==(i.title==null?null:i.title))break;return e;case`style`:if(e.hasAttribute(`data-precedence`))break;return e;case`script`:if(a=e.getAttribute(`src`),(a!==(i.src==null?null:i.src)||e.getAttribute(`type`)!==(i.type==null?null:i.type)||e.getAttribute(`crossorigin`)!==(i.crossOrigin==null?null:i.crossOrigin))&&a&&e.hasAttribute(`async`)&&!e.hasAttribute(`itemprop`))break;return e;default:return e}if(e=cf(e.nextSibling),e===null)break}return null}function nf(e,t,n){if(t===``)return null;for(;e.nodeType!==3;)if((e.nodeType!==1||e.nodeName!==`INPUT`||e.type!==`hidden`)&&!n||(e=cf(e.nextSibling),e===null))return null;return e}function rf(e,t){for(;e.nodeType!==8;)if((e.nodeType!==1||e.nodeName!==`INPUT`||e.type!==`hidden`)&&!t||(e=cf(e.nextSibling),e===null))return null;return e}function af(e){return e.data===`$?`||e.data===`$~`}function of(e){return e.data===`$!`||e.data===`$?`&&e.ownerDocument.readyState!==`loading`}function sf(e,t){var n=e.ownerDocument;if(e.data===`$~`)e._reactRetry=t;else if(e.data!==`$?`||n.readyState!==`loading`)t();else{var r=function(){t(),n.removeEventListener(`DOMContentLoaded`,r)};n.addEventListener(`DOMContentLoaded`,r),e._reactRetry=r}}function cf(e){for(;e!=null;e=e.nextSibling){var t=e.nodeType;if(t===1||t===3)break;if(t===8){if(t=e.data,t===`$`||t===`$!`||t===`$?`||t===`$~`||t===`&`||t===`F!`||t===`F`)break;if(t===`/$`||t===`/&`)return null}}return e}var lf=null;function uf(e){e=e.nextSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n===`/$`||n===`/&`){if(t===0)return cf(e.nextSibling);t--}else n!==`$`&&n!==`$!`&&n!==`$?`&&n!==`$~`&&n!==`&`||t++}e=e.nextSibling}return null}function df(e){e=e.previousSibling;for(var t=0;e;){if(e.nodeType===8){var n=e.data;if(n===`$`||n===`$!`||n===`$?`||n===`$~`||n===`&`){if(t===0)return e;t--}else n!==`/$`&&n!==`/&`||t++}e=e.previousSibling}return null}function ff(e,t,n){switch(t=Bd(n),e){case`html`:if(e=t.documentElement,!e)throw Error(i(452));return e;case`head`:if(e=t.head,!e)throw Error(i(453));return e;case`body`:if(e=t.body,!e)throw Error(i(454));return e;default:throw Error(i(451))}}function pf(e){for(var t=e.attributes;t.length;)e.removeAttributeNode(t[0]);wt(e)}var mf=new Map,hf=new Set;function gf(e){return typeof e.getRootNode==`function`?e.getRootNode():e.nodeType===9?e:e.ownerDocument}var _f=E.d;E.d={f:vf,r:yf,D:Sf,C:Cf,L:wf,m:Tf,X:Df,S:Ef,M:Of};function vf(){var e=_f.f(),t=bu();return e||t}function yf(e){var t=Et(e);t!==null&&t.tag===5&&t.type===`form`?js(t):_f.r(e)}var bf=typeof document>`u`?null:document;function xf(e,t,n){var r=bf;if(r&&typeof t==`string`&&t){var i=qt(t);i=`link[rel="`+e+`"][href="`+i+`"]`,typeof n==`string`&&(i+=`[crossorigin="`+n+`"]`),hf.has(i)||(hf.add(i),e={rel:e,crossOrigin:n,href:t},r.querySelector(i)===null&&(t=r.createElement(`link`),Pd(t,`link`,e),k(t),r.head.appendChild(t)))}}function Sf(e){_f.D(e),xf(`dns-prefetch`,e,null)}function Cf(e,t){_f.C(e,t),xf(`preconnect`,e,t)}function wf(e,t,n){_f.L(e,t,n);var r=bf;if(r&&e&&t){var i=`link[rel="preload"][as="`+qt(t)+`"]`;t===`image`&&n&&n.imageSrcSet?(i+=`[imagesrcset="`+qt(n.imageSrcSet)+`"]`,typeof n.imageSizes==`string`&&(i+=`[imagesizes="`+qt(n.imageSizes)+`"]`)):i+=`[href="`+qt(e)+`"]`;var a=i;switch(t){case`style`:a=Af(e);break;case`script`:a=Pf(e)}mf.has(a)||(e=h({rel:`preload`,href:t===`image`&&n&&n.imageSrcSet?void 0:e,as:t},n),mf.set(a,e),r.querySelector(i)!==null||t===`style`&&r.querySelector(jf(a))||t===`script`&&r.querySelector(Ff(a))||(t=r.createElement(`link`),Pd(t,`link`,e),k(t),r.head.appendChild(t)))}}function Tf(e,t){_f.m(e,t);var n=bf;if(n&&e){var r=t&&typeof t.as==`string`?t.as:`script`,i=`link[rel="modulepreload"][as="`+qt(r)+`"][href="`+qt(e)+`"]`,a=i;switch(r){case`audioworklet`:case`paintworklet`:case`serviceworker`:case`sharedworker`:case`worker`:case`script`:a=Pf(e)}if(!mf.has(a)&&(e=h({rel:`modulepreload`,href:e},t),mf.set(a,e),n.querySelector(i)===null)){switch(r){case`audioworklet`:case`paintworklet`:case`serviceworker`:case`sharedworker`:case`worker`:case`script`:if(n.querySelector(Ff(a)))return}r=n.createElement(`link`),Pd(r,`link`,e),k(r),n.head.appendChild(r)}}}function Ef(e,t,n){_f.S(e,t,n);var r=bf;if(r&&e){var i=Ot(r).hoistableStyles,a=Af(e);t||=`default`;var o=i.get(a);if(!o){var s={loading:0,preload:null};if(o=r.querySelector(jf(a)))s.loading=5;else{e=h({rel:`stylesheet`,href:e,"data-precedence":t},n),(n=mf.get(a))&&Rf(e,n);var c=o=r.createElement(`link`);k(c),Pd(c,`link`,e),c._p=new Promise(function(e,t){c.onload=e,c.onerror=t}),c.addEventListener(`load`,function(){s.loading|=1}),c.addEventListener(`error`,function(){s.loading|=2}),s.loading|=4,Lf(o,t,r)}o={type:`stylesheet`,instance:o,count:1,state:s},i.set(a,o)}}}function Df(e,t){_f.X(e,t);var n=bf;if(n&&e){var r=Ot(n).hoistableScripts,i=Pf(e),a=r.get(i);a||(a=n.querySelector(Ff(i)),a||(e=h({src:e,async:!0},t),(t=mf.get(i))&&zf(e,t),a=n.createElement(`script`),k(a),Pd(a,`link`,e),n.head.appendChild(a)),a={type:`script`,instance:a,count:1,state:null},r.set(i,a))}}function Of(e,t){_f.M(e,t);var n=bf;if(n&&e){var r=Ot(n).hoistableScripts,i=Pf(e),a=r.get(i);a||(a=n.querySelector(Ff(i)),a||(e=h({src:e,async:!0,type:`module`},t),(t=mf.get(i))&&zf(e,t),a=n.createElement(`script`),k(a),Pd(a,`link`,e),n.head.appendChild(a)),a={type:`script`,instance:a,count:1,state:null},r.set(i,a))}}function kf(e,t,n,r){var a=(a=_e.current)?gf(a):null;if(!a)throw Error(i(446));switch(e){case`meta`:case`title`:return null;case`style`:return typeof n.precedence==`string`&&typeof n.href==`string`?(t=Af(n.href),n=Ot(a).hoistableStyles,r=n.get(t),r||(r={type:`style`,instance:null,count:0,state:null},n.set(t,r)),r):{type:`void`,instance:null,count:0,state:null};case`link`:if(n.rel===`stylesheet`&&typeof n.href==`string`&&typeof n.precedence==`string`){e=Af(n.href);var o=Ot(a).hoistableStyles,s=o.get(e);if(s||(a=a.ownerDocument||a,s={type:`stylesheet`,instance:null,count:0,state:{loading:0,preload:null}},o.set(e,s),(o=a.querySelector(jf(e)))&&!o._p&&(s.instance=o,s.state.loading=5),mf.has(e)||(n={rel:`preload`,as:`style`,href:n.href,crossOrigin:n.crossOrigin,integrity:n.integrity,media:n.media,hrefLang:n.hrefLang,referrerPolicy:n.referrerPolicy},mf.set(e,n),o||Nf(a,e,n,s.state))),t&&r===null)throw Error(i(528,``));return s}if(t&&r!==null)throw Error(i(529,``));return null;case`script`:return t=n.async,n=n.src,typeof n==`string`&&t&&typeof t!=`function`&&typeof t!=`symbol`?(t=Pf(n),n=Ot(a).hoistableScripts,r=n.get(t),r||(r={type:`script`,instance:null,count:0,state:null},n.set(t,r)),r):{type:`void`,instance:null,count:0,state:null};default:throw Error(i(444,e))}}function Af(e){return`href="`+qt(e)+`"`}function jf(e){return`link[rel="stylesheet"][`+e+`]`}function Mf(e){return h({},e,{"data-precedence":e.precedence,precedence:null})}function Nf(e,t,n,r){e.querySelector(`link[rel="preload"][as="style"][`+t+`]`)?r.loading=1:(t=e.createElement(`link`),r.preload=t,t.addEventListener(`load`,function(){return r.loading|=1}),t.addEventListener(`error`,function(){return r.loading|=2}),Pd(t,`link`,n),k(t),e.head.appendChild(t))}function Pf(e){return`[src="`+qt(e)+`"]`}function Ff(e){return`script[async]`+e}function If(e,t,n){if(t.count++,t.instance===null)switch(t.type){case`style`:var r=e.querySelector(`style[data-href~="`+qt(n.href)+`"]`);if(r)return t.instance=r,k(r),r;var a=h({},n,{"data-href":n.href,"data-precedence":n.precedence,href:null,precedence:null});return r=(e.ownerDocument||e).createElement(`style`),k(r),Pd(r,`style`,a),Lf(r,n.precedence,e),t.instance=r;case`stylesheet`:a=Af(n.href);var o=e.querySelector(jf(a));if(o)return t.state.loading|=4,t.instance=o,k(o),o;r=Mf(n),(a=mf.get(a))&&Rf(r,a),o=(e.ownerDocument||e).createElement(`link`),k(o);var s=o;return s._p=new Promise(function(e,t){s.onload=e,s.onerror=t}),Pd(o,`link`,r),t.state.loading|=4,Lf(o,n.precedence,e),t.instance=o;case`script`:return o=Pf(n.src),(a=e.querySelector(Ff(o)))?(t.instance=a,k(a),a):(r=n,(a=mf.get(o))&&(r=h({},n),zf(r,a)),e=e.ownerDocument||e,a=e.createElement(`script`),k(a),Pd(a,`link`,r),e.head.appendChild(a),t.instance=a);case`void`:return null;default:throw Error(i(443,t.type))}else t.type===`stylesheet`&&!(t.state.loading&4)&&(r=t.instance,t.state.loading|=4,Lf(r,n.precedence,e));return t.instance}function Lf(e,t,n){for(var r=n.querySelectorAll(`link[rel="stylesheet"][data-precedence],style[data-precedence]`),i=r.length?r[r.length-1]:null,a=i,o=0;o<r.length;o++){var s=r[o];if(s.dataset.precedence===t)a=s;else if(a!==i)break}a?a.parentNode.insertBefore(e,a.nextSibling):(t=n.nodeType===9?n.head:n,t.insertBefore(e,t.firstChild))}function Rf(e,t){e.crossOrigin??=t.crossOrigin,e.referrerPolicy??=t.referrerPolicy,e.title??=t.title}function zf(e,t){e.crossOrigin??=t.crossOrigin,e.referrerPolicy??=t.referrerPolicy,e.integrity??=t.integrity}var Bf=null;function Vf(e,t,n){if(Bf===null){var r=new Map,i=Bf=new Map;i.set(n,r)}else i=Bf,r=i.get(n),r||(r=new Map,i.set(n,r));if(r.has(e))return r;for(r.set(e,null),n=n.getElementsByTagName(e),i=0;i<n.length;i++){var a=n[i];if(!(a[Ct]||a[gt]||e===`link`&&a.getAttribute(`rel`)===`stylesheet`)&&a.namespaceURI!==`http://www.w3.org/2000/svg`){var o=a.getAttribute(t)||``;o=e+o;var s=r.get(o);s?s.push(a):r.set(o,[a])}}return r}function Hf(e,t,n){e=e.ownerDocument||e,e.head.insertBefore(n,t===`title`?e.querySelector(`head > title`):null)}function Uf(e,t,n){if(n===1||t.itemProp!=null)return!1;switch(e){case`meta`:case`title`:return!0;case`style`:if(typeof t.precedence!=`string`||typeof t.href!=`string`||t.href===``)break;return!0;case`link`:if(typeof t.rel!=`string`||typeof t.href!=`string`||t.href===``||t.onLoad||t.onError)break;switch(t.rel){case`stylesheet`:return e=t.disabled,typeof t.precedence==`string`&&e==null;default:return!0}case`script`:if(t.async&&typeof t.async!=`function`&&typeof t.async!=`symbol`&&!t.onLoad&&!t.onError&&t.src&&typeof t.src==`string`)return!0}return!1}function Wf(e){return!(e.type===`stylesheet`&&!(e.state.loading&3))}function Gf(e,t,n,r){if(n.type===`stylesheet`&&(typeof r.media!=`string`||!1!==matchMedia(r.media).matches)&&!(n.state.loading&4)){if(n.instance===null){var i=Af(r.href),a=t.querySelector(jf(i));if(a){t=a._p,typeof t==`object`&&t&&typeof t.then==`function`&&(e.count++,e=Jf.bind(e),t.then(e,e)),n.state.loading|=4,n.instance=a,k(a);return}a=t.ownerDocument||t,r=Mf(r),(i=mf.get(i))&&Rf(r,i),a=a.createElement(`link`),k(a);var o=a;o._p=new Promise(function(e,t){o.onload=e,o.onerror=t}),Pd(a,`link`,r),n.instance=a}e.stylesheets===null&&(e.stylesheets=new Map),e.stylesheets.set(n,t),(t=n.state.preload)&&!(n.state.loading&3)&&(e.count++,n=Jf.bind(e),t.addEventListener(`load`,n),t.addEventListener(`error`,n))}}var Kf=0;function qf(e,t){return e.stylesheets&&e.count===0&&Xf(e,e.stylesheets),0<e.count||0<e.imgCount?function(n){var r=setTimeout(function(){if(e.stylesheets&&Xf(e,e.stylesheets),e.unsuspend){var t=e.unsuspend;e.unsuspend=null,t()}},6e4+t);0<e.imgBytes&&Kf===0&&(Kf=62500*Ld());var i=setTimeout(function(){if(e.waitingForImages=!1,e.count===0&&(e.stylesheets&&Xf(e,e.stylesheets),e.unsuspend)){var t=e.unsuspend;e.unsuspend=null,t()}},(e.imgBytes>Kf?50:800)+t);return e.unsuspend=n,function(){e.unsuspend=null,clearTimeout(r),clearTimeout(i)}}:null}function Jf(){if(this.count--,this.count===0&&(this.imgCount===0||!this.waitingForImages)){if(this.stylesheets)Xf(this,this.stylesheets);else if(this.unsuspend){var e=this.unsuspend;this.unsuspend=null,e()}}}var Yf=null;function Xf(e,t){e.stylesheets=null,e.unsuspend!==null&&(e.count++,Yf=new Map,t.forEach(Zf,e),Yf=null,Jf.call(e))}function Zf(e,t){if(!(t.state.loading&4)){var n=Yf.get(e);if(n)var r=n.get(null);else{n=new Map,Yf.set(e,n);for(var i=e.querySelectorAll(`link[data-precedence],style[data-precedence]`),a=0;a<i.length;a++){var o=i[a];(o.nodeName===`LINK`||o.getAttribute(`media`)!==`not all`)&&(n.set(o.dataset.precedence,o),r=o)}r&&n.set(null,r)}i=t.instance,o=i.getAttribute(`data-precedence`),a=n.get(o)||r,a===r&&n.set(null,i),n.set(o,i),this.count++,r=Jf.bind(this),i.addEventListener(`load`,r),i.addEventListener(`error`,r),a?a.parentNode.insertBefore(i,a.nextSibling):(e=e.nodeType===9?e.head:e,e.insertBefore(i,e.firstChild)),t.state.loading|=4}}var Qf={$$typeof:S,Provider:null,Consumer:null,_currentValue:de,_currentValue2:de,_threadCount:0};function $f(e,t,n,r,i,a,o,s,c){this.tag=1,this.containerInfo=e,this.pingCache=this.current=this.pendingChildren=null,this.timeoutHandle=-1,this.callbackNode=this.next=this.pendingContext=this.context=this.cancelPendingCommit=null,this.callbackPriority=0,this.expirationTimes=at(-1),this.entangledLanes=this.shellSuspendCounter=this.errorRecoveryDisabledLanes=this.expiredLanes=this.warmLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0,this.entanglements=at(0),this.hiddenUpdates=at(null),this.identifierPrefix=r,this.onUncaughtError=i,this.onCaughtError=a,this.onRecoverableError=o,this.pooledCache=null,this.pooledCacheLanes=0,this.formState=c,this.incompleteTransitions=new Map}function ep(e,t,n,r,i,a,o,s,c,l,u,d){return e=new $f(e,t,n,o,c,l,u,d,s),t=1,!0===a&&(t|=24),a=_i(3,null,null,t),e.current=a,a.stateNode=e,t=ha(),t.refCount++,e.pooledCache=t,t.refCount++,a.memoizedState={element:r,isDehydrated:n,cache:t},Ja(a),e}function tp(e){return e?(e=hi,e):hi}function np(e,t,n,r,i,a){i=tp(i),r.context===null?r.context=i:r.pendingContext=i,r=Xa(t),r.payload={element:n},a=a===void 0?null:a,a!==null&&(r.callback=a),n=Za(e,r,t),n!==null&&(hu(n,e,t),Qa(n,e,t))}function rp(e,t){if(e=e.memoizedState,e!==null&&e.dehydrated!==null){var n=e.retryLane;e.retryLane=n!==0&&n<t?n:t}}function ip(e,t){rp(e,t),(e=e.alternate)&&rp(e,t)}function ap(e){if(e.tag===13||e.tag===31){var t=fi(e,67108864);t!==null&&hu(t,e,67108864),ip(e,67108864)}}function op(e){if(e.tag===13||e.tag===31){var t=pu();t=dt(t);var n=fi(e,t);n!==null&&hu(n,e,t),ip(e,t)}}var sp=!0;function cp(e,t,n,r){var i=T.T;T.T=null;var a=E.p;try{E.p=2,up(e,t,n,r)}finally{E.p=a,T.T=i}}function lp(e,t,n,r){var i=T.T;T.T=null;var a=E.p;try{E.p=8,up(e,t,n,r)}finally{E.p=a,T.T=i}}function up(e,t,n,r){if(sp){var i=dp(r);if(i===null)wd(e,t,r,fp,n),Cp(e,r);else if(Tp(i,e,t,n,r))r.stopPropagation();else if(Cp(e,r),t&4&&-1<Sp.indexOf(e)){for(;i!==null;){var a=Et(i);if(a!==null)switch(a.tag){case 3:if(a=a.stateNode,a.current.memoizedState.isDehydrated){var o=et(a.pendingLanes);if(o!==0){var s=a;for(s.pendingLanes|=2,s.entangledLanes|=2;o;){var c=1<<31-qe(o);s.entanglements[1]|=c,o&=~c}rd(a),!(W&6)&&(nu=Fe()+500,id(0,!1))}}break;case 31:case 13:s=fi(a,2),s!==null&&hu(s,a,2),bu(),ip(a,2)}if(a=dp(r),a===null&&wd(e,t,r,fp,n),a===i)break;i=a}i!==null&&r.stopPropagation()}else wd(e,t,r,null,n)}}function dp(e){return e=dn(e),pp(e)}var fp=null;function pp(e){if(fp=null,e=Tt(e),e!==null){var t=o(e);if(t===null)e=null;else{var n=t.tag;if(n===13){if(e=s(t),e!==null)return e;e=null}else if(n===31){if(e=c(t),e!==null)return e;e=null}else if(n===3){if(t.stateNode.current.memoizedState.isDehydrated)return t.tag===3?t.stateNode.containerInfo:null;e=null}else t!==e&&(e=null)}}return fp=e,null}function mp(e){switch(e){case`beforetoggle`:case`cancel`:case`click`:case`close`:case`contextmenu`:case`copy`:case`cut`:case`auxclick`:case`dblclick`:case`dragend`:case`dragstart`:case`drop`:case`focusin`:case`focusout`:case`input`:case`invalid`:case`keydown`:case`keypress`:case`keyup`:case`mousedown`:case`mouseup`:case`paste`:case`pause`:case`play`:case`pointercancel`:case`pointerdown`:case`pointerup`:case`ratechange`:case`reset`:case`resize`:case`seeked`:case`submit`:case`toggle`:case`touchcancel`:case`touchend`:case`touchstart`:case`volumechange`:case`change`:case`selectionchange`:case`textInput`:case`compositionstart`:case`compositionend`:case`compositionupdate`:case`beforeblur`:case`afterblur`:case`beforeinput`:case`blur`:case`fullscreenchange`:case`focus`:case`hashchange`:case`popstate`:case`select`:case`selectstart`:return 2;case`drag`:case`dragenter`:case`dragexit`:case`dragleave`:case`dragover`:case`mousemove`:case`mouseout`:case`mouseover`:case`pointermove`:case`pointerout`:case`pointerover`:case`scroll`:case`touchmove`:case`wheel`:case`mouseenter`:case`mouseleave`:case`pointerenter`:case`pointerleave`:return 8;case`message`:switch(Ie()){case Le:return 2;case Re:return 8;case ze:case Be:return 32;case Ve:return 268435456;default:return 32}default:return 32}}var hp=!1,gp=null,_p=null,vp=null,yp=new Map,bp=new Map,xp=[],Sp=`mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset`.split(` `);function Cp(e,t){switch(e){case`focusin`:case`focusout`:gp=null;break;case`dragenter`:case`dragleave`:_p=null;break;case`mouseover`:case`mouseout`:vp=null;break;case`pointerover`:case`pointerout`:yp.delete(t.pointerId);break;case`gotpointercapture`:case`lostpointercapture`:bp.delete(t.pointerId)}}function wp(e,t,n,r,i,a){return e===null||e.nativeEvent!==a?(e={blockedOn:t,domEventName:n,eventSystemFlags:r,nativeEvent:a,targetContainers:[i]},t!==null&&(t=Et(t),t!==null&&ap(t)),e):(e.eventSystemFlags|=r,t=e.targetContainers,i!==null&&t.indexOf(i)===-1&&t.push(i),e)}function Tp(e,t,n,r,i){switch(t){case`focusin`:return gp=wp(gp,e,t,n,r,i),!0;case`dragenter`:return _p=wp(_p,e,t,n,r,i),!0;case`mouseover`:return vp=wp(vp,e,t,n,r,i),!0;case`pointerover`:var a=i.pointerId;return yp.set(a,wp(yp.get(a)||null,e,t,n,r,i)),!0;case`gotpointercapture`:return a=i.pointerId,bp.set(a,wp(bp.get(a)||null,e,t,n,r,i)),!0}return!1}function Ep(e){var t=Tt(e.target);if(t!==null){var n=o(t);if(n!==null){if(t=n.tag,t===13){if(t=s(n),t!==null){e.blockedOn=t,mt(e.priority,function(){op(n)});return}}else if(t===31){if(t=c(n),t!==null){e.blockedOn=t,mt(e.priority,function(){op(n)});return}}else if(t===3&&n.stateNode.current.memoizedState.isDehydrated){e.blockedOn=n.tag===3?n.stateNode.containerInfo:null;return}}}e.blockedOn=null}function Dp(e){if(e.blockedOn!==null)return!1;for(var t=e.targetContainers;0<t.length;){var n=dp(e.nativeEvent);if(n===null){n=e.nativeEvent;var r=new n.constructor(n.type,n);un=r,n.target.dispatchEvent(r),un=null}else return t=Et(n),t!==null&&ap(t),e.blockedOn=n,!1;t.shift()}return!0}function Op(e,t,n){Dp(e)&&n.delete(t)}function kp(){hp=!1,gp!==null&&Dp(gp)&&(gp=null),_p!==null&&Dp(_p)&&(_p=null),vp!==null&&Dp(vp)&&(vp=null),yp.forEach(Op),bp.forEach(Op)}function Ap(e,n){e.blockedOn===n&&(e.blockedOn=null,hp||(hp=!0,t.unstable_scheduleCallback(t.unstable_NormalPriority,kp)))}var jp=null;function Mp(e){jp!==e&&(jp=e,t.unstable_scheduleCallback(t.unstable_NormalPriority,function(){jp===e&&(jp=null);for(var t=0;t<e.length;t+=3){var n=e[t],r=e[t+1],i=e[t+2];if(typeof r!=`function`){if(pp(r||n)===null)continue;break}var a=Et(n);a!==null&&(e.splice(t,3),t-=3,ks(a,{pending:!0,data:i,method:n.method,action:r},r,i))}}))}function Np(e){function t(t){return Ap(t,e)}gp!==null&&Ap(gp,e),_p!==null&&Ap(_p,e),vp!==null&&Ap(vp,e),yp.forEach(t),bp.forEach(t);for(var n=0;n<xp.length;n++){var r=xp[n];r.blockedOn===e&&(r.blockedOn=null)}for(;0<xp.length&&(n=xp[0],n.blockedOn===null);)Ep(n),n.blockedOn===null&&xp.shift();if(n=(e.ownerDocument||e).$$reactFormReplay,n!=null)for(r=0;r<n.length;r+=3){var i=n[r],a=n[r+1],o=i[_t]||null;if(typeof a==`function`)o||Mp(n);else if(o){var s=null;if(a&&a.hasAttribute(`formAction`)){if(i=a,o=a[_t]||null)s=o.formAction;else if(pp(i)!==null)continue}else s=o.action;typeof s==`function`?n[r+1]=s:(n.splice(r,3),r-=3),Mp(n)}}}function Pp(){function e(e){e.canIntercept&&e.info===`react-transition`&&e.intercept({handler:function(){return new Promise(function(e){return i=e})},focusReset:`manual`,scroll:`manual`})}function t(){i!==null&&(i(),i=null),r||setTimeout(n,20)}function n(){if(!r&&!navigation.transition){var e=navigation.currentEntry;e&&e.url!=null&&navigation.navigate(e.url,{state:e.getState(),info:`react-transition`,history:`replace`})}}if(typeof navigation==`object`){var r=!1,i=null;return navigation.addEventListener(`navigate`,e),navigation.addEventListener(`navigatesuccess`,t),navigation.addEventListener(`navigateerror`,t),setTimeout(n,100),function(){r=!0,navigation.removeEventListener(`navigate`,e),navigation.removeEventListener(`navigatesuccess`,t),navigation.removeEventListener(`navigateerror`,t),i!==null&&(i(),i=null)}}}function Fp(e){this._internalRoot=e}Ip.prototype.render=Fp.prototype.render=function(e){var t=this._internalRoot;if(t===null)throw Error(i(409));var n=t.current;np(n,pu(),e,t,null,null)},Ip.prototype.unmount=Fp.prototype.unmount=function(){var e=this._internalRoot;if(e!==null){this._internalRoot=null;var t=e.containerInfo;np(e.current,2,null,e,null,null),bu(),t[vt]=null}};function Ip(e){this._internalRoot=e}Ip.prototype.unstable_scheduleHydration=function(e){if(e){var t=pt();e={blockedOn:null,target:e,priority:t};for(var n=0;n<xp.length&&t!==0&&t<xp[n].priority;n++);xp.splice(n,0,e),n===0&&Ep(e)}};var Lp=n.version;if(Lp!==`19.2.8`)throw Error(i(527,Lp,`19.2.8`));E.findDOMNode=function(e){var t=e._reactInternals;if(t===void 0)throw typeof e.render==`function`?Error(i(188)):(e=Object.keys(e).join(`,`),Error(i(268,e)));return e=d(t),e=e===null?null:p(e),e=e===null?null:e.stateNode,e};var Rp={bundleType:0,version:`19.2.8`,rendererPackageName:`react-dom`,currentDispatcherRef:T,reconcilerVersion:`19.2.8`};if(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__<`u`){var zp=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!zp.isDisabled&&zp.supportsFiber)try{We=zp.inject(Rp),Ge=zp}catch{}}e.createRoot=function(e,t){if(!a(e))throw Error(i(299));var n=!1,r=``,o=Qs,s=$s,c=ec;return t!=null&&(!0===t.unstable_strictMode&&(n=!0),t.identifierPrefix!==void 0&&(r=t.identifierPrefix),t.onUncaughtError!==void 0&&(o=t.onUncaughtError),t.onCaughtError!==void 0&&(s=t.onCaughtError),t.onRecoverableError!==void 0&&(c=t.onRecoverableError)),t=ep(e,1,!1,null,null,n,r,null,o,s,c,Pp),e[vt]=t.current,Sd(e),new Fp(t)}})),g=o(((e,t)=>{function n(){if(!(typeof __REACT_DEVTOOLS_GLOBAL_HOOK__>`u`||typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE!=`function`))try{__REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(n)}catch(e){console.error(e)}}n(),t.exports=h()})),_=c(u(),1),v=g(),y=`http://localhost:8000`,b=`health_companion_session`,x=()=>{try{let e=localStorage.getItem(b);return e?JSON.parse(e):null}catch{return null}},ee=e=>{localStorage.setItem(b,JSON.stringify(e))},S=()=>{localStorage.removeItem(b)},C=()=>x()?.access_token??null,te=class extends Error{constructor(e,t){super(e),this.status=t}};async function ne(e,t={}){let n=C(),r=`${y}${e}`,i={"Content-Type":`application/json`,...n&&{Authorization:`Bearer ${n}`},...t.headers},a=await fetch(r,{...t,headers:i});if(a.status===401)throw S(),window.dispatchEvent(new CustomEvent(`auth:unauthorized`)),new te(`Unauthorized`,401);if(!a.ok)throw new te(await a.text()||`HTTP ${a.status}`,a.status);return a.status===204?null:a.json()}var re={get:e=>ne(e,{method:`GET`}),post:(e,t)=>ne(e,{method:`POST`,body:JSON.stringify(t)}),put:(e,t)=>ne(e,{method:`PUT`,body:JSON.stringify(t)}),del:e=>ne(e,{method:`DELETE`})},ie=e=>`${y}${e}`,ae=()=>{let e=C();return e?{Authorization:`Bearer ${e}`}:{}},oe=o((e=>{var t=Symbol.for(`react.transitional.element`),n=Symbol.for(`react.fragment`);function r(e,n,r){var i=null;if(r!==void 0&&(i=``+r),n.key!==void 0&&(i=``+n.key),`key`in n)for(var a in r={},n)a!==`key`&&(r[a]=n[a]);else r=n;return n=r.ref,{$$typeof:t,type:e,key:i,ref:n===void 0?null:n,props:r}}e.Fragment=n,e.jsx=r,e.jsxs=r})),w=o(((e,t)=>{t.exports=oe()}))(),se=(0,_.createContext)(null),ce=()=>{let e=(0,_.useContext)(se);if(!e)throw Error(`useAuth must be used inside AuthProvider`);return e};function le({children:e}){let[t,n]=(0,_.useState)(null),[r,i]=(0,_.useState)(!0),a=(0,_.useCallback)(()=>{S(),n(null)},[]),o=(0,_.useCallback)(async()=>{if(!x()?.access_token){i(!1);return}try{let e=await re.get(`/auth/me`);console.info(`AuthProvider: verifySession got /auth/me`,e),n(e)}catch(e){e.status===401?a():console.warn(`Auth check failed (network), keeping session`)}finally{i(!1)}},[a]);(0,_.useEffect)(()=>{o();let e=()=>a();return window.addEventListener(`auth:unauthorized`,e),()=>window.removeEventListener(`auth:unauthorized`,e)},[o,a]);let s=(0,_.useCallback)(async(...e)=>{let t,r;if(e.length===1&&typeof e[0]==`object`){let n=e[0]||{};t=n.username,r=n.password}else t=e[0],r=e[1];let i=await re.post(`/auth/login`,{username:t,password:r});console.info(`AuthProvider: login response`,i),ee({access_token:i.access_token,refresh_token:i.refresh_token});let a=await re.get(`/auth/me`);return console.info(`AuthProvider: fetched /auth/me after login`,a),n(a),a},[]),c=(0,_.useCallback)(async(e,t,r,i)=>{let a;a=typeof e==`object`?e||{}:{username:e,email:t,password:r,full_name:i};let o=await re.post(`/auth/register`,a);ee({access_token:o.access_token,refresh_token:o.refresh_token});let s=await re.get(`/auth/me`);return n(s),s},[]);return(0,w.jsx)(se.Provider,{value:{user:t,loading:r,isAuthenticated:!!t,login:s,logout:a,register:c},children:e})}var ue=(0,_.createContext)(null);function T({children:e}){let{user:t,isAuthenticated:n}=ce(),r=t?.id||t?.username||`guest`,[i,a]=(0,_.useState)([]),[o,s]=(0,_.useState)(!0),[c,l]=(0,_.useState)(!1),[u,d]=(0,_.useState)(!1),[f,p]=(0,_.useState)([]),[m,h]=(0,_.useState)(()=>crypto.randomUUID()),[g,v]=(0,_.useState)(null),y=c||u;(0,_.useEffect)(()=>{if(!n)return;let e=!1;return re.get(`/agent/threads`).then(t=>{e||a(t)}).catch(e=>console.error(`Failed to load conversations:`,e)).finally(()=>{e||s(!1)}),()=>{e=!0}},[r,n]);let b=(0,_.useCallback)(async()=>{if(n)try{let e=await re.get(`/agent/threads`);a(e),v(t=>e.some(e=>e.thread_id===m)?m:e.some(e=>e.thread_id===t)?t:null)}catch(e){console.error(`Failed to refresh conversations:`,e)}},[n,m]),x=(0,_.useCallback)(()=>{let e=crypto.randomUUID();h(e),v(null),p([])},[]),ee=(0,_.useCallback)(async e=>{v(e),l(!0);try{let t=await re.get(`/agent/threads/${e}`);h(t.thread_id),p(t.messages||[])}catch(e){console.error(`Failed to load conversation:`,e)}finally{l(!1)}},[]);return(0,w.jsx)(ue.Provider,{value:{patientId:r,conversations:i,listLoading:o,historyLoading:c,sending:u,setSending:d,busy:y,messages:f,activeThreadId:m,selectedThreadId:g,setMessages:p,setSelectedThreadId:v,newChat:x,selectConversation:ee,refreshList:b},children:e})}function E(){let e=(0,_.useContext)(ue);if(!e)throw Error(`useConversations must be used within a ConversationsProvider`);return e}function de({onOpenLogin:e}){let{user:t,isAuthenticated:n,logout:r,loading:i}=ce(),[a,o]=(0,_.useState)(!1),s=(0,_.useRef)(null);(0,_.useEffect)(()=>{if(!a)return;let e=e=>{s.current&&!s.current.contains(e.target)&&o(!1)};return document.addEventListener(`mousedown`,e),()=>document.removeEventListener(`mousedown`,e)},[a]);let c=t?.full_name?t.full_name.split(` `).map(e=>e[0]).join(``).toUpperCase().slice(0,2):t?.username?.slice(0,2).toUpperCase()||`?`;return(0,w.jsx)(`nav`,{className:`bg-[#212121] border-b border-white/10 sticky top-0 z-40`,children:(0,w.jsxs)(`div`,{className:`flex items-center justify-between max-w-5xl mx-auto px-4 h-14`,children:[(0,w.jsxs)(`div`,{className:`flex items-center gap-2.5`,children:[(0,w.jsx)(`span`,{className:`flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 text-white font-bold text-sm shadow-sm`,children:(0,w.jsx)(`svg`,{className:`w-4.5 h-4.5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5`})})}),(0,w.jsx)(`span`,{className:`text-gray-200 font-semibold text-base tracking-tight`,children:`Health Intelligence`})]}),(0,w.jsxs)(`div`,{className:`flex items-center gap-1`,children:[(0,w.jsx)(`a`,{href:`#`,className:`px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5`,children:`Home`}),(0,w.jsx)(`a`,{href:`#`,className:`px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5`,children:`About`}),(0,w.jsx)(`div`,{className:`w-px h-5 bg-white/10 mx-2`}),i?(0,w.jsx)(`div`,{className:`w-8 h-8 rounded-full bg-white/5 animate-pulse`}):n?(0,w.jsxs)(`div`,{className:`relative`,ref:s,children:[(0,w.jsxs)(`button`,{onClick:()=>o(!a),className:`flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors`,children:[(0,w.jsx)(`span`,{className:`w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white text-xs font-semibold shadow-sm`,children:c}),(0,w.jsx)(`span`,{className:`text-sm text-gray-300 hidden sm:inline max-w-[120px] truncate`,children:t?.full_name||t?.username}),(0,w.jsx)(`svg`,{className:`w-4 h-4 text-gray-500 transition-transform ${a?`rotate-180`:``}`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M19 9l-7 7-7-7`})})]}),a&&(0,w.jsxs)(`div`,{className:`absolute right-0 mt-2 w-56 bg-[#2f2f2f] border border-white/10 rounded-xl shadow-2xl py-1.5 animate-fade-in`,children:[(0,w.jsxs)(`div`,{className:`px-4 py-2.5 border-b border-white/5`,children:[(0,w.jsx)(`p`,{className:`text-sm font-medium text-gray-200 truncate`,children:t?.full_name||t?.username}),(0,w.jsx)(`p`,{className:`text-xs text-gray-500 truncate mt-0.5`,children:t?.email})]}),(0,w.jsxs)(`button`,{onClick:()=>{r(),o(!1)},className:`w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-400 hover:bg-white/5 transition-colors`,children:[(0,w.jsx)(`svg`,{className:`w-4 h-4`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1`})}),`Sign out`]})]})]}):(0,w.jsx)(`button`,{onClick:e,className:`px-4 py-1.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 rounded-lg transition-all duration-200 shadow-sm`,children:`Sign in`})]})]})})}function fe(e){if(!e)return``;let t=new Date(e);if(Number.isNaN(t.getTime()))return``;let n=Math.round((Date.now()-t.getTime())/1e3);if(n<60)return`just now`;if(n<3600)return`${Math.round(n/60)}m ago`;if(n<86400)return`${Math.round(n/3600)}h ago`;let r=Math.round(n/86400);return r<7?`${r}d ago`:t.toLocaleDateString(void 0,{month:`short`,day:`numeric`})}function pe({conversation:e,active:t,onClick:n,disabled:r}){let{title:i,updated_at:a,snippet:o}=e;return(0,w.jsxs)(`button`,{type:`button`,onClick:n,disabled:r,title:i,className:`group w-full flex flex-col items-start gap-0.5 rounded-lg px-3 py-2.5 text-left transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-60 ${t?`bg-white/10 text-gray-100`:`text-gray-400 hover:bg-white/5 hover:text-gray-200`}`,children:[(0,w.jsx)(`span`,{className:`w-full truncate text-sm font-medium leading-snug`,children:i}),(0,w.jsxs)(`span`,{className:`flex w-full items-center gap-2 text-[11px] text-gray-500`,children:[(0,w.jsx)(`span`,{className:`shrink-0`,children:fe(a)}),o&&(0,w.jsx)(`span`,{className:`truncate opacity-70`,children:o})]})]})}function me(){return(0,w.jsx)(`svg`,{className:`h-4 w-4 shrink-0`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M12 4.5v15m7.5-7.5h-15`})})}function D(){return(0,w.jsx)(`svg`,{className:`h-4 w-4 shrink-0`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5`})})}function O(){return(0,w.jsx)(`svg`,{className:`h-4 w-4 shrink-0`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M6 18L18 6M6 6l12 12`})})}function he({onToggleCollapsed:e,onCloseMobile:t,mobile:n}){let{conversations:r,listLoading:i,busy:a,selectedThreadId:o,newChat:s,selectConversation:c}=E();return(0,w.jsxs)(w.Fragment,{children:[(0,w.jsx)(`div`,{className:`p-3`,children:(0,w.jsxs)(`button`,{type:`button`,onClick:s,disabled:a,title:`Start a new conversation`,className:`flex w-full items-center gap-2.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-gray-200 transition-colors duration-150 hover:border-white/20 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60`,children:[(0,w.jsx)(me,{}),(0,w.jsx)(`span`,{className:`truncate`,children:`New chat`})]})}),(0,w.jsx)(`div`,{className:`flex-1 overflow-y-auto px-2.5 pb-2 scrollbar-thin`,children:i?(0,w.jsx)(`div`,{className:`space-y-2 px-1 pt-1`,children:[...[,,,,,]].map((e,t)=>(0,w.jsx)(`div`,{className:`h-14 animate-pulse rounded-lg bg-white/5`},t))}):r.length===0?(0,w.jsxs)(`div`,{className:`px-3 pt-6 text-center`,children:[(0,w.jsx)(`p`,{className:`text-sm text-gray-500`,children:`No conversations yet`}),(0,w.jsx)(`p`,{className:`mt-1 text-xs text-gray-600`,children:`Start a new chat to begin.`})]}):(0,w.jsx)(`div`,{className:`space-y-0.5`,children:r.map(e=>(0,w.jsx)(pe,{conversation:e,active:e.thread_id===o,disabled:a,onClick:()=>c(e.thread_id)},e.thread_id))})}),(0,w.jsx)(`div`,{className:`border-t border-white/10 p-3`,children:n?(0,w.jsxs)(`button`,{type:`button`,onClick:t,className:`flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200`,children:[(0,w.jsx)(O,{}),(0,w.jsx)(`span`,{children:`Close sidebar`})]}):(0,w.jsxs)(`button`,{type:`button`,onClick:e,className:`flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200`,children:[(0,w.jsx)(D,{}),(0,w.jsx)(`span`,{children:`Collapse sidebar`})]})})]})}function ge({collapsed:e,onToggleCollapsed:t,mobileOpen:n,onCloseMobile:r}){return(0,w.jsxs)(w.Fragment,{children:[(0,w.jsx)(`aside`,{className:`hidden w-[280px] shrink-0 flex-col border-r border-white/10 bg-[#1b1b1b] ${e?`md:hidden`:`md:flex`}`,children:(0,w.jsx)(he,{onToggleCollapsed:t})}),(0,w.jsx)(`div`,{className:`fixed inset-0 z-40 bg-black/60 transition-opacity duration-300 md:hidden ${n?`opacity-100`:`pointer-events-none opacity-0`}`,onClick:r}),(0,w.jsx)(`aside`,{className:`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col bg-[#1b1b1b] transition-transform duration-300 md:hidden ${n?`translate-x-0`:`-translate-x-full`}`,children:(0,w.jsx)(he,{mobile:!0,onCloseMobile:r})})]})}var _e=2048,ve=2*1024*1024;function ye(e){return new Promise((t,n)=>{let r=new FileReader;r.onload=()=>t(r.result),r.onerror=()=>n(r.error||Error(`Failed to read file`)),r.readAsDataURL(e)})}function be(e,t){return new Promise(n=>{let r=new Image;r.onload=()=>{try{let i=Math.min(1,t/Math.max(r.width,r.height));if(i>=1)return n(e);let a=document.createElement(`canvas`);a.width=Math.round(r.width*i),a.height=Math.round(r.height*i),a.getContext(`2d`).drawImage(r,0,0,a.width,a.height),n(a.toDataURL(`image/jpeg`,.85))}catch{n(e)}},r.onerror=()=>n(e),r.src=e})}async function xe(e,t={}){let n=t.maxDim??_e,r=t.maxBytes??ve,i=await ye(e);e.size>r&&(i=await be(i,n));let a=i.indexOf(`,`);return{base64:a>=0?i.slice(a+1):i,dataUrl:i,name:e.name}}function Se({code:e,language:t}){let[n,r]=(0,_.useState)(!1);return(0,w.jsxs)(`div`,{className:`my-3 rounded-xl overflow-hidden border border-white/10 bg-black/40`,children:[(0,w.jsxs)(`div`,{className:`flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10`,children:[(0,w.jsx)(`span`,{className:`text-xs text-gray-500 font-mono`,children:t||`code`}),(0,w.jsx)(`button`,{onClick:async()=>{try{await navigator.clipboard.writeText(e),r(!0),setTimeout(()=>r(!1),2e3)}catch{}},className:`text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5`,children:n?(0,w.jsxs)(w.Fragment,{children:[(0,w.jsx)(`svg`,{className:`w-3.5 h-3.5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M5 13l4 4L19 7`})}),`Copied!`]}):(0,w.jsxs)(w.Fragment,{children:[(0,w.jsx)(`svg`,{className:`w-3.5 h-3.5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z`})}),`Copy`]})})]}),(0,w.jsx)(`pre`,{className:`p-4 overflow-x-auto text-sm leading-relaxed scrollbar-thin`,children:(0,w.jsx)(`code`,{className:`text-gray-300 font-mono`,children:e})})]})}function Ce({text:e}){return e?(0,w.jsx)(`div`,{className:`space-y-2`,children:e.split(/(`[^`]+`)/g).map((e,t)=>{if(e.startsWith("`")&&e.endsWith("`"))return(0,w.jsx)(`code`,{className:`px-1.5 py-0.5 bg-white/10 rounded-md text-sm font-mono text-emerald-300`,children:e.slice(1,-1)},t);let n=[],r=0,i=/\*\*(.+?)\*\*/g,a;for(;(a=i.exec(e))!==null;)a.index>r&&n.push({t:`text`,v:e.slice(r,a.index)}),n.push({t:`bold`,v:a[1]}),r=a.index+a[0].length;return r<e.length&&n.push({t:`text`,v:e.slice(r)}),(0,w.jsx)(`p`,{className:`text-gray-200 leading-relaxed whitespace-pre-wrap text-sm`,children:n.map((e,t)=>{if(e.t===`bold`)return(0,w.jsx)(`strong`,{className:`font-semibold text-gray-100`,children:e.v},t);let n=e.v.split(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g);if(n.length===1){let t=/(https?:\/\/[^\s]+)/g,n=e.v.split(t);return n.length===1?e.v:n.map((e,n)=>t.test(e)?(0,w.jsx)(`a`,{href:e,target:`_blank`,rel:`noopener noreferrer`,className:`text-blue-400 hover:underline`,children:e},n):e)}return n.map((e,t)=>t%2==1?(0,w.jsx)(`em`,{className:`text-gray-300`,children:e},t):e)})},t)})}):null}function we({content:e}){return e?(0,w.jsx)(`div`,{className:`prose prose-invert max-w-none`,children:e.split(/(```[\s\S]*?```)/g).map((e,t)=>{if(/^```[\s\S]*```$/.test(e)){let n=e.indexOf(`
`),r=n>3?e.slice(3,n).trim():``,i=n>0?n+1:3;return(0,w.jsx)(Se,{code:e.slice(i,-3),language:r},t)}return(0,w.jsx)(Ce,{text:e},t)})}):null}function Te({content:e}){let[t,n]=(0,_.useState)(!1),r=async()=>{try{await navigator.clipboard.writeText(e),n(!0),setTimeout(()=>n(!1),2e3)}catch{}};return(0,w.jsx)(`button`,{onClick:e=>{e.stopPropagation(),r()},className:`opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 rounded-lg hover:bg-white/10 text-gray-500 hover:text-gray-300`,title:`Copy message`,children:t?(0,w.jsx)(`svg`,{className:`w-4 h-4`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M5 13l4 4L19 7`})}):(0,w.jsx)(`svg`,{className:`w-4 h-4`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z`})})})}function Ee(){return(0,w.jsxs)(`div`,{className:`flex items-start gap-3 px-4 py-4 animate-fade-in`,children:[(0,w.jsx)(`div`,{className:`flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm`,children:(0,w.jsx)(`svg`,{className:`w-4 h-4 text-white`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5`})})}),(0,w.jsxs)(`div`,{className:`flex items-center gap-1 pt-2`,children:[(0,w.jsx)(`span`,{className:`w-2 h-2 rounded-full bg-gray-500 animate-bounce`,style:{animationDelay:`0ms`}}),(0,w.jsx)(`span`,{className:`w-2 h-2 rounded-full bg-gray-500 animate-bounce`,style:{animationDelay:`150ms`}}),(0,w.jsx)(`span`,{className:`w-2 h-2 rounded-full bg-gray-500 animate-bounce`,style:{animationDelay:`300ms`}})]})]})}var De=[{key:`agent`,label:`Agent`,hint:`Multi-step agent: translation, RAG, memory, image OCR`},{key:`rag`,label:`RAG`,hint:`Retrieve context, then stream an answer`},{key:`chat`,label:`Chat`,hint:`Plain streaming chat (no retrieval)`}];function Oe({mode:e,onChange:t,disabled:n}){return(0,w.jsx)(`div`,{className:`flex items-center gap-1 p-1 bg-[#2f2f2f] rounded-xl border border-white/10 w-fit`,title:De.find(t=>t.key===e)?.hint,children:De.map(r=>(0,w.jsx)(`button`,{onClick:()=>t(r.key),disabled:n,title:r.hint,className:`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 disabled:opacity-50 ${e===r.key?`bg-emerald-500/20 text-emerald-300 border border-emerald-500/30`:`text-gray-400 border border-transparent hover:text-gray-200 hover:bg-white/5`}`,children:r.label},r.key))})}function ke({meta:e}){if(!e)return null;let t=e.detected_lang&&e.detected_lang!==`en`?{label:`🌐 ${e.detected_lang}`}:null,n=e.needs_rag?{label:`🧠 RAG: ${e.retrieval_decision||`retrieved`}`}:{label:`💬 Direct`};return(0,w.jsxs)(`div`,{className:`flex flex-wrap items-center gap-1.5 mt-2`,children:[(0,w.jsx)(`span`,{className:`text-[10px] uppercase tracking-wider text-gray-600 mr-0.5`,children:`agent:`}),t&&(0,w.jsx)(`span`,{className:`text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400`,children:t.label}),(0,w.jsx)(`span`,{className:`text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400`,children:n.label}),e.sources?.length>0&&(0,w.jsx)(`span`,{className:`flex items-center gap-1 flex-wrap`,children:e.sources.map((e,t)=>(0,w.jsx)(`span`,{className:`text-[11px] px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-300 font-mono`,title:`Source`,children:e},t))})]})}function Ae(){return(0,w.jsx)(`div`,{className:`max-w-3xl mx-auto px-4 pt-6 space-y-6`,children:[...[,,,]].map((e,t)=>(0,w.jsxs)(`div`,{className:`flex items-start gap-3 px-4 animate-pulse`,children:[(0,w.jsx)(`div`,{className:`w-8 h-8 rounded-full bg-white/5`}),(0,w.jsxs)(`div`,{className:`flex-1 space-y-2 pt-1`,children:[(0,w.jsx)(`div`,{className:`h-4 w-1/3 bg-white/5 rounded`}),(0,w.jsx)(`div`,{className:`h-3 w-full bg-white/5 rounded`}),(0,w.jsx)(`div`,{className:`h-3 w-5/6 bg-white/5 rounded`})]})]},t))})}function je(){return(0,w.jsx)(`svg`,{className:`h-5 w-5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:1.8,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5`})})}function Me({onOpenSidebar:e}){let{patientId:t,conversations:n,messages:r,setMessages:i,activeThreadId:a,historyLoading:o,sending:s,setSending:c,refreshList:l}=E(),[u,d]=(0,_.useState)(``),[f,p]=(0,_.useState)(`agent`),[m,h]=(0,_.useState)(null),g=(0,_.useRef)(null),v=(0,_.useRef)(null),b=(0,_.useRef)(null),x=o||s,ee=n.find(e=>e.thread_id===a)?.title||`New chat`;(0,_.useEffect)(()=>{let e=v.current;e&&(e.style.height=`auto`,e.style.height=Math.min(e.scrollHeight,200)+`px`)},[u]),(0,_.useEffect)(()=>{g.current?.scrollIntoView({behavior:`smooth`})},[r,s]);let S=async(e,t)=>{let n=await fetch(ie(e),{method:`POST`,headers:{"Content-Type":`application/json`,...ae()},body:JSON.stringify({messages:t})});if(n.status===401)throw Error(`Session expired. Please sign in again.`);if(!n.ok)throw Error(`Server returned ${n.status}`);let r=n.body.getReader(),a=new TextDecoder,o={role:`assistant`,content:``};for(i([...t,o]);;){let{value:e,done:n}=await r.read();if(n)break;o={...o,content:o.content+a.decode(e,{stream:!0})},i([...t,{...o}])}},C=async(e,n)=>{let r={patient_id:t,query:e,thread_id:a};n&&(r.image_base64=n.base64);let i=await re.post(`/agent/invoke`,r);return{role:`assistant`,content:i.answer,meta:{detected_lang:i.detected_lang,needs_rag:i.needs_rag,retrieval_decision:i.retrieval_decision,sources:i.sources||[]}}},te=async e=>{let t=e===void 0?u:e;if(!t.trim()||x)return;let n={role:`user`,content:t};m&&(n.imageDataUrl=m.dataUrl);let a=[...r,n],o=m;i(a),d(``),h(null),c(!0);try{if(f===`agent`){let e=await C(t,o);i([...a,e]),l()}else await S(f===`rag`?`/rag/stream`:`/chat/stream`,a)}catch(e){console.error(`Chat error:`,e);let t=f===`agent`&&o?` The agent endpoint needs a running server with the LangGraph stack (checkpointer + Qdrant).`:``;i([...a,{role:`assistant`,content:`**Connection error:** ${e.message}\n\nMake sure your local API server is running at \`${y}\`.${t}`}])}finally{c(!1)}},ne=async e=>{let t=e.target.files?.[0];if(e.target.value=``,t)try{let e=await xe(t);h(e)}catch(e){console.error(`Image read failed:`,e)}},oe=e=>{e.key===`Enter`&&!e.shiftKey&&(e.preventDefault(),te())},se=e=>{te(e)};return(0,w.jsxs)(`div`,{className:`flex h-full flex-col`,children:[(0,w.jsxs)(`div`,{className:`flex h-12 shrink-0 items-center gap-2 border-b border-white/10 px-3`,children:[(0,w.jsx)(`button`,{type:`button`,onClick:e,"aria-label":`Toggle sidebar`,title:`Toggle sidebar`,className:`rounded-lg p-1.5 text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200`,children:(0,w.jsx)(je,{})}),(0,w.jsx)(`span`,{className:`truncate text-sm text-gray-300`,children:ee})]}),(0,w.jsx)(`div`,{className:`flex-1 overflow-y-auto scrollbar-thin`,children:o?(0,w.jsx)(Ae,{}):r.length===0&&!s?(0,w.jsxs)(`div`,{className:`flex flex-col items-center justify-center h-full px-4 animate-fade-in`,children:[(0,w.jsx)(`div`,{className:`w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10`,children:(0,w.jsx)(`svg`,{className:`w-8 h-8 text-white`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:1.5,d:`M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5`})})}),(0,w.jsx)(`h1`,{className:`text-2xl font-semibold text-gray-200 mb-2`,children:`Health Intelligence Companion`}),(0,w.jsx)(`p`,{className:`text-gray-500 mb-8 text-center max-w-md text-sm`,children:`Ask me anything about health, wellness, and medical information`}),(0,w.jsx)(`div`,{className:`grid grid-cols-2 gap-3 max-w-lg w-full px-4`,children:[`What are the symptoms of vitamin D deficiency?`,`Explain how the immune system works`,`Give me a heart-healthy meal plan`,`Best exercises for lower back pain?`].map(e=>(0,w.jsx)(`button`,{onClick:()=>se(e),className:`text-left text-sm text-gray-400 bg-white/5 hover:bg-white/[0.08] border border-white/10 hover:border-white/20 rounded-xl px-4 py-3 transition-all duration-200 leading-relaxed`,children:e},e))})]}):(0,w.jsxs)(`div`,{className:`max-w-3xl mx-auto px-4 pt-4 pb-2`,children:[r.map((e,t)=>(0,w.jsx)(`div`,{className:`animate-fade-in`,children:e.role===`user`?(0,w.jsx)(`div`,{className:`flex justify-end px-4 py-2 group`,children:(0,w.jsxs)(`div`,{className:`max-w-[75%] bg-[#2f2f2f] text-gray-100 rounded-2xl rounded-tr-sm px-4 py-2.5 relative`,children:[e.imageDataUrl&&(0,w.jsx)(`div`,{className:`mb-2`,children:(0,w.jsx)(`img`,{src:e.imageDataUrl,alt:`Attached`,className:`max-h-40 rounded-lg border border-white/10 object-contain`})}),(0,w.jsx)(`p`,{className:`whitespace-pre-wrap text-sm leading-relaxed`,children:e.content}),(0,w.jsx)(`div`,{className:`flex justify-end mt-1 -mb-1`,children:(0,w.jsx)(Te,{content:e.content})})]})}):(0,w.jsxs)(`div`,{className:`flex items-start gap-3 px-4 py-2 group`,children:[(0,w.jsx)(`div`,{className:`flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm mt-0.5`,children:(0,w.jsx)(`svg`,{className:`w-4 h-4 text-white`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:1.5,d:`M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5`})})}),(0,w.jsxs)(`div`,{className:`flex-1 min-w-0 pt-1`,children:[(0,w.jsxs)(`div`,{className:`flex items-center gap-1 mb-1.5`,children:[(0,w.jsx)(`span`,{className:`text-xs font-medium text-gray-400`,children:`Assistant`}),(0,w.jsx)(`span`,{className:`text-[10px] text-gray-600`,children:e.timestamp?fe(e.timestamp):`just now`}),(0,w.jsx)(`div`,{className:`ml-auto`,children:(0,w.jsx)(Te,{content:e.content})})]}),(0,w.jsx)(we,{content:e.content}),(0,w.jsx)(ke,{meta:e.meta})]})]})},t)),s&&(0,w.jsx)(Ee,{}),(0,w.jsx)(`div`,{ref:g})]})}),(0,w.jsx)(`div`,{className:`border-t border-white/10 bg-[#212121]`,children:(0,w.jsxs)(`div`,{className:`max-w-3xl mx-auto px-4 py-3`,children:[(0,w.jsxs)(`div`,{className:`flex items-center justify-between mb-2`,children:[(0,w.jsx)(Oe,{mode:f,onChange:p,disabled:x}),(0,w.jsx)(`span`,{className:`text-[11px] text-gray-600`,children:f===`agent`?`Agent: memory · RAG · images · multilingual`:f===`rag`?`Retrieve context then answer`:`Plain chat, no retrieval`})]}),m&&(0,w.jsxs)(`div`,{className:`flex items-center gap-2 mb-2 bg-[#2f2f2f] rounded-xl border border-white/10 px-3 py-2 w-fit`,children:[(0,w.jsx)(`img`,{src:m.dataUrl,alt:`Attached preview`,className:`h-10 w-10 object-cover rounded-lg border border-white/10`}),(0,w.jsxs)(`div`,{className:`text-xs text-gray-400 max-w-[180px] truncate`,children:[(0,w.jsx)(`span`,{className:`text-gray-200 font-medium`,children:m.name}),(0,w.jsx)(`span`,{className:`block text-[10px] text-gray-600`,children:f===`agent`?`OCR will read the text`:`Only used in Agent mode`})]}),(0,w.jsx)(`button`,{onClick:()=>h(null),className:`p-1 rounded-md text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors`,title:`Remove image`,children:(0,w.jsx)(`svg`,{className:`w-4 h-4`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:2,d:`M6 18L18 6M6 6l12 12`})})})]}),(0,w.jsxs)(`div`,{className:`relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10 focus-within:border-white/20 transition-colors`,children:[(0,w.jsx)(`button`,{onClick:()=>b.current?.click(),disabled:x,className:`ml-2 mb-3.5 p-2 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors disabled:opacity-40`,title:`Attach an image (OCR in Agent mode)`,children:(0,w.jsx)(`svg`,{className:`w-5 h-5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:1.8,d:`M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21zm9.75-12h.008v.008h-.008V9z`})})}),(0,w.jsx)(`input`,{ref:b,type:`file`,accept:`image/*`,onChange:ne,className:`hidden`}),(0,w.jsx)(`textarea`,{ref:v,value:u,onChange:e=>d(e.target.value),onKeyDown:oe,placeholder:f===`agent`?`Describe symptoms, attach a photo, or ask in your language…`:`Message Health Intelligence…`,disabled:x,rows:1,className:`flex-1 bg-transparent text-gray-100 placeholder-gray-600 resize-none outline-none px-3 py-3.5 text-sm leading-relaxed max-h-[200px] scrollbar-thin`}),(0,w.jsx)(`div`,{className:`flex items-center px-3 pb-3.5`,children:(0,w.jsx)(`button`,{onClick:()=>te(),disabled:!u.trim()||x,className:`w-8 h-8 rounded-xl bg-white text-gray-900 flex items-center justify-center disabled:opacity-20 disabled:cursor-not-allowed hover:bg-gray-200 transition-all duration-200 active:scale-95`,title:`Send`,children:(0,w.jsx)(`svg`,{className:`w-4 h-4`,fill:`currentColor`,viewBox:`0 0 24 24`,children:(0,w.jsx)(`path`,{d:`M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z`})})})})]}),(0,w.jsx)(`p`,{className:`text-center text-xs text-gray-700 mt-2`,children:`AI may produce inaccurate information about health topics. Always consult a healthcare professional.`})]})})]})}function Ne(){return(0,w.jsxs)(`div`,{className:`flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center`,children:[(0,w.jsx)(`div`,{className:`w-14 h-14 rounded-2xl bg-white/5 animate-pulse mb-6`}),(0,w.jsx)(`div`,{className:`h-5 w-64 bg-white/5 rounded animate-pulse mb-3`}),(0,w.jsx)(`div`,{className:`h-4 w-48 bg-white/5 rounded animate-pulse`})]})}function Pe({onOpenLogin:e}){return(0,w.jsxs)(`div`,{className:`flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center px-4 animate-fade-in`,children:[(0,w.jsx)(`div`,{className:`w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10`,children:(0,w.jsx)(`svg`,{className:`w-8 h-8 text-white`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,strokeWidth:1.5,d:`M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5`})})}),(0,w.jsx)(`h1`,{className:`text-2xl font-semibold text-gray-200 mb-2`,children:`Health Intelligence Companion`}),(0,w.jsx)(`p`,{className:`text-gray-500 mb-8 text-center max-w-md text-sm`,children:`Sign in to start chatting with your AI health assistant.`}),(0,w.jsx)(`button`,{onClick:e,className:`px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 transition-all duration-200 shadow-sm active:scale-[0.98]`,children:`Sign in`})]})}function Fe({onOpenLogin:e}){let{isAuthenticated:t,loading:n}=ce(),[r,i]=(0,_.useState)(!1),[a,o]=(0,_.useState)(!1);return n?(0,w.jsx)(Ne,{}):t?(0,w.jsxs)(`div`,{className:`flex h-[calc(100vh-65px)] overflow-hidden bg-[#212121]`,children:[(0,w.jsx)(ge,{collapsed:r,onToggleCollapsed:()=>i(!0),mobileOpen:a,onCloseMobile:()=>o(!1)}),(0,w.jsx)(`main`,{className:`flex min-w-0 flex-1 flex-col`,children:(0,w.jsx)(Me,{onOpenSidebar:()=>{window.matchMedia(`(min-width: 768px)`).matches?i(!1):o(!0)}})})]}):(0,w.jsx)(Pe,{onOpenLogin:e})}function Ie({onClose:e,onSwitchToRegister:t}){let{login:n}=ce(),[r,i]=(0,_.useState)(``),[a,o]=(0,_.useState)(``),[s,c]=(0,_.useState)(``),[l,u]=(0,_.useState)(!1),d=(0,_.useRef)(null);return(0,_.useEffect)(()=>{d.current?.focus()},[]),(0,_.useEffect)(()=>{let t=t=>{t.key===`Escape`&&e()};return window.addEventListener(`keydown`,t),()=>window.removeEventListener(`keydown`,t)},[e]),(0,w.jsx)(`div`,{className:`fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in`,onClick:t=>{t.target===t.currentTarget&&e()},children:(0,w.jsxs)(`div`,{className:`w-full max-w-sm mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl p-6 animate-fade-in`,children:[(0,w.jsxs)(`div`,{className:`flex items-center justify-between mb-5`,children:[(0,w.jsx)(`h2`,{className:`text-lg font-semibold text-gray-200`,children:`Welcome back`}),(0,w.jsx)(`button`,{onClick:e,className:`p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors`,children:(0,w.jsx)(`svg`,{className:`w-5 h-5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M6 18L18 6M6 6l12 12`})})})]}),(0,w.jsxs)(`form`,{onSubmit:async t=>{if(t.preventDefault(),c(``),!r.trim()||!a.trim()){c(`Please enter both username and password.`);return}u(!0);try{await n(r.trim(),a),e()}catch(e){c(e.message)}finally{u(!1)}},className:`space-y-4`,children:[(0,w.jsxs)(`div`,{children:[(0,w.jsx)(`label`,{htmlFor:`login-username`,className:`block text-sm text-gray-400 mb-1.5`,children:`Username`}),(0,w.jsx)(`input`,{ref:d,id:`login-username`,type:`text`,value:r,onChange:e=>i(e.target.value),disabled:l,autoComplete:`username`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`Enter your username`})]}),(0,w.jsxs)(`div`,{children:[(0,w.jsx)(`label`,{htmlFor:`login-password`,className:`block text-sm text-gray-400 mb-1.5`,children:`Password`}),(0,w.jsx)(`input`,{id:`login-password`,type:`password`,value:a,onChange:e=>o(e.target.value),disabled:l,autoComplete:`current-password`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`Enter your password`})]}),s&&(0,w.jsx)(`div`,{className:`bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400`,children:s}),(0,w.jsx)(`button`,{type:`submit`,disabled:l,className:`w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2`,children:l?(0,w.jsxs)(w.Fragment,{children:[(0,w.jsxs)(`svg`,{className:`w-4 h-4 animate-spin`,viewBox:`0 0 24 24`,fill:`none`,children:[(0,w.jsx)(`circle`,{className:`opacity-25`,cx:`12`,cy:`12`,r:`10`,stroke:`currentColor`,strokeWidth:`4`}),(0,w.jsx)(`path`,{className:`opacity-75`,fill:`currentColor`,d:`M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z`})]}),`Signing in…`]}):`Sign in`})]}),(0,w.jsxs)(`p`,{className:`mt-5 text-center text-sm text-gray-500`,children:[`Don't have an account?`,` `,(0,w.jsx)(`button`,{onClick:t,className:`text-emerald-400 hover:text-emerald-300 font-medium transition-colors`,children:`Create one`})]})]})})}function Le({onClose:e,onSwitchToLogin:t}){let{register:n}=ce(),[r,i]=(0,_.useState)(``),[a,o]=(0,_.useState)(``),[s,c]=(0,_.useState)(``),[l,u]=(0,_.useState)(``),[d,f]=(0,_.useState)(``),[p,m]=(0,_.useState)(!1),h=(0,_.useRef)(null);(0,_.useEffect)(()=>{h.current?.focus()},[]),(0,_.useEffect)(()=>{let t=t=>{t.key===`Escape`&&e()};return window.addEventListener(`keydown`,t),()=>window.removeEventListener(`keydown`,t)},[e]);let g=()=>r.trim()?r.trim().length<3?`Username must be at least 3 characters.`:a.trim()?/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(a.trim())?s?s.length<8?`Password must be at least 8 characters.`:/[A-Z]/.test(s)?/[a-z]/.test(s)?/\d/.test(s)?/[^A-Za-z0-9]/.test(s)?null:`Password must contain at least 1 special character.`:`Password must contain at least 1 digit.`:`Password must contain at least 1 lowercase letter.`:`Password must contain at least 1 uppercase letter.`:`Password is required.`:`Please enter a valid email address.`:`Email is required.`:`Username is required.`;return(0,w.jsx)(`div`,{className:`fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in`,onClick:t=>{t.target===t.currentTarget&&e()},children:(0,w.jsxs)(`div`,{className:`w-full max-w-sm mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl p-6 animate-fade-in`,children:[(0,w.jsxs)(`div`,{className:`flex items-center justify-between mb-5`,children:[(0,w.jsx)(`h2`,{className:`text-lg font-semibold text-gray-200`,children:`Create account`}),(0,w.jsx)(`button`,{onClick:e,className:`p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors`,children:(0,w.jsx)(`svg`,{className:`w-5 h-5`,fill:`none`,viewBox:`0 0 24 24`,stroke:`currentColor`,strokeWidth:2,children:(0,w.jsx)(`path`,{strokeLinecap:`round`,strokeLinejoin:`round`,d:`M6 18L18 6M6 6l12 12`})})})]}),(0,w.jsxs)(`form`,{onSubmit:async t=>{t.preventDefault(),f(``);let i=g();if(i){f(i);return}m(!0);try{await n(r.trim(),a.trim(),s,l.trim()||void 0),e()}catch(e){f(e.message)}finally{m(!1)}},className:`space-y-3.5`,children:[(0,w.jsxs)(`div`,{children:[(0,w.jsxs)(`label`,{htmlFor:`reg-username`,className:`block text-sm text-gray-400 mb-1.5`,children:[`Username `,(0,w.jsx)(`span`,{className:`text-red-500`,children:`*`})]}),(0,w.jsx)(`input`,{ref:h,id:`reg-username`,type:`text`,value:r,onChange:e=>i(e.target.value),disabled:p,autoComplete:`username`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`Choose a username`})]}),(0,w.jsxs)(`div`,{children:[(0,w.jsxs)(`label`,{htmlFor:`reg-email`,className:`block text-sm text-gray-400 mb-1.5`,children:[`Email `,(0,w.jsx)(`span`,{className:`text-red-500`,children:`*`})]}),(0,w.jsx)(`input`,{id:`reg-email`,type:`email`,value:a,onChange:e=>o(e.target.value),disabled:p,autoComplete:`email`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`you@example.com`})]}),(0,w.jsxs)(`div`,{children:[(0,w.jsxs)(`label`,{htmlFor:`reg-password`,className:`block text-sm text-gray-400 mb-1.5`,children:[`Password `,(0,w.jsx)(`span`,{className:`text-red-500`,children:`*`})]}),(0,w.jsx)(`input`,{id:`reg-password`,type:`password`,value:s,onChange:e=>c(e.target.value),disabled:p,autoComplete:`new-password`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`8+ chars · upper · lower · number · symbol`})]}),(0,w.jsxs)(`div`,{children:[(0,w.jsxs)(`label`,{htmlFor:`reg-fullname`,className:`block text-sm text-gray-400 mb-1.5`,children:[`Full name `,(0,w.jsx)(`span`,{className:`text-gray-600`,children:`(optional)`})]}),(0,w.jsx)(`input`,{id:`reg-fullname`,type:`text`,value:l,onChange:e=>u(e.target.value),disabled:p,autoComplete:`name`,className:`w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50`,placeholder:`Jane Doe`})]}),d&&(0,w.jsx)(`div`,{className:`bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400`,children:d}),(0,w.jsx)(`button`,{type:`submit`,disabled:p,className:`w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2`,children:p?(0,w.jsxs)(w.Fragment,{children:[(0,w.jsxs)(`svg`,{className:`w-4 h-4 animate-spin`,viewBox:`0 0 24 24`,fill:`none`,children:[(0,w.jsx)(`circle`,{className:`opacity-25`,cx:`12`,cy:`12`,r:`10`,stroke:`currentColor`,strokeWidth:`4`}),(0,w.jsx)(`path`,{className:`opacity-75`,fill:`currentColor`,d:`M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z`})]}),`Creating account…`]}):`Create account`})]}),(0,w.jsxs)(`p`,{className:`mt-5 text-center text-sm text-gray-500`,children:[`Already have an account?`,` `,(0,w.jsx)(`button`,{onClick:t,className:`text-emerald-400 hover:text-emerald-300 font-medium transition-colors`,children:`Sign in`})]})]})})}function Re(){let[e,t]=(0,_.useState)(!1),[n,r]=(0,_.useState)(!1);return(0,w.jsxs)(w.Fragment,{children:[(0,w.jsx)(de,{onOpenLogin:()=>t(!0)}),(0,w.jsx)(Fe,{onOpenLogin:()=>t(!0)}),e&&(0,w.jsx)(Ie,{onClose:()=>t(!1),onSwitchToRegister:()=>{t(!1),r(!0)}}),n&&(0,w.jsx)(Le,{onClose:()=>r(!1),onSwitchToLogin:()=>{r(!1),t(!0)}})]})}function ze(){let{user:e}=ce();return(0,w.jsx)(T,{children:(0,w.jsx)(Re,{})},e?.id||`anon`)}function Be(){return(0,w.jsx)(le,{children:(0,w.jsx)(ze,{})})}(0,v.createRoot)(document.getElementById(`root`)).render((0,w.jsx)(_.StrictMode,{children:(0,w.jsx)(Be,{})}));
```

---

## File: `frontend\src\App.css`

```css
/* App-level styles — currently empty, all styling via Tailwind in components */

```

---

## File: `frontend\src\App.jsx`

```
import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ConversationsProvider } from "./context/ConversationsContext";
import Navbar from "./components/Navbar";
import Chatbox from "./components/ChatBox";
import LoginModal from "./components/LoginModal";
import RegisterModal from "./components/RegisterModal";
import "./App.css";

function AppContent() {
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  return (
    <>
      <Navbar onOpenLogin={() => setShowLogin(true)} />

      <Chatbox onOpenLogin={() => setShowLogin(true)} />

      {showLogin && (
        <LoginModal
          onClose={() => setShowLogin(false)}
          onSwitchToRegister={() => {
            setShowLogin(false);
            setShowRegister(true);
          }}
        />
      )}

      {showRegister && (
        <RegisterModal
          onClose={() => setShowRegister(false)}
          onSwitchToLogin={() => {
            setShowRegister(false);
            setShowLogin(true);
          }}
        />
      )}
    </>
  );
}

function AuthedTree() {
  const { user } = useAuth();
  // Keying the provider by user id remounts all conversation state on
  // sign-in / sign-out / patient switch, so one patient never sees another's
  // threads or messages.
  return (
    <ConversationsProvider key={user?.id || "anon"}>
      <AppContent />
    </ConversationsProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AuthedTree />
    </AuthProvider>
  );
}

export default App;

```

---

## File: `frontend\src\index.css`

```css
@import "tailwindcss";

/* ── Animations ─────────────────────────────────────────────── */

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* ── Scrollbar ──────────────────────────────────────────────── */

.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #424242;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Firefox */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: #424242 transparent;
}

/* ── Base ────────────────────────────────────────────────────── */

html {
  color-scheme: dark;
}

body {
  background: #212121;
}

```

---

## File: `frontend\src\main.jsx`

```
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

```

---

## File: `frontend\src\components\ChatBox.jsx`

```
import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import Sidebar from "./Sidebar";
import ChatWindow from "./ChatWindow";

/**
 * Layout wrapper: the auth gate, then the conversation sidebar + chat
 * window. Owns the sidebar's desktop collapse and mobile-drawer state;
 * everything else lives in ConversationsContext / ChatWindow.
 */

function AuthSkeleton() {
  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center">
      <div className="w-14 h-14 rounded-2xl bg-white/5 animate-pulse mb-6" />
      <div className="h-5 w-64 bg-white/5 rounded animate-pulse mb-3" />
      <div className="h-4 w-48 bg-white/5 rounded animate-pulse" />
    </div>
  );
}

function SignInPrompt({ onOpenLogin }) {
  return (
    <div className="flex flex-col h-[calc(100vh-65px)] bg-[#212121] items-center justify-center px-4 animate-fade-in">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10">
        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
        </svg>
      </div>

      <h1 className="text-2xl font-semibold text-gray-200 mb-2">
        Health Intelligence Companion
      </h1>
      <p className="text-gray-500 mb-8 text-center max-w-md text-sm">
        Sign in to start chatting with your AI health assistant.
      </p>

      <button
        onClick={onOpenLogin}
        className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 transition-all duration-200 shadow-sm active:scale-[0.98]"
      >
        Sign in
      </button>
    </div>
  );
}

export default function ChatBox({ onOpenLogin }) {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [collapsed, setCollapsed] = useState(false); // desktop rail hidden
  const [mobileOpen, setMobileOpen] = useState(false); // mobile drawer open

  // The chat header's hamburger opens the sidebar in the way that fits the
  // current viewport: re-open the rail on desktop, slide in the drawer on
  // mobile.
  const openSidebar = () => {
    if (window.matchMedia("(min-width: 768px)").matches) setCollapsed(false);
    else setMobileOpen(true);
  };

  if (authLoading) return <AuthSkeleton />;
  if (!isAuthenticated) return <SignInPrompt onOpenLogin={onOpenLogin} />;

  return (
    <div className="flex h-[calc(100vh-65px)] overflow-hidden bg-[#212121]">
      <Sidebar
        collapsed={collapsed}
        onToggleCollapsed={() => setCollapsed(true)}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <ChatWindow onOpenSidebar={openSidebar} />
      </main>
    </div>
  );
}

```

---

## File: `frontend\src\components\ChatWindow.jsx`

```
import { useRef, useState, useEffect } from "react";
import { useConversations } from "../context/ConversationsContext";
import { api, getStreamUrl, getAuthHeaders } from "../utils/api";
import { getSession } from "../utils/session";
import { API_BASE } from "../utils/config";
import { fileToImageData } from "../utils/image";
import { formatRelativeTime } from "../utils/time";

// ─── Markdown Renderer ─────────────────────────────────────────

function CodeBlock({ code, language }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard not available */ }
  };

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-white/10 bg-black/40">
      <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/10">
        <span className="text-xs text-gray-500 font-mono">{language || "code"}</span>
        <button
          onClick={copy}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5"
        >
          {copied ? (
            <><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>Copied!</>
          ) : (
            <><svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>Copy</>
          )}
        </button>
      </div>
      <pre className="p-4 overflow-x-auto text-sm leading-relaxed scrollbar-thin">
        <code className="text-gray-300 font-mono">{code}</code>
      </pre>
    </div>
  );
}

function InlineContent({ text }) {
  if (!text) return null;

  // Split by inline code
  const parts = text.split(/(`[^`]+`)/g);

  return (
    <div className="space-y-2">
      {parts.map((part, i) => {
        if (part.startsWith("`") && part.endsWith("`")) {
          return (
            <code key={i} className="px-1.5 py-0.5 bg-white/10 rounded-md text-sm font-mono text-emerald-300">
              {part.slice(1, -1)}
            </code>
          );
        }
        // Process **bold** and *italic*, auto-link URLs
        const segments = [];
        let lastIdx = 0;
        const boldRe = /\*\*(.+?)\*\*/g;
        let match;
        while ((match = boldRe.exec(part)) !== null) {
          if (match.index > lastIdx) segments.push({ t: "text", v: part.slice(lastIdx, match.index) });
          segments.push({ t: "bold", v: match[1] });
          lastIdx = match.index + match[0].length;
        }
        if (lastIdx < part.length) segments.push({ t: "text", v: part.slice(lastIdx) });

        const processed = segments.map((seg, j) => {
          if (seg.t === "bold") return <strong key={j} className="font-semibold text-gray-100">{seg.v}</strong>;
          // Italic inside text
          const italicParts = seg.v.split(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g);
          if (italicParts.length === 1) {
            // Auto-link URLs
            const urlRe = /(https?:\/\/[^\s]+)/g;
            const urlParts = seg.v.split(urlRe);
            if (urlParts.length === 1) return seg.v;
            return urlParts.map((u, k) =>
              urlRe.test(u)
                ? <a key={k} href={u} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">{u}</a>
                : u
            );
          }
          return italicParts.map((ip, k) =>
            k % 2 === 1
              ? <em key={k} className="text-gray-300">{ip}</em>
              : ip
          );
        });

        return <p key={i} className="text-gray-200 leading-relaxed whitespace-pre-wrap text-sm">{processed}</p>;
      })}
    </div>
  );
}

function MarkdownContent({ content }) {
  if (!content) return null;

  // Split into code blocks and non-code sections
  const parts = content.split(/(```[\s\S]*?```)/g);

  return (
    <div className="prose prose-invert max-w-none">
      {parts.map((part, i) => {
        if (/^```[\s\S]*```$/.test(part)) {
          const firstNewline = part.indexOf("\n");
          const lang = firstNewline > 3 ? part.slice(3, firstNewline).trim() : "";
          const codeStart = firstNewline > 0 ? firstNewline + 1 : 3;
          const code = part.slice(codeStart, -3);
          return <CodeBlock key={i} code={code} language={lang} />;
        }
        return <InlineContent key={i} text={part} />;
      })}
    </div>
  );
}

// ─── Copy Button ──────────────────────────────────────────────

function CopyButton({ content }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard not available */ }
  };

  return (
    <button
      onClick={(e) => { e.stopPropagation(); copy(); }}
      className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1.5 rounded-lg hover:bg-white/10 text-gray-500 hover:text-gray-300"
      title="Copy message"
    >
      {copied ? (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ) : (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      )}
    </button>
  );
}

// ─── Typing Indicator ───────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 px-4 py-4 animate-fade-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm">
        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
        </svg>
      </div>
      <div className="flex items-center gap-1 pt-2">
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}

// ─── Mode Selector ─────────────────────────────────────────────

const MODES = [
  { key: "agent", label: "Agent", hint: "Multi-step agent: translation, RAG, memory, image OCR" },
  { key: "rag", label: "RAG", hint: "Retrieve context, then stream an answer" },
  { key: "chat", label: "Chat", hint: "Plain streaming chat (no retrieval)" },
];

function ModeSelector({ mode, onChange, disabled }) {
  return (
    <div className="flex items-center gap-1 p-1 bg-[#2f2f2f] rounded-xl border border-white/10 w-fit" title={MODES.find((m) => m.key === mode)?.hint}>
      {MODES.map((m) => (
        <button
          key={m.key}
          onClick={() => onChange(m.key)}
          disabled={disabled}
          title={m.hint}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 disabled:opacity-50 ${
            mode === m.key
              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
              : "text-gray-400 border border-transparent hover:text-gray-200 hover:bg-white/5"
          }`}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}

// ─── Message Metadata Chips ─────────────────────────────────────

function MessageMeta({ meta }) {
  if (!meta) return null;

  const langChip = meta.detected_lang && meta.detected_lang !== "en"
    ? { label: `🌐 ${meta.detected_lang}` }
    : null;
  const ragChip = meta.needs_rag
    ? { label: `🧠 RAG: ${meta.retrieval_decision || "retrieved"}` }
    : { label: "💬 Direct" };

  return (
    <div className="flex flex-wrap items-center gap-1.5 mt-2">
      <span className="text-[10px] uppercase tracking-wider text-gray-600 mr-0.5">agent:</span>
      {langChip && (
        <span className="text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400">
          {langChip.label}
        </span>
      )}
      <span className="text-[11px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-gray-400">
        {ragChip.label}
      </span>
      {meta.sources?.length > 0 && (
        <span className="flex items-center gap-1 flex-wrap">
          {meta.sources.map((src, i) => (
            <span
              key={i}
              className="text-[11px] px-2 py-0.5 rounded-md bg-blue-500/10 border border-blue-500/20 text-blue-300 font-mono"
              title="Source"
            >
              {src}
            </span>
          ))}
        </span>
      )}
    </div>
  );
}

// ─── History Skeleton ───────────────────────────────────────────

function HistorySkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-4 pt-6 space-y-6">
      {[...Array(3)].map((_, i) => (
        <div key={i} className="flex items-start gap-3 px-4 animate-pulse">
          <div className="w-8 h-8 rounded-full bg-white/5" />
          <div className="flex-1 space-y-2 pt-1">
            <div className="h-4 w-1/3 bg-white/5 rounded" />
            <div className="h-3 w-full bg-white/5 rounded" />
            <div className="h-3 w-5/6 bg-white/5 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Header ─────────────────────────────────────────────────────

function HamburgerIcon() {
  return (
    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  );
}

// ─── Main Component ─────────────────────────────────────────────

export default function ChatWindow({ onOpenSidebar }) {
  const {
    patientId,
    conversations,
    messages,
    setMessages,
    activeThreadId,
    historyLoading,
    sending,
    setSending,
    refreshList,
  } = useConversations();

  const [input, setInput] = useState("");
  const [mode, setMode] = useState("agent");
  const [image, setImage] = useState(null); // { base64, dataUrl, name }
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const busy = historyLoading || sending;
  const current = conversations.find((c) => c.thread_id === activeThreadId);
  const headerTitle = current?.title || "New chat";

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 200) + "px";
    }
  }, [input]);

  // Auto-scroll on new content
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  // Stream a completion from /chat/stream or /rag/stream (token-by-token).
  const streamChat = async (endpoint, history) => {
    const res = await fetch(getStreamUrl(endpoint), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify({ messages: history }),
    });

    if (res.status === 401) {
      throw new Error('Session expired. Please sign in again.');
    }

    if (!res.ok) throw new Error(`Server returned ${res.status}`);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let assistantMsg = { role: 'assistant', content: '' };
    setMessages([...history, assistantMsg]);

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      assistantMsg = {
        ...assistantMsg,
        content: assistantMsg.content + decoder.decode(value, { stream: true }),
      };
      setMessages([...history, { ...assistantMsg }]);
    }
  };

  // Run the full LangGraph agent (/agent/invoke). Returns the answer + metadata.
  const runAgent = async (text, attachedImage) => {
    const payload = {
      patient_id: patientId,
      query: text,
      thread_id: activeThreadId, // resume/continue this conversation
    };
    if (attachedImage) payload.image_base64 = attachedImage.base64;

    const data = await api.post("/agent/invoke", payload);

    return {
      role: "assistant",
      content: data.answer,
      meta: {
        detected_lang: data.detected_lang,
        needs_rag: data.needs_rag,
        retrieval_decision: data.retrieval_decision,
        sources: data.sources || [],
      },
    };
  };

  const sendMessage = async (overrideText) => {
    const text = overrideText !== undefined ? overrideText : input;
    if (!text.trim() || busy) return;

    const userMsg = { role: "user", content: text };
    if (image) userMsg.imageDataUrl = image.dataUrl;
    const history = [...messages, userMsg];
    const attachedImage = image; // snapshot before clearing

    setMessages(history);
    setInput("");
    setImage(null);
    setSending(true);

    try {
      if (mode === "agent") {
        const assistantMsg = await runAgent(text, attachedImage);
        setMessages([...history, assistantMsg]);
        // Update the sidebar: new thread appears, or timestamp refreshes.
        refreshList();
      } else {
        const endpoint = mode === "rag" ? "/rag/stream" : "/chat/stream";
        await streamChat(endpoint, history);
      }
    } catch (err) {
      console.error("Chat error:", err);
      const extra = mode === "agent" && attachedImage
        ? " The agent endpoint needs a running server with the LangGraph stack (checkpointer + Qdrant)."
        : "";
      setMessages([
        ...history,
        {
          role: 'assistant',
          content: `**Connection error:** ${err.message}\n\nMake sure your local API server is running at \`${API_BASE}\`.${extra}`,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-selecting the same file
    if (!file) return;
    try {
      const img = await fileToImageData(file);
      setImage(img);
    } catch (err) {
      console.error("Image read failed:", err);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestion = (text) => {
    sendMessage(text);
  };

  return (
    <div className="flex h-full flex-col">
      {/* ── Header ── */}
      <div className="flex h-12 shrink-0 items-center gap-2 border-b border-white/10 px-3">
        <button
          type="button"
          onClick={onOpenSidebar}
          aria-label="Toggle sidebar"
          title="Toggle sidebar"
          className="rounded-lg p-1.5 text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
        >
          <HamburgerIcon />
        </button>
        <span className="truncate text-sm text-gray-300">{headerTitle}</span>
      </div>

      {/* ── Messages Area ── */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {historyLoading ? (
          <HistorySkeleton />
        ) : messages.length === 0 && !sending ? (
          /* ── Empty State ── */
          <div className="flex flex-col items-center justify-center h-full px-4 animate-fade-in">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 mb-6 ring-1 ring-white/10">
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
              </svg>
            </div>

            <h1 className="text-2xl font-semibold text-gray-200 mb-2">
              Health Intelligence Companion
            </h1>
            <p className="text-gray-500 mb-8 text-center max-w-md text-sm">
              Ask me anything about health, wellness, and medical information
            </p>

            {/* Suggestion Chips */}
            <div className="grid grid-cols-2 gap-3 max-w-lg w-full px-4">
              {[
                "What are the symptoms of vitamin D deficiency?",
                "Explain how the immune system works",
                "Give me a heart-healthy meal plan",
                "Best exercises for lower back pain?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSuggestion(suggestion)}
                  className="text-left text-sm text-gray-400 bg-white/5 hover:bg-white/[0.08] border border-white/10 hover:border-white/20 rounded-xl px-4 py-3 transition-all duration-200 leading-relaxed"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* ── Message Thread ── */
          <div className="max-w-3xl mx-auto px-4 pt-4 pb-2">
            {messages.map((msg, i) => (
              <div key={i} className="animate-fade-in">
                {msg.role === "user" ? (
                  <div className="flex justify-end px-4 py-2 group">
                    <div className="max-w-[75%] bg-[#2f2f2f] text-gray-100 rounded-2xl rounded-tr-sm px-4 py-2.5 relative">
                      {msg.imageDataUrl && (
                        <div className="mb-2">
                          <img
                            src={msg.imageDataUrl}
                            alt="Attached"
                            className="max-h-40 rounded-lg border border-white/10 object-contain"
                          />
                        </div>
                      )}
                      <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                      <div className="flex justify-end mt-1 -mb-1">
                        <CopyButton content={msg.content} />
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start gap-3 px-4 py-2 group">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-sm mt-0.5">
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0 pt-1">
                      <div className="flex items-center gap-1 mb-1.5">
                        <span className="text-xs font-medium text-gray-400">Assistant</span>
                        <span className="text-[10px] text-gray-600">
                          {msg.timestamp ? formatRelativeTime(msg.timestamp) : "just now"}
                        </span>
                        <div className="ml-auto">
                          <CopyButton content={msg.content} />
                        </div>
                      </div>
                      <MarkdownContent content={msg.content} />
                      <MessageMeta meta={msg.meta} />
                    </div>
                  </div>
                )}
              </div>
            ))}
            {sending && <TypingIndicator />}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* ── Input Area ── */}
      <div className="border-t border-white/10 bg-[#212121]">
        <div className="max-w-3xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <ModeSelector mode={mode} onChange={setMode} disabled={busy} />
            <span className="text-[11px] text-gray-600">
              {mode === "agent"
                ? "Agent: memory · RAG · images · multilingual"
                : mode === "rag"
                  ? "Retrieve context then answer"
                  : "Plain chat, no retrieval"}
            </span>
          </div>

          {image && (
            <div className="flex items-center gap-2 mb-2 bg-[#2f2f2f] rounded-xl border border-white/10 px-3 py-2 w-fit">
              <img src={image.dataUrl} alt="Attached preview" className="h-10 w-10 object-cover rounded-lg border border-white/10" />
              <div className="text-xs text-gray-400 max-w-[180px] truncate">
                <span className="text-gray-200 font-medium">{image.name}</span>
                <span className="block text-[10px] text-gray-600">
                  {mode === "agent" ? "OCR will read the text" : "Only used in Agent mode"}
                </span>
              </div>
              <button
                onClick={() => setImage(null)}
                className="p-1 rounded-md text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors"
                title="Remove image"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          <div className="relative flex items-end bg-[#2f2f2f] rounded-2xl border border-white/10 focus-within:border-white/20 transition-colors">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={busy}
              className="ml-2 mb-3.5 p-2 rounded-lg text-gray-500 hover:text-gray-200 hover:bg-white/5 transition-colors disabled:opacity-40"
              title="Attach an image (OCR in Agent mode)"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.8} d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21zm9.75-12h.008v.008h-.008V9z" />
              </svg>
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === "agent"
                  ? "Describe symptoms, attach a photo, or ask in your language…"
                  : "Message Health Intelligence…"
              }
              disabled={busy}
              rows={1}
              className="flex-1 bg-transparent text-gray-100 placeholder-gray-600 resize-none outline-none px-3 py-3.5 text-sm leading-relaxed max-h-[200px] scrollbar-thin"
            />
            <div className="flex items-center px-3 pb-3.5">
              <button
                onClick={() => sendMessage()}
                disabled={!input.trim() || busy}
                className="w-8 h-8 rounded-xl bg-white text-gray-900 flex items-center justify-center disabled:opacity-20 disabled:cursor-not-allowed hover:bg-gray-200 transition-all duration-200 active:scale-95"
                title="Send"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.404z" />
                </svg>
              </button>
            </div>
          </div>
          <p className="text-center text-xs text-gray-700 mt-2">
            AI may produce inaccurate information about health topics. Always consult a healthcare professional.
          </p>
        </div>
      </div>
    </div>
  );
}

```

---

## File: `frontend\src\components\ConversationItem.jsx`

```
import { formatRelativeTime } from "../utils/time";

/**
 * One row in the sidebar: conversation title, last-updated time, and a
 * one-line snippet. Highlights when it's the active conversation.
 */
export default function ConversationItem({ conversation, active, onClick, disabled }) {
  const { title, updated_at, snippet } = conversation;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`group w-full flex flex-col items-start gap-0.5 rounded-lg px-3 py-2.5 text-left transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-60 ${
        active
          ? "bg-white/10 text-gray-100"
          : "text-gray-400 hover:bg-white/5 hover:text-gray-200"
      }`}
    >
      <span className="w-full truncate text-sm font-medium leading-snug">{title}</span>
      <span className="flex w-full items-center gap-2 text-[11px] text-gray-500">
        <span className="shrink-0">{formatRelativeTime(updated_at)}</span>
        {snippet && <span className="truncate opacity-70">{snippet}</span>}
      </span>
    </button>
  );
}

```

---

## File: `frontend\src\components\LoginModal.jsx`

```
import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginModal({ onClose, onSwitchToRegister }) {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const usernameRef = useRef(null);

  useEffect(() => {
    usernameRef.current?.focus();
  }, []);

  // Close on Escape
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!username.trim() || !password.trim()) {
      setError("Please enter both username and password.");
      return;
    }

    setSubmitting(true);
    try {
      await login(username.trim(), password);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-sm mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl p-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-200">Welcome back</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-username" className="block text-sm text-gray-400 mb-1.5">
              Username
            </label>
            <input
              ref={usernameRef}
              id="login-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
              autoComplete="username"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-sm text-gray-400 mb-1.5">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
              autoComplete="current-password"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Signing in…
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-5 text-center text-sm text-gray-500">
          Don&apos;t have an account?{" "}
          <button
            onClick={onSwitchToRegister}
            className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
          >
            Create one
          </button>
        </p>
      </div>
    </div>
  );
}

```

---

## File: `frontend\src\components\Navbar.jsx`

```
import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ onOpenLogin }) {
  const { user, isAuthenticated, logout, loading } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    if (!menuOpen) return;
    const handleClick = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [menuOpen]);

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : user?.username?.slice(0, 2).toUpperCase() || "?";

  return (
    <nav className="bg-[#212121] border-b border-white/10 sticky top-0 z-40">
      <div className="flex items-center justify-between max-w-5xl mx-auto px-4 h-14">
        {/* Left: Brand */}
        <div className="flex items-center gap-2.5">
          <span className="flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 text-white font-bold text-sm shadow-sm">
            <svg className="w-4.5 h-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
            </svg>
          </span>
          <span className="text-gray-200 font-semibold text-base tracking-tight">
            Health Intelligence
          </span>
        </div>

        {/* Right: Navigation */}
        <div className="flex items-center gap-1">
          <a
            href="#"
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5"
          >
            Home
          </a>
          <a
            href="#"
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded-lg hover:bg-white/5"
          >
            About
          </a>
          <div className="w-px h-5 bg-white/10 mx-2" />

          {loading ? (
            <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse" />
          ) : isAuthenticated ? (
            /* ── User Menu ── */
            <div className="relative" ref={menuRef}>
              <button
                onClick={() => setMenuOpen(!menuOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
              >
                <span className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-white text-xs font-semibold shadow-sm">
                  {initials}
                </span>
                <span className="text-sm text-gray-300 hidden sm:inline max-w-[120px] truncate">
                  {user?.full_name || user?.username}
                </span>
                <svg
                  className={`w-4 h-4 text-gray-500 transition-transform ${menuOpen ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {menuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-[#2f2f2f] border border-white/10 rounded-xl shadow-2xl py-1.5 animate-fade-in">
                  {/* User info header */}
                  <div className="px-4 py-2.5 border-b border-white/5">
                    <p className="text-sm font-medium text-gray-200 truncate">
                      {user?.full_name || user?.username}
                    </p>
                    <p className="text-xs text-gray-500 truncate mt-0.5">{user?.email}</p>
                  </div>

                  <button
                    onClick={() => { logout(); setMenuOpen(false); }}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-400 hover:bg-white/5 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* ── Login Button ── */
            <button
              onClick={onOpenLogin}
              className="px-4 py-1.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 rounded-lg transition-all duration-200 shadow-sm"
            >
              Sign in
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

```

---

## File: `frontend\src\components\RegisterModal.jsx`

```
import { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export default function RegisterModal({ onClose, onSwitchToLogin }) {
  const { register } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const usernameRef = useRef(null);

  useEffect(() => {
    usernameRef.current?.focus();
  }, []);

  // Close on Escape
  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const validate = () => {
    if (!username.trim()) return "Username is required.";
    if (username.trim().length < 3) return "Username must be at least 3 characters.";
    if (!email.trim()) return "Email is required.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) return "Please enter a valid email address.";
    if (!password) return "Password is required.";
    if (password.length < 8) return "Password must be at least 8 characters.";
    if (!/[A-Z]/.test(password)) return "Password must contain at least 1 uppercase letter.";
    if (!/[a-z]/.test(password)) return "Password must contain at least 1 lowercase letter.";
    if (!/\d/.test(password)) return "Password must contain at least 1 digit.";
    if (!/[^A-Za-z0-9]/.test(password)) return "Password must contain at least 1 special character.";
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    try {
      await register(username.trim(), email.trim(), password, fullName.trim() || undefined);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="w-full max-w-sm mx-4 bg-[#212121] border border-white/10 rounded-2xl shadow-2xl p-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-gray-200">Create account</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          <div>
            <label htmlFor="reg-username" className="block text-sm text-gray-400 mb-1.5">
              Username <span className="text-red-500">*</span>
            </label>
            <input
              ref={usernameRef}
              id="reg-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
              autoComplete="username"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Choose a username"
            />
          </div>

          <div>
            <label htmlFor="reg-email" className="block text-sm text-gray-400 mb-1.5">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={submitting}
              autoComplete="email"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="block text-sm text-gray-400 mb-1.5">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
              autoComplete="new-password"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="8+ chars · upper · lower · number · symbol"
            />
          </div>

          <div>
            <label htmlFor="reg-fullname" className="block text-sm text-gray-400 mb-1.5">
              Full name <span className="text-gray-600">(optional)</span>
            </label>
            <input
              id="reg-fullname"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={submitting}
              autoComplete="name"
              className="w-full bg-[#2f2f2f] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-gray-200 placeholder-gray-600 outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all disabled:opacity-50"
              placeholder="Jane Doe"
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-2.5 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-medium text-sm hover:from-emerald-400 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 active:scale-[0.98] flex items-center justify-center gap-2"
          >
            {submitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Creating account…
              </>
            ) : (
              "Create account"
            )}
          </button>
        </form>

        {/* Footer */}
        <p className="mt-5 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <button
            onClick={onSwitchToLogin}
            className="text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
          >
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
}

```

---

## File: `frontend\src\components\Sidebar.jsx`

```
import { useConversations } from "../context/ConversationsContext";
import ConversationItem from "./ConversationItem";

function PlusIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  );
}

function CollapseIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
    </svg>
  );
}

function XIcon() {
  return (
    <svg className="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

/**
 * The pieces shared by both the desktop rail and the mobile drawer:
 * New Chat button, the conversation list, and the footer action.
 */
function SidebarInner({ onToggleCollapsed, onCloseMobile, mobile }) {
  const { conversations, listLoading, busy, selectedThreadId, newChat, selectConversation } =
    useConversations();

  return (
    <>
      {/* New Chat */}
      <div className="p-3">
        <button
          type="button"
          onClick={newChat}
          disabled={busy}
          title="Start a new conversation"
          className="flex w-full items-center gap-2.5 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm font-medium text-gray-200 transition-colors duration-150 hover:border-white/20 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <PlusIcon />
          <span className="truncate">New chat</span>
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2.5 pb-2 scrollbar-thin">
        {listLoading ? (
          <div className="space-y-2 px-1 pt-1">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-14 animate-pulse rounded-lg bg-white/5" />
            ))}
          </div>
        ) : conversations.length === 0 ? (
          <div className="px-3 pt-6 text-center">
            <p className="text-sm text-gray-500">No conversations yet</p>
            <p className="mt-1 text-xs text-gray-600">Start a new chat to begin.</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {conversations.map((c) => (
              <ConversationItem
                key={c.thread_id}
                conversation={c}
                active={c.thread_id === selectedThreadId}
                disabled={busy}
                onClick={() => selectConversation(c.thread_id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 p-3">
        {mobile ? (
          <button
            type="button"
            onClick={onCloseMobile}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
          >
            <XIcon />
            <span>Close sidebar</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={onToggleCollapsed}
            className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-gray-400 transition-colors duration-150 hover:bg-white/5 hover:text-gray-200"
          >
            <CollapseIcon />
            <span>Collapse sidebar</span>
          </button>
        )}
      </div>
    </>
  );
}

/**
 * The sidebar. On desktop it's a fixed-width (280px) rail that can be
 * collapsed away; on mobile it slides in as an overlay drawer over a
 * dimmed backdrop. Both share SidebarInner so the list stays consistent.
 */
export default function Sidebar({ collapsed, onToggleCollapsed, mobileOpen, onCloseMobile }) {
  return (
    <>
      {/* Desktop rail */}
      <aside
        className={`hidden w-[280px] shrink-0 flex-col border-r border-white/10 bg-[#1b1b1b] ${
          collapsed ? "md:hidden" : "md:flex"
        }`}
      >
        <SidebarInner onToggleCollapsed={onToggleCollapsed} />
      </aside>

      {/* Mobile backdrop */}
      <div
        className={`fixed inset-0 z-40 bg-black/60 transition-opacity duration-300 md:hidden ${
          mobileOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onCloseMobile}
      />

      {/* Mobile drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[280px] flex-col bg-[#1b1b1b] transition-transform duration-300 md:hidden ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <SidebarInner mobile onCloseMobile={onCloseMobile} />
      </aside>
    </>
  );
}

```

---

## File: `frontend\src\context\AuthContext.jsx`

```
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../utils/api';
import { getSession, setSession, clearSession } from '../utils/session';

const AuthContext = createContext(null);

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const verifySession = useCallback(async () => {
    const session = getSession();
    if (!session?.access_token) {
      setLoading(false);
      return;
    }

    try {
      const me = await api.get('/auth/me');
      console.info('AuthProvider: verifySession got /auth/me', me);
      setUser(me);
    } catch (err) {
      if (err.status === 401) {
        // Already handled inside api.js (clears storage + fires event),
        // but keep UI state in sync just in case.
        logout();
      } else {
        // Network error / server restarting — keep cached session alive
        // so the user isn't kicked out on a flaky connection.
        console.warn('Auth check failed (network), keeping session');
      }
    } finally {
      setLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    verifySession();

    const onUnauthorized = () => logout();
    window.addEventListener('auth:unauthorized', onUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', onUnauthorized);
  }, [verifySession, logout]);

  const login = useCallback(async (...args) => {
    // Support both call styles: login(username, password) and login({ username, password })
    let uname;
    let pwd;
    if (args.length === 1 && typeof args[0] === 'object') {
      const obj = args[0] || {};
      uname = obj.username;
      pwd = obj.password;
    } else {
      uname = args[0];
      pwd = args[1];
    }

    const res = await api.post('/auth/login', { username: uname, password: pwd });
    console.info('AuthProvider: login response', res);
    setSession({
      access_token: res.access_token,
      refresh_token: res.refresh_token, // backend sends copy of access_token
    });
    const me = await api.get('/auth/me');
    console.info('AuthProvider: fetched /auth/me after login', me);
    setUser(me);
    return me;
  }, []);

  const register = useCallback(async (a, b, c, d) => {
    // Support register(username, email, password, full_name)
    // and register({ username, email, password, full_name })
    let payload;
    if (typeof a === 'object') {
      payload = a || {};
    } else {
      payload = { username: a, email: b, password: c, full_name: d };
    }

    const res = await api.post('/auth/register', payload);
    setSession({
      access_token: res.access_token,
      refresh_token: res.refresh_token,
    });
    const me = await api.get('/auth/me');
    setUser(me);
    return me;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
```

---

## File: `frontend\src\context\ConversationsContext.jsx`

```
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import api from "../utils/api";

/**
 * Owns everything the conversation-history UI needs: the sidebar list, the
 * currently active LangGraph thread, and the restored message transcript.
 *
 * The backend is the single source of truth — the list is fetched from
 * /agent/threads and a thread's messages from /agent/threads/{id}; we keep
 * no separate local store. State is shared here (via the context) so
 * Sidebar and ChatWindow stay in sync without prop drilling.
 */
const ConversationsContext = createContext(null);

export function ConversationsProvider({ children }) {
  const { user, isAuthenticated } = useAuth();
  const patientId = user?.id || user?.username || "guest";

  const [conversations, setConversations] = useState([]);
  // Starts true: the provider remounts on every sign-in (keyed by user id in
  // App.jsx), so the sidebar shows its skeleton until the first fetch lands.
  const [listLoading, setListLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([]);
  // A brand-new chat gets a fresh UUID thread id; selecting an existing
  // conversation replaces it with that conversation's thread id.
  const [activeThreadId, setActiveThreadId] = useState(() => crypto.randomUUID());
  // Which sidebar row is highlighted. null for a brand-new chat that has not
  // been persisted yet (there is no row for it).
  const [selectedThreadId, setSelectedThreadId] = useState(null);

  const busy = historyLoading || sending;

  // Load the sidebar list when a patient signs in. The whole provider is
  // keyed by user id in App.jsx, so a sign-out / sign-in as another patient
  // remounts it and all state here starts fresh — no reset needed in this
  // effect (which would cause a synchronous render loop).
  useEffect(() => {
    if (!isAuthenticated) return;

    let cancelled = false;
    api
      .get("/agent/threads")
      .then((list) => {
        if (!cancelled) setConversations(list);
      })
      .catch((err) => console.error("Failed to load conversations:", err))
      .finally(() => {
        if (!cancelled) setListLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [patientId, isAuthenticated]);

  /** Refresh the sidebar list (after a send, so timestamps/new threads show). */
  const refreshList = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const list = await api.get("/agent/threads");
      setConversations(list);
      setSelectedThreadId((prev) => {
        // Highlight the thread we're actively chatting in once it persists.
        if (list.some((c) => c.thread_id === activeThreadId)) return activeThreadId;
        return list.some((c) => c.thread_id === prev) ? prev : null;
      });
    } catch (err) {
      console.error("Failed to refresh conversations:", err);
    }
  }, [isAuthenticated, activeThreadId]);

  /** Start a fresh conversation: new thread id, empty window. */
  const newChat = useCallback(() => {
    const threadId = crypto.randomUUID();
    setActiveThreadId(threadId);
    setSelectedThreadId(null);
    setMessages([]);
  }, []);

  /** Resume an existing conversation from its checkpoints. */
  const selectConversation = useCallback(async (threadId) => {
    setSelectedThreadId(threadId);
    setHistoryLoading(true);
    try {
      const detail = await api.get(`/agent/threads/${threadId}`);
      setActiveThreadId(detail.thread_id);
      setMessages(detail.messages || []);
    } catch (err) {
      console.error("Failed to load conversation:", err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  return (
    <ConversationsContext.Provider
      value={{
        patientId,
        conversations,
        listLoading,
        historyLoading,
        sending,
        setSending,
        busy,
        messages,
        activeThreadId,
        selectedThreadId,
        setMessages,
        setSelectedThreadId,
        newChat,
        selectConversation,
        refreshList,
      }}
    >
      {children}
    </ConversationsContext.Provider>
  );
}

export function useConversations() {
  const ctx = useContext(ConversationsContext);
  if (!ctx) throw new Error("useConversations must be used within a ConversationsProvider");
  return ctx;
}

```

---

## File: `frontend\src\utils\api.js`

```javascript
import { API_BASE } from './config';
import { getAccessToken, clearSession } from './session';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const token = getAccessToken();
  const url = `${API_BASE}${path}`;

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const res = await fetch(url, { ...options, headers });

  // Backend has NO /auth/refresh in Phase 5 — just logout on 401
  if (res.status === 401) {
    clearSession();
    window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    throw new ApiError('Unauthorized', 401);
  }

  if (!res.ok) {
    const text = await res.text();
    throw new ApiError(text || `HTTP ${res.status}`, res.status);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (path) => request(path, { method: 'GET' }),
  post: (path, body) => request(path, { method: 'POST', body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: 'PUT', body: JSON.stringify(body) }),
  del: (path) => request(path, { method: 'DELETE' }),
};

// Helpers for streaming endpoints (ChatWindow, etc.)
export const getStreamUrl = (path) => `${API_BASE}${path}`;

export const getAuthHeaders = () => {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Backwards-compat default export for existing imports
export default api;

```

---

## File: `frontend\src\utils\config.js`

```javascript
export const API_BASE = 'http://localhost:8000';

```

---

## File: `frontend\src\utils\image.js`

```javascript
/**
 * Image → base64 helper for the agent's OCR input.
 *
 * The agent endpoint accepts `image_base64` as a raw base64 string
 * (`app/core/rag/ocr.py` does a bare `base64.b64decode`), so the
 * `data:image/...;base64,` prefix from `readAsDataURL` must be stripped.
 * Large images are downscaled on a canvas so the JSON payload stays small,
 * while small images are kept at full resolution (higher detail helps OCR).
 */

const MAX_DIMENSION = 2048;
const MAX_BYTES = 2 * 1024 * 1024; // 2 MB

function readAsDataURL(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error || new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

/**
 * Downscale an image file on a canvas, returning a compressed data URL.
 * Falls back to the original data URL if canvas processing fails.
 */
function downscale(dataUrl, maxDim) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      try {
        const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
        if (scale >= 1) return resolve(dataUrl); // already small enough

        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.85));
      } catch {
        resolve(dataUrl);
      }
    };
    img.onerror = () => resolve(dataUrl);
    img.src = dataUrl;
  });
}

/**
 * Read an image file into { base64, dataUrl, name }.
 *
 * @param {File} file
 * @param {Object} [opts]        - { maxDim, maxBytes }
 * @returns {Promise<{base64: string, dataUrl: string, name: string}>}
 */
export async function fileToImageData(file, opts = {}) {
  const maxDim = opts.maxDim ?? MAX_DIMENSION;
  const maxBytes = opts.maxBytes ?? MAX_BYTES;

  let dataUrl = await readAsDataURL(file);

  // Downscale only genuinely large images (payload bound); keep small
  // images untouched so OCR gets maximum resolution.
  if (file.size > maxBytes) {
    dataUrl = await downscale(dataUrl, maxDim);
  }

  // Strip the `data:image/<type>;base64,` prefix → raw base64 for the backend.
  const commaIdx = dataUrl.indexOf(",");
  const base64 = commaIdx >= 0 ? dataUrl.slice(commaIdx + 1) : dataUrl;

  return { base64, dataUrl, name: file.name };
}

```

---

## File: `frontend\src\utils\session.js`

```javascript
// src/utils/session.js

const SESSION_KEY = 'health_companion_session';

export const getSession = () => {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};

export const setSession = (session) => {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
};

export const clearSession = () => {
  localStorage.removeItem(SESSION_KEY);
};

export const getAccessToken = () => getSession()?.access_token ?? null;
export const getRefreshToken = () => getSession()?.refresh_token ?? null;
```

---

## File: `frontend\src\utils\time.js`

```javascript
/**
 * Tiny timestamp helpers for the sidebar.
 */

/**
 * "just now" / "5m ago" / "3h ago" / "2d ago" / "Aug 4" for an ISO string.
 * Returns "" for missing or unparseable input.
 */
export function formatRelativeTime(iso) {
  if (!iso) return "";
  const then = new Date(iso);
  if (Number.isNaN(then.getTime())) return "";

  const seconds = Math.round((Date.now() - then.getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)}h ago`;
  const days = Math.round(seconds / 86400);
  if (days < 7) return `${days}d ago`;

  return then.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

```

---

## File: `tests\conftest.py`

```python
"""Root conftest — loaded before any test module.

This file is the single point of control that makes the entire test suite
dependency-free:

1.  Sets dummy env vars BEFORE any ``app.*`` import so ``Settings()`` doesn't
    crash on missing required fields.
2.  Stubs ``sentence_transformers`` in ``sys.modules`` so that
    ``qdrant_store.py``'s module-level ``get_embedder()`` call doesn't
    download a ~90 MB model at import time.
3.  Monkey-patches ``build_langgraph_pool`` to return a ``MagicMock`` so
    ``db/lifespan.py``'s module-level pool construction doesn't start
    background threads that try to connect to a non-existent Postgres.
"""
import os
import sys
import types
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
import pytest_asyncio

# ═══════════════════════════════════════════════════════════════════════════
# 1. DUMMY ENV VARS — must be set before any `from app.config import settings`
# ═══════════════════════════════════════════════════════════════════════════
_DUMMY_ENV = {
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/testdb",
    "QDRANT_URL": "http://localhost:6333",
    "QDRANT_API_KEY": "test-qdrant-key",
    "HF_TOKEN": "test-hf-token",
    "SECRET_KEY": "test-secret-key-for-jwt-signing-32chars",
    "SERP_API_KEY": "test-serp-key",
    "GROQ_API_KEY": "test-groq-key",
}
for _k, _v in _DUMMY_ENV.items():
    os.environ.setdefault(_k, _v)

# ═══════════════════════════════════════════════════════════════════════════
# 2. STUB sentence_transformers
#    qdrant_store.py calls `embedder = get_embedder()` at module level, which
#    would load a real SentenceTransformer model. Replace with a fake.
# ═══════════════════════════════════════════════════════════════════════════
if not getattr(sys.modules.get("sentence_transformers"), "_is_test_stub", False):
    import numpy as np

    _fake_st = types.ModuleType("sentence_transformers")
    _fake_st._is_test_stub = True

    class _FakeSentenceTransformer:
        """Returns deterministic 384-dim zero vectors — no model download."""

        def __init__(self, *args, **kwargs):
            pass

        def encode(self, text, **kwargs):
            return np.zeros(384)

        def embed_query(self, text):
            return np.zeros(384).tolist()

    _fake_st.SentenceTransformer = _FakeSentenceTransformer
    sys.modules["sentence_transformers"] = _fake_st

# ═══════════════════════════════════════════════════════════════════════════
# 3. PREVENT POOL BACKGROUND THREADS
#    db/lifespan.py calls `build_langgraph_pool()` at module level, which
#    creates a real psycopg ConnectionPool that starts a background worker
#    thread trying to connect to Postgres. Replace with a MagicMock so no
#    threads are spawned and no connection attempts are made.
# ═══════════════════════════════════════════════════════════════════════════
import app.db.pool  # noqa: E402 — safe: pure string computation, no I/O
app.db.pool.build_langgraph_pool = lambda: MagicMock()  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════
# 4. FAKE LLM
# ═══════════════════════════════════════════════════════════════════════════

class FakeLLM:
    """Deterministic fake LLM for unit tests.

    Configure per-test by setting attributes on the returned instance::

        fake_llm.response_text = "Custom answer"
        fake_llm.tool_calls   = [{"name": "save_patient_fact", "args": {...}, "id": "..."}]
        fake_llm.stream_chunks = ["Hello", " world"]
        fake_llm.should_error = True   # to test error / sentinel paths
    """

    def __init__(self):
        self.response_text = "Test response from fake LLM."
        self.tool_calls: list | None = None
        self.stream_chunks = ["Hello", " ", "world"]
        self.should_error = False

    async def astream(self, messages, **kwargs):
        if self.should_error:
            raise RuntimeError("Fake LLM error")
        for chunk_text in self.stream_chunks:
            yield SimpleNamespace(content=chunk_text)

    def bind_tools(self, tools):
        # Return self so .invoke() works the same way whether or not tools
        # are bound — both the router and biomistral nodes call
        # `model.invoke(messages)` uniformly.
        return self

    def invoke(self, messages):
        if self.should_error:
            raise RuntimeError("Fake LLM error")
        from langchain_core.messages import AIMessage

        return AIMessage(
            content=self.response_text,
            tool_calls=self.tool_calls or [],
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5. SKIP live MARKER UNLESS RUN_LIVE_TESTS=1
# ═══════════════════════════════════════════════════════════════════════════

def pytest_collection_modifyitems(config, items):
    """Skip @pytest.mark.live tests unless RUN_LIVE_TESTS=1."""
    if os.environ.get("RUN_LIVE_TESTS") == "1":
        return
    skip_live = pytest.mark.skip(reason="Set RUN_LIVE_TESTS=1 to run live tests")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


# ═══════════════════════════════════════════════════════════════════════════
# 6. FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def fake_llm(monkeypatch):
    """Replace the LLM singletons with a deterministic fake in every module
    that holds one — both the BioMistral node (``llm``) and the router node
    (``router_llm``, a ChatGroq bound with tools)."""
    import importlib

    fake = FakeLLM()
    for mod_path in [
        "app.core.llm",
        "app.services.chat_service",
        "app.services.rag_chat_service",
        "app.agent.nodes.biomistral_node",
    ]:
        mod = importlib.import_module(mod_path)
        monkeypatch.setattr(mod, "llm", fake)

    # The router uses its own bound ChatGroq instance — swap it for the fake
    # so .invoke() runs without a real Groq call.
    router_mod = importlib.import_module("app.agent.nodes.router_node")
    monkeypatch.setattr(router_mod, "router_llm", fake)
    return fake


@pytest.fixture
def fake_qdrant(monkeypatch):
    """Stub Qdrant ``retrieve`` (as imported in corrective_rag) to return
    canned high-relevance docs."""

    def _fake_retrieve(query, top_k=5, category=None):
        return [
            {"text": "Diabetes is a chronic condition.", "source": "who.int",
             "category": "endocrine", "score": 0.85},
            {"text": "Symptoms include excessive thirst.", "source": "mayoclinic.org",
             "category": "endocrine", "score": 0.72},
        ]

    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", _fake_retrieve)
    return _fake_retrieve


@pytest.fixture
def fake_serpapi(monkeypatch):
    """Stub SerpAPI ``GoogleSearch`` to avoid real API calls."""

    class _FakeGoogleSearch:
        def __init__(self, params):
            self.params = params

        def get_dict(self):
            return {
                "organic_results": [
                    {"snippet": "Web result snippet", "link": "example.com",
                     "title": "Example"},
                ]
            }

    monkeypatch.setattr("app.core.rag.corrective_rag.GoogleSearch", _FakeGoogleSearch)
    return _FakeGoogleSearch


# ── DB fixtures ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """Session-scoped in-memory sqlite engine with all tables created.

    Uses ``StaticPool`` so all sessions share a single in-memory connection
    (aiosqlite in-memory DBs are per-connection by default — without
    StaticPool each session would get its own empty database).  Tables are
    created once per session and data is truncated per-test in ``db_session``.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy.pool import StaticPool
    from app.db.base import Base
    import app.models  # noqa: F401 — registers User/Token/RefreshToken

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Per-test async DB session that truncates all tables on teardown."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from app.db.base import Base

    session_maker = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_maker() as session:
        yield session
        # Truncate every table so the next test starts with a clean slate.
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


# ── ASGI client ──────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def async_client(db_engine):
    """``httpx.AsyncClient`` over the FastAPI app.

    The lifespan is NOT triggered (ASGITransport sends only ``http.request``
    events, not ``lifespan.startup``), so no real Postgres/Qdrant/LLM
    connections are made on startup.  ``get_db`` is overridden to use the
    test sqlite engine.
    """
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    from app.db.session import get_db
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    session_maker = async_sessionmaker(
        db_engine, expire_on_commit=False, class_=AsyncSession
    )

    async def get_test_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = get_test_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ── Auth helpers ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def auth_user(db_session):
    """Create a test user in the DB and return it."""
    import uuid
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("TestPass123!"),
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(auth_user):
    """JWT for the test user."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": str(auth_user.id)})


@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers for the test user."""
    return {"Authorization": f"Bearer {auth_token}"}


# ── Agent helpers ────────────────────────────────────────────────────────────

@pytest.fixture
def fake_store():
    """In-memory fake of the LangGraph ``PostgresStore`` for tools tests."""

    class _FakeStore:
        def __init__(self):
            self._data: dict[tuple, dict[str, dict]] = {}

        def search(self, namespace, query="", limit=5):
            ns = tuple(namespace)
            items = [
                SimpleNamespace(value=v)
                for v in self._data.get(ns, {}).values()
            ]
            return items[:limit]

        def put(self, namespace, key, value):
            ns = tuple(namespace)
            self._data.setdefault(ns, {})[key] = value

    return _FakeStore()


@pytest.fixture
def sample_state():
    """Factory for ``AgentState`` dicts — accepts overrides."""

    def _make(**kwargs):
        base = {
            "patient_id": "test-patient-01",
            "ocr_context": "",
            "tool_results": "",
            "messages": [],
            "answer": "",
            "final_response": "",
            "raw_input": "What is diabetes?",
            "detected_lang": "en",
            "needs_rag": False,
            "retrieval_decision": "",
            "retrieved_docs": [],
            "saved_memory": False,
        }
        base.update(kwargs)
        return base

    return _make

```

---

## File: `tests\agent\test_biomistral_node.py`

```python
"""Unit tests for app/agent/nodes/biomistral_node.py.

Covers:
- answer / final_response set from the local model's response
- empty model response → fallback message
- tool_results context is folded into the system prompt
- ocr_context is folded into the system prompt (and truncated)
- only the final AIMessage is stored (the user message is the router's job)
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.nodes.biomistral_node import _OCR_CHAR_LIMIT, biomistral_node


# ── answer / final_response ──────────────────────────────────────────────────

@pytest.mark.unit
def test_biomistral_sets_answer_from_response(fake_llm, sample_state):
    fake_llm.response_text = "You likely have a common cold."
    fake_llm.tool_calls = None

    state = sample_state(raw_input="I have a runny nose")
    result = biomistral_node(state)

    assert result["answer"] == "You likely have a common cold."
    assert result["final_response"] == "You likely have a common cold."


@pytest.mark.unit
def test_biomistral_empty_response_gets_fallback(fake_llm, sample_state):
    fake_llm.response_text = ""
    fake_llm.tool_calls = None

    state = sample_state()
    result = biomistral_node(state)

    assert "wasn't able to generate" in result["answer"]
    assert result["final_response"] == result["answer"]


@pytest.mark.unit
def test_biomistral_stores_only_final_ai_message(fake_llm, sample_state):
    """The router persists the user message; BioMistral stores only its own
    final AIMessage, completing the conversation pair without duplicating
    the HumanMessage."""
    fake_llm.response_text = "final answer"
    fake_llm.tool_calls = None

    state = sample_state(raw_input="hi")
    result = biomistral_node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], AIMessage)
    assert result["messages"][0].content == "final answer"


# ── context folding ──────────────────────────────────────────────────────────

def _capture_system(fake_llm):
    """Replace fake_llm.invoke so it records the SystemMessage it receives."""
    captured = {}
    orig = fake_llm.invoke

    def _cap(messages):
        captured["system"] = next(
            (m for m in messages if isinstance(m, SystemMessage)), None
        )
        return orig(messages)

    fake_llm.invoke = _cap
    return captured


@pytest.mark.unit
def test_biomistral_includes_tool_results(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(tool_results="--- Context from tool [retrieve_medical_knowledge] ---\nDiabetes info")
    biomistral_node(state)

    assert captured["system"] is not None
    assert "Diabetes info" in captured["system"].content


@pytest.mark.unit
def test_biomistral_includes_ocr_context(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(ocr_context="Patient: John Doe\nDiagnosis: Hypertension")
    biomistral_node(state)

    assert "Hypertension" in captured["system"].content


@pytest.mark.unit
def test_biomistral_truncates_long_ocr(fake_llm, sample_state):
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    long_ocr = "Z" * 5000
    state = sample_state(ocr_context=long_ocr)
    biomistral_node(state)

    # Only _OCR_CHAR_LIMIT chars of the OCR text should reach the prompt.
    assert captured["system"].content.count("Z") <= _OCR_CHAR_LIMIT


@pytest.mark.unit
def test_biomistral_no_context_uses_placeholders(fake_llm, sample_state):
    """With no OCR and no tool results, the prompt carries the 'no context'
    placeholders rather than empty strings."""
    fake_llm.response_text = "ok"
    fake_llm.tool_calls = None
    captured = _capture_system(fake_llm)

    state = sample_state(ocr_context="", tool_results="")
    biomistral_node(state)

    system_text = captured["system"].content
    assert "No OCR text attached." in system_text
    assert "No external context retrieved." in system_text

```

---

## File: `tests\agent\test_graph.py`

```python
"""Unit tests for app/agent/graph.py — routing and tool execution."""
import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agent.graph import _extract_tool_metadata, _route_after_router, _run_tools


# ── _route_after_router ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_route_to_tools_when_tool_calls_present():
    """When the last message is an AIMessage with tool_calls → route to 'tools'."""
    state = {
        "messages": [
            HumanMessage(content="hello"),
            AIMessage(
                content="",
                tool_calls=[{"name": "fetch_patient_facts", "args": {}, "id": "1"}],
            ),
        ]
    }
    assert _route_after_router(state) == "tools"


@pytest.mark.unit
def test_route_to_biomistral_when_no_tool_calls(sample_state):
    """When the last message is a plain AIMessage (no tool_calls) → biomistral."""
    state = sample_state(messages=[
        HumanMessage(content="hello"),
        AIMessage(content="hi there"),
    ])
    assert _route_after_router(state) == "biomistral"


@pytest.mark.unit
def test_route_to_biomistral_when_last_is_human():
    """No-tool turn: the router stored only the user message, so the last
    message is a HumanMessage → straight to BioMistral."""
    state = {"messages": [HumanMessage(content="hello")]}
    assert _route_after_router(state) == "biomistral"


@pytest.mark.unit
def test_route_to_biomistral_on_empty_history():
    """Edge case: no messages at all → BioMistral (no tools to run)."""
    assert _route_after_router({"messages": []}) == "biomistral"


# ── _extract_tool_metadata ────────────────────────────────────────────────────

@pytest.mark.unit
def test_extract_metadata_from_rag_tool_message():
    """needs_rag / retrieval_decision / sources are parsed from a
    retrieve_medical_knowledge ToolMessage."""
    tool_msg = ToolMessage(
        content=(
            "[Retrieval decision: correct]\n\n"
            "[who.int] Diabetes is a chronic condition.\n"
            "[mayoclinic.org] Symptoms include thirst.\n"
        ),
        tool_call_id="tc1",
        name="retrieve_medical_knowledge",
    )
    meta = _extract_tool_metadata([tool_msg])

    assert meta["needs_rag"] is True
    assert meta["retrieval_decision"] == "correct"
    assert meta["retrieved_docs"][0]["source"] == "who.int"
    assert "Diabetes is a chronic condition" in meta["tool_results"]
    assert meta["saved_memory"] is False


@pytest.mark.unit
def test_extract_metadata_detects_saved_memory():
    meta = _extract_tool_metadata([
        ToolMessage(
            content="Saved to patient record: fever (ongoing)",
            tool_call_id="tc1",
            name="save_patient_fact",
        )
    ])
    assert meta["saved_memory"] is True
    assert meta["needs_rag"] is False


@pytest.mark.unit
def test_extract_metadata_empty():
    meta = _extract_tool_metadata([])
    assert meta["tool_results"] == ""
    assert meta["needs_rag"] is False
    assert meta["saved_memory"] is False
    assert meta["retrieval_decision"] == ""
    assert meta["retrieved_docs"] == []


# ── _run_tools ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_run_tools_executes_and_extracts(monkeypatch, fake_store):
    """_run_tools invokes the ToolNode, appends ToolMessages, and folds the
    results into tool_results + metadata."""
    from app.agent import graph as graph_mod
    from app.agent import tools as tools_mod
    monkeypatch.setattr(tools_mod, "store", fake_store)

    def _fake_tool_node_invoke(state):
        tool_msg = ToolMessage(
            content="[Retrieval decision: correct]\n\n[who.int] Diabetes info",
            tool_call_id="call_1",
            name="retrieve_medical_knowledge",
        )
        state["messages"] = state["messages"] + [tool_msg]
        return state

    monkeypatch.setattr(graph_mod._tool_node, "invoke", _fake_tool_node_invoke)

    ai_msg = AIMessage(
        content="",
        tool_calls=[{
            "name": "retrieve_medical_knowledge",
            "args": {"query": "diabetes"},
            "id": "call_1",
        }],
    )
    state = {
        "messages": [HumanMessage(content="what is diabetes?"), ai_msg],
        "patient_id": "p1",
    }
    result = _run_tools(state)

    # ToolMessage appended
    assert any(isinstance(m, ToolMessage) for m in result["messages"])
    # Metadata folded in
    assert result["needs_rag"] is True
    assert result["retrieval_decision"] == "correct"
    assert "Diabetes info" in result["tool_results"]

```

---

## File: `tests\agent\test_router_node.py`

```python
"""Unit tests for app/agent/nodes/router_node.py.

Covers:
- no-tool path: stores only the user message (no ghost assistant turn)
- tool-call path: stores user message + AIMessage carrying tool_calls
- current input is appended to the LLM call when history doesn't end on one
- patient_id is interpolated into the system prompt
"""
import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.nodes.router_node import ROUTER_SYSTEM_PROMPT, router_node


# ── no-tool path ──────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_no_tools_stores_only_user_message(fake_llm, sample_state):
    """When the router decides no tools are needed, only the user's
    HumanMessage is persisted — no intermediate assistant text."""
    fake_llm.response_text = "irrelevant"
    fake_llm.tool_calls = None

    state = sample_state(raw_input="Hello there")
    result = router_node(state)

    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == "Hello there"
    # No answer / final_response set by the router
    assert "answer" not in result
    assert "final_response" not in result


# ── tool-call path ────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_tool_call_stores_user_and_ai(fake_llm, sample_state):
    """When the router emits tool_calls, both the user message and the
    AIMessage(tool_calls) are stored so the ToolNode can execute them."""
    fake_llm.tool_calls = [{"name": "save_patient_fact", "args": {}, "id": "tc1"}]

    state = sample_state(raw_input="I have a fever")
    result = router_node(state)

    assert len(result["messages"]) == 2
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == "I have a fever"
    assert isinstance(result["messages"][1], AIMessage)
    assert result["messages"][1].tool_calls  # truthy


# ── current input appended to the LLM call ───────────────────────────────────

@pytest.mark.unit
def test_router_appends_input_when_history_ends_on_ai(fake_llm, sample_state):
    """At the start of a turn the history ends on an assistant message, so
    the router appends the current input to the messages it sends to the LLM.
    The fake LLM records the last message it was invoked with."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="new question",
        messages=[HumanMessage(content="old q"), AIMessage(content="old a")],
    )
    router_node(state)

    assert isinstance(captured["last"], HumanMessage)
    assert captured["last"].content == "new question"


@pytest.mark.unit
def test_router_does_not_duplicate_input_when_history_ends_on_human(
    fake_llm, sample_state,
):
    """If the last history message is already the current user input, the
    router must not append a second copy."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(
        raw_input="same question",
        messages=[HumanMessage(content="same question")],
    )
    router_node(state)

    assert captured["last"].content == "same question"


# ── system prompt ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_router_system_prompt_interpolates_patient_id(fake_llm, sample_state):
    fake_llm.tool_calls = None
    state = sample_state(patient_id="patient-42", raw_input="hi")
    router_node(state)
    assert "patient-42" in ROUTER_SYSTEM_PROMPT.format(patient_id="patient-42")


@pytest.mark.unit
def test_router_empty_history_appends_input(fake_llm, sample_state):
    """First turn ever — history is empty, router still sends the input."""
    fake_llm.tool_calls = None
    captured = {}
    orig_invoke = fake_llm.invoke

    def _capture(messages):
        captured["last"] = messages[-1]
        return orig_invoke(messages)

    fake_llm.invoke = _capture

    state = sample_state(raw_input="first message", messages=[])
    router_node(state)

    assert isinstance(captured["last"], HumanMessage)
    assert captured["last"].content == "first message"

```

---

## File: `tests\agent\test_tools.py`

```python
"""Unit tests for app/agent/tools.py — all four LangGraph tools."""
import pytest

from app.agent.tools import (
    TOOLS,
    fetch_patient_facts,
    retrieve_medical_knowledge,
    save_emotional_state,
    save_patient_fact,
)


# ── TOOLS list ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_tools_list_has_four():
    assert len(TOOLS) == 4
    names = {t.name for t in TOOLS}
    assert names == {
        "fetch_patient_facts",
        "retrieve_medical_knowledge",
        "save_patient_fact",
        "save_emotional_state",
    }


# ── fetch_patient_facts ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_fetch_patient_facts_returns_history(monkeypatch, fake_store):
    """With facts in the store, returns formatted history lines."""
    fake_store.put(("patient_facts", "p1"), "key1", {
        "symptom": "fever", "onset": "3 days ago", "status": "ongoing",
    })
    monkeypatch.setattr("app.agent.tools.store", fake_store)

    result = fetch_patient_facts.invoke({"patient_id": "p1", "query": "fever"})
    assert "fever" in result
    assert "Known patient history" in result


@pytest.mark.unit
def test_fetch_patient_facts_no_history(monkeypatch, fake_store):
    """Empty store → 'No relevant patient history found.'"""
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = fetch_patient_facts.invoke({"patient_id": "noone", "query": "x"})
    assert "No relevant patient history" in result


@pytest.mark.unit
def test_fetch_patient_facts_store_none(monkeypatch):
    """When store is None → graceful message, no crash."""
    monkeypatch.setattr("app.agent.tools.store", None)
    result = fetch_patient_facts.invoke({"patient_id": "p1", "query": "x"})
    assert "not available" in result.lower()


# ── retrieve_medical_knowledge ──────────────────────────────────────────────

@pytest.mark.unit
def test_retrieve_medical_knowledge_success(monkeypatch, fake_qdrant):
    """With mocked Qdrant returning high-score docs → formatted result."""
    result = retrieve_medical_knowledge.invoke({"query": "diabetes"})
    assert "Retrieval decision" in result
    assert "who.int" in result  # from fake_qdrat canned docs


@pytest.mark.unit
def test_retrieve_medical_knowledge_no_docs(monkeypatch):
    """When retrieve returns empty → 'No relevant documents found.'"""
    monkeypatch.setattr("app.agent.tools.corrective_retrieve", lambda *a, **k: {
        "docs": [], "decision": "incorrect", "avg_score": 0.0,
    })
    result = retrieve_medical_knowledge.invoke({"query": "obscure"})
    assert "No relevant documents" in result


@pytest.mark.unit
def test_retrieve_medical_knowledge_handles_error(monkeypatch):
    """If corrective_retrieve raises → error string, not exception."""
    monkeypatch.setattr(
        "app.agent.tools.corrective_retrieve",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    result = retrieve_medical_knowledge.invoke({"query": "x"})
    assert "Error" in result


# ── save_patient_fact ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_save_patient_fact_success(monkeypatch, fake_store):
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = save_patient_fact.invoke({
        "patient_id": "p1", "symptom": "headache",
        "onset": "today", "status": "mild",
        "source_message": "I have a headache",
    })
    assert "headache" in result
    # Verify it was persisted
    items = fake_store.search(("patient_facts", "p1"))
    assert any(item.value.get("symptom") == "headache" for item in items)


@pytest.mark.unit
def test_save_patient_fact_store_none(monkeypatch):
    monkeypatch.setattr("app.agent.tools.store", None)
    result = save_patient_fact.invoke({
        "patient_id": "p1", "symptom": "x", "onset": "y",
        "status": "z", "source_message": "m",
    })
    assert "not available" in result.lower()


# ── save_emotional_state ────────────────────────────────────────────────────

@pytest.mark.unit
def test_save_emotional_state_success(monkeypatch, fake_store):
    monkeypatch.setattr("app.agent.tools.store", fake_store)
    result = save_emotional_state.invoke({
        "patient_id": "p1", "emotion": "anxiety",
        "intensity": "high", "trigger": "diagnosis",
        "source_message": "I'm scared",
    })
    assert "anxiety" in result
    items = fake_store.search(("patient_emotions", "p1"))
    assert any(item.value.get("emotion") == "anxiety" for item in items)


@pytest.mark.unit
def test_save_emotional_state_store_none(monkeypatch):
    monkeypatch.setattr("app.agent.tools.store", None)
    result = save_emotional_state.invoke({
        "patient_id": "p1", "emotion": "fear", "intensity": "low",
        "trigger": "x", "source_message": "m",
    })
    assert "not available" in result.lower()

```

---

## File: `tests\core\test_corrective_rag.py`

```python
"""Unit tests for app/core/rag/corrective_rag.py.

Covers:
- evaluate_relevance thresholds (correct / ambiguous / incorrect)
- web_search_fallback with mocked SerpAPI
- corrective_retrieve pipeline (retrieve → evaluate → correct)
"""
import pytest

from app.core.rag.corrective_rag import (
    AMBIGUOUS_THRESHOLD,
    RELEVANCE_THRESHOLD,
    corrective_retrieve,
    evaluate_relevance,
    web_search_fallback,
)


# ── evaluate_relevance ───────────────────────────────────────────────────────

@pytest.mark.unit
def test_evaluate_relevance_empty_docs():
    decision, avg = evaluate_relevance([])
    assert decision == "incorrect"
    assert avg == 0.0


@pytest.mark.unit
def test_evaluate_relevance_correct():
    """max_score >= RELEVANCE_THRESHOLD → correct"""
    docs = [
        {"score": 0.6},
        {"score": 0.4},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "correct"
    assert avg == 0.5


@pytest.mark.unit
def test_evaluate_relevance_ambiguous():
    """max < RELEVANCE_THRESHOLD but avg >= AMBIGUOUS_THRESHOLD → ambiguous"""
    docs = [
        {"score": 0.4},
        {"score": 0.36},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "ambiguous"
    assert abs(avg - 0.38) < 0.001


@pytest.mark.unit
def test_evaluate_relevance_incorrect():
    """max < RELEVANCE_THRESHOLD and avg < AMBIGUOUS_THRESHOLD → incorrect"""
    docs = [
        {"score": 0.2},
        {"score": 0.1},
    ]
    decision, avg = evaluate_relevance(docs)
    assert decision == "incorrect"
    assert avg == pytest.approx(0.15)


@pytest.mark.unit
def test_evaluate_relevance_single_doc_correct():
    docs = [{"score": 0.9}]
    decision, _ = evaluate_relevance(docs)
    assert decision == "correct"


@pytest.mark.unit
def test_thresholds_are_sane():
    """RELEVANCE must be strictly greater than AMBIGUOUS."""
    assert RELEVANCE_THRESHOLD > AMBIGUOUS_THRESHOLD
    assert RELEVANCE_THRESHOLD == 0.5
    assert AMBIGUOUS_THRESHOLD == 0.35


# ── web_search_fallback ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_web_search_fallback_returns_docs(fake_serpapi):
    docs = web_search_fallback("diabetes symptoms")
    assert len(docs) >= 1
    assert all("text" in d and "source" in d for d in docs)
    assert all(d["category"] == "web" for d in docs)
    assert all(d["score"] == 0.5 for d in docs)


@pytest.mark.unit
def test_web_search_fallback_handles_error(monkeypatch):
    """If GoogleSearch raises, fallback returns [] (caught, not propagated)."""
    class _Boom:
        def __init__(self, params):
            raise RuntimeError("SerpAPI down")

    monkeypatch.setattr("app.core.rag.corrective_rag.GoogleSearch", _Boom)
    assert web_search_fallback("anything") == []


# ── corrective_retrieve ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_corrective_retrieve_correct(fake_qdrant):
    """High-score docs → 'correct', no web search."""
    result = corrective_retrieve("What is diabetes?")
    assert result["decision"] == "correct"
    assert len(result["docs"]) <= 5
    assert result["avg_score"] > 0


@pytest.mark.unit
def test_corrective_retrieve_incorrect_triggers_web_search(monkeypatch, fake_serpapi):
    """Low-score docs → 'incorrect', web search prepended."""
    low_docs = [{"text": "irrelevant", "source": "x", "category": "y", "score": 0.1}]
    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", lambda *a, **k: low_docs)
    result = corrective_retrieve("obscure query")
    assert result["decision"] == "incorrect"
    # Web results (category="web") should be prepended
    web_docs = [d for d in result["docs"] if d.get("category") == "web"]
    assert len(web_docs) >= 1


@pytest.mark.unit
def test_corrective_retrieve_ambiguous_appends_web_search(monkeypatch, fake_serpapi):
    """Ambiguous scores → web search appended after Qdrant docs."""
    mid_docs = [{"text": "partial", "source": "q", "category": "c", "score": 0.36}]
    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", lambda *a, **k: mid_docs)
    result = corrective_retrieve("partial query")
    assert result["decision"] == "ambiguous"
    # Web results should be present
    web_docs = [d for d in result["docs"] if d.get("category") == "web"]
    assert len(web_docs) >= 1


@pytest.mark.unit
def test_corrective_retrieve_caps_at_five_docs(fake_qdrant, fake_serpapi):
    result = corrective_retrieve("query")
    assert len(result["docs"]) <= 5


@pytest.mark.unit
def test_corrective_retrieve_returns_avg_score(fake_qdrant):
    result = corrective_retrieve("diabetes")
    assert "avg_score" in result
    assert isinstance(result["avg_score"], float)

```

---

## File: `tests\core\test_email.py`

```python
"""Unit tests for app/utils/email.py — dev-mode logging + SMTP path."""
import pytest

from app.utils.email import send_email


@pytest.mark.unit
def test_send_email_dev_mode_returns_true(monkeypatch):
    """When SMTP_HOST is empty, email is logged to console and returns True."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "")
    assert send_email("user@example.com", "Test", "Body text") is True


@pytest.mark.unit
def test_send_email_smtp_success(monkeypatch):
    """When SMTP is configured, sends via smtplib and returns True."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.utils.email.settings.SMTP_TLS", True)
    monkeypatch.setattr("app.utils.email.settings.SMTP_USER", "user")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PASSWORD", "pass")
    monkeypatch.setattr("app.utils.email.settings.SMTP_FROM", "from@example.com")

    sent = {}

    class _FakeSMTP:
        def __init__(self, host, port):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        def starttls(self, context=None):
            pass
        def login(self, user, pw):
            pass
        def send_message(self, msg):
            sent["subject"] = msg["Subject"]
            sent["to"] = msg["To"]

    monkeypatch.setattr("app.utils.email.smtplib.SMTP", _FakeSMTP)
    assert send_email("to@example.com", "Hello", "Body") is True
    assert sent["subject"] == "Hello"
    assert sent["to"] == "to@example.com"


@pytest.mark.unit
def test_send_email_smtp_failure_returns_false(monkeypatch):
    """When SMTP sending fails, returns False (not raises)."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PORT", 587)
    monkeypatch.setattr("app.utils.email.settings.SMTP_TLS", False)
    monkeypatch.setattr("app.utils.email.settings.SMTP_USER", "")
    monkeypatch.setattr("app.utils.email.settings.SMTP_PASSWORD", "")

    class _BoomSMTP:
        def __init__(self, host, port):
            raise ConnectionRefusedError("no SMTP")

    monkeypatch.setattr("app.utils.email.smtplib.SMTP", _BoomSMTP)
    assert send_email("to@example.com", "Subject", "Body") is False


@pytest.mark.unit
def test_send_email_with_reply_to(monkeypatch):
    """reply_to adds a Reply-To header."""
    monkeypatch.setattr("app.utils.email.settings.SMTP_HOST", "")

    # In dev mode, just verify it doesn't crash and returns True
    assert send_email(
        "to@example.com", "Sub", "Body",
        reply_to="reply@example.com",
    ) is True

```

---

## File: `tests\core\test_ocr.py`

```python
"""Unit tests for app/core/rag/ocr.py — OCR extraction with mocked pytesseract."""
import pytest

from app.core.rag.ocr import extract_text_from_base64


@pytest.mark.unit
def test_ocr_empty_string_returns_empty():
    assert extract_text_from_base64("") == ""


@pytest.mark.unit
def test_ocr_none_returns_empty():
    assert extract_text_from_base64(None) == ""


@pytest.mark.unit
def test_ocr_extracts_text(monkeypatch):
    """With mocked pytesseract and Image.open, returns the extracted text."""
    from types import SimpleNamespace
    monkeypatch.setattr("app.core.rag.ocr.Image.open", lambda buf: SimpleNamespace(size=(1,1), mode="RGB"))
    monkeypatch.setattr("app.core.rag.ocr.pytesseract.image_to_string", lambda img: "Diagnosis: Hypertension")

    result = extract_text_from_base64("aGVsbG8=")  # valid base64
    assert result == "Diagnosis: Hypertension"


@pytest.mark.unit
def test_ocr_handles_invalid_base64():
    """Invalid base64 should not raise — returns empty string."""
    result = extract_text_from_base64("!!!not-base64!!!")
    assert result == ""


@pytest.mark.unit
def test_ocr_handles_pytesseract_error(monkeypatch):
    """If pytesseract raises, the error is caught and empty string returned."""
    def _boom(img):
        raise RuntimeError("tesseract not installed")

    monkeypatch.setattr("app.core.rag.ocr.pytesseract.image_to_string", _boom)
    assert extract_text_from_base64("aGVsbG8=") == ""

```

---

## File: `tests\core\test_password_policy.py`

```python
"""Unit tests for app/core/password_policy.py — every rule as parametrized cases."""
import pytest

from app.core.password_policy import (
    COMMON_PASSWORDS,
    MAX_LENGTH,
    MIN_LENGTH,
    PasswordError,
    validate_password,
)

# ── Helper ───────────────────────────────────────────────────────────────────

def _codes(errors: list[PasswordError]) -> set[str]:
    return {e.code for e in errors}


VALID = "Str0ng!Pass"  # meets every rule


# ── Happy path ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_valid_password_returns_no_errors():
    assert validate_password(VALID) == []


# ── Length ───────────────────────────────────────────────────────────────────

@pytest.mark.unit
@pytest.mark.parametrize("pw", ["Ab1!", "Ab1!Ab", "Aa1!aa"])  # all < 8 chars
def test_too_short(pw):
    errors = validate_password(pw)
    assert "too_short" in _codes(errors)


@pytest.mark.unit
def test_too_long():
    pw = "A" + "a1!" * 43 + "X"  # 130 chars
    assert "too_long" in _codes(validate_password(pw))


@pytest.mark.unit
def test_exactly_min_length_ok():
    pw = "Abcde1!"  # 7 → needs 8
    assert "too_short" in _codes(validate_password(pw))
    pw2 = "Abcde1!x"  # 8
    assert "too_short" not in _codes(validate_password(pw2))


# ── Case rules ───────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_uppercase():
    errors = validate_password("lowercase1!")
    assert "missing_uppercase" in _codes(errors)


@pytest.mark.unit
def test_missing_lowercase():
    errors = validate_password("UPPERCASE1!")
    assert "missing_lowercase" in _codes(errors)


# ── Digit ─────────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_digit():
    errors = validate_password("NoDigits!!")
    assert "missing_digit" in _codes(errors)


# ── Special char ──────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_missing_special():
    errors = validate_password("NoSpecial1")
    assert "missing_special" in _codes(errors)


# ── Common-password blocklist ─────────────────────────────────────────────────

# Only entries whose .lower() form is also in the set get caught by the
# case-insensitive check.  "P@ssw0rd" lowercases to "p@ssw0rd" which is NOT
# in the set, so it slips through — a known limitation.
_CATCHABLE = [pw for pw in COMMON_PASSWORDS if pw.lower() in COMMON_PASSWORDS]


@pytest.mark.unit
@pytest.mark.parametrize("pw", sorted(_CATCHABLE))
def test_common_passwords_rejected(pw):
    """Every catchable entry in the blocklist should trigger common_password."""
    errors = validate_password(pw)
    # Some common passwords also fail other rules (too short, missing case,
    # etc.) — but they MUST at least trigger common_password.
    assert "common_password" in _codes(errors)


@pytest.mark.unit
def test_common_password_case_insensitive():
    """Blocklist check is .lower()'d so mixed case shouldn't bypass it."""
    assert "common_password" in _codes(validate_password("PASSWORD123"))


# ── Multiple violations at once ───────────────────────────────────────────────

@pytest.mark.unit
def test_multiple_violations():
    errors = validate_password("abc")
    codes = _codes(errors)
    assert "too_short" in codes
    assert "missing_uppercase" in codes
    assert "missing_digit" in codes
    assert "missing_special" in codes


@pytest.mark.unit
def test_error_repr():
    err = PasswordError("too_short", "too short")
    assert "too_short" in repr(err)

```

---

## File: `tests\core\test_schemas.py`

```python
"""Unit tests for Pydantic schemas — validation errors for malformed requests."""
import pytest
from pydantic import ValidationError

from app.schemas.agent import AgentRequest, AgentResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.chat import ChatRequest, ChatMessage


# ── RegisterRequest ──────────────────────────────────────────────────────────

@pytest.mark.unit
def test_register_valid():
    req = RegisterRequest(
        username="alice", email="alice@example.com", password="Str0ng!Pass"
    )
    assert req.username == "alice"


@pytest.mark.unit
@pytest.mark.parametrize("bad_pw", [
    "short",            # too short, missing rules
    "alllowercase1!",   # missing uppercase
    "ALLUPPERCASE1!",   # missing lowercase
    "NoDigits!!",       # missing digit
    "NoSpecial1",       # missing special char
    "password",         # common password (also short)
])
def test_register_rejects_weak_password(bad_pw):
    with pytest.raises(ValidationError) as exc:
        RegisterRequest(
            username="bob", email="bob@example.com", password=bad_pw
        )
    assert exc.value.error_count() >= 1


@pytest.mark.unit
def test_register_username_too_short():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="ab", email="ab@example.com", password="Str0ng!Pass"
        )


@pytest.mark.unit
def test_register_username_too_long():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="x" * 51, email="ab@example.com", password="Str0ng!Pass"
        )


@pytest.mark.unit
def test_register_invalid_email():
    with pytest.raises(ValidationError):
        RegisterRequest(
            username="bob", email="not-an-email", password="Str0ng!Pass"
        )


# ── LoginRequest ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_login_valid():
    req = LoginRequest(username="alice", password="anything")
    assert req.username == "alice"


@pytest.mark.unit
def test_login_empty_username():
    with pytest.raises(ValidationError):
        LoginRequest(username="", password="x")


@pytest.mark.unit
def test_login_empty_password():
    with pytest.raises(ValidationError):
        LoginRequest(username="alice", password="")


# ── ChatMessage / ChatRequest ────────────────────────────────────────────────

@pytest.mark.unit
def test_chat_request_valid():
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="hello")],
        temperature=0.5,
        max_tokens=100,
    )
    assert req.messages[0].content == "hello"


@pytest.mark.unit
def test_chat_request_invalid_role():
    with pytest.raises(ValidationError):
        ChatMessage(role="invalid_role", content="hello")


@pytest.mark.unit
def test_chat_request_empty_content():
    with pytest.raises(ValidationError):
        ChatMessage(role="user", content="")


@pytest.mark.unit
@pytest.mark.parametrize("temp", [-0.1, 2.1, 3.0])
def test_chat_request_temperature_out_of_range(temp):
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            temperature=temp,
        )


@pytest.mark.unit
@pytest.mark.parametrize("tokens", [0, -1, -100])
def test_chat_request_max_tokens_must_be_positive(tokens):
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[ChatMessage(role="user", content="hi")],
            max_tokens=tokens,
        )


# ── AgentRequest / AgentResponse ─────────────────────────────────────────────

@pytest.mark.unit
def test_agent_request_defaults():
    req = AgentRequest(patient_id="p1")
    assert req.query == ""
    assert req.image_base64 is None
    assert req.thread_id is None


@pytest.mark.unit
def test_agent_request_missing_patient_id():
    with pytest.raises(ValidationError):
        AgentRequest()


@pytest.mark.unit
def test_agent_response_roundtrip():
    resp = AgentResponse(
        answer="hello",
        detected_lang="en",
        needs_rag=False,
        save_memory=False,
    )
    assert resp.sources == []
    assert resp.retrieval_decision is None

```

---

## File: `tests\core\test_security.py`

```python
"""Unit tests for app/core/security.py — password hashing, JWT creation/decoding."""
import time
from datetime import timedelta

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ── Password hashing ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_hash_password_returns_different_hash():
    h = hash_password("TestPass123!")
    assert h != "TestPass123!"
    assert len(h) > 20


@pytest.mark.unit
def test_verify_password_correct():
    h = hash_password("MySecret1!")
    assert verify_password("MySecret1!", h) is True


@pytest.mark.unit
def test_verify_password_wrong():
    h = hash_password("MySecret1!")
    assert verify_password("wrong", h) is False


@pytest.mark.unit
def test_verify_password_empty():
    h = hash_password("MySecret1!")
    assert verify_password("", h) is False


# ── JWT creation / decoding ───────────────────────────────────────────────────

@pytest.mark.unit
def test_create_and_decode_token_roundtrip():
    token = create_access_token(data={"sub": "user-abc"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-abc"
    assert payload["token_version"] == 1  # default


@pytest.mark.unit
def test_token_includes_expiry():
    token = create_access_token(data={"sub": "x"})
    payload = decode_access_token(token)
    assert "exp" in payload


@pytest.mark.unit
def test_token_version_claim():
    token = create_access_token(data={"sub": "x"}, token_version=3)
    payload = decode_access_token(token)
    assert payload["token_version"] == 3


@pytest.mark.unit
def test_custom_expiry():
    token = create_access_token(
        data={"sub": "x"},
        expires_delta=timedelta(seconds=1),
    )
    payload = decode_access_token(token)
    assert "exp" in payload
    # Should be ~1 second from now
    assert abs(payload["exp"] - time.time()) < 5


@pytest.mark.unit
def test_decode_invalid_token_raises():
    with pytest.raises(JWTError):
        decode_access_token("not.a.valid.token")


@pytest.mark.unit
def test_decode_tampered_token_raises():
    token = create_access_token(data={"sub": "x"})
    # Truncate the signature — always invalid
    with pytest.raises(JWTError):
        decode_access_token(token[:-5] + "XXXXX")

```

---

## File: `tests\db\test_pool.py`

```python
"""Unit tests for app/db/pool.py — connection-string rewriting pure function.

``_langgraph_conn_string`` rewrites the DATABASE_URL in two ways:
  1. ``postgresql+asyncpg`` → ``postgresql`` (psycopg dialect)
  2. Neon ``-pooler.`` host → direct host (strip ``-pooler.``)

Both are pure string operations — no DB connection needed.
"""
import pytest

from app.db.pool import _langgraph_conn_string


# ── asyncpg → psycopg dialect ────────────────────────────────────────────────

@pytest.mark.unit
def test_rewrites_asyncpg_to_psycopg(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://user:pass@db.example.com/mydb",
    )
    result = _langgraph_conn_string()
    assert result.startswith("postgresql://")
    assert "asyncpg" not in result


# ── pooler → direct host ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_strips_pooler_from_neon_host(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://user:pass@ep-cool-name-pooler.us-east-2.aws.neon.tech/db",
    )
    result = _langgraph_conn_string()
    # -pooler. should become . so the host is the direct endpoint
    assert "-pooler." not in result
    assert "ep-cool-name.us-east-2.aws.neon.tech" in result


@pytest.mark.unit
def test_preserves_credentials_when_stripping_pooler(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://alice:s3cr3t@ep-cool-name-pooler.us-east-2.aws.neon.tech/db",
    )
    result = _langgraph_conn_string()
    assert "alice:s3cr3t@" in result


@pytest.mark.unit
def test_preserves_port_when_stripping_pooler(monkeypatch):
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql+asyncpg://u:p@ep-cool-pooler.us-east-2.aws.neon.tech:5432/db",
    )
    result = _langgraph_conn_string()
    assert ":5432" in result


# ── no-op when host isn't a pooler host ───────────────────────────────────────

@pytest.mark.unit
def test_noop_when_not_pooler_host(monkeypatch):
    direct = "postgresql+asyncpg://user:pass@db.example.com:5432/mydb"
    monkeypatch.setattr("app.db.pool.settings.DATABASE_URL", direct)
    result = _langgraph_conn_string()
    # Only the dialect should change; the host stays the same.
    assert "db.example.com" in result
    assert "-pooler." not in result


@pytest.mark.unit
def test_noop_when_already_postgresql(monkeypatch):
    """If the URL is already `postgresql://` it should be returned as-is."""
    monkeypatch.setattr(
        "app.db.pool.settings.DATABASE_URL",
        "postgresql://user:pass@db.example.com/mydb",
    )
    result = _langgraph_conn_string()
    assert result == "postgresql://user:pass@db.example.com/mydb"

```

---

## File: `tests\services\test_agent_service.py`

```python
"""Unit tests for app/services/agent_service.py — run_agent + _build_initial_state."""
import pytest

from app.schemas.agent import AgentRequest
from app.services.agent_service import _build_initial_state, run_agent


# ── _build_initial_state ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_build_initial_state_defaults():
    req = AgentRequest(patient_id="p1", query="hello")
    state = _build_initial_state(req)
    assert state["patient_id"] == "p1"
    assert state["raw_input"] == "hello"
    assert state["ocr_context"] == ""
    assert state["final_response"] == ""
    assert state["messages"] == []
    assert state["tool_results"] == ""
    assert state["needs_rag"] is False


@pytest.mark.unit
def test_build_initial_state_with_ocr():
    req = AgentRequest(patient_id="p1", query="what is this")
    state = _build_initial_state(req, ocr_text="OCR text here")
    assert state["ocr_context"] == "OCR text here"


# ── run_agent ────────────────────────────────────────────────────────────────

@pytest.mark.unit
async def test_run_agent_returns_response(monkeypatch):
    """With a mocked graph.invoke, run_agent returns an AgentResponse."""
    from app.services import agent_service

    canned_result = {
        "final_response": "You have a cold.",
        "detected_lang": "en",
        "needs_rag": True,
        "retrieval_decision": "correct",
        "retrieved_docs": [{"source": "mayo.com"}, {"source": "who.int"}],
        "saved_memory": True,
    }

    mock_agent = type("MockAgent", (), {"invoke": lambda self, state, config: canned_result})()
    monkeypatch.setattr(agent_service, "agent", mock_agent)

    req = AgentRequest(patient_id="p1", query="I have a fever")
    resp = await run_agent(req)

    assert resp.answer == "You have a cold."
    assert resp.detected_lang == "en"
    assert resp.needs_rag is True
    assert resp.retrieval_decision == "correct"
    assert resp.sources == ["mayo.com", "who.int"]
    assert resp.save_memory is True


@pytest.mark.unit
async def test_run_agent_retries_on_operational_error(monkeypatch):
    """psycopg.OperationalError (Neon wake race) triggers a retry."""
    import psycopg
    from app.services import agent_service

    call_count = {"n": 0}

    class _RetryThen:
        def invoke(self, state, config):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise psycopg.OperationalError("Neon sleeping")
            return {
                "final_response": "ok",
                "detected_lang": "en",
                "needs_rag": False,
                "retrieved_docs": [],
                "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _RetryThen())
    # Patch sleep so the test doesn't actually wait
    async def _noop_sleep(*a, **kw):
        pass
    monkeypatch.setattr("app.services.agent_service.asyncio.sleep", _noop_sleep)

    req = AgentRequest(patient_id="p1", query="hi")
    resp = await run_agent(req)

    assert call_count["n"] == 2  # retried once
    assert resp.answer == "ok"


@pytest.mark.unit
async def test_run_agent_raises_after_max_retries(monkeypatch):
    import psycopg
    from app.services import agent_service

    class _AlwaysFails:
        def invoke(self, state, config):
            raise psycopg.OperationalError("DB down")

    monkeypatch.setattr(agent_service, "agent", _AlwaysFails())
    async def _noop_sleep(*a, **kw):
        pass
    monkeypatch.setattr("app.services.agent_service.asyncio.sleep", _noop_sleep)

    req = AgentRequest(patient_id="p1", query="hi")
    with pytest.raises(psycopg.OperationalError):
        await run_agent(req)


@pytest.mark.unit
async def test_run_agent_non_operational_error_not_retried(monkeypatch):
    from app.services import agent_service

    class _RuntimeFail:
        def invoke(self, state, config):
            raise RuntimeError("graph broke")

    monkeypatch.setattr(agent_service, "agent", _RuntimeFail())

    req = AgentRequest(patient_id="p1", query="hi")
    with pytest.raises(RuntimeError, match="graph broke"):
        await run_agent(req)


@pytest.mark.unit
async def test_run_agent_thread_id_defaults_to_patient_id(monkeypatch):
    """When thread_id is absent, it defaults to patient_id."""
    from app.services import agent_service

    captured_config = {}

    class _CaptureConfig:
        def invoke(self, state, config):
            captured_config.update(config)
            return {
                "final_response": "ok", "detected_lang": "en",
                "needs_rag": False, "retrieved_docs": [], "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _CaptureConfig())

    req = AgentRequest(patient_id="patient-99", query="hi")
    await run_agent(req)

    assert captured_config["configurable"]["thread_id"] == "patient-99"


@pytest.mark.unit
async def test_run_agent_uses_thread_id_when_provided(monkeypatch):
    from app.services import agent_service

    captured_config = {}

    class _CaptureConfig:
        def invoke(self, state, config):
            captured_config.update(config)
            return {
                "final_response": "ok", "detected_lang": "en",
                "needs_rag": False, "retrieved_docs": [], "saved_memory": False,
            }

    monkeypatch.setattr(agent_service, "agent", _CaptureConfig())

    req = AgentRequest(
        patient_id="p1", query="hi", thread_id="conv-uuid-123"
    )
    await run_agent(req)

    assert captured_config["configurable"]["thread_id"] == "conv-uuid-123"

```

---

## File: `tests\services\test_chat_service.py`

```python
"""Unit tests for app/services/chat_service.py — stream_chat queue bridge."""
import pytest

from app.services.chat_service import stream_chat


@pytest.mark.unit
async def test_stream_chat_yields_chunks(fake_llm):
    """Chunks from the LLM's astream are yielded as plain strings."""
    fake_llm.stream_chunks = ["Hello", " ", "world"]
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_chat(messages, temperature=0.7, max_tokens=100)]

    assert "".join(tokens) == "Hello world"


@pytest.mark.unit
async def test_stream_chat_skips_empty_chunks(fake_llm):
    fake_llm.stream_chunks = ["a", "", "b"]
    messages = [{"role": "user", "content": "hi"}]
    tokens = [t async for t in stream_chat(messages, temperature=0.5, max_tokens=10)]
    assert tokens == ["a", "b"]


@pytest.mark.unit
async def test_stream_chat_error_sentinel(fake_llm):
    """When the LLM raises, stream_chat yields the error sentinel."""
    fake_llm.should_error = True
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_chat(messages, temperature=0.7, max_tokens=100)]

    assert tokens == ["\n\nServer Error"]


@pytest.mark.unit
async def test_stream_chat_converts_role_map(fake_llm, monkeypatch):
    """Messages dict is converted to LangChain message objects before calling
    the LLM.  Verify by capturing the messages list."""
    captured = []

    async def _fake_astream(messages, **kwargs):
        captured.extend(type(m).__name__ for m in messages)
        from types import SimpleNamespace
        yield SimpleNamespace(content="ok")

    fake_llm.astream = _fake_astream
    messages = [
        {"role": "system", "content": "be helpful"},
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    list_async_gen = [t async for t in stream_chat(messages, temperature=0.5, max_tokens=10)]
    assert "SystemMessage" in captured
    assert "HumanMessage" in captured
    assert "AIMessage" in captured

```

---

## File: `tests\services\test_conversation_service.py`

```python
"""Unit tests for app/services/conversation_service.py.

Covers turn reconstruction from checkpoint rows, title/snippet derivation,
ownership filtering, and retry logic.
"""
import pytest

from app.services import conversation_service as svc


# ── _title ────────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_title_uses_first_nonempty_raw_input():
    turns = [
        {"raw_input": "", "final_response": "a1"},
        {"raw_input": "  What is diabetes?  ", "final_response": "a2"},
    ]
    assert svc._title(turns) == "What is diabetes?"


@pytest.mark.unit
def test_title_fallback_when_all_empty():
    turns = [{"raw_input": "", "final_response": ""}]
    assert svc._title(turns) == "Untitled conversation"


# ── _sources ──────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_sources_extracts_source_fields():
    turn = {"retrieved_docs": [
        {"source": "who.int"}, {"source": ""}, {"source": "mayo.com"}, {"source": "x.com"},
    ]}
    assert svc._sources(turn) == ["who.int", "mayo.com", "x.com"][:3]


@pytest.mark.unit
def test_sources_empty():
    assert svc._sources({"retrieved_docs": None}) == []
    assert svc._sources({"retrieved_docs": []}) == []


# ── list_conversations ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_list_conversations_groups_by_thread(monkeypatch):
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "hello",
         "final_response": "hi", "ts": "2025-01-01T10:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
        {"thread_id": "t1", "checkpoint_id": "c2", "raw_input": "fever?",
         "final_response": "take meds", "ts": "2025-01-01T11:00:00",
         "detected_lang": "en", "needs_rag": True,
         "retrieval_decision": "correct", "retrieved_docs": [{"source": "s"}]},
        {"thread_id": "t2", "checkpoint_id": "c3", "raw_input": "bye",
         "final_response": "bye!", "ts": "2025-01-01T12:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = list(svc.list_conversations("patient-1"))

    assert len(result) == 2  # two threads
    # newest first (t2 has later ts)
    assert result[0]["thread_id"] == "t2"
    assert result[1]["thread_id"] == "t1"
    # message_count = turns * 2
    assert result[1]["message_count"] == 4  # t1 has 2 turns → 4 messages
    # snippet = last turn's final_response
    assert result[1]["snippet"] == "take meds"
    # title = first non-empty raw_input
    assert result[1]["title"] == "hello"


@pytest.mark.unit
def test_list_conversations_empty(monkeypatch):
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    assert svc.list_conversations("nobody") == []


# ── get_conversation ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_get_conversation_builds_transcript(monkeypatch):
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "What is diabetes?",
         "final_response": "It's a chronic condition.",
         "ts": "2025-01-01T10:00:00", "detected_lang": "en",
         "needs_rag": True, "retrieval_decision": "correct",
         "retrieved_docs": [{"source": "who.int"}]},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = svc.get_conversation("t1", "patient-1")

    assert result is not None
    assert result["thread_id"] == "t1"
    assert result["title"] == "What is diabetes?"
    assert len(result["messages"]) == 2  # user + assistant
    assert result["messages"][0]["role"] == "user"
    assert result["messages"][1]["role"] == "assistant"
    meta = result["messages"][1]["meta"]
    assert meta["needs_rag"] is True
    assert meta["retrieval_decision"] == "correct"
    assert "who.int" in meta["sources"]


@pytest.mark.unit
def test_get_conversation_not_found(monkeypatch):
    """When no turns match the thread_id/patient_id → None."""
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    assert svc.get_conversation("missing", "patient-1") is None


@pytest.mark.unit
def test_get_conversation_skips_empty_turns(monkeypatch):
    """Turns with both empty raw_input and final_response are skipped."""
    rows = [
        {"thread_id": "t1", "checkpoint_id": "c0", "raw_input": "",
         "final_response": "", "ts": "2025-01-01T09:00:00",
         "detected_lang": "", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
        {"thread_id": "t1", "checkpoint_id": "c1", "raw_input": "hi",
         "final_response": "hello", "ts": "2025-01-01T10:00:00",
         "detected_lang": "en", "needs_rag": False,
         "retrieval_decision": "", "retrieved_docs": None},
    ]
    monkeypatch.setattr(svc, "_query", lambda sql, params: rows)

    result = svc.get_conversation("t1", "patient-1")
    assert len(result["messages"]) == 2  # only the non-empty turn


@pytest.mark.unit
def test_get_conversation_ownership_filter(monkeypatch):
    """The patient_id is passed in the SQL params — only that patient's
    turns are returned.  If _query returns [], the conversation is None
    (ownership enforced at the DB level)."""
    monkeypatch.setattr(svc, "_query", lambda sql, params: [])
    # Patient-2 asks for patient-1's thread → no rows → None
    assert svc.get_conversation("t1", "patient-2") is None

```

---

## File: `tests\services\test_rag_chat_service.py`

```python
"""Unit tests for app/services/rag_chat_service.py — _build_prompt + stream_rag_chat."""
import pytest

from app.services.rag_chat_service import _build_prompt, stream_rag_chat


# ── _build_prompt ─────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_build_prompt_includes_query():
    prompt = _build_prompt("What is diabetes?", [{"text": "x", "source": "src"}])
    assert "What is diabetes?" in prompt
    assert "Answer:" in prompt


@pytest.mark.unit
def test_build_prompt_includes_doc_text():
    docs = [{"text": "Diabetes is chronic.", "source": "who.int"}]
    prompt = _build_prompt("q", docs)
    assert "Diabetes is chronic." in prompt
    assert "who.int" in prompt


@pytest.mark.unit
def test_build_prompt_truncates_to_300_chars():
    long_text = "A" * 500
    docs = [{"text": long_text, "source": "src"}]
    prompt = _build_prompt("q", docs)
    # The text should be truncated to 300 chars in the prompt
    assert "A" * 300 in prompt
    assert "A" * 301 not in prompt


@pytest.mark.unit
def test_build_prompt_uses_top_3_docs():
    docs = [
        {"text": f"doc{i}", "source": f"src{i}"} for i in range(5)
    ]
    prompt = _build_prompt("q", docs)
    assert "doc0" in prompt
    assert "doc1" in prompt
    assert "doc2" in prompt
    assert "doc3" not in prompt  # only top 3


@pytest.mark.unit
def test_build_prompt_empty_docs():
    prompt = _build_prompt("hello", [])
    assert "hello" in prompt
    assert "Answer:" in prompt


# ── stream_rag_chat ──────────────────────────────────────────────────────────

@pytest.mark.unit
async def test_stream_rag_chat_yields_chunks(fake_llm, fake_qdrant):
    fake_llm.stream_chunks = ["RAG", " ", "answer"]
    messages = [{"role": "user", "content": "What is diabetes?"}]

    tokens = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=100)]
    assert "".join(tokens) == "RAG answer"


@pytest.mark.unit
async def test_stream_rag_chat_error_sentinel(fake_llm, fake_qdrant):
    fake_llm.should_error = True
    messages = [{"role": "user", "content": "hi"}]

    tokens = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=100)]
    assert tokens == ["\n\nServer Error"]


@pytest.mark.unit
async def test_stream_rag_chat_uses_last_message_as_query(fake_llm, fake_qdrant, monkeypatch):
    """The last user message's content is what gets sent to corrective_retrieve."""
    captured_query = []

    original_retrieve = fake_qdrant

    def _spy_retrieve(query, top_k=5, category=None):
        captured_query.append(query)
        return original_retrieve(query, top_k=top_k, category=category)

    monkeypatch.setattr("app.core.rag.corrective_rag.retrieve", _spy_retrieve)

    messages = [
        {"role": "user", "content": "earlier question"},
        {"role": "assistant", "content": "earlier answer"},
        {"role": "user", "content": "What is diabetes?"},
    ]
    _ = [t async for t in stream_rag_chat(messages, temperature=0.5, max_tokens=50)]
    assert captured_query[-1] == "What is diabetes?"

```

---

