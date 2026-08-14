# app/agent/nodes/agent_node.py
import json
import re

from llama_cpp import LlamaGrammar
from langchain_core.messages import AIMessage

from app.core.llm import llm, llm_lock
from app.agent.state import AgentState
from app.schemas.agent import ToolCall
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = ToolCall.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))
MAX_TOOL_CALLS = 4
MAX_ANSWER_TOKENS = 900

# Below this many characters, we treat the model's "answer" as effectively
# blank and try to recover real content instead of showing it to the user.
MIN_USABLE_ANSWER_CHARS = 5

_TOOL_DOCS = """
1. fetch_patient_facts(query: str) — check past symptoms/history
2. retrieve_medical_knowledge(query: str) — look up diagnosis/treatment facts
3. save_patient_fact(symptom, onset, status, source_message) — record a NEW symptom
4. save_emotional_state(emotion, intensity, trigger, source_message) — record expressed emotion
5. final_answer(answer) — respond when you have enough information
"""

SYSTEM_PROMPT = """You are an empathetic Pakistani AI health companion.

IMPORTANT RULES:
- If the patient's message is a greeting, small talk, thanks, a personal
  question (e.g. "what is my name"), or ANYTHING that is not a medical
  symptom or health question, use final_answer immediately with a short,
  direct, normal reply. Do NOT call any tools, do NOT use the
  Diagnosis/Medicines format, and do NOT tell them to see a doctor for
  these — that advice only belongs on real medical concerns.
- Never call the same tool with the same input more than once. Check
  "Tool results so far" below before picking an action — if it already
  answers what you need (even if it says "no relevant history found"),
  move on to final_answer or a DIFFERENT tool instead of repeating it.
- Only use fetch_patient_facts / retrieve_medical_knowledge when the
  patient describes an actual symptom or asks a medical question.
- The "answer" field in your JSON output is REQUIRED and must contain
  real, non-empty text on EVERY response — even when your action is a
  tool call, write a short one-line note there (e.g. "Checking history
  first"). Never leave it blank.

Reason briefly, then pick ONE action. Only call final_answer once you have
what you need.

For final_answer about a MEDICAL concern, format the response with:
**Diagnosis:** ...
**Confidence:** ...
**Medicines:** ...
**Diet:** ...
**Exercise:** ...
**When to see a doctor:** ...

For final_answer to anything else (greetings, personal questions, general
requests), just reply normally in plain text.

Tools:
{tool_docs}

Patient ID: {patient_id}
Query: {query}

Tool results so far:
{tool_results}

Respond with ONLY the JSON object."""


def _document_section(state: AgentState) -> str:
    text = state.get("ocr_context", "")
    if not text:
        return ""
    return (
        "Attached document (from the patient's photo):\n"
        f"{text[:1000]}\n\n"
        "The patient attached this medical document and wants it explained, "
        "verified, or advised on — answer questions about it directly."
    )


def _plain_answer_fallback(query: str, doc_section: str) -> str:
    """Recovery path: the JSON-constrained call produced a blank answer.

    Ask the model to just answer in plain text, no JSON, no grammar. This
    is a much easier generation task for a small model, so it reliably
    produces real content even when the structured call didn't.
    """
    prompt = (
        (doc_section + "\n\n" if doc_section else "")
        + "You are a helpful, empathetic health companion. Answer the "
        "patient's message directly and naturally in a few sentences.\n\n"
        f"Patient: {query}\n"
        "Answer:"
    )
    try:
        with llm_lock:
            llm.reset()
            output = llm(prompt, max_tokens=400, temperature=0.4, stop=["Patient:"])
        text = output["choices"][0]["text"].strip()
        return text
    except Exception:
        logger.exception("Plain-text answer fallback also failed")
        return ""


def agent_node(state: AgentState) -> AgentState:
    count = state.get("tool_call_count", 0)

    messages = state.get("messages", [])
    tool_msgs = []
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            if not getattr(m, "tool_calls", None):
                break
            continue
        if getattr(m, "type", None) == "tool":
            tool_msgs.append(m)
    tool_results = (
        "\n\n".join(f"Tool '{m.name}' returned:\n{m.content[:500]}" for m in reversed(tool_msgs))
        if tool_msgs else "(No tool results yet)"
    )
    state["tool_results"] = tool_results

    forced_final = count >= MAX_TOOL_CALLS

    prompt = SYSTEM_PROMPT.format(
        tool_docs=_TOOL_DOCS if not forced_final else "final_answer(answer) — you MUST use this now.",
        patient_id=state["patient_id"],
        query=state["raw_input"],
        tool_results=tool_results,
    )
    doc_section = _document_section(state)
    if doc_section:
        prompt = doc_section + "\n\n" + prompt

    with llm_lock:
        llm.reset()
        output = llm(prompt, grammar=_GRAMMAR, max_tokens=MAX_ANSWER_TOKENS, temperature=0.3)

    raw = output["choices"][0]["text"]
    finish_reason = output["choices"][0].get("finish_reason")

    try:
        decision = ToolCall.model_validate_json(raw)
        if forced_final:
            decision.action = "final_answer"
    except Exception:
        logger.exception(f"Agent validation failed | finish_reason={finish_reason} | raw={raw!r}")
        decision = ToolCall(
            thought="Fallback.", action="final_answer", answer="",
        )

    if decision.action == "final_answer":
        answer_text = (decision.answer or "").strip()

        # THE ACTUAL FIX: instead of silently swapping in a misleading
        # "see a doctor" message whenever the JSON-constrained call left
        # answer blank/too short, try ONE plain-text generation to get a
        # real, relevant reply first.
        if len(answer_text) < MIN_USABLE_ANSWER_CHARS:
            logger.warning(
                "final_answer had a blank/too-short answer (%r) — retrying with plain completion",
                answer_text,
            )
            recovered = _plain_answer_fallback(state["raw_input"], doc_section)
            if len(recovered) >= MIN_USABLE_ANSWER_CHARS:
                answer_text = recovered
            else:
                # Both attempts failed to produce real content — be honest
                # about it instead of giving unrelated medical advice.
                answer_text = (
                    "I'm sorry, I wasn't able to generate a proper response "
                    "to that. Could you try rephrasing your message?"
                )

        state["answer"] = answer_text
        state["final_response"] = answer_text
        new_message = AIMessage(content=answer_text)
    else:
        args = dict(decision.action_input or {})
        args.setdefault("patient_id", state["patient_id"])
        if decision.action in ("save_patient_fact", "save_emotional_state"):
            args.setdefault("source_message", state["raw_input"])
        elif decision.action in ("retrieve_medical_knowledge", "fetch_patient_facts"):
            args.setdefault("query", state["raw_input"])
        new_message = AIMessage(
            content=decision.thought,
            tool_calls=[{"id": f"tc_{count}", "name": decision.action, "args": args}],
        )
        state["tool_call_count"] = count + 1

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

    state["saved_memory"] = any(
        getattr(m, "name", "") in ("save_patient_fact", "save_emotional_state")
        for m in tool_msgs
    )

    state["messages"] = [new_message]
    return state