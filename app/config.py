from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str
    QDRANT_URL: str
    QDRANT_API_KEY: str

    # ── Auth ──────────────────────────────────────────────────────────────
    GROQ_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15          # short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7             # longer-lived refresh token
    RESET_TOKEN_EXPIRE_HOURS: int = 1              # password-reset token TTL
    VERIFY_TOKEN_EXPIRE_HOURS: int = 48            # email-verify token TTL

    # ── Model & CORS (sensible dev defaults) ──────────────────────────────
    MODEL_PATH: str = r"C:\Users\jason\.cache\models\biomistral-Q4_K_M.gguf"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ── Email / SMTP (leave unset for dev — emails are logged to console) ─
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
