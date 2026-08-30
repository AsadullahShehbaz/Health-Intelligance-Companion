# evals/compute_metrics.py
import json
import os
import sys
import time
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
)
from deepeval.test_case import LLMTestCase

# ── Judge LLM = Gemini via OpenAI Env Override ───────────────────────────
load_dotenv()

# Override the OpenAI env vars to point to Google Gemini OpenAI Endpoint
os.environ["OPENAI_API_KEY"] = os.environ["GOOGLE_API_KEY"]
os.environ["OPENAI_BASE_URL"] = "https://generativelanguage.googleapis.com/v1beta/openai/"

judge_model = "gemini-3.6-flash"

# ── Metrics ─────────────────────────────────────────────────────────────
metrics_shared = dict(model=judge_model, threshold=0.5)
answer_rel   = AnswerRelevancyMetric(**metrics_shared)
faithfulness = FaithfulnessMetric(**metrics_shared)
ctx_prec     = ContextualPrecisionMetric(**metrics_shared)
ctx_rec      = ContextualRecallMetric(**metrics_shared)
halluc       = HallucinationMetric(**metrics_shared)

metrics_list = [answer_rel, faithfulness, ctx_prec, ctx_rec, halluc]

# ── Load traces ────────────────────────────────────────────────────────
with open("evals/eval_results.json") as f:
    traces = json.load(f)

test_cases = []
for t in traces:
    if t.get("error") or not t.get("actual_answer"):
        continue
    retrieval_context = t.get("sources") or []
    expected = " ".join(t.get("expected_answer_keywords", []))
    test_cases.append(LLMTestCase(
        input=t["question"],
        actual_output=t["actual_answer"],
        expected_output=expected,
        retrieval_context=retrieval_context if retrieval_context else ["(no retrieval)"],
        context=[expected]
    ))

# ── Measure helper with Retry Logic & Delay ──────────────────────────────
def run_metric_with_retry(metric, test_case, max_retries=5, initial_delay=12):
    """Runs a single DeepEval metric measurement with exponential backoff for 429 errors."""
    delay = initial_delay
    for attempt in range(max_retries):
        try:
            metric.measure(test_case)
            return round(metric.score, 3) if metric.score is not None else None
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"    [!] Rate limited (429). Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay *= 1.5  # Increase wait time for next retry
            else:
                print(f"    [!] Error with {metric.__class__.__name__}: {e}")
                return None
    return None

# ── Run Sequential Loop with Rate Limiting ────────────────────────────────
rows = []
# 15 RPM = 1 request every 4 seconds. To stay safe across 5 metrics, pause 4-5 seconds between calls.
DELAY_BETWEEN_CALLS_SEC = 4.5

for i, tc in enumerate(test_cases):
    print(f"\nEvaluating test case {i+1}/{len(test_cases)}...")
    row = {"input": tc.input[:60]}
    
    for m in metrics_list:
        score = run_metric_with_retry(m, tc)
        row[m.__class__.__name__] = score
        # Throttle request rate
        time.sleep(DELAY_BETWEEN_CALLS_SEC)
            
    rows.append(row)

# ── Export to CSV ──────────────────────────────────────────────────────
df = pd.DataFrame(rows)
df.to_csv("evals/metrics.csv", index=False)
print("\nResults:")
print(df)
print("\nMeans:")
print(df.drop(columns="input").mean())