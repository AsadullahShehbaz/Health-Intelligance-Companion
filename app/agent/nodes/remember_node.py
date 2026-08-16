# app/agent/nodes/remember_node.py
"""Node 1 — Remember.

Runs before RAG/routing on every turn. Loads existing patient memories from
the Postgres store, asks gpt-oss-120b (via Groq, structured output) to
extract atomic facts from the user's latest message and flag which are
genuinely new, then writes only the new ones back to the store.

Memories are now category-tagged (identity, symptom, medication, etc.) so
downstream BioMistral can reason over structured patient history rather than
an undifferentiated bullet list.
"""
import time
import uuid

from langchain_core.messages import SystemMessage

from app.agent.memory_schema import MemoryCategory, MemoryDecision, MemoryItem
from app.agent.state import AgentState
from app.config import settings
from app.db.lifespan import store
from app.db.pool import run_with_retry
from app.utils.logging_config import get_logger
from langchain_groq import ChatGroq

logger = get_logger(__name__)

# Same model as the router — gpt-oss-120b via Groq, per the architecture
# diagram. Kept as a separate instance (not router_llm) because this one
# uses structured output, not tool-calling.
_memory_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,   # "openai/gpt-oss-120b"
    temperature=0.0,
).with_structured_output(MemoryDecision)

MEMORY_NAMESPACE = "patient_memories"  # store namespace segment

# ── helpers ──────────────────────────────────────────────────────────────────


def _namespace(patient_id: str) -> tuple:
    return (MEMORY_NAMESPACE, patient_id)


def _load_existing_memories(patient_id: str) -> list[dict]:
    """Return every stored memory for *patient_id* as a list of dicts.

    Each dict contains the full MemoryItem fields (text, category, status,
    severity, onset) so we can format them into categorized sections
    downstream.  Returns an empty list on any DB error.
    """
    try:
        items = run_with_retry(store.search, _namespace(patient_id), limit=200)
    except Exception:
        logger.exception("Failed to load existing memories | patient=%s", patient_id)
        return []
    memories: list[dict] = []
    for item in items:
        data = item.value.get("data")
        if not data:
            continue
        # data is a dict of the MemoryItem fields; keep it as-is.
        if isinstance(data, dict):
            memories.append(data)
        else:
            # Back-compat: old flat-string memories (no category field)
            # are promoted to "identity" / "active".
            memories.append({"text": str(data), "category": "identity", "status": "active"})
    return memories


def _format_existing(memories: list[dict]) -> str:
    """Format a list of memory dicts into categorized sections.

    Active facts are grouped under their category heading. Resolved/historical
    facts appear in a short tail section.  This is the block consumed by both
    the Remember extraction prompt and BioMistral's diagnostic prompt.
    """
    if not memories:
        return "(empty)"

    from collections import OrderedDict

    # Bucket by (category, status) — active facts first.
    buckets: dict[tuple[str, str], list[str]] = OrderedDict()
    for cat in MemoryCategory:
        buckets[(cat.value, "active")] = []

    lines: list[str] = []
    for mem in memories:
        cat = mem.get("category", "identity")
        status = mem.get("status", "active")
        text = mem.get("text", "")
        extras = _detail_suffix(mem)
        entry = f"{text}{extras}"
        if status == "active":
            buckets.setdefault((cat, "active"), []).append(entry)
        else:
            buckets.setdefault((cat, status), []).append(entry)

    # Render active sections first
    label_map = {
        "identity": "IDENTITY",
        "symptom": "ACTIVE SYMPTOMS",
        "medication": "MEDICATIONS",
        "lab_result": "LAB RESULTS",
        "lifestyle": "LIFESTYLE",
        "emotional": "EMOTIONAL STATE",
    }
    for cat in MemoryCategory:
        entries = buckets.get((cat.value, "active"), [])
        if entries:
            lines.append(f"{label_map[cat.value]}: {'; '.join(entries)}")

    # Resolved / historical tail
    resolved = []
    for key, entries in buckets.items():
        _, status = key
        if status != "active" and entries:
            resolved.extend(entries)
    if resolved:
        lines.append(f"RESOLVED HISTORY: {'; '.join(resolved)}")

    return "\n".join(lines) if lines else "(empty)"


