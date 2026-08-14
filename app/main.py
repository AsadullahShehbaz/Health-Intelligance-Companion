from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.rag.embedder import get_embedder
from app.api import auth, chat, rag, agent
from app.config import settings
from app.db.lifespan import lifespan as db_lifespan
from app.db.session import init_models
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_settings():

    required = [
        settings.DATABASE_URL,
        settings.SECRET_KEY,
        settings.QDRANT_URL,
        settings.GROQ_API_KEY,
        settings.LLM_API_KEY,
    ]

    if not all(required):
        logger.error("Missing required environment variables — aborting startup")
        raise RuntimeError("Missing required environment variables")

    logger.info("✓ All required environment variables present")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("▶ Application lifespan starting...")

    # DB backends (LangGraph checkpointer + store) must be set up before the
    # async SQLAlchemy tables and embedder warm-up run.
    async with db_lifespan(app):
        validate_settings()
        # get_embedder()
        # app.state.llm = load_llm()
        # app.state.embedder = load_embedder()      # new
        # app.state.agent = build_health_agent()    # new
        await init_models()

        logger.info("✓ Application startup complete — ready to serve requests")
        yield
        logger.info("■ Application shutting down...")


app = FastAPI(
    title="Medical Chat API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(rag.router)
app.include_router(agent.router)   # new

@app.get("/")
async def root():
    return {"message": "API Running"}