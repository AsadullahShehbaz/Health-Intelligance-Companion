## Week 4 Complete Plan — Corrective RAG Pipeline

---

## Your Hardware Reality Check First

```
CPU:     Core i5 (no GPU)
RAM:     16GB (Docker + Qdrant already running)
C: Drive: 25.5 GB free ← tight
D: Drive: 10.7 GB free ← very tight
Total free: ~36 GB

Constraints this creates:
❌ Cannot run BioMistral locally (needs 8GB+ VRAM)
❌ Cannot store large embedding models locally
❌ Cannot run heavy RAG data processing locally
✅ Qdrant already running in Docker ← perfect
✅ LangGraph + LangChain run on CPU fine
✅ FastAPI runs on CPU fine
✅ RAG retrieval runs on CPU fine
```

---

## The Smart Solution — Same Pattern as Week 3

```
Week 3 problem: No GPU for fine-tuning
Week 3 solution: Use Kaggle free GPU

Week 4 problem: No disk space for embeddings + data
Week 4 solution: 
  → Build RAG knowledge base on Kaggle
  → Export vectors to local Qdrant
  → Run inference via HuggingFace API (free)
  → Everything heavy stays in cloud
  → Only lightweight pipeline runs locally
```

---

## What is Corrective RAG (C-RAG)?

```
Normal RAG:
Query → Retrieve → Generate → Answer
Problem: retrieved docs might be irrelevant
         model generates anyway → hallucination

Corrective RAG adds a correction step:
Query → Retrieve → EVALUATE RELEVANCE
                        ↓
              Relevant? → Generate → Answer
                        ↓
              Not relevant? → Web Search
                        ↓
                   Better docs → Generate → Answer

This is why it is called CORRECTIVE RAG.
It corrects bad retrievals before generating.
Academic contribution for your FYP ✅
```

---

## Complete Week 4 Day by Day Plan

---

### Day 1 — Build RAG Knowledge Base on Kaggle

**Why Kaggle:** Free internet, free disk space (20GB), no RAM constraints

```python
# ═══════════════════════════════════════
# KAGGLE NOTEBOOK — RAG Data Collection
# Run this on Kaggle, not locally
# ═══════════════════════════════════════

!pip install -q sentence-transformers \
                datasets \
                qdrant-client \
                langchain \
                langchain-community \
                pypdf \
                requests

import os
import json
import torch
import pandas as pd
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

# Use lightweight embedding model
# all-MiniLM-L6-v2 = 90MB only, 384 dim
# Fast on CPU, good quality
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM   = 384

embedder = SentenceTransformer(EMBED_MODEL)
print(f"✅ Embedder loaded: {EMBED_MODEL}")
```

```python
# ── Collect RAG Knowledge Sources ──────────────────

all_documents = []

# Source 1 — Disease Symptoms (already have this)
print("Loading disease symptoms...")
ds = load_dataset("QuyenAnhDE/Diseases_Symptoms")
for row in ds['train']:
    name     = str(row.get('Name','')).strip()
    symptoms = str(row.get('Symptoms','')).strip()
    treats   = str(row.get('Treatments','')).strip()
    if name and symptoms:
        all_documents.append({
            "text": f"Disease: {name}\nSymptoms: {symptoms}\nTreatments: {treats}",
            "source": "disease_db",
            "category": "disease",
            "disease": name.lower()
        })
print(f"✅ Disease docs: {len(all_documents)}")

# Source 2 — MedQA as knowledge (answers = knowledge)
print("Loading MedQA knowledge...")
medqa = load_dataset("GBaker/MedQA-USMLE-4-options")
for row in medqa['train'].select(range(3000)):
    q = str(row['question']).strip()
    a = str(row['answer']).strip()
    all_documents.append({
        "text": f"Medical Knowledge:\nQ: {q}\nA: {a}",
        "source": "medqa",
        "category": "clinical_knowledge",
        "disease": "general"
    })
print(f"✅ Total after MedQA: {len(all_documents)}")

# Source 3 — PubMedQA research findings
print("Loading PubMedQA...")
pubmed = load_dataset(
    "qiaojin/PubMedQA", "pqa_labeled",
    trust_remote_code=True
)
for row in pubmed['train'].select(range(500)):
    q      = str(row['question']).strip()
    answer = str(row['long_answer']).strip()
    all_documents.append({
        "text": f"Research Finding:\n{q}\nConclusion: {answer}",
        "source": "pubmed",
        "category": "research",
        "disease": "general"
    })
print(f"✅ Total after PubMed: {len(all_documents)}")

# Source 4 — ChatDoctor as knowledge base
print("Loading ChatDoctor knowledge...")
chat = load_dataset("lavita/ChatDoctor-HealthCareMagic-100k")
for row in chat['train'].select(range(5000)):
    inp = str(row.get('input','')).strip()
    out = str(row.get('output','')).strip()
    if len(inp) > 30 and len(out) > 50:
        all_documents.append({
            "text": f"Patient Case:\n{inp}\nDoctor Response:\n{out}",
            "source": "chatdoctor",
            "category": "consultation",
            "disease": "general"
        })

print(f"✅ Total documents: {len(all_documents)}")
```

