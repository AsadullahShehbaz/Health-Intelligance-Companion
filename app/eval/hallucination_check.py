GROUNDING_PROMPT = """
Question: {query}
Retrieved sources used: {sources}
Model answer: {answer}

Rate the answer on this scale:
0 = answer contains claims not supported by the sources and not general medical knowledge
1 = answer is mostly grounded, with minor unsupported claims
2 = answer is fully grounded in the sources or safe, general medical knowledge

Respond with only the number.
"""