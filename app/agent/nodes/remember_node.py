# app/agent/nodes/remember_node.py
"""Node 1 — Remember.

Runs before RAG/routing on every turn. Loads existing patient memories from
the Postgres store, asks gpt-oss-120b (via Groq, structured output) to
extract atomic facts from the user's latest message — and from any OCR'd
document text attached this turn (prescriptions, lab reports) — then writes
only the genuinely new ones back to the store.

OCR runs outside the graph (API layer) so Base64 payloads never enter
checkpoints; only the extracted structured facts are persisted here. The raw
OCR text itself lives in this turn's state only.

Memories are category-tagged (identity, symptom, medication, etc.) so
downstream BioMistral can reason over structured patient history rather than
an undifferentiated bullet list. Facts update in place via supersedes_id
instead of piling up contradictions.

Scaling (Phase 4): neither the extraction prompt nor the downstream context
ever sees the full history dump. Identity facts always survive selection;
everything else is recency-prefiltered, then ranked by semantic similarity
to the turn's topic (user text + OCR) via the RAG embedder — falling back to
plain recency when embeddings are unavailable.
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

# Phase 4 scaling knobs:
#   - hard ceiling on what one turn echoes into prompts, regardless of how
#     much history the patient has accumulated
#   - how many of the most recent non-identity memories are candidates for
#     semantic ranking (bounds the embedder's work per turn)
_EXTRACTION_PROMPT_CAP = 30
_CANDIDATE_POOL = 60

# ── helpers ──────────────────────────────────────────────────────────────────


def _namespace(patient_id: str) -> tuple:
    return (MEMORY_NAMESPACE, patient_id)


def _load_existing_memories(patient_id: str) -> list[dict]:
    """Return every stored memory for *patient_id* as a list of dicts.

    Each dict contains the full MemoryItem fields (text, category, status,
    severity, onset) plus the store ``key`` — needed so supersession can
    reference and update records in place.  Returns an empty list on any DB
    error.
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
            mem = dict(data)
        else:
            # Back-compat: old flat-string memories (no category field)
            # are promoted to "identity" / "active".
            mem = {"text": str(data), "category": "identity", "status": "active"}
        mem["key"] = item.key
        # Internal recency marker (never persisted) for Phase 4 selection.
        mem["_ts"] = (
            getattr(item, "updated_at", None) or getattr(item, "created_at", None)
        )
        memories.append(mem)
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


def _format_for_extraction(memories: list[dict]) -> str:
    """Format memories with store keys visible, for the extraction LLM only.

    The Remember LLM needs each memory's [key] so it can set supersedes_id
    when a new fact updates an existing one.  This block is NEVER shown to
    BioMistral — the downstream block comes from _format_existing().
    """
    if not memories:
        return "(empty)"
    lines = []
    for mem in memories:
        key = mem.get("key", "?")
        cat = mem.get("category", "identity")
        status = mem.get("status", "active")
        extras = _detail_suffix(mem)
        lines.append(f"[{key}] {cat}/{status}: {mem.get('text', '')}{extras}")
    return "\n".join(lines)


def _sort_by_recency(memories: list[dict]) -> list[dict]:
    """Oldest → newest.  Timestamped records (real PostgresStore items) sort
    by updated_at/created_at; undated ones (test fakes) keep their relative
    insertion order and land before the dated ones."""
    def _ts(m: dict):
        return m.get("_ts")

    undated = [m for m in memories if _ts(m) is None]
    dated = sorted((m for m in memories if _ts(m) is not None), key=_ts)
    return undated + dated


def _semantic_scores(pool: list[dict], topic: str) -> list[float] | None:
    """Cosine similarity of each memory text against the turn's topic.

    Returns None when embeddings can't be produced — empty topic, embedder
    unavailable, or an all-zero topic vector (e.g. stubbed in tests) — so the
    caller falls back to plain recency order.
    """
    if not topic:
        return None
    try:
        import numpy as np

        from app.core.rag.embedder import get_embedder

        embedder = get_embedder()
        topic_vec = np.asarray(embedder.encode(topic), dtype=float).ravel()
        if not np.any(topic_vec):
            return None
        mat = np.asarray(
            [
                np.asarray(embedder.encode(m.get("text", "")), dtype=float).ravel()
                for m in pool
            ],
            dtype=float,
        )
        denom = np.linalg.norm(mat, axis=1) * np.linalg.norm(topic_vec)
        sims = np.where(denom > 0, mat.dot(topic_vec) / np.where(denom == 0, 1.0, denom), 0.0)
        return [float(s) for s in sims]
    except Exception:
        logger.debug(
            "Semantic memory ranking unavailable — falling back to recency",
            exc_info=True,
        )
        return None