```python
# ── Generate Embeddings ────────────────────────────
print("\nGenerating embeddings...")
print("This takes 10-20 minutes on Kaggle CPU...")

texts = [doc['text'] for doc in all_documents]

# Batch encode for speed
embeddings = embedder.encode(
    texts,
    batch_size    = 64,
    show_progress_bar = True,
    normalize_embeddings = True  # important for cosine
)

print(f"✅ Embeddings shape: {embeddings.shape}")
```

```python
# ── Save as JSON for export to local Qdrant ────────
print("\nSaving for export...")

export_data = []
for i, (doc, emb) in enumerate(
    zip(all_documents, embeddings)
):
    export_data.append({
        "id":      i + 1,
        "vector":  emb.tolist(),
        "payload": doc
    })

# Save in chunks to avoid memory issues
CHUNK_SIZE = 2000
for chunk_idx in range(
    0, len(export_data), CHUNK_SIZE
):
    chunk = export_data[chunk_idx:chunk_idx+CHUNK_SIZE]
    fname = f"rag_vectors_{chunk_idx//CHUNK_SIZE}.json"
    with open(fname, 'w') as f:
        json.dump(chunk, f)
    print(f"✅ Saved {fname}: {len(chunk)} vectors")

print(f"\nTotal chunks: {len(export_data)//CHUNK_SIZE+1}")
print("Download all rag_vectors_*.json files")
```

Download all JSON files from Kaggle output to your D: drive.

---

### Day 2 — Import Vectors Into Local Qdrant

**This runs locally — Qdrant already running on Docker**

```python
# ═══════════════════════════════════════
# LOCAL — Import vectors into Qdrant
# Run on your machine
# ═══════════════════════════════════════
pip install qdrant-client sentence-transformers

import json
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)

# Connect to your local Qdrant
client = QdrantClient(host="localhost", port=6333)
print("✅ Connected to Qdrant")

# Create collection
COLLECTION = "health_knowledge"
EMBED_DIM  = 384

# Delete if exists (fresh start)
try:
    client.delete_collection(COLLECTION)
    print("Deleted existing collection")
except:
    pass

client.create_collection(
    collection_name = COLLECTION,
    vectors_config  = VectorParams(
        size     = EMBED_DIM,
        distance = Distance.COSINE
    )
)
print(f"✅ Collection created: {COLLECTION}")

# Import all JSON chunks
vector_files = sorted(
    glob.glob("D:/rag_vectors_*.json")
)
print(f"\nFound {len(vector_files)} vector files")

total_imported = 0

for fpath in vector_files:
    with open(fpath, 'r') as f:
        chunk = json.load(f)

    points = [
        PointStruct(
            id      = item['id'],
            vector  = item['vector'],
            payload = item['payload']
        )
        for item in chunk
    ]

    # Upsert in batches of 100
    for i in range(0, len(points), 100):
        batch = points[i:i+100]
        client.upsert(
            collection_name = COLLECTION,
            points          = batch
        )

    total_imported += len(points)
    print(f"✅ {fpath}: {len(points)} vectors imported")

print(f"\n✅ Total imported: {total_imported:,} vectors")

# Verify
info = client.get_collection(COLLECTION)
print(f"✅ Qdrant collection size: "
      f"{info.points_count:,} points")
```

