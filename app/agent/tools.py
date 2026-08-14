# app/agent/tools.py
import re
import uuid
from datetime import date

from langchain_core.tools import tool

from app.db.lifespan import store
from app.core.rag.rag_tool import perform_direct_rag
from app.core.rag.corrective_rag import web_search_fallback
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def _normalize_field_key(field: str) -> str:
    """Turn any free-text field label into a stable storage key.
    'Emergency Contact', 'emergency  contact' -> 'emergency_contact'.
    Kept intentionally permissive — this store is NOT limited to a
    fixed set of fields; any identity/background fact is allowed.
    """
    key = field.strip().lower()
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    return key or "unlabeled_fact"


@tool
def fetch_patient_facts(patient_id: str, query: str) -> str:
    """Retrieve relevant MEDICAL/symptom history about a patient from persistent
    memory (e.g. past complaints, onset dates, resolved conditions).
    Do NOT use this for identity/background questions (name, age, occupation,
    etc.) — use fetch_patient_profile for that."""
    logger.info("▶ fetch_patient_facts | patient=%s | query=%s", patient_id, query[:80])
    if store is None:
        logger.warning("Memory store not available for fetch_patient_facts")
        return "Memory store not available."
    try:
        items = store.search(("patient_facts", patient_id), query=query, limit=5)
        facts = [item.value for item in items]
        if not facts:
            logger.info("No patient history found | patient=%s", patient_id)
            return "No relevant patient history found."

        lines = []
        for f in facts:
            if not isinstance(f, dict) or "symptom" not in f:
                logger.warning(
                    "Skipping malformed patient_facts record | patient=%s | record=%s",
                    patient_id, f,
                )
                continue
            lines.append(
                f"- {f['symptom']} (onset: {f.get('onset', 'unknown')}, "
                f"status: {f.get('status', 'unknown')})"
            )

        if not lines:
            return "No relevant patient history found."

        logger.info("✓ Fetched %d patient facts | patient=%s", len(lines), patient_id)
        return "Known patient history:\n" + "\n".join(lines)
    except Exception as e:
        logger.exception("fetch_patient_facts failed")
        return f"Error retrieving patient facts: {e}"


@tool
def fetch_patient_profile(patient_id: str) -> str:
    """Retrieve ALL saved identity/background details about the patient — name,
    age, occupation, family info, emergency contact, preferences, or anything
    else previously stated. Use this for any question about the patient's own
    non-medical personal details. Returns everything on file, not a fixed
    field list, so it reflects however much or little has actually been saved."""
    logger.info("▶ fetch_patient_profile | patient=%s", patient_id)
    if store is None:
        logger.warning("Memory store not available for fetch_patient_profile")
        return "Memory store not available."
    try:
        # No query = return everything under this namespace, not a
        # semantic-similarity subset. This is a profile, not a search index.
        items = store.search(("patient_profile", patient_id), limit=100)
        if not items:
            logger.info("No profile data found | patient=%s", patient_id)
            return "No profile information saved for this patient yet."

        lines = []
        for item in items:
            v = item.value
            if not isinstance(v, dict) or "value" not in v:
                continue
            lines.append(f"- {item.key}: {v['value']}")

        if not lines:
            return "No profile information saved for this patient yet."

        logger.info("✓ Fetched %d patient profile fields | patient=%s", len(lines), patient_id)
        return "Known patient profile:\n" + "\n".join(lines)
    except Exception as e:
        logger.exception("fetch_patient_profile failed")
        return f"Error retrieving patient profile: {e}"


@tool
def save_patient_profile(patient_id: str, field: str, value: str, source_message: str) -> str:
    """Save or update ANY identity/background fact the patient states about
    themselves — name, age, gender, occupation, city, family details,
    emergency contact, allergies to non-medical things, preferences, etc.
    field is a free-text label (e.g. 'name', 'occupation', 'emergency contact')
    — it is NOT restricted to a fixed list. Call this once per distinct fact
    stated. Saving the same field again overwrites the previous value."""
    logger.info(
        "▶ save_patient_profile | patient=%s | field=%s | value=%s",
        patient_id, field, value,
    )
    if store is None:
        logger.warning("Memory store not available for save_patient_profile")
        return "Memory store not available."

    if not field.strip() or not value.strip():
        return "Both field and value are required to save a profile fact."

    normalized_key = _normalize_field_key(field)

    try:
        store.put(("patient_profile", patient_id), normalized_key, {
            "label": field.strip(),
            "value": value.strip(),
            "recorded_on": date.today().isoformat(),
            "source_message": source_message,
        })
        logger.info("✓ Saved patient profile field | patient=%s | key=%s", patient_id, normalized_key)
        return f"Saved to patient profile: {field.strip()} = {value.strip()}"
    except Exception as e:
        logger.exception("save_patient_profile failed")
        return f"Error saving profile field: {e}"


@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieves relevant medical guidelines, clinical notes, or local health docs from the vector database."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    try:
        docs = perform_direct_rag(query, top_k=5)
        if not docs:
            return "No relevant internal medical documents found."
        logger.info("✓ retrieve_medical_knowledge returned %d docs", len(docs))
        lines = [f"[{d.get('source', 'Medical Knowledge')}]: {d.get('text', '')[:400]}" for d in docs]
        return "Internal Medical Knowledge Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}"


@tool
def save_patient_fact(patient_id: str, symptom: str, onset: str, status: str, source_message: str) -> str:
    """Save a newly reported MEDICAL SYMPTOM to the patient's persistent record.
    Do NOT use this for identity/background info — use save_patient_profile."""
    logger.info(
        "▶ save_patient_fact | patient=%s | symptom=%s | status=%s",
        patient_id, symptom, status,
    )
    if store is None:
        logger.warning("Memory store not available for save_patient_fact")
        return "Memory store not available."
    key = f"{symptom}_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_facts", patient_id), key, {
            "symptom": symptom, "onset": onset, "status": status,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        logger.info("✓ Saved patient fact | patient=%s | key=%s", patient_id, key)
        return f"Saved to patient record: {symptom} ({status})"
    except Exception as e:
        logger.exception("save_patient_fact failed")
        return f"Error saving fact: {e}"


@tool
def save_emotional_state(patient_id: str, emotion: str, intensity: str, trigger: str, source_message: str) -> str:
    """Save the patient's emotional state when they express anxiety, stress, or fear."""
    logger.info(
        "▶ save_emotional_state | patient=%s | emotion=%s | intensity=%s",
        patient_id, emotion, intensity,
    )
    if store is None:
        logger.warning("Memory store not available for save_emotional_state")
        return "Memory store not available."
    key = f"emotion_{date.today().isoformat()}_{uuid.uuid4().hex[:4]}"
    try:
        store.put(("patient_emotions", patient_id), key, {
            "emotion": emotion, "intensity": intensity, "trigger": trigger,
            "recorded_on": date.today().isoformat(), "source_message": source_message,
        })
        logger.info("✓ Saved emotional state | patient=%s | key=%s", patient_id, key)
        return f"Noted emotional state: {emotion} ({intensity})"
    except Exception as e:
        logger.exception("save_emotional_state failed")
        return f"Error saving emotion: {e}"


@tool
def search_web_medical(query: str) -> str:
    """Searches the web via SerpAPI for current health information or external guidelines."""
    logger.info("▶ search_web_medical | query=%s", query[:80])
    try:
        results = web_search_fallback(query)
        if not results:
            return "No web search results found."
        lines = [f"[{r.get('title', 'Web Source')}]: {r.get('text', '')}" for r in results[:3]]
        return "Web Search Results:\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("search_web_medical failed")
        return f"Error executing web search: {e}"


TOOLS = [
    fetch_patient_facts,
    fetch_patient_profile,
    save_patient_profile,
    retrieve_medical_knowledge,
    save_patient_fact,
    save_emotional_state,
    search_web_medical,
]