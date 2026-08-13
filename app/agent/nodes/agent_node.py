# app/agent/nodes/agent_node.py
import json
import re
import time

from llama_cpp import LlamaGrammar
from langchain_core.messages import AIMessage

from app.agent.prompt import SYSTEM_PROMPT  
from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import ToolCall
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_SCHEMA = ToolCall.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))
MAX_TOOL_CALLS = 4   # hard cap — prevents an unbounded agent<->tools loop

_TOOL_DOCS = """
1. fetch_patient_facts(query: str)
   Use when previous patient history is relevant to the current question.

2. retrieve_medical_knowledge(query: str)
   Use when reliable medical knowledge is needed to answer the question.

3. save_patient_fact(symptom, onset, status, source_message)
   Use only when the patient shares a new useful health fact that should be remembered.

4. save_emotional_state(emotion, intensity, trigger, source_message)
   Use only when the patient clearly expresses an emotional state worth remembering.

5. final_answer(answer)
   Use when you can respond directly to the patient.
"""

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

    logger.info(
        "Agent started | tool calls used: %d/%d",
        count,
        MAX_TOOL_CALLS,
    )

    # Build tool_results from message history.
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
        "\n\n".join(
            f"Tool '{m.name}' returned:\n{m.content[:500]}"
            for m in reversed(tool_msgs)
        )
        if tool_msgs
        else "(No tool results yet)"
    )

    state["tool_results"] = tool_results

    # Force a final answer once the loop budget is exhausted.
    forced_final = count >= MAX_TOOL_CALLS

    prompt = SYSTEM_PROMPT.format(
        tool_docs=(
            _TOOL_DOCS
            if not forced_final
            else "final_answer(answer) — you MUST use this now."
        ),
        patient_id=state["patient_id"],
        query=state["raw_input"],
        tool_results=tool_results,
    )

    doc_section = _document_section(state)

    if doc_section:
        prompt = doc_section + "\n\n" + prompt
        logger.info("Agent received OCR document context")

    # ---------------------------------------------------------
    # LLM GENERATION
    # ---------------------------------------------------------
    logger.info("Agent LLM generation started")

    start_time = time.monotonic()

    try:
        output = llm(
            prompt,
            grammar=_GRAMMAR,
            max_tokens=500,
            temperature=0.3,
        )

    except Exception:
        logger.exception("Agent LLM generation failed")
        raise

    elapsed = time.monotonic() - start_time

    raw = output["choices"][0]["text"]

    # llama.cpp usually provides token usage in the completion response.
    usage = output.get("usage", {})
    completion_tokens = usage.get("completion_tokens")

    if completion_tokens:
        tokens_per_second = completion_tokens / elapsed if elapsed > 0 else 0

        logger.info(
            "Agent LLM finished in %.2fs | tokens: %d | speed: %.2f tokens/sec",
            elapsed,
            completion_tokens,
            tokens_per_second,
        )
    else:
        # Fallback when token usage is not available.
        logger.info(
            "Agent LLM finished in %.2fs | token count unavailable",
            elapsed,
        )

    # ---------------------------------------------------------
    # PARSE MODEL DECISION
    # ---------------------------------------------------------
    try:
        decision = ToolCall.model_validate_json(raw)

        if forced_final:
            decision.action = "final_answer"

            if not decision.answer:
                decision.answer = (
                    "Sorry, I couldn't quite process that — could you tell me "
                    "a bit more about what's going on, or rephrase your message?"
                )

    except Exception:
        logger.exception("Agent validation failed")

        decision = ToolCall(
            thought="Fallback.",
            action="final_answer",
            answer=(
                "I apologize, I encountered an issue. "
                "Please consult a doctor for urgent concerns."
            ),
        )

    logger.info("Agent selected action: %s", decision.action)

    # ---------------------------------------------------------
    # HANDLE FINAL ANSWER / TOOL CALL
    # ---------------------------------------------------------
    if decision.action == "final_answer":

        answer_text = decision.answer or (
            "Based on what you've shared, please consult a doctor "
            "for a full evaluation."
        )

        state["answer"] = answer_text
        state["final_response"] = answer_text

        new_message = AIMessage(content=answer_text)

    else:

        args = dict(decision.action_input or {})
        args.setdefault("patient_id", state["patient_id"])

        if decision.action in (
            "save_patient_fact",
            "save_emotional_state",
        ):
            args.setdefault("source_message", state["raw_input"])

        elif decision.action in (
            "retrieve_medical_knowledge",
            "fetch_patient_facts",
        ):
            args.setdefault("query", state["raw_input"])

        new_message = AIMessage(
            content=decision.thought,
            tool_calls=[
                {
                    "id": f"tc_{count}",
                    "name": decision.action,
                    "args": args,
                }
            ],
        )

        state["tool_call_count"] = count + 1

    # ---------------------------------------------------------
    # RAG / MEMORY STATUS
    # ---------------------------------------------------------
    rag_used = any(
        getattr(m, "name", "") == "retrieve_medical_knowledge"
        for m in tool_msgs
    )

    state["needs_rag"] = rag_used

    decision_text = ""
    sources: list[str] = []

    for m in tool_msgs:

        if getattr(m, "name", "") != "retrieve_medical_knowledge":
            continue

        for line in (m.content or "").splitlines():

            if "Retrieval decision" in line:

                match = re.search(
                    r"Retrieval decision:\s*([A-Za-z]+)",
                    line,
                )

                if match:
                    decision_text = match.group(1)

            else:

                match = re.match(
                    r"^\s*\[([^\]]+)\]",
                    line,
                )

                if match:
                    sources.append(match.group(1))

    state["retrieval_decision"] = (
        decision_text
        or ("retrieved" if rag_used else "")
    )

    state["retrieved_docs"] = [
        {"source": s}
        for s in sources[:3]
    ]

    state["saved_memory"] = any(
        getattr(m, "name", "") in (
            "save_patient_fact",
            "save_emotional_state",
        )
        for m in tool_msgs
    )

    state["messages"] = [new_message]

    return state