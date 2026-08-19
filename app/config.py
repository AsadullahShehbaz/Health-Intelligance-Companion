from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # LangSmith Configs
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str = "default"


    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # ── Auth ──────────────────────────────────────────────────────────────
    HF_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60          # short-lived access token (was 15, too short for slow local inference)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7             # longer-lived refresh token
    RESET_TOKEN_EXPIRE_HOURS: int = 1              # password-reset token TTL
    VERIFY_TOKEN_EXPIRE_HOURS: int = 48            # email-verify token TTL

    # ── Model & CORS (sensible dev defaults) ──────────────────────────────
    LLM_MODEL: str = r"C:\Users\jason\.cache\models\biomistral-Q4_K_M.gguf"
    LLM_BASE_URL: str = "http://127.0.0.1:8080/v1"
    LLM_API_KEY: str = "api-key"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── Email / SMTP (leave unset for dev — emails are logged to console) ─
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True

    SERP_API_KEY : str
    GROQ_API_KEY : str
    GROQ_MODEL: str = "openai/gpt-oss-120b"  # fast & reliable free tool-calling model
    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