---

### Day 3 — Build Corrective RAG Pipeline

**Runs locally — CPU only, lightweight**

```python
# ═══════════════════════════════════════
# CORRECTIVE RAG PIPELINE
# File: src/rag/corrective_rag.py
# ═══════════════════════════════════════
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import requests
import os

class CorrectiveRAG:
    """
    Corrective RAG Pipeline
    Evaluates retrieval quality and corrects
    bad retrievals before generation
    """

    def __init__(self):
        # Lightweight embedder — runs on CPU fine
        self.embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Local Qdrant
        self.qdrant = QdrantClient(
            host="localhost", port=6333
        )

        self.collection = "health_knowledge"

        # Relevance threshold
        # Score below this = retrieval is bad
        # Trigger correction step
        self.relevance_threshold = 0.5

        print("✅ CorrectiveRAG initialized")

    # ── Step 1: Retrieve ──────────────────────────
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category_filter: str = None
    ) -> List[Dict]:

        query_vector = self.embedder.encode(
            query, normalize_embeddings=True
        ).tolist()

        # Build filter if category specified
        search_filter = None
        if category_filter:
            search_filter = Filter(
                must=[FieldCondition(
                    key   = "category",
                    match = MatchValue(
                        value=category_filter
                    )
                )]
            )

        results = self.qdrant.search(
            collection_name = self.collection,
            query_vector    = query_vector,
            query_filter    = search_filter,
            limit           = top_k,
            with_payload    = True,
            score_threshold = 0.3  # minimum score
        )

        docs = []
        for r in results:
            docs.append({
                "text":     r.payload.get("text",""),
                "source":   r.payload.get("source",""),
                "category": r.payload.get("category",""),
                "score":    r.score
            })

        return docs

    # ── Step 2: Evaluate Relevance ────────────────
    def evaluate_relevance(
        self,
        query: str,
        docs: List[Dict]
    ) -> Tuple[str, float]:
        """
        Evaluate if retrieved docs are relevant
        Returns: (decision, avg_score)
        decision = 'correct' | 'incorrect' | 'ambiguous'
        """
        if not docs:
            return 'incorrect', 0.0

        scores = [d['score'] for d in docs]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        if max_score >= self.relevance_threshold:
            return 'correct', avg_score
        elif avg_score >= 0.35:
            return 'ambiguous', avg_score
        else:
            return 'incorrect', avg_score

    # ── Step 3: Correct (Web Search fallback) ─────
    def web_search_fallback(
        self, query: str
    ) -> List[Dict]:
        """
        Called when retrieval quality is poor.
        Uses DuckDuckGo free search — no API key.
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(
                    f"medical {query}",
                    max_results=3
                ):
                    results.append({
                        "text":     r.get('body',''),
                        "source":   "web_search",
                        "category": "web",
                        "score":    0.5
                    })
            return results

        except Exception as e:
            print(f"Web search failed: {e}")
            return []

    # ── Step 4: Generate via HuggingFace API ──────
    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict]
    ) -> str:
        """
        Uses HuggingFace Inference API
        Free tier — no GPU needed locally
        Calls your fine-tuned BioMistral model
        """
        # Build context from retrieved docs
        context = "\n\n".join([
            f"[Source: {d['source']}]\n{d['text'][:300]}"
            for d in context_docs[:3]
        ])

        # Build prompt
        prompt = f"""### Question:
{query}

### Relevant Medical Context:
{context}

### Answer:
Based on the medical context provided,"""

        # Call HuggingFace Inference API
        # Free tier: 1000 requests/day
        HF_TOKEN  = os.getenv("HF_TOKEN")
        if not HF_TOKEN:
            return "Generation failed: HF_TOKEN not found in environment variables."

        MODEL_URL = (
            "https://api-inference.huggingface.co"
            "/models/asadullahshehbaz/"
            "biomistral-health-fyp"
        )

        print(f"  Requesting HF API: {MODEL_URL}")

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        payload = {
            "inputs":     prompt,
            "parameters": {
                "max_new_tokens":     300,
                "temperature":        0.7,
                "return_full_text":   False,
                "do_sample":          True,
            }
        }

        try:
            response = requests.post(
                MODEL_URL,
                headers = headers,
                json    = payload,
                timeout = 30
            )
            
            # Check for HTTP errors first
            if response.status_code != 200:
                return f"Generation failed: API returned status {response.status_code}. Content: {response.text[:100]}"

            result = response.json()

            if "error" in result:
                return f"Generation failed: {result['error']}"

            if isinstance(result, list):
                return result[0].get(
                    'generated_text', ''
                ).strip()
            else:
                return str(result)

        except Exception as e:
            return f"Generation failed: {e}"

    # ── Main Pipeline: Full C-RAG Flow ────────────
    def run(self, patient_query: str) -> Dict:
        """
        Complete Corrective RAG pipeline
        Returns full diagnostic result
        """
        print(f"\n{'='*50}")
        print(f"Query: {patient_query[:80]}")
        print(f"{'='*50}")

        # Step 1 — Initial retrieval
        print("Step 1: Retrieving documents...")
        docs = self.retrieve(patient_query, top_k=5)
        print(f"  Retrieved: {len(docs)} documents")

        # Step 2 — Evaluate relevance
        print("Step 2: Evaluating relevance...")
        decision, avg_score = self.evaluate_relevance(
            patient_query, docs
        )
        print(f"  Decision: {decision} "
              f"(avg score: {avg_score:.3f})")

        # Step 3 — Correct if needed
        if decision == 'incorrect':
            print("Step 3: CORRECTING — web search...")
            web_docs = self.web_search_fallback(
                patient_query
            )
            docs = web_docs + docs  # prepend web results
            print(f"  Added {len(web_docs)} web docs")

        elif decision == 'ambiguous':
            print("Step 3: AMBIGUOUS — adding web docs...")
            web_docs = self.web_search_fallback(
                patient_query
            )
            docs = docs + web_docs  # append web results
            print(f"  Added {len(web_docs)} web docs")

        else:
            print("Step 3: Retrieval CORRECT — no correction needed")

        # Step 4 — Generate answer
        print("Step 4: Generating answer...")
        answer = self.generate_answer(
            patient_query, docs
        )

        return {
            "query":        patient_query,
            "answer":       answer,
            "sources":      [d['source'] for d in docs[:3]],
            "retrieval":    decision,
            "avg_score":    round(avg_score, 3),
            "docs_used":    len(docs),
            "context_docs": docs[:3]
        }
```