def _detail_suffix(mem: dict) -> str:
    """Append severity/onset info in parens if present."""
    parts: list[str] = []
    if mem.get("onset"):
        parts.append(mem["onset"])
    if mem.get("severity"):
        parts.append(mem["severity"])
    if not parts:
        return ""
    return f" ({', '.join(parts)})"


def _mem_to_store_dict(mem: MemoryItem) -> dict:
    """Serialize a MemoryItem into the dict persisted by store.put."""
    return {
        "text": mem.text,
        "category": mem.category.value,
        "status": mem.status,
        "severity": mem.severity,
        "onset": mem.onset,
    }


# ── prompt ───────────────────────────────────────────────────────────────────

REMEMBER_SYSTEM_PROMPT = """You are responsible for updating and maintaining accurate patient memory
for a healthcare companion system.

CURRENT PATIENT DETAILS (existing memories):
{existing_memories}

TASK:
- Review the patient's latest message.
- Extract patient-specific info worth storing long-term. For EACH item, pick
  the most appropriate category:
    identity       — name, age, occupation, city, family, emergency contact
    symptom       — medical complaints (headache, fever, pain, etc.)
    medication    — current or past drugs, dosage, frequency
    lab_result     — test values, blood work, imaging findings
    lifestyle      — diet, exercise, sleep, habits (smoking, alcohol)
    emotional      — mood, stress, anxiety, depression
- Set status to "active" for things that are currently true.
  Set "resolved" if the patient says a prior symptom/condition is gone or a
  medication was stopped.
  Set "historical" for past events (e.g. "had surgery in 2022").
- For symptoms, set severity (mild/moderate/severe) and onset (e.g. "3 days
  ago", "last week") when the patient mentions them.
- For each extracted item, set is_new=true ONLY if it adds NEW information
  compared to CURRENT PATIENT DETAILS.
- If it is basically the same meaning as something already present, set
  is_new=false.
- Keep each memory text as a short atomic sentence.
- No speculation; only facts stated by the patient.
- If there is nothing memory-worthy (e.g. a greeting, a question with no new
  personal info), return should_write=false and an empty list.
"""


# ── node ─────────────────────────────────────────────────────────────────────

def remember_node(state: AgentState) -> dict:
    patient_id = state["patient_id"]
    logger.info("▶ Remember Node Started | patient=%s", patient_id)

    if store is None:
        logger.warning("Memory store not available — skipping remember step")
        return {"remembered_context": "", "saved_memory": False}

    existing_memories = _load_existing_memories(patient_id)
    existing_block = _format_existing(existing_memories)

    user_message = (state.get("raw_input") or "").strip()
    if not user_message:
        logger.info("No user input to extract memories from | patient=%s", patient_id)
        return {
            "remembered_context": existing_block,
            "saved_memory": False,
        }

    system_msg = SystemMessage(content=REMEMBER_SYSTEM_PROMPT.format(existing_memories=existing_block))

    start = time.monotonic()
    try:
        decision: MemoryDecision = _memory_llm.invoke([
            system_msg,
            {"role": "user", "content": user_message},
        ])
    except Exception:
        logger.exception("Memory extraction failed | patient=%s", patient_id)
        # Fail open: don't block the turn on a memory-extraction error.
        return {"remembered_context": existing_block, "saved_memory": False}
    logger.info("✓ Remember LLM call finished in %.2fs", time.monotonic() - start)

    newly_written: list[dict] = []
    if decision.should_write:
        for mem in decision.memories:
            if not mem.is_new:
                continue
            try:
                store_dict = _mem_to_store_dict(mem)
                run_with_retry(
                    store.put,
                    _namespace(patient_id),
                    str(uuid.uuid4()),
                    {"data": store_dict},
                )
                newly_written.append(store_dict)
            except Exception:
                logger.exception(
                    "Failed to persist memory | patient=%s | text=%s",
                    patient_id, mem.text,
                )

    if newly_written:
        logger.info(
            "✓ Wrote %d new memories | patient=%s", len(newly_written), patient_id,
        )

    # Rebuild the context block including anything just written, so the
    # downstream RAG/router and Chat nodes see the fully up-to-date picture
    # without a second DB round-trip.
    all_memories = existing_memories + newly_written
    return {
        "remembered_context": _format_existing(all_memories),
        "saved_memory": bool(newly_written),
    }
