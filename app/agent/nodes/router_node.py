# app/agent/nodes/router_node.py
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.0,
).bind_tools(TOOLS)

ROUTER_SYSTEM_PROMPT = """You are an expert triage and RAG (Retrieval-Augmented Generation) routing agent for a healthcare companion system.
Your job is to analyze the user's input and call the APPROPRIATE tool(s) based on strict criteria:

CRITICAL INSTRUCTIONS:

1. Medical Symptoms/Queries: If the user mentions ANY medical symptom, pain, illness, medication, or medical question (e.g., "headache", "stomach pain", "fever", "medication advice"), you MUST call 'retrieve_medical_knowledge' or 'search_web_medical'.

2. Patient History / Identity Questions: No tool is needed. Patient memory context (past symptoms, identity details, emotional states) is already injected into the conversation by a separate memory system. Answer from the context you already have.

EXCEPTIONS:
- ONLY skip calling tools if the message is purely conversational (e.g., "Hello", "Hi", "Thank you", "Who are you?", "Good morning").

Patient ID: {patient_id}
"""

# File: app/agent/nodes/router_node.py

def rag_router_node(state: AgentState) -> dict:
    logger.info("▶ RAG Router Node Started | patient=%s", state["patient_id"])

    system_msg = SystemMessage(content=ROUTER_SYSTEM_PROMPT.format(patient_id=state["patient_id"]))
    
    # Isolate user's current message
    current_user_text = state.get("raw_input", "")
    
    # Build clean message chain for the router model:
    # 1. System Prompt
    # 2. Historical messages (if any)
    # 3. Current Human Message
    messages = [system_msg]
    
    existing_messages = state.get("messages", [])
    if existing_messages:
        messages.extend(existing_messages)
        
    # Append current input if it's not already the trailing message
    if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != current_user_text:
        messages.append(HumanMessage(content=current_user_text))

    start = time.monotonic()
    response = router_llm.invoke(messages)
    logger.info("✓ Router invoke finished in %.2fs", time.monotonic() - start)

    tool_calls = getattr(response, "tool_calls", None)

    if tool_calls:
        names = [tc.get("name", "?") for tc in tool_calls]
        logger.info("✓ Router successfully selected tools: %s", ", ".join(names))
        
        return {"messages": [HumanMessage(content=current_user_text), response]}

    logger.info("ℹ Router determined query is purely conversational (no tools needed) → straight to BioMistral")
    return {"messages": [HumanMessage(content=current_user_text)]}


router_node = rag_router_node
