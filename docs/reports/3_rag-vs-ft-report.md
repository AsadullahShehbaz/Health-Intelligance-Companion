# Retrieval-Augmented Generation vs. Fine-Tuned-Only Baseline

**Evaluation Report — Health Intelligence Companion (FYP 2026)**

*Base model: BioMistral-7B (QLoRA fine-tuned) · Corrective RAG over Qdrant · Evaluated on held-out in-distribution test set*

---

## 1. Purpose

This report compares the response quality of the fine-tuned BioMistral-7B model used alone against the same model augmented with the project's Corrective RAG pipeline. Both pipelines were evaluated on the same held-out, in-distribution test set using reference-based text-similarity metrics (ROUGE-1, ROUGE-2, ROUGE-L) and semantic similarity (BERTScore F1), consistent with the metrics used in the original fine-tuning evaluation.

---

## 2. Evaluation Setup Notes

BERTScore computes semantic similarity by encoding both the generated and reference answers with a pretrained contextual embedding model — this evaluation used `roberta-large` as the underlying scorer, which is BERTScore's standard default model for English text.

### 2.1 roberta-large Load Report (BERTScore scorer)

The load report lists two categories of mismatch between the downloaded checkpoint and the `RobertaModel` class being loaded:

- **UNEXPECTED keys** (`lm_head.*`) — weights belonging to RoBERTa's original masked-language-modeling head. BERTScore only needs the base encoder's hidden states, not the language-modeling head, so these weights are loaded from the checkpoint but unused and safely discarded.

- **MISSING keys** (`pooler.dense.*`) — the pooling layer is randomly initialized because BERTScore does not use the pooled `[CLS]` output; it scores token-level embeddings directly, so the uninitialized pooler has no effect on the reported scores.

Both notices are expected, standard behavior any time `roberta-large` is loaded through Hugging Face Transformers for an embedding-only task such as BERTScore, and appear identically whether the pipeline is scoring the fine-tuned-only outputs or the RAG outputs. They confirm the scorer loaded successfully, not a failure.

---

## 3. Results

| Metric | Fine-Tuned Only | RAG (Corrective RAG) | Absolute Gain | Relative Gain |
|--------|----------------|----------------------|---------------|---------------|
| **ROUGE-1** | 0.2041 | **0.2789** | +0.0748 | **+36.6%** |
| **ROUGE-2** | 0.0693 | **0.1051** | +0.0358 | **+51.7%** |
| **ROUGE-L** | 0.1574 | **0.2249** | +0.0675 | **+42.9%** |
| **BERTScore F1** | 0.8711 | **0.8842** | +0.0131 | **+1.5%** |

---

## 4. Interpretation

RAG improved every metric over the fine-tuned-only baseline, with the largest relative gains on n-gram overlap metrics:

- **ROUGE-1 (+36.6%)** and **ROUGE-L (+42.9%)** show the RAG pipeline's answers share substantially more exact wording and phrase structure with the reference answers — consistent with retrieved context supplying concrete facts (symptoms, treatments) that the model can restate accurately rather than relying on parametric recall alone.

- **ROUGE-2 (+51.7%)** shows the largest relative jump of any metric, indicating RAG-generated answers preserve more correct two-word medical phrasing (e.g., specific symptom-treatment pairings) than the fine-tuned model alone.

- **BERTScore F1 (+1.5%)** shows a smaller but still positive gain, which is expected: BERTScore measures semantic similarity rather than exact wording, and the fine-tuned model already scores highly (0.8711) on this axis since QLoRA fine-tuning taught it the general shape and vocabulary of correct medical answers. RAG's contribution here is refining factual specificity on top of already-reasonable semantic alignment, not correcting a semantically incoherent baseline.

Together, these results support the core claim of the Corrective RAG design: grounding generation in retrieved, evaluated context measurably improves factual precision over a fine-tuned model answering from parametric knowledge alone, without a loss in fluency or semantic coherence.

---

## 5. Conclusion

The evaluation confirms that adding Corrective RAG on top of the fine-tuned BioMistral-7B model improves response quality on every measured metric for in-distribution medical queries. This result supports using the RAG-augmented pipeline as the primary answer-generation path in the deployed system, with the fine-tuned model's standalone performance retained as a fallback and as the baseline for this comparison.

---