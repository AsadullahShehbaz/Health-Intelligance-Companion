# app/core/llm.py
import os
from llama_cpp import Llama

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading Biomistral Fine Tuned model...")

llm = Llama(
    model_path=settings.MODEL_PATH,
    n_ctx=2048,
    n_threads=os.cpu_count(),
    n_batch=512,
    verbose=False
)

logger.info("Biomistral Fine Tuned model loaded.")