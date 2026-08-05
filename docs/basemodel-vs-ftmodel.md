For your setup (BioMistral + Unsloth + Kaggle + LoRA fine-tuning), the professional approach is:

1. Load the **base model**
2. Load your **fine-tuned model** from Hugging Face
3. Use the **same evaluation dataset**
4. Generate predictions from both
5. Calculate exactly the same metrics
6. Compare results in a table

---

# Install Libraries

```python
!pip install -q unsloth
!pip install -q transformers datasets evaluate bert-score rouge-score accelerate sentencepiece
```

---

# Import Libraries

```python
import torch
import evaluate
import pandas as pd

from datasets import load_dataset
from transformers import AutoTokenizer
from unsloth import FastLanguageModel
```

---

# Load Evaluation Dataset

Example:

```python
dataset = load_dataset(
    "json",
    data_files="/kaggle/input/medical-dataset/test.json",
    split="train"
)
```

Example dataset format

```python
{
    "instruction":"What is diabetes?",
    "output":"Diabetes is a chronic disease..."
}
```

---

# Load Base BioMistral

```python
BASE_MODEL = "BioMistral/BioMistral-7B"

model_base, tokenizer = FastLanguageModel.from_pretrained(
    model_name=BASE_MODEL,
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

FastLanguageModel.for_inference(model_base)
```

---

# Load Fine-tuned Model

Replace with your Hugging Face repository.

```python
FINETUNED_MODEL = "YOUR_USERNAME/biomistral-medical-lora"

model_ft, tokenizer = FastLanguageModel.from_pretrained(
    model_name=FINETUNED_MODEL,
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

FastLanguageModel.for_inference(model_ft)
```

---

# Text Generation Function

```python
def generate_answer(model, tokenizer, prompt):

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
    ).to(model.device)

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.0,
            do_sample=False,
        )

    prediction = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    return prediction
```

---

# Generate Predictions

```python
references = []

base_predictions = []

ft_predictions = []

for sample in dataset:

    prompt = sample["instruction"]

    reference = sample["output"]

    references.append(reference)

    base_predictions.append(
        generate_answer(model_base, tokenizer, prompt)
    )

    ft_predictions.append(
        generate_answer(model_ft, tokenizer, prompt)
    )
```

---

# Load Metrics

```python
rouge = evaluate.load("rouge")

bertscore = evaluate.load("bertscore")

perplexity = evaluate.load("perplexity")
```

---

# ROUGE Evaluation

```python
def rouge_scores(predictions, references):

    scores = rouge.compute(
        predictions=predictions,
        references=references,
    )

    return scores
```

---

# BERTScore

```python
def bert_scores(predictions, references):

    score = bertscore.compute(
        predictions=predictions,
        references=references,
        lang="en",
    )

    return sum(score["f1"]) / len(score["f1"])
```

---

# Perplexity

For causal language models:

```python
def ppl_score(predictions):

    result = perplexity.compute(
        predictions=predictions,
        model_id="BioMistral/BioMistral-7B",
    )

    return result["mean_perplexity"]
```

> Using the same evaluator model for both prediction sets ensures a fair comparison.

---

# Evaluate Base Model

```python
base_rouge = rouge_scores(
    base_predictions,
    references,
)

base_bert = bert_scores(
    base_predictions,
    references,
)

base_ppl = ppl_score(
    base_predictions,
)
```

---

# Evaluate Fine-tuned Model

```python
ft_rouge = rouge_scores(
    ft_predictions,
    references,
)

ft_bert = bert_scores(
    ft_predictions,
    references,
)

ft_ppl = ppl_score(
    ft_predictions,
)
```

---

# Comparison Table

```python
comparison = pd.DataFrame({

    "Metric":[
        "Perplexity",
        "ROUGE-1",
        "ROUGE-2",
        "ROUGE-L",
        "BERTScore F1",
    ],

    "Base Model":[
        base_ppl,
        base_rouge["rouge1"],
        base_rouge["rouge2"],
        base_rouge["rougeL"],
        base_bert,
    ],

    "Fine-tuned":[
        ft_ppl,
        ft_rouge["rouge1"],
        ft_rouge["rouge2"],
        ft_rouge["rougeL"],
        ft_bert,
    ]

})

comparison
```

Example output:

| Metric       | Base  | Fine-tuned |
| ------------ | ----- | ---------- |
| Perplexity   | 16.42 | **8.91**   |
| ROUGE-1      | 0.43  | **0.59**   |
| ROUGE-2      | 0.22  | **0.39**   |
| ROUGE-L      | 0.40  | **0.55**   |
| BERTScore F1 | 0.86  | **0.92**   |

---

## About ROUGE-3

The Hugging Face `evaluate` implementation of ROUGE computes **ROUGE-1**, **ROUGE-2**, **ROUGE-L**, and **ROUGE-Lsum**. It **does not provide ROUGE-3** directly.

If your paper or supervisor specifically requires ROUGE-3, use the `rouge-score` library directly:

```python
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(
    ["rouge3"],
    use_stemmer=True,
)

scores = []

for pred, ref in zip(ft_predictions, references):
    score = scorer.score(ref, pred)
    scores.append(score["rouge3"].fmeasure)

rouge3 = sum(scores) / len(scores)

print("ROUGE-3:", rouge3)
```

Run the same loop for `base_predictions` to compare both models.

---

## Interpreting the Metrics

| Metric       | Better Direction | What it Measures                                                                         |
| ------------ | ---------------- | ---------------------------------------------------------------------------------------- |
| Perplexity   | Lower ↓          | How confidently the model predicts text. Lower values indicate better language modeling. |
| ROUGE-1      | Higher ↑         | Unigram (word-level) overlap with the reference.                                         |
| ROUGE-2      | Higher ↑         | Bigram overlap, reflecting phrase-level similarity.                                      |
| ROUGE-3      | Higher ↑         | Trigram overlap, indicating stronger preservation of multi-word sequences.               |
| ROUGE-L      | Higher ↑         | Longest common subsequence, capturing structural similarity.                             |
| BERTScore F1 | Higher ↑         | Semantic similarity using contextual embeddings, even when wording differs.              |

This evaluation pipeline follows a standard research workflow for comparing a base language model with a fine-tuned version on the same held-out test set, making it suitable for coursework, reports, and reproducible experiments.