def _select_memories(
    memories: list[dict],
    topic: str,
    cap: int = _EXTRACTION_PROMPT_CAP,
) -> list[dict]:
    """Choose which memories this turn is allowed to see (Phase 4 fix).

    Identity facts always survive selection — personalization needs the
    patient's name even when the turn is off-topic.  Everything else is
    recency-prefiltered to ``_CANDIDATE_POOL``, then ranked by semantic
    similarity to the topic; the top ``cap`` minus identity survive.  With
    embeddings unavailable, the most recent ``budget`` facts win instead.
    """
    if len(memories) <= cap:
        return memories

    identity = [m for m in memories if m.get("category") == "identity"]
    others = [m for m in memories if m.get("category") != "identity"]
    budget = max(cap - len(identity), 0)
    if len(others) <= budget:
        return identity + others

    ordered = _sort_by_recency(others)
    pool = ordered[-_CANDIDATE_POOL:]

    scores = _semantic_scores(pool, topic)
    if scores is None:
        selected = pool[-budget:]
    else:
        # Highest similarity first; ties resolved toward the more recent
        # fact (later index in the recency-ordered pool).
        ranked = sorted(
            zip(scores, range(len(pool)), pool),
            key=lambda t: (-t[0], -t[1]),
        )
        selected = [m for _, _, m in ranked[:budget]]
    return identity + selected


def _mem_to_store_dict(mem: MemoryItem) -> dict:
    """Serialize a MemoryItem into the dict persisted by store.put."""
    return {
        "text": mem.text,
        "category": mem.category.value,
        "status": mem.status,
        "severity": mem.severity,
        "onset": mem.onset,
    }


def _apply_supersession(patient_id: str, mem: MemoryItem) -> dict | None:
    """Update an existing record in place when a new fact supersedes it.

    The superseding fact wins for every field it carries; the record keeps
    its original store key so history stays one-row-per-fact.  Returns the
    updated memory dict, or None when the referenced key doesn't exist (LLM
    hallucination) so the caller falls back to a fresh write.
    """
    existing = run_with_retry(store.get, _namespace(patient_id), mem.supersedes_id)
    if existing is None:
        return None

    data = existing.value.get("data")
    if isinstance(data, dict):
        updated = dict(data)
    else:  # old flat-string record being superseded
        updated = {"text": str(data or ""), "category": "identity", "status": "active"}

    updated["text"] = mem.text
    updated["category"] = mem.category.value
    updated["status"] = mem.status
    if mem.severity:
        updated["severity"] = mem.severity
    if mem.onset:
        updated["onset"] = mem.onset

    run_with_retry(
        store.put,
        _namespace(patient_id),
        mem.supersedes_id,
        # "key"/"_ts" are in-memory markers from _load_existing_memories —
        # never persist them.
        {"data": {k: v for k, v in updated.items() if k not in ("key", "_ts")}},
    )
    updated["key"] = mem.supersedes_id
    return updated


# ── prompt ───────────────────────────────────────────────────────────────────

