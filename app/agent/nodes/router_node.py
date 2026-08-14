# app/agent/nodes/router_node.py
"""Node 1 — Router.

A fast Groq model (llama-3.3-70b-versatile) bound with the healthcare tools
decides whether the turn needs any tools (memory / RAG) and emits the
tool_calls when it does. It never produces the final answer — that is the
BioMistral node's job — so on a no-tool turn the router stores only the
user's message (no intermediate assistant text that would pollute history).
"""
import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.agent.state import AgentState
from app.agent.tools import TOOLS
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Groq is used strictly for routing / tool-calling — reliable .bind_tools()
# support that the local GGUF model can't do cleanly.
router_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0.0,
).bind_tools(TOOLS)

ROUTER_SYSTEM_PROMPT = """You are an expert triage and tool routing agent for a healthcare companion system.
Your job is to analyze the user's input and call the APPROPRIATE tool(s) based on strict criteria:

CRITICAL INSTRUCTIONS:

1. Medical Symptoms/Queries: If the user mentions ANY medical symptom, pain, illness, medication, or medical question (e.g., "headache", "stomach pain", "fever", "medication advice"), you MUST call 'retrieve_medical_knowledge' or 'search_web_medical'.

2. Patient History Elicitation: If the user asks about past visits, past symptoms, or recorded medical conditions, you MUST call 'fetch_patient_facts'.

3. Recording Facts: If the user explicitly states new personal health details, diagnosis, age, or symptom onset (e.g., "I have had a headache for 2 days"), you MUST call 'save_patient_fact'.

4. Identity/Background Statements: If the user states ANY personal, non-medical detail about themselves — name, age, gender, occupation, city, family info, emergency contact, preferences, or anything else self-descriptive — you MUST call 'save_patient_profile' with an appropriate free-text 'field' label and the stated 'value'. This is NOT limited to a fixed list of fields — save whatever the patient tells you about themselves.

5. Identity/Background Questions: If the user asks about their OWN previously-stated personal details (name, age, occupation, or anything else non-medical), you MUST call 'fetch_patient_profile', which returns everything saved. NEVER call 'fetch_patient_facts' for this — that tool only covers medical/symptom history.

EXCEPTIONS:
- ONLY skip calling tools if the message is purely conversational (e.g., "Hello", "Hi", "Thank you", "Who are you?", "Good morning").

Patient ID: {patient_id}
"""

# File: app/agent/nodes/router_node.py

def router_node(state: AgentState) -> dict:
    logger.info("▶ Router Node Started | patient=%s", state["patient_id"])

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
