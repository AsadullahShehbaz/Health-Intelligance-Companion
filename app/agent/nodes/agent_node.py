# app/agent/nodes/agent_node.py
import json
import re

from llama_cpp import LlamaGrammar
from langchain_core.messages import AIMessage

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import ToolCall
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = ToolCall.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))
MAX_TOOL_CALLS = 4   # hard cap — prevents an unbounded agent<->tools loop

_TOOL_DOCS = """
1. fetch_patient_facts(query: str) — check past symptoms/history
2. retrieve_medical_knowledge(query: str) — look up diagnosis/treatment facts
3. save_patient_fact(symptom, onset, status, source_message) — record a NEW symptom
4. save_emotional_state(emotion, intensity, trigger, source_message) — record expressed emotion
5. final_answer(answer) — respond when you have enough information
"""

SYSTEM_PROMPT = """You are an empathetic Pakistani AI health companion.
Reason briefly, then pick ONE action. Use tools before diagnosing. Only
call final_answer once you have what you need.

For final_answer, format the response with:
**Diagnosis:** ...
**Confidence:** ...
**Medicines:** ...
**Diet:** ...
**Exercise:** ...
**When to see a doctor:** ...

Tools:
{tool_docs}

Patient ID: {patient_id}
Query: {query}

Tool results so far:
{tool_results}

Respond with ONLY the JSON object."""


def _document_section(state: AgentState) -> str:
    """OCR'd document text, fed to the agent so the patient's photo is the
    subject of the answer rather than inert. Empty when no image was attached."""
    text = state.get("ocr_context", "")
    if not text:
        return ""
    return (
        "Attached document (from the patient's photo):\n"
        f"{text[:1000]}\n\n"
        "The patient attached this medical document and wants it explained, "
        "verified, or advised on — answer questions about it directly."
    )


def agent_node(state: AgentState) -> AgentState:
    count = state.get("tool_call_count", 0)

    # build tool_results from message history (replaces a separate post_tool node).
    messages = state.get("messages", [])
    tool_msgs = []
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            if not getattr(m, "tool_calls", None):
                break  # previous turn's final answer → this turn starts after it
            continue  # this turn's tool-call announcement → keep scanning older
        if getattr(m, "type", None) == "tool":
            tool_msgs.append(m)
    tool_results = (
        "\n\n".join(f"Tool '{m.name}' returned:\n{m.content[:500]}" for m in reversed(tool_msgs))
        if tool_msgs else "(No tool results yet)"
    )
    state["tool_results"] = tool_results

    # force a final answer once the loop budget is exhausted
    forced_final = count >= MAX_TOOL_CALLS

    # Phase 2: no more translation node, so we reason directly on raw_input
    # (the user's original text, whatever language it's in).
    prompt = SYSTEM_PROMPT.format(
        tool_docs=_TOOL_DOCS if not forced_final else "final_answer(answer) — you MUST use this now.",
        patient_id=state["patient_id"],
        query=state["raw_input"],
        tool_results=tool_results,
    )
    doc_section = _document_section(state)
    if doc_section:
        prompt = doc_section + "\n\n" + prompt

    output = llm(prompt, grammar=_GRAMMAR, max_tokens=500, temperature=0.3)
    raw = output["choices"][0]["text"]

    try:
        decision = ToolCall.model_validate_json(raw)
        if forced_final:
            decision.action = "final_answer"
            decision.answer = decision.answer or "Based on what you've shared, please consult a doctor for a full evaluation."
    except Exception:
        logger.exception(f"Agent validation failed: {raw!r}")
        decision = ToolCall(
            thought="Fallback.", action="final_answer",
            answer="I apologize, I encountered an issue. Please consult a doctor for urgent concerns.",
        )

    if decision.action == "final_answer":
        answer_text = decision.answer or (
            "Based on what you've shared, please consult a doctor for a full evaluation."
        )
        # translate_out_node is gone (Phase 2), so this node must write
        # final_response itself now — the sidebar's turn-end filter in
        # conversation_service.py keys on final_response being non-empty.
        state["answer"] = answer_text
        state["final_response"] = answer_text
        new_message = AIMessage(content=answer_text)
    else:
        args = dict(decision.action_input or {})
        args.setdefault("patient_id", state["patient_id"])
        if decision.action in ("save_patient_fact", "save_emotional_state"):
            args.setdefault("source_message", state["raw_input"])
        elif decision.action in ("retrieve_medical_knowledge", "fetch_patient_facts"):
            # The 7B grammar output sometimes drops the query field entirely
            # (empty action_input) — fall back to the user's own question.
            args.setdefault("query", state["raw_input"])
        new_message = AIMessage(
            content=decision.thought,
            tool_calls=[{"id": f"tc_{count}", "name": decision.action, "args": args}],
        )
        state["tool_call_count"] = count + 1

    # RAG status for the sidebar meta chips + /agent/invoke response
    rag_used = any(
        getattr(m, "name", "") == "retrieve_medical_knowledge" for m in tool_msgs
    )
    state["needs_rag"] = rag_used
    decision_text = ""
    sources: list[str] = []
    for m in tool_msgs:
        if getattr(m, "name", "") != "retrieve_medical_knowledge":
            continue
        for line in (m.content or "").splitlines():
            if "Retrieval decision" in line:
                match = re.search(r"Retrieval decision:\s*([A-Za-z]+)", line)
                if match:
                    decision_text = match.group(1)
            else:
                match = re.match(r"^\s*\[([^\]]+)\]", line)
                if match:
                    sources.append(match.group(1))
    state["retrieval_decision"] = decision_text or ("retrieved" if rag_used else "")
    state["retrieved_docs"] = [{"source": s} for s in sources[:3]]

    # Per-turn memory flag, consumed by agent_service's AgentResponse.
    state["saved_memory"] = any(
        getattr(m, "name", "") in ("save_patient_fact", "save_emotional_state")
        for m in tool_msgs
    )

    state["messages"] = [new_message]
    return state