# app/agent/nodes/translate_node.py
from app.agent.state import AgentState
from app.core.rag.translation import detect_language, to_english, from_english


def translate_in_node(state: AgentState) -> AgentState:
    lang = detect_language(state["raw_input"])
    state["detected_lang"] = lang
    state["english_query"] = to_english(state["raw_input"], lang)
    return state


def translate_out_node(state: AgentState) -> AgentState:
    if state["detected_lang"] == "en":
        state["final_response"] = state["answer"]
    else:
        state["final_response"] = from_english(state["answer"], state["detected_lang"])
    return state