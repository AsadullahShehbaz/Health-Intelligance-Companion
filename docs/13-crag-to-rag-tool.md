Got it! Converting CRAG (Corrective RAG) into a direct, streamlined RAG tool makes total sense—especially since your pipeline already leverages fine-tuned models, local knowledge vector search, and web tools via the Groq agent router. Dropping the evaluation/rewrite loops simplifies the architecture and speeds up node latency considerably.

Here is the updated step-by-step technical plan to replace CRAG with a clean, direct RAG tool while integrating SerpAPI and fixing the router memory triggers.

---

## 🛠️ Updated Technical Implementation Plan

### Step 1: Replace CRAG Logic with Direct RAG Tool (`app/core/rag/rag_tool.py`)

Remove the grade/rewrite heuristic from `corrective_rag.py` and implement a straightforward hybrid or vector retrieval function that queries your local vector database (Qdrant/FAISS) and returns top documents directly.

* **Create/Modify `app/core/rag/rag_tool.py`:**

```python
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def perform_direct_rag(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Executes direct vector retrieval from the local knowledge base without 
    corrective re-ranking or query rewriting loops.
    """
    logger.info("▶ Direct RAG Search | query=%s", query[:80])
    try:
        # Replace 'vector_store' with your actual retriever/vector store instance
        # e.g., vector_store.similarity_search_with_score(query, k=top_k)
        docs = vector_store.similarity_search(query, k=top_k)
        
        results = []
        for doc in docs:
            results.append({
                "title": doc.metadata.get("title", "Medical Knowledge Base"),
                "text": doc.page_content,
                "score": doc.metadata.get("score", None)
            })
        return results
    except Exception as e:
        logger.exception("Direct RAG retrieval failed")
        return []

```

---

### Step 2: Define & Register Direct RAG & SerpAPI Tools (`app/agent/tools.py`)

Update `retrieve_medical_knowledge` to call the simplified RAG function, define `search_web_medical`, and export both in `TOOLS`.

* **Modify `app/agent/tools.py`:**

```python
from langchain_core.tools import tool
from app.core.rag.rag_tool import perform_direct_rag
from app.core.rag.web_search import web_search_fallback  # or your direct SerpAPI wrapper

@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieves relevant medical guidelines, clinical notes, or local health docs from the vector database."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    results = perform_direct_rag(query)
    
    if not results:
        return "No relevant internal medical documents found."
    
    formatted = []
    for r in results:
        formatted.append(f"[{r['title']}]: {r['text']}")
    return "Internal Medical Knowledge Results:\n" + "\n\n".join(formatted)

@tool
def search_web_medical(query: str) -> str:
    """Searches the web via SerpAPI for current health information or external guidelines."""
    logger.info("▶ search_web_medical | query=%s", query[:80])
    try:
        results = web_search_fallback(query)
        if not results:
            return "No web search results found."
        lines = [f"[{r.get('title', 'Web Source')}]: {r.get('text', '')}" for r in results[:3]]
        return "Web Search Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("search_web_medical failed")
        return f"Error executing web search: {e}"

# Register tools for the agent router
TOOLS = [
    fetch_patient_facts,
    retrieve_medical_knowledge,  # Direct RAG Tool
    save_patient_fact,
    save_emotional_state,
    search_web_medical,          # SerpAPI Tool
]

```

---

### Step 3: Update Router System Prompt (`app/agent/nodes/router_node.py`)

Update the system prompt so the Groq router knows when to trigger direct vector retrieval vs. web search, while expanding memory tool triggers for user background info.

* **Modify `app/agent/nodes/router_node.py`:**

```python
ROUTER_SYSTEM_PROMPT = """You are an intelligent routing agent for a healthcare assistant.
Your job is to analyze the conversation and call appropriate tools ONLY if required:

1. Call 'fetch_patient_facts' if you need to recall past medical history or saved context.
2. Call 'retrieve_medical_knowledge' for clinical, diagnostic, or general medical queries to fetch local vector database knowledge.
3. Call 'search_web_medical' if the query asks for recent medical news, external guidelines, or information unlikely to be in local knowledge.
4. Call 'save_patient_fact' if the user shares personal details, medical history, age, or new symptoms.
5. Call 'save_emotional_state' if the user expresses emotional distress or anxiety.

If no tool execution is required (e.g., pure greetings or general banter), do NOT call any tools.
Patient ID: {patient_id}
"""

```

---

### Step 4: Streamline Metadata Extraction (`app/agent/graph.py`)

Clean up the tool metadata parser to remove any leftover CRAG logic (e.g., "Retrieval decision" grading checks) and directly record sources from both RAG and Web tools.

* **Modify `app/agent/graph.py`:**

```python
if name in ("retrieve_medical_knowledge", "search_web_medical"):
    rag_used = True
    # Parse source titles from formatted tool outputs
    for line in content.splitlines():
        match = re.match(r"^\s*\[([^\]]+)\]", line)
        if match:
            sources.append(match.group(1))

```

---

## 🧪 Quick Test Plan

1. **Direct RAG Execution:** Send a clinical/medical query (e.g., *"What are the key contraindications for Metformin?"*). Confirm `retrieve_medical_knowledge` runs directly without CRAG evaluation overhead.
2. **SerpAPI Execution:** Send a recent news/external search query. Confirm `search_web_medical` gets invoked by the router.
3. **Memory Persistence:** Send personal details (e.g., *"Hi, I'm 24 years old and was diagnosed with hypertension"*). Verify that `save_patient_fact` triggers and writes directly to `PostgresStore`.