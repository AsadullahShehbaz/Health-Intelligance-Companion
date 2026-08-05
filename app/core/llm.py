from llama_cpp import Llama

from app.config import settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

logger.info("Loading Llama model...")

llm = Llama(
    model_path=settings.MODEL_PATH,
    n_ctx=2048,
)

logger.info("Llama model loaded.")