---

### Day 4 — LangGraph Agent Integration

```python
# ═══════════════════════════════════════
# LANGGRAPH AGENT WITH CORRECTIVE RAG
# File: src/agent/health_agent.py
# ═══════════════════════════════════════
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from src.rag.corrective_rag import CorrectiveRAG
from deep_translator import GoogleTranslator
from langdetect import detect
import psycopg2
import json

# ── State Definition ──────────────────────────────
class PatientState(TypedDict):
    patient_id:       str
    original_input:   str
    detected_lang:    str
    english_input:    str
    retrieved_docs:   List[dict]
    retrieval_status: str
    diagnosis:        str
    treatment_plan:   str
    final_response:   str
    session_id:       str

# ── Initialize RAG ────────────────────────────────
crag = CorrectiveRAG()

# ── Node 1: Language Detection + Translation ──────
def detect_and_translate(state: PatientState) -> PatientState:
    text = state['original_input']
    try:
        lang = detect(text)
    except:
        lang = 'en'

    if lang != 'en':
        english = GoogleTranslator(
            source='auto', target='english'
        ).translate(text)
    else:
        english = text

    state['detected_lang'] = lang
    state['english_input'] = english
    print(f"✅ Node 1: Lang={lang}, "
          f"Translated={english[:50]}")
    return state

# ── Node 2: Load Patient History from PostgreSQL ──
def load_patient_history(
    state: PatientState
) -> PatientState:
    try:
        conn = psycopg2.connect(
            dbname   = "health_companion",
            user     = "postgres",
            password = "password",
            host     = "localhost"
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT chief_complaint, diagnoses_made,
                   treatment_given, session_date
            FROM sessions
            WHERE patient_id = %s
            ORDER BY session_date DESC
            LIMIT 3
        """, (state['patient_id'],))

        history = cur.fetchall()
        if history:
            history_text = "\n".join([
                f"Past visit {i+1}: {h[0]}"
                for i, h in enumerate(history)
            ])
            state['english_input'] = (
                f"Patient history: {history_text}\n\n"
                f"Current complaint: {state['english_input']}"
            )
        conn.close()
    except Exception as e:
        print(f"DB note: {e}")

    print("✅ Node 2: Patient history loaded")
    return state

# ── Node 3: Corrective RAG ────────────────────────
def corrective_rag_node(
    state: PatientState
) -> PatientState:
    result = crag.run(state['english_input'])

    state['retrieved_docs']   = result['context_docs']
    state['retrieval_status'] = result['retrieval']
    state['diagnosis']        = result['answer']

    print(f"✅ Node 3: C-RAG done "
          f"({result['retrieval']}, "
          f"score={result['avg_score']})")
    return state

# ── Node 4: Treatment Plan ────────────────────────
def generate_treatment(
    state: PatientState
) -> PatientState:
    # Retrieve treatment-specific docs
    treatment_docs = crag.retrieve(
        state['english_input'],
        top_k           = 3,
        category_filter = "disease"
    )

    treatment_context = "\n".join([
        d['text'][:200] for d in treatment_docs
    ])

    state['treatment_plan'] = (
        f"Based on diagnosis:\n{state['diagnosis']}\n\n"
        f"Recommended approach:\n{treatment_context}"
    )

    print("✅ Node 4: Treatment plan generated")
    return state

# ── Node 5: Translate Response Back ──────────────
def translate_response(
    state: PatientState
) -> PatientState:
    full_response = (
        f"{state['diagnosis']}\n\n"
        f"Treatment Plan:\n{state['treatment_plan']}"
    )

    if state['detected_lang'] == 'ur':
        try:
            translated = GoogleTranslator(
                source='english', target='ur'
            ).translate(full_response[:500])
            state['final_response'] = translated
        except:
            state['final_response'] = full_response
    else:
        state['final_response'] = full_response

    print("✅ Node 5: Response ready")
    return state

# ── Node 6: Save to PostgreSQL ────────────────────
def save_to_memory(
    state: PatientState
) -> PatientState:
    try:
        conn = psycopg2.connect(
            dbname   = "health_companion",
            user     = "postgres",
            password = "password",
            host     = "localhost"
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions
            (patient_id, chief_complaint,
             diagnoses_made, treatment_given)
            VALUES (%s, %s, %s, %s)
        """, (
            state['patient_id'],
            state['original_input'][:500],
            json.dumps({"diagnosis": state['diagnosis']}),
            json.dumps({"plan": state['treatment_plan']})
        ))
        conn.commit()
        conn.close()
        print("✅ Node 6: Saved to PostgreSQL")
    except Exception as e:
        print(f"DB save note: {e}")

    return state

# ── Build LangGraph ───────────────────────────────
def build_health_agent():
    graph = StateGraph(PatientState)

    # Add nodes
    graph.add_node("translate",     detect_and_translate)
    graph.add_node("load_history",  load_patient_history)
    graph.add_node("corrective_rag",corrective_rag_node)
    graph.add_node("treatment",     generate_treatment)
    graph.add_node("respond",       translate_response)
    graph.add_node("save_memory",   save_to_memory)

    # Add edges
    graph.set_entry_point("translate")
    graph.add_edge("translate",      "load_history")
    graph.add_edge("load_history",   "corrective_rag")
    graph.add_edge("corrective_rag", "treatment")
    graph.add_edge("treatment",      "respond")
    graph.add_edge("respond",        "save_memory")
    graph.add_edge("save_memory",    END)

    return graph.compile()

# ── Test ──────────────────────────────────────────
if __name__ == "__main__":
    agent = build_health_agent()

    result = agent.invoke({
        "patient_id":     "patient_001",
        "original_input": "I have fever and headache for 3 days",
        "session_id":     "session_001",
        "detected_lang":  "",
        "english_input":  "",
        "retrieved_docs": [],
        "retrieval_status": "",
        "diagnosis":      "",
        "treatment_plan": "",
        "final_response": ""
    })

    print("\n" + "="*50)
    print("FINAL RESPONSE:")
    print(result['final_response'])
```

