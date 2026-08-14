# app/core/llm.py
import os
import threading
from llama_cpp import Llama

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading Biomistral Fine Tuned model...")

llm = Llama(
    model_path=settings.MODEL_PATH,
    n_ctx=3072,
    n_threads=os.cpu_count(),
    n_batch=512,
    verbose=False
)

# Three different services share this one Llama object: chat_service and
# rag_chat_service call llm.create_chat_completion(...), while agent_node
# calls llm(...) directly with a grammar — a different call style entirely.
# llama.cpp keeps internal KV-cache state on the object between calls to
# avoid recomputing prompts from scratch. Mixing unrelated prompts/call
# styles back-to-back on that shared state (with no reset) can cause
# expensive cache-recompute stalls or corrupted-looking output.
#
# llm_lock ensures only one caller ever runs inference at a time.
# Each caller should also run `llm.reset()` right before generating —
# see chat_service.py / rag_chat_service.py / agent_node.py.
llm_lock = threading.Lock()

logger.info("Biomistral Fine Tuned model loaded.")