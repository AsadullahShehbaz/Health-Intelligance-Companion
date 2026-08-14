Here is a detailed, step-by-step technical plan to resolve the router behavior issue and integrate the SerpAPI search tool into your LangGraph agent execution pipeline.

---

## 🔍 Root Cause Analysis

Based on the provided server log snippet:

1. **Router Prompt Constraints:** The router prompt instructs calling `save_patient_fact` or `save_emotional_state` *only* if the user directly reports new symptoms or emotional distress. When a user introduces themselves or provides contextual info without explicit symptom reports, the router correctly opts out of saving facts.
2. **Missing Tool Schema:** SerpAPI fallback currently exists inside `app/core/rag/corrective_rag.py`, but it is not exposed as a standalone LangGraph tool (`@tool`) inside `app/agent/tools.py`.
3. **Implicit Memory Retrieval/Persistence:** Fact saving relies strictly on explicit symptom/emotion detection rather than extracting user background metadata (e.g., identity, age, past conditions) to store in the `PostgresStore`.

---

## 🛠️ Step-by-Step Fix & Implementation Plan

### Step 1: Update Router Prompt & Instructions

Update `ROUTER_SYSTEM_PROMPT` in `app/agent/nodes/router_node.py` to instruct the Groq router model to explicitly recognize and persist user background information, personal details, or health metrics into memory via tool calls.

* **Modify `app/agent/nodes/router_node.py`:**
Update the system prompt so the router triggers memory-saving actions whenever user identity or health background is stated:
```python
ROUTER_SYSTEM_PROMPT = """You are an intelligent routing agent for a healthcare assistant.
Your job is to analyze the conversation and call appropriate tools ONLY if required:
1. Call 'fetch_patient_facts' if the user mentions past history, medical records, or previous symptoms.
2. Call 'retrieve_medical_knowledge' if the user asks a specific medical, clinical, or general health query.
3. Call 'save_patient_fact' if the user reports personal details, general health information, or new symptoms.
4. Call 'save_emotional_state' if the user expresses anxiety, stress, or emotional concerns.
5. Call 'search_web_medical' if the query requires recent or external health news/guidelines not covered by local knowledge.

If no tools are needed (e.g., pure greetings, simple farewells), do NOT call any tools.
Patient ID: {patient_id}
"""

```



---

### Step 2: Define & Register SerpAPI Web Search Tool

Create a standalone `@tool` for SerpAPI search inside `app/agent/tools.py` and register it in `TOOLS`.

* **Modify `app/agent/tools.py`:**
Add the web search tool definition and include it in `TOOLS`:
```python
from app.core.rag.corrective_rag import web_search_fallback

@tool
def search_web_medical(query: str) -> str:
    """Search the web for up-to-date medical guidelines, local health news, or general health information."""
    logger.info("▶ search_web_medical | query=%s", query[:80])
    try:
        results = web_search_fallback(query)
        if not results:
            return "No web results found."
        lines = [f"[{r.get('title', 'Web Source')}] ({r.get('source', '')}): {r.get('text', '')}" for r in results[:3]]
        return "Web Search Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("search_web_medical failed")
        return f"Error executing web search: {e}"

# Register tool
TOOLS = [
    fetch_patient_facts,
    retrieve_medical_knowledge,
    save_patient_fact,
    save_emotional_state,
    search_web_medical,  # <-- Added
]

```



---

### Step 3: Update Tool Metadata Extraction in Graph

Update `_extract_tool_metadata` in `app/agent/graph.py` to capture execution signals from `search_web_medical`.

* **Modify `app/agent/graph.py`:**
Update the metadata loop inside `_extract_tool_metadata`:
```python
if name in ("retrieve_medical_knowledge", "search_web_medical"):
    rag_used = True
    # Extract web sources if available
    for line in content.splitlines():
        if "Retrieval decision" in line:
            match = re.search(r"Retrieval decision:\s*([A-Za-z]+)", line)
            if match:
                decision_text = match.group(1)
        else:
            match = re.match(r"^\s*\[([^\]]+)\]", line)
            if match:
                sources.append(match.group(1))

```



---

### Step 4: Verification & Testing Strategy

1. **Memory Tool Trigger Verification:**
* Send a test request containing patient details: `POST /agent/invoke` with `"I'm Asadullah, 22 years old, diagnosed with Type 1 Diabetes."`
* Check logs to confirm `Router requested tools: save_patient_fact` and verify the entry in the `PostgresStore`.


2. **SerpAPI Web Search Verification:**
* Query recent medical information or external guidelines: `"What are the latest WHO guidelines for Dengue prevention in 2026?"`
* Confirm that the router invokes `search_web_medical` and that `tool_results` are passed down to the `biomistral_node`.