---

### Day 5 — FastAPI Backend

```python
# ═══════════════════════════════════════
# FASTAPI BACKEND
# File: src/api/main.py
# ═══════════════════════════════════════
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.health_agent import build_health_agent
import uvicorn

app   = FastAPI(title="Health Intelligence Companion")
agent = build_health_agent()

class PatientQuery(BaseModel):
    patient_id: str
    query:      str

class DiagnosisResponse(BaseModel):
    patient_id:       str
    diagnosis:        str
    treatment_plan:   str
    final_response:   str
    retrieval_status: str
    sources:          list

@app.post("/diagnose", response_model=DiagnosisResponse)
async def diagnose(request: PatientQuery):
    try:
        result = agent.invoke({
            "patient_id":     request.patient_id,
            "original_input": request.query,
            "session_id":     f"session_{request.patient_id}",
            "detected_lang":  "",
            "english_input":  "",
            "retrieved_docs": [],
            "retrieval_status": "",
            "diagnosis":      "",
            "treatment_plan": "",
            "final_response": ""
        })

        return DiagnosisResponse(
            patient_id       = request.patient_id,
            diagnosis        = result['diagnosis'],
            treatment_plan   = result['treatment_plan'],
            final_response   = result['final_response'],
            retrieval_status = result['retrieval_status'],
            sources          = [
                d['source']
                for d in result['retrieved_docs'][:3]
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e)
        )

@app.get("/health")
def health_check():
    return {"status": "running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Week 4 Complete Schedule

```
Day 1 → Kaggle: collect + embed RAG data
         Download JSON vector files
         (runs on Kaggle — zero local disk used)

