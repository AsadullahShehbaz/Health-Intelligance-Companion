import os
import re
from typing import Tuple
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

# Initialize ChatGroq Vision Model lazily / globally
_groq_vision_llm = None


def get_groq_vision_client() -> ChatGroq:
    """Lazy initialization for ChatGroq Vision Client."""
    global _groq_vision_llm
    if _groq_vision_llm is None:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            logger.error("GROQ_API_KEY is missing from environment variables!")
            raise ValueError("GROQ_API_KEY is not configured.")

        _groq_vision_llm = ChatGroq(
            model_name="qwen/qwen3.6-27b",
            temperature=0.1,  # Low temperature for factual document extraction
            max_tokens=1024,
            groq_api_key=api_key,
        )
    return _groq_vision_llm


def parse_base64_payload(raw_b64_string: str) -> Tuple[str, str]:
    """
    Parses Base64 string and preserves MIME type if sent from frontend as a Data URI scheme.

    Examples:
        Input: "data:image/png;base64,iVBORw0KGgo..."
        Output: ("image/png", "iVBORw0KGgo...")

        Input: "/9j/4AAQSkZJRg..."
        Output: ("image/jpeg", "/9j/4AAQSkZJRg...")
    """
    # Regex pattern to capture data URI scheme like data:image/png;base64,
    data_uri_pattern = r"^data:(image\/[a-zA-Z0-9\+\-\.]+);base64,(.+)$"
    match = re.match(data_uri_pattern, raw_b64_string.strip())

    if match:
        mime_type = match.group(1)
        clean_b64 = match.group(2)
        logger.info("Preserved MIME type '%s' from Data URI header", mime_type)
        return mime_type, clean_b64

    # If header is missing, fallback to default JPEG
    logger.info("No Data URI scheme found. Defaulting MIME type to 'image/jpeg'")
    return "image/jpeg", raw_b64_string.strip()


def extract_text_from_base64(image_b64: str) -> str:
    """
    Extracts structured text from medical documents, lab reports, and prescriptions
    using Groq LLaMA 3.2 Vision via LangChain.
    """
    if not image_b64:
        logger.info("OCR skipped — empty image_base64")
        return ""

    logger.info("▶ Vision extraction started via Groq | raw_len=%d", len(image_b64))

    try:
        # Extract MIME type and clean raw base64 data
        mime_type, clean_b64 = parse_base64_payload(image_b64)

        # Reconstruct the exact Data URI string required by LLM vision specs
        formatted_data_url = f"data:{mime_type};base64,{clean_b64}"

        # Get Groq client instance
        vision_llm = get_groq_vision_client()

        # Construct Multimodal LangChain HumanMessage
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        """Analyze this medical image and extract only clinically relevant information.
                        
                        Return concise structured text containing:
                        - Patient details
                        - Diagnosis
                        - Symptoms
                        - Vital signs
                        - Lab results with values and units
                        - Medications and dosages
                        - Doctor instructions
                        - Important findings
                        
                        Do not explain your reasoning.
                        Do not use <think>.
                        Do not speculate.
                        If something is unreadable, write [unclear].
                        Preserve exact numbers, units, medication names, and dosages."""
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": formatted_data_url
                    },
                },
            ]
        )

        # Invoke model
        response = vision_llm.invoke([message])
        extracted_text = response.content.strip()

        logger.info(
            "✓ Groq Vision extraction completed | chars=%d | mime=%s",
            len(extracted_text),
            mime_type,
        )
        return extracted_text

    except Exception:
        logger.exception("Groq Vision extraction failed")
        return ""  