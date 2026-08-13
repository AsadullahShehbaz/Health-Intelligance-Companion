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