Day 2 → Local: import vectors into Qdrant
         Install pip packages
         Run import script
         Verify collection in Qdrant dashboard
         http://localhost:6333/dashboard

Day 3 → Local: build CorrectiveRAG class
         Test retrieval on 10 medical queries
         Verify C-RAG correction step works
         Install: duckduckgo-search deep-translator

Day 4 → Local: build LangGraph agent
         Connect all 6 nodes
         Test end-to-end with sample patient

Day 5 → Local: FastAPI backend
         Test /diagnose endpoint with Postman
         Week 4 complete ✅
```

---

## Disk Space Management

```
C: Drive usage (25.5GB free):
  Project code:     ~50 MB   ✅ tiny
  pip packages:     ~2 GB    ✅ fine
  Python env:       ~1 GB    ✅ fine

D: Drive usage (10.7GB free):
  RAG JSON files:   ~500 MB  ✅ fits
  Qdrant storage:   ~1 GB    ✅ fits
  (already running in Docker)

What stays on Kaggle/HuggingFace:
  BioMistral model: 14 GB    ← never downloaded locally
  Embedding model:  90 MB    ← cached after first use

Total local disk needed: ~4 GB ✅ fits comfortably
```

---

## Install Everything Needed

```bash
pip install qdrant-client \
            sentence-transformers \
            langchain \
            langchain-community \
            langgraph \
            langchain-qdrant \
            fastapi \
            uvicorn \
            psycopg2-binary \
            deep-translator \
            langdetect \
            duckduckgo-search \
            requests
```

Start Day 1 Kaggle notebook today. The vector generation is the longest step — get it running and we build the pipeline while it runs. 🚀