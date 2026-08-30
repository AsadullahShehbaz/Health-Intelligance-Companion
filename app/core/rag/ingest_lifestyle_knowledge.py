"""
ingest_lifestyle_knowledge.py
------------------------------
Fills the "diet / exercise / prevention / self-care" gap in the
`health_knowledge` Qdrant collection by ingesting the relevant slice of
MedQuAD (https://github.com/abachaa/MedQuAD, CC-BY 4.0, NIH/CDC-sourced).

Why this source: the existing collection (ChatDoctor dialogues + PubMedQA
abstracts + a disease-relationship table) has no formal treatment/prevention/
lifestyle content, which is exactly what the thesis's "holistic treatment
plan" claim depends on. MedQuAD's `treatment`, `prevention`, and
`considerations` (i.e. "what to do for X" / self-care) question types are a
direct, free, properly-licensed fix for that gap.

Usage:
    python ingest_lifestyle_knowledge.py --dry-run          # preview only
    python ingest_lifestyle_knowledge.py                    # actually upsert
    python ingest_lifestyle_knowledge.py --conditions diabetes,hypertension

Requires the same env vars your app already uses:
    QDRANT_URL, QDRANT_API_KEY, HF_TOKEN (optional)

Reuses the exact embedding model + collection name your qdrant_store.py
already queries against, so nothing downstream (retrieve(), rag_tool.py,
router_node.py) needs to change.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# --------------------------------------------------------------------------
# Config — mirrors app/core/rag/embedder.py and app/core/rag/qdrant_store.py
# --------------------------------------------------------------------------

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION = "health_knowledge"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dim

QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
HF_TOKEN = os.environ.get("HF_TOKEN")

REPO_URL = "https://github.com/abachaa/MedQuAD.git"
REPO_DIR = Path("./MedQuAD")

# Folders in the MedQuAD repo worth pulling from. Skipped: drug-name folders
# (11_MPlusDrugs_QA) and pure genetics folders (2_GARD_QA, 3_GHR_QA) — low
# relevance to diet/exercise/self-care, and drug-brand data is already a poor
# match for a diagnostic-support agent.
SOURCE_FOLDERS = [
    "5_NIDDK_QA",             # diabetes, digestive, kidney — heavy diet content
    "9_CDC_QA",                # chronic disease prevention
    "8_NHLBI_QA_XML",          # heart, lung, blood — diet/exercise heavy
    "4_MPlus_Health_Topics_QA",  # broad general health topics
    "7_SeniorHealth_QA",       # lifestyle/self-care framed for older adults
]

# Question types that map to "how do I manage/prevent/live with this" rather
# than pure clinical facts (causes, symptoms, diagnosis stay out — those are
# closer to what ChatDoctor/PubMedQA already cover).
WANTED_QTYPES = {
    "treatment": "treatment",
    "prevention": "lifestyle",
    "considerations": "lifestyle",  # MedQuAD's "what to do for X" bucket
    "susceptibility": "risk_factors",
    "complications": "risk_factors",
}

# Restrict to conditions relevant to a Pakistani primary-care population by
# default. Override with --conditions or --all.
DEFAULT_CONDITIONS = [
    "diabetes", "hypertension", "high blood pressure", "obesity",
    "overweight", "cholesterol", "heart disease", "coronary",
    "thyroid", "hypothyroidism", "arthritis", "gerd", "acid reflux",
    "asthma", "kidney disease", "chronic kidney", "anemia",
    "depression", "anxiety", "pcos", "polycystic",
]

MIN_ANSWER_CHARS = 80     # skip near-empty answers
MAX_ANSWER_CHARS = 2500   # split anything longer into ~2 chunks


# --------------------------------------------------------------------------
# Step 1: fetch MedQuAD if not already present locally
# --------------------------------------------------------------------------

def ensure_repo() -> None:
    if REPO_DIR.exists():
        print(f"[skip] {REPO_DIR} already exists, not re-cloning")
        return
    print(f"[fetch] cloning {REPO_URL} ...")
    subprocess.run(
        ["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)],
        check=True,
    )


# --------------------------------------------------------------------------
# Step 2: parse + filter QA pairs
# --------------------------------------------------------------------------

def condition_matches(focus: str, conditions: list[str] | None) -> bool:
    if not conditions:  # empty list => --all, no filtering
        return True
    focus_lower = focus.lower()
    return any(c in focus_lower for c in conditions)


def chunk_answer(text: str) -> list[str]:
    """Split long answers on paragraph breaks, keeping chunks under
    MAX_ANSWER_CHARS. Most MedQuAD answers are already a single coherent
    paragraph or two, so this is a light split, not aggressive chunking."""
    text = text.strip()
    if len(text) <= MAX_ANSWER_CHARS:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) + 1 > MAX_ANSWER_CHARS and current:
            chunks.append(current.strip())
            current = p
        else:
            current = f"{current}\n{p}" if current else p
    if current:
        chunks.append(current.strip())
    return chunks


def parse_documents(conditions: list[str] | None) -> list[dict]:
    records = []
    seen_hashes: set[str] = set()

    for folder in SOURCE_FOLDERS:
        folder_path = REPO_DIR / folder
        if not folder_path.exists():
            print(f"[warn] {folder_path} not found, skipping")
            continue

        xml_files = list(folder_path.glob("*.xml"))
        print(f"[parse] {folder}: {len(xml_files)} documents")

        for xml_path in xml_files:
            try:
                tree = ET.parse(xml_path)
            except ET.ParseError:
                continue
            root = tree.getroot()

            focus_el = root.find("Focus")
            focus = (focus_el.text or "").strip() if focus_el is not None else ""
            if not condition_matches(focus, conditions):
                continue

            source_attr = root.attrib.get("source", folder)

            for qa in root.findall(".//QAPair"):
                q_el = qa.find("Question")
                a_el = qa.find("Answer")
                if q_el is None or a_el is None:
                    continue

                qtype = q_el.attrib.get("qtype", "").strip().lower()
                if qtype not in WANTED_QTYPES:
                    continue

                answer = (a_el.text or "").strip()
                if len(answer) < MIN_ANSWER_CHARS:
                    continue

                question = (q_el.text or "").strip()
                category = WANTED_QTYPES[qtype]

                for chunk in chunk_answer(answer):
                    h = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                    if h in seen_hashes:
                        continue  # dedup within this run
                    seen_hashes.add(h)

                    records.append({
                        "text": f"{question}\n{chunk}" if question else chunk,
                        "source": f"MedQuAD:{source_attr}",
                        "category": category,
                        "condition": focus.lower(),
                        "content_hash": h,
                    })

    print(f"[parse] {len(records)} candidate chunks after filtering + dedup")
    return records


# --------------------------------------------------------------------------
# Step 3: embed + upsert
# --------------------------------------------------------------------------

def ensure_collection(client: QdrantClient) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION in existing:
        return
    print(f"[qdrant] collection '{COLLECTION}' not found, creating it")
    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )


def upsert_records(records: list[dict], batch_size: int = 64) -> None:
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("[error] QDRANT_URL / QDRANT_API_KEY not set in environment")
        sys.exit(1)

    print("[embed] loading SentenceTransformer model...")
    embedder = SentenceTransformer(EMBED_MODEL_NAME, token=HF_TOKEN)

    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
    ensure_collection(client)

    total = len(records)
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        vectors = embedder.encode(
            [r["text"] for r in batch],
            normalize_embeddings=True,
        ).tolist()

        points = [
            PointStruct(
                # deterministic ID from content hash => reruns overwrite
                # rather than duplicate, safe to re-run this script anytime.
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, r["content_hash"])),
                vector=vec,
                payload={
                    "text": r["text"],
                    "source": r["source"],
                    "category": r["category"],
                    "condition": r["condition"],
                },
            )
            for r, vec in zip(batch, vectors)
        ]
        client.upsert(collection_name=COLLECTION, points=points)
        print(f"[upsert] {min(i + batch_size, total)}/{total}")

    print(f"[done] upserted {total} chunks into '{COLLECTION}'")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--conditions",
        type=str,
        default=None,
        help="Comma-separated condition keywords to filter on "
             "(default: a built-in Pakistan-relevant chronic-disease list)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Ingest all conditions in MedQuAD, ignoring the condition filter",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Parse and print sample output only, skip embedding/upsert",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Cap number of chunks ingested (useful for a quick test run)",
    )
    args = parser.parse_args()

    if args.all:
        conditions = None
    elif args.conditions:
        conditions = [c.strip().lower() for c in args.conditions.split(",")]
    else:
        conditions = DEFAULT_CONDITIONS

    ensure_repo()
    records = parse_documents(conditions)

    if args.limit:
        records = records[:args.limit]

    # quick category breakdown so you can see what you're about to add
    from collections import Counter
    breakdown = Counter(r["category"] for r in records)
    print(f"[summary] category breakdown: {dict(breakdown)}")

    if args.dry_run:
        print("\n[dry-run] sample records:\n")
        for r in records[:3]:
            print("-" * 60)
            print(f"source:    {r['source']}")
            print(f"category:  {r['category']}")
            print(f"condition: {r['condition']}")
            print(f"text:      {r['text'][:300]}...")
        print(f"\n[dry-run] would upsert {len(records)} chunks. Re-run without --dry-run to commit.")
        return

    upsert_records(records)


if __name__ == "__main__":
    main()
