# app/agent/nodes/router_node.py
import json
from llama_cpp import LlamaGrammar

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import RouterDecision
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compile the Pydantic model's JSON schema directly into a llama.cpp
# grammar. This is the actual link between "Pydantic" and "Structured
# Output" in your stack — the model is physically unable to emit
# anything that doesn't validate against RouterDecision.
_SCHEMA = RouterDecision.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))

ROUTER_PROMPT = """You are a routing assistant for a medical Q&A system.
Given the user's message, decide:
- needs_rag: true if this is a medical question needing factual lookup, false for greetings/small talk/non-medical chat
- save_memory: true if this message contains meaningful health info worth remembering, false for small talk

Examples:
User: "hello, how are you"
{{"needs_rag": false, "save_memory": false}}

User: "I have had a fever and body pain for two days"
{{"needs_rag": true, "save_memory": true}}

User: "what's the weather like today"
{{"needs_rag": false, "save_memory": false}}

User: "I feel dizzy"
{{"needs_rag": true, "save_memory": true}}

User: "is this the same headache as last time"
{{"needs_rag": true, "save_memory": true}}

User: "thank you, that helps"
{{"needs_rag": false, "save_memory": false}}

Now classify this message:
User: "{query}"
Respond with ONLY the JSON object."""


def router_node(state: AgentState) -> AgentState:
    output = llm(
        ROUTER_PROMPT.format(query=state["english_query"]),
        grammar=_GRAMMAR,
        max_tokens=50,
        temperature=0.1,
    )
    raw = output["choices"][0]["text"]

    try:
        decision = RouterDecision.model_validate_json(raw)
    except Exception:
        logger.exception(f"Router output failed validation: {raw!r} — defaulting to safe fallback")
        decision = RouterDecision(needs_rag=True, save_memory=True)  # fail safe, not silent

    state["needs_rag"] = decision.needs_rag
    state["save_memory"] = decision.save_memory

    logger.info(
        "router | decision | needs_rag=%s | save_memory=%s",
        decision.needs_rag,
        decision.save_memory,
    )
    return state