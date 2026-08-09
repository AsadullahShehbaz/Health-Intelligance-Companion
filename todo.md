Two separate problems here, and both are serious enough to fix before you build anything further on top of this.

## Problem 1: ~9 minutes for one turn — this is not usable for a demo

Look at the per-node times: Router 115s, Rewrite 108s, Reasoner 135s, Extract_facts 180s. That's absurd for grammar-constrained generation on a 7B model — even on CPU, a well-configured `llama-cpp-python` setup should be single-digit seconds for short structured outputs like Router's JSON.

The most likely cause: **`llm.py` isn't using your CPU's cores.** `Llama()` defaults `n_threads` to a conservative value if you never set it explicitly. Check `app/core/llm.py`:

```python
# app/core/llm.py
import os
from llama_cpp import Llama
from app.config import settings

llm = Llama(
    model_path=settings.MODEL_PATH,
    n_ctx=2048,
    n_threads=os.cpu_count(),      # was likely missing or defaulting low
    n_batch=512,                    # speeds up prompt processing on long contexts
)
```

**Second cause, compounding it:** your OCR text (877 chars) plus everything appended to it is getting fed into *every single node's prompt* — Router, Rewriter, Reasoner, Extract_facts all reprocess that full context from scratch, with no KV-cache reuse between calls since each is an independent `llm()` invocation. Router and Rewriter don't need the full prescription text at all — they need the patient's actual question. Carrying 877 chars of OCR noise into a JSON-classification call is pure waste.

**Fix: stop concatenating OCR text into `raw_input`/`english_query` for every node.** Keep them separate in state, and only hand the OCR text to the node that actually needs it (Reasoner):

```python
# app/agent/state.py — add a field
class AgentState(TypedDict):
    # ...existing...
    ocr_context: str   # NEW — separate from the patient's actual question
```

```python
# app/agent/nodes/ocr_node.py — don't merge into raw_input anymore
def ocr_node(state: AgentState) -> AgentState:
    if not state.get("has_image"):
        return state
    extracted = extract_text_from_base64(state["image_base64"])
    state["ocr_context"] = extracted   # kept separate now
    return state
```

Router, Rewriter, and fact-fetch nodes then only see `state["english_query"]` (the patient's actual short question), not the prescription dump. Only `reasoner_node` pulls in `state.get("ocr_context", "")` alongside retrieved docs. This alone should cut most nodes' latency dramatically, since they're no longer reprocessing ~900 extra characters of context every time.

## Problem 2: the rewrite is actually wrong, not just slow

This is the more important bug. The patient typed **"what it mean"** — asking you to explain the prescription. The Rewriter turned that into **"what is the correct format for a medical prescription... "** — a completely different question (a template request), because it was reading the OCR'd prescription text as if it were part of the user's question rather than context attached alongside it.

That's exactly the failure mode created by mixing the two. Once you stop concatenating OCR text into `english_query` (fix above), the Rewriter will see just `"what it mean"` — which is still vague enough to need a better prompt. Update the Rewriter to explicitly know it may have attached document context, and to rewrite around the user's actual intent, not the document's contents:

```python
# app/agent/nodes/rewriter_node.py
REWRITER_PROMPT = """Rewrite the patient's message into a clear, specific
medical question. The patient may have attached a document (e.g. a
prescription) — if so, their question is usually asking you to explain,
verify, or advise on that document, not asking you to generate a new one.
Preserve their actual intent. Keep it to one sentence.

Attached document context (if any): {has_doc}

Recent conversation:
{memory}

Patient message: "{query}"

Rewritten query:"""

def query_rewriter_node(state: AgentState) -> AgentState:
    prompt = REWRITER_PROMPT.format(
        has_doc="Yes — a prescription/medical document was attached" if state.get("ocr_context") else "No",
        memory=_format_memory(state.get("recent_memory", [])),
        query=state["english_query"],
    )
    # ...unchanged...
```

For a message this short and vague ("what it mean"), you might also reasonably skip the Rewriter entirely when `ocr_context` is present and just pass "explain this prescription to the patient" as the query directly — worth testing which is more reliable.

## What I'd do next, in order

1. **Fix `n_threads`/`n_batch`** — retest one query, see how much latency drops. This alone might resolve most of the 9-minute problem.
2. **Separate `ocr_context` from `english_query`** — stops the Rewriter/Router from getting confused by document content.
3. **Re-test the exact same prescription image + "what it mean" query** and confirm the answer now actually explains the prescription rather than answering a template question.
4. Only after those three are confirmed working — move on to Week 6/7 additions. Building STT/TTS/TrOCR on top of a pipeline that takes 9 minutes and answers the wrong question would just compound the problem into something harder to debug later.

Want me to also check whether `extract_facts` taking 180s with no logged decision means it's silently failing validation and retrying, or if that's the same thread-count issue?

Assalam-o-Alaikum ! Hope you're doing well.

I recently launched a **Complete MLOps Course** on my YouTube channel, **AI Valley**. Since you're in the tech/AI space, I thought you might find it useful.

🎥 https://youtu.be/lZWA1KJcOLw

I'd really appreciate your feedback. If you find it valuable, please consider subscribing and sharing it with others who might benefit.

Jazaak ALLAH SWT!