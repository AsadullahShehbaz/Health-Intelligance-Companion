# app/agent/nodes/reasoner_node.py
from app.core.llm import llm
from app.agent.state import AgentState
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _format_context(docs: list[dict]) -> str:
    if not docs:
        return ""
    return "\n\n".join(f"[{d['source']}] {d['text'][:300]}" for d in docs[:3])


def _format_facts(facts: list[dict]) -> str:
    if not facts:
        return ""
    lines = [f"- {f['symptom']} (onset: {f['onset']}, status: {f['status']})" for f in facts]
    return "Known patient history:\n" + "\n".join(lines)


def _format_ocr(text: str) -> str:
    if not text:
        return ""
    # The patient's photo is the primary subject — give it room without
    # letting a big scan crowd out the retrieved context.
    return f"Attached document (from the patient's photo):\n{text[:1000]}"


def reasoner_node(state: AgentState) -> AgentState:
    query = state.get("rewritten_query") or state["english_query"]

    parts = []
    facts_block = _format_facts(state.get("patient_facts", []))
    if facts_block:
        parts.append(facts_block)

    if state.get("needs_rag"):
        context_block = _format_context(state.get("retrieved_docs", []))
        if context_block:
            parts.append(f"Relevant medical context:\n{context_block}")

    ocr_block = _format_ocr(state.get("ocr_context", ""))
    if ocr_block:
        parts.append(ocr_block)

    parts.append(f"Question: {query}\nAnswer:")
    prompt = "\n\n".join(parts)

    response = llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=400,
        stream=False,
    )
    state["answer"] = response["choices"][0]["message"]["content"].strip()

    logger.info(
        "reasoner | needs_rag=%s | docs=%d | facts=%d | answer_len=%d",
        state.get("needs_rag"),
        len(state.get("retrieved_docs", [])),
        len(state.get("patient_facts", [])),
        len(state["answer"]),
    )
    return state