REMEMBER_SYSTEM_PROMPT = """You are responsible for updating and maintaining accurate patient memory
for a healthcare companion system.

CURRENT PATIENT DETAILS (existing memories):
{existing_memories}

{ocr_block}
TASK:
- Review the patient's latest message and any document text below.
- Extract patient-specific info worth storing long-term. For EACH item, pick
  the most appropriate category:
    identity       — name, age, occupation, city, family, emergency contact
    symptom       — medical complaints (headache, fever, pain, etc.)
    medication    — current or past drugs, dosage, frequency
    lab_result    — test values, blood work, imaging findings
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
- UPDATING EXISTING FACTS: when the message CHANGES or CLOSES OUT a memory
  already on file (symptom gone → resolved, headache worsening → new
  severity, dose changed, medication stopped), set supersedes_id to that
  memory's [key] from CURRENT PATIENT DETAILS (copy it exactly) and reflect
  the new state in status/severity/onset/text. The system updates the
  referenced record in place — do not ALSO emit it as a separate new fact.
- If it is basically the same meaning as something already present with no
  change, set is_new=false.
- Keep each memory text as a short atomic sentence.
- No speculation; only facts stated by the patient or present in the document.
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

    user_message = (state.get("raw_input") or "").strip()
    ocr_text = (state.get("ocr_context") or "").strip()

    # Phase 4: bound what this turn echoes — identity always, plus recent
    # facts ranked by similarity to the turn's topic (user text + OCR).
    # Applies to both the extraction prompt and the downstream block, so a
    # "hi" pays for a handful of facts, not the patient's entire history.
    topic = f"{user_message}\n{ocr_text}".strip()
    context_memories = _select_memories(existing_memories, topic)
    existing_block = _format_existing(context_memories)

    # Build the OCR block for the extraction prompt when document text exists.
    if ocr_text:
        ocr_block = (
            "DOCUMENT TEXT (from OCR of prescription / lab report / medical document):\n"
            f"{ocr_text}\n\n"
            "Extract medication names, dosages, test values, diagnoses, and other\n"
            "clinically relevant facts from the document above. Tag them with\n"
            "category=medication or category=lab_result as appropriate.\n"
        )
    else:
        ocr_block = ""

    if not user_message and not ocr_text:
        logger.info("No user input or OCR text to extract memories from | patient=%s", patient_id)
        return {
            "remembered_context": existing_block,
            "saved_memory": False,
        }

    system_msg = SystemMessage(
        content=REMEMBER_SYSTEM_PROMPT.format(
            existing_memories=_format_for_extraction(context_memories),
            ocr_block=ocr_block,
        )
    )

    start = time.monotonic()
    # When an image arrived with no accompanying text, still give the LLM a
    # non-empty user turn so extraction runs on the document alone.
    llm_user_content = user_message or "(patient uploaded a document with no text message)"
    try:
        decision: MemoryDecision = _memory_llm.invoke([
            system_msg,
            {"role": "user", "content": llm_user_content},
        ])
    except Exception:
        logger.exception("Memory extraction failed | patient=%s", patient_id)
        # Fail open: don't block the turn on a memory-extraction error.
        return {"remembered_context": existing_block, "saved_memory": False}
    logger.info("✓ Remember LLM call finished in %.2fs", time.monotonic() - start)

    # Working set for the final context block: superseded entries get
    # replaced in place, genuinely new facts appended — no second DB read.
    # Seeded from the Phase 4 selection, so the downstream block stays
    # bounded too.
    all_memories = list(context_memories)
    changes = 0
    if decision.should_write:
        for mem in decision.memories:
            if not mem.is_new:
                continue
            try:
                if mem.supersedes_id:
                    updated = _apply_supersession(patient_id, mem)
                    if updated is not None:
                        all_memories = [
                            updated if m.get("key") == mem.supersedes_id else m
                            for m in all_memories
                        ]
                        changes += 1
                        continue
                    logger.warning(
                        "supersedes_id points at missing key — writing as new | "
                        "patient=%s | key=%s", patient_id, mem.supersedes_id,
                    )
                key = str(uuid.uuid4())
                store_dict = _mem_to_store_dict(mem)
                run_with_retry(
                    store.put,
                    _namespace(patient_id),
                    key,
                    # Persist a copy — store_dict gains in-memory markers
                    # ("key") for the working set right after this.
                    {"data": dict(store_dict)},
                )
                store_dict["key"] = key
                all_memories.append(store_dict)
                changes += 1
            except Exception:
                logger.exception(
                    "Failed to persist memory | patient=%s | text=%s",
                    patient_id, mem.text,
                )

    if changes:
        logger.info(
            "✓ Applied %d memory changes (new + updates) | patient=%s",
            changes, patient_id,
        )

    return {
        "remembered_context": _format_existing(all_memories),
        "saved_memory": changes > 0,
    }
