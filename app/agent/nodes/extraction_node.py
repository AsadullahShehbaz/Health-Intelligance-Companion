# app/agent/nodes/extraction_node.py
import json
from datetime import date
from llama_cpp import LlamaGrammar

from app.core.llm import llm
from app.agent.state import AgentState
from app.schemas.agent import SymptomFact
from app.db.store import store
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Compile the Pydantic model's JSON schema directly into a llama.cpp
# grammar, exactly like the Router Agent does. The model is physically
# unable to emit anything that doesn't validate against SymptomFact.
_SCHEMA = SymptomFact.model_json_schema()
_GRAMMAR = LlamaGrammar.from_json_schema(json.dumps(_SCHEMA))

EXTRACTION_PROMPT = """Extract any symptom or medical fact from this message.
If none is mentioned, set has_fact to false.

Examples:
User: "I have had a fever since yesterday"
{{"has_fact": true, "symptom": "fever", "onset": "yesterday", "status": "ongoing"}}

User: "hello, how are you"
{{"has_fact": false, "symptom": null, "onset": null, "status": null}}

User: "my headache from last week is finally gone"
{{"has_fact": true, "symptom": "headache", "onset": "last week", "status": "resolved"}}

Now extract from this message:
User: "{query}"
Respond with ONLY the JSON object."""


def extraction_node(state: AgentState) -> AgentState:
    if not state.get("save_memory"):
        return state  # router already decided this turn isn't worth remembering

    output = llm(
        EXTRACTION_PROMPT.format(query=state["english_query"]),
        grammar=_GRAMMAR,
        max_tokens=80,
        temperature=0.1,
    )
    raw = output["choices"][0]["text"]

    try:
        fact = SymptomFact.model_validate_json(raw)
    except Exception:
        logger.exception(f"Extraction output failed validation: {raw!r}")
        return state

    if not fact.has_fact:
        return state

    # Namespace by ("patient_facts", patient_id) so every fact for a patient
    # lives under one queryable bucket, independent of conversation turns.
    # This is what makes "fever a week ago" survive regardless of how many
    # unrelated chats happened since.
    namespace = ("patient_facts", state["patient_id"])
    key = f"{fact.symptom}_{date.today().isoformat()}"
    store.put(namespace, key, {
        "symptom": fact.symptom,
        "onset": fact.onset,
        "status": fact.status,
        "recorded_on": date.today().isoformat(),
        "source_message": state["english_query"],
    })

    return state