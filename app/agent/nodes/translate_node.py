# app/agent/nodes/translate_node.py
from app.agent.state import AgentState
from app.core.rag.translation import detect_language, to_english, from_english
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def translate_in_node(state: AgentState) -> AgentState:
    lang = detect_language(state["raw_input"])
    state["detected_lang"] = lang
    state["english_query"] = to_english(state["raw_input"], lang)

    logger.info(
        "translate_in | detected_lang=%s | english_query_len=%d",
        lang,
        len(state["english_query"]),
    )
    return state


def translate_out_node(state: AgentState) -> AgentState:
    if state["detected_lang"] == "en":
        state["final_response"] = state["answer"]
    else:
        state["final_response"] = from_english(state["answer"], state["detected_lang"])

    logger.info(
        "translate_out | target_lang=%s | answer_len=%d -> response_len=%d",
        state["detected_lang"],
        len(state.get("answer", "")),
        len(state["final_response"]),
    )
    return state