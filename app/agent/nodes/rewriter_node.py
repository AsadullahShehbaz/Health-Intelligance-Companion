# app/agent/nodes/rewriter_node.py
from app.core.llm import llm
from app.agent.state import AgentState
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

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


def _format_memory(memory: list[dict]) -> str:
    if not memory:
        return "(no prior context)"
    return "\n".join(f"Q: {m['query']}\nA: {m['answer'][:150]}" for m in memory)


def query_rewriter_node(state: AgentState) -> AgentState:
    prompt = REWRITER_PROMPT.format(
        has_doc=(
            "Yes — a prescription/medical document was attached"
            if state.get("ocr_context")
            else "No"
        ),
        memory=_format_memory(state.get("recent_memory", [])),
        query=state["english_query"],
    )

    try:
        output = llm(prompt, max_tokens=80, temperature=0.3)
        rewritten = output["choices"][0]["text"].strip()
    except Exception:
        logger.exception("rewriter | LLM call failed; falling back to original query")
        rewritten = ""

    state["rewritten_query"] = rewritten if rewritten else state["english_query"]

    logger.info("rewriter | rewritten_query=%r", state["rewritten_query"])
    return state