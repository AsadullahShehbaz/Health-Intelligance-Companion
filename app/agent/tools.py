# app/agent/tools.py
import uuid
from datetime import date

from langchain_core.tools import tool

from app.db.lifespan import store
from app.core.rag.corrective_rag import corrective_retrieve
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


@tool
def fetch_patient_facts(patient_id: str, query: str) -> str:
    """Retrieve relevant medical facts about a patient from persistent memory.
    Use when the patient refers to past symptoms or history."""
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
        logger.info("✓ Fetched %d patient facts | patient=%s", len(facts), patient_id)
        lines = [f"- {f['symptom']} (onset: {f['onset']}, status: {f['status']})" for f in facts]
        return "Known patient history:\n" + "\n".join(lines)
    except Exception as e:
        logger.exception("fetch_patient_facts failed")
        return f"Error retrieving patient facts: {e}"


@tool
def retrieve_medical_knowledge(query: str) -> str:
    """Retrieve evidence-based medical knowledge for diagnosis or treatment questions."""
    logger.info("▶ retrieve_medical_knowledge | query=%s", query[:80])
    try:
        result = corrective_retrieve(query, top_k=5)
        docs = result["docs"]
        if not docs:
            logger.info("No documents found | decision=%s", result["decision"])
            return f"[Retrieval decision: {result['decision']}] No relevant documents found."
        logger.info(
            "✓ retrieve_medical_knowledge returned %d docs | decision=%s",
            len(docs),
            result["decision"],
        )
        lines = [f"[{d['source']}] {d['text'][:400]}" for d in docs[:3]]
        return f"[Retrieval decision: {result['decision']}]\n\n" + "\n\n".join(lines)
    except Exception as e:
        logger.exception("retrieve_medical_knowledge failed")
        return f"Error retrieving knowledge: {e}"


@tool
def save_patient_fact(patient_id: str, symptom: str, onset: str, status: str, source_message: str) -> str:
    """Save a newly reported symptom to the patient's persistent record."""
    logger.info(
        "▶ save_patient_fact | patient=%s | symptom=%s | status=%s",
        patient_id,
        symptom,
        status,
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
        patient_id,
        emotion,
        intensity,
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


TOOLS = [fetch_patient_facts, retrieve_medical_knowledge, save_patient_fact, save_emotional_state]