from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.config import settings
from app.db.session import init_models
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_settings():

    required = [
        settings.DATABASE_URL,
        settings.SECRET_KEY,
        settings.QDRANT_URL,
        settings.GROQ_API_KEY,
    ]

    if not all(required):
        raise RuntimeError("Missing required environment variables")


@asynccontextmanager
async def lifespan(app: FastAPI):

    validate_settings()

    await init_models()

    yield


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

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "API Running"}