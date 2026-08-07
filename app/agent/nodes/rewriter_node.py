# app/agent/nodes/rewriter_node.py
from app.core.llm import llm
from app.agent.state import AgentState

REWRITER_PROMPT = """Rewrite the user's message into a clear, specific
medical question suitable for a search query. Keep it short — one
sentence. If the message is already clear, return it unchanged.

Recent conversation:
{memory}

User message: "{query}"

Rewritten query:"""


def _format_memory(memory: list[dict]) -> str:
    if not memory:
        return "(no prior context)"
    return "\n".join(f"Q: {m['query']}\nA: {m['answer'][:150]}" for m in memory)


def query_rewriter_node(state: AgentState) -> AgentState:
    prompt = REWRITER_PROMPT.format(
        memory=_format_memory(state.get("recent_memory", [])),
        query=state["english_query"],
    )
    output = llm(prompt, max_tokens=80, temperature=0.3)
    rewritten = output["choices"][0]["text"].strip()
    state["rewritten_query"] = rewritten if rewritten else state["english_query"]
    return state