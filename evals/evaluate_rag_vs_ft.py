#!/usr/bin/env python3
"""
evaluate_rag_vs_ft.py

Evaluation pipeline comparing Fine-tuned BioMistral-7B WITH Retrieval-Augmented 
Generation (RAG) vs. WITHOUT RAG (Plain Instruction Prompting).
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Optional

import numpy as np
from bert_score import score as bert_score
from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from rouge_score import rouge_scorer
from sacrebleu import corpus_bleu
from sentence_transformers import SentenceTransformer

from app.config import Settings, settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_LLM_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_SECONDS = 2.0


class Retriever:
    def __init__(self, cfg: Settings):
        self.cfg = cfg
        self.client = QdrantClient(url=cfg.QDRANT_URL, api_key=cfg.QDRANT_API_KEY)
        self.embedder = SentenceTransformer(cfg.EMBEDDING_MODEL)

    def retrieve(self, query: str) -> list[str]:
        vector = self.embedder.encode(query).tolist()
        hits = self.client.query_points(
            collection_name=self.cfg.QDRANT_COLLECTION,
            query=vector,
            limit=self.cfg.TOP_K,
            score_threshold=self.cfg.SIMILARITY_THRESHOLD,
        ).points
        return [
            h.payload.get("text") or h.payload.get("content") or str(h.payload)
            for h in hits if h.payload
        ]


class LlamaServerClient:
    def __init__(self, cfg: Settings):
        self.llm = ChatOpenAI(
            base_url=cfg.LLM_BASE_URL,
            api_key=cfg.LLM_API_KEY,
            model=cfg.LLM_MODEL,
            temperature=0.0,
            max_tokens=cfg.MAX_NEW_TOKENS,
            timeout=300,
            max_retries=0,
            stop=["### Question:", "</s>"],
        )
        self.max_retries = getattr(cfg, "LLM_MAX_RETRIES", DEFAULT_LLM_MAX_RETRIES)
        self.retry_backoff_seconds = getattr(cfg, "LLM_RETRY_BACKOFF_SECONDS", DEFAULT_RETRY_BACKOFF_SECONDS)

    def complete(self, prompt: str) -> tuple[str, float]:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                start = time.time()
                response = self.llm.invoke(prompt)
                return response.content.strip(), time.time() - start
            except Exception as exc:  # noqa: BLE001
                last_exception = exc
                if attempt >= self.max_retries:
                    raise
                delay = self.retry_backoff_seconds * (2 ** attempt)
                logger.warning(
                    "LLM call failed (attempt %s/%s). Retrying in %.1f seconds. Error: %s",
                    attempt + 1,
                    self.max_retries + 1,
                    delay,
                    exc,
                )
                time.sleep(delay)

        raise RuntimeError("LLM request failed after all retries") from last_exception


def extract_mcq_choice(text: str) -> Optional[str]:
    match = re.search(r"\b([A-E])\b", text[:200])
    return match.group(1) if match else None


def compute_metrics(preds: list[str], refs: list[str]) -> dict[str, float]:
    # ROUGE
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    rouge_scores = {k: [] for k in ["rouge1", "rouge2", "rougeL"]}
    for p, r in zip(preds, refs):
        res = scorer.score(r, p)
        for k in rouge_scores:
            rouge_scores[k].append(res[k].fmeasure)

    # BERTScore & BLEU
    _, _, f1 = bert_score(preds, refs, lang="en", verbose=False)
    
    return {
        "rouge1": float(np.mean(rouge_scores["rouge1"])),
        "rouge2": float(np.mean(rouge_scores["rouge2"])),
        "rougeL": float(np.mean(rouge_scores["rougeL"])),
        "bleu": corpus_bleu(preds, [refs]).score / 100.0,
        "bertscore_f1": float(f1.mean().item()),
    }


def _save_checkpoint(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def _load_checkpoint(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.warning("Checkpoint file %s was unreadable; starting from scratch.", path)
        return []

    if not isinstance(data, list):
        logger.warning("Checkpoint file %s did not contain a list; starting from scratch.", path)
        return []
    return data


def _row_key(row: dict) -> Optional[str]:
    row_id = row.get("id")
    return str(row_id) if row_id is not None else None


def run_arm(
    label: str,
    rows: list[dict],
    llama: LlamaServerClient,
    retriever: Optional[Retriever],
    cfg: Settings,
    checkpoint_path: Optional[Path | str] = None,
) -> list[dict]:
    checkpoint_file = Path(checkpoint_path) if checkpoint_path else None
    result_rows = _load_checkpoint(checkpoint_file) if checkpoint_file else []
    completed_ids = { _row_key(r) for r in result_rows if _row_key(r) is not None }

    for i, row in enumerate(rows):
        row_id = _row_key(row)
        if row_id is not None and row_id in completed_ids:
            continue

        question = row["question"]
        if retriever:
            chunks = retriever.retrieve(question)
            context = "\n---\n".join(chunks) if chunks else "(no relevant documents found)"
            prompt = (
                "Below is a medical question, along with relevant reference information retrieved from a medical knowledge base. "
                "Write a response that appropriately answers the question, grounded in the reference information where relevant.\n\n"
                "### Reference Information:\n{context}\n\n### Question:\n{question}\n\n### Response:\n"
            ).format(question=question, context=context)
        else:
            prompt = (
                "Below is a medical question. Write a response that appropriately answers it.\n\n"
                "### Question:\n{question}\n\n### Response:\n"
            ).format(question=question)

        generated, latency = llama.complete(prompt)
        logger.info(f"[{label}] {i+1}/{len(rows)} | latency={latency:.2f}s | id={row.get('id')}")

        entry = {
            "id": row.get("id"),
            "question": question,
            "reference_answer": row["reference_answer"],
            "generated": generated,
            "latency_s": latency,
            "is_mcq": row.get("is_mcq", False),
            "correct_option": row.get("correct_option"),
            "predicted_option": extract_mcq_choice(generated) if row.get("is_mcq") else None,
        }
        result_rows.append(entry)
        if checkpoint_file is not None:
            _save_checkpoint(checkpoint_file, result_rows)

    return result_rows


def summarize(results: list[dict]) -> dict:
    preds = [r["generated"] for r in results]
    refs = [r["reference_answer"] for r in results]
    metrics = compute_metrics(preds, refs)

    mcq_rows = [r for r in results if r["is_mcq"]]
    mcq_acc = sum(1 for r in mcq_rows if r["predicted_option"] == r["correct_option"]) / len(mcq_rows) if mcq_rows else None
    latencies = [r["latency_s"] for r in results]

    return {
        "n": len(results),
        **metrics,
        "mcq_accuracy": mcq_acc,
        "mcq_n": len(mcq_rows),
        "latency_mean_s": float(np.mean(latencies)),
        "latency_median_s": float(np.median(latencies)),
    }


def print_comparison_table(no_rag: dict, rag: dict) -> None:
    rows = [
        ("ROUGE-1", "rouge1"), ("ROUGE-2", "rouge2"), ("ROUGE-L", "rougeL"),
        ("BLEU", "bleu"), ("BERTScore F1", "bertscore_f1"),
        ("MCQ Accuracy", "mcq_accuracy"),
        ("Mean latency (s)", "latency_mean_s"), ("Median latency (s)", "latency_median_s")
    ]
    print("\n" + "=" * 78)
    print(f"{'Metric':<20}{'No-RAG':>14}{'RAG':>14}{'Abs. Delta':>15}{'Rel. Delta':>15}")
    print("-" * 78)
    for label, key in rows:
        a, b = no_rag[key], rag[key]
        if a is None or b is None:
            print(f"{label:<20}{'n/a':>14}{'n/a':>14}{'n/a':>15}{'n/a':>15}")
            continue
        delta = b - a
        rel = f"{(delta / abs(a)) * 100:+.1f}%" if a != 0 else "n/a"
        print(f"{label:<20}{a:>14.4f}{b:>14.4f}{delta:>+15.4f}{rel:>15}")
    print("=" * 78 + "\n")


def _resolve_dataset_path(test_data_path: str) -> Path:
    candidate = Path(test_data_path)
    if candidate.is_absolute():
        return candidate

    repo_root = Path(__file__).resolve().parents[1]
    for base in [Path.cwd(), repo_root]:
        resolved = (base / candidate).resolve()
        if resolved.exists():
            return resolved
    return (repo_root / candidate).resolve()


def main():
    cfg: Settings = settings
    out_dir = Path(cfg.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    data_path = _resolve_dataset_path(cfg.TEST_DATA_PATH)
    with open(data_path, encoding="utf-8") as f:
        rows = json.load(f)

    llama = LlamaServerClient(cfg)
    retriever = Retriever(cfg)

    no_rag_checkpoint = out_dir / "no_rag_results.json"
    rag_checkpoint = out_dir / "rag_results.json"

    logger.info(f"Running {len(rows)} examples WITHOUT RAG...")
    no_rag_results = run_arm("no-rag", rows, llama, retriever=None, cfg=cfg, checkpoint_path=no_rag_checkpoint)

    logger.info(f"Running {len(rows)} examples WITH RAG...")
    rag_results = run_arm("rag", rows, llama, retriever=retriever, cfg=cfg, checkpoint_path=rag_checkpoint)

    no_rag_summary = summarize(no_rag_results)
    rag_summary = summarize(rag_results)

    for filename, data in [
        ("no_rag_results.json", no_rag_results),
        ("rag_results.json", rag_results),
        ("summary.json", {"no_rag": no_rag_summary, "rag": rag_summary}),
    ]:
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    print_comparison_table(no_rag_summary, rag_summary)
    logger.info(f"Results saved to: {out_dir}/")


if __name__ == "__main__":
    main() 