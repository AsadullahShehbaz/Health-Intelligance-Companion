# eval/perplexity.py
import math
from app.core.llm import llm


def compute_perplexity(prompt: str, reference: str) -> float:
    """
    Perplexity of the reference answer conditioned on the prompt.
    Lower = model assigns higher probability to the correct answer.
    """
    full_text = f"{prompt}\n{reference}"

    output = llm(
        full_text,
        max_tokens=0,      # don't generate — just score existing tokens
        logprobs=True,
        echo=True,
    )

    token_logprobs = output["choices"][0]["logprobs"]["token_logprobs"]
    # drop None entries (first token has no logprob)
    logprobs = [lp for lp in token_logprobs if lp is not None]

    avg_neg_logprob = -sum(logprobs) / len(logprobs)
    return math.exp(avg_neg_logprob)