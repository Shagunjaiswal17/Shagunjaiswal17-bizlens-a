import os
from typing import List

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    USE_PYDANTIC_SETTINGS = True
except ImportError:
    from pydantic import BaseModel
    USE_PYDANTIC_SETTINGS = False


if USE_PYDANTIC_SETTINGS:
    class Settings(BaseSettings):
        """Application configuration loaded from environment or defaults."""
        PROJECT_NAME: str = "BizLens AI"
        VERSION: str = "1.0.0"
        API_V1_STR: str = "/api"
        PORT: int = 8000

        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        GEMINI_MODEL: str = "gemini-2.5-flash"
        GEMINI_TIMEOUT_SECONDS: int = 30
        GEMINI_MAX_RETRIES: int = 3

        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bizlens.db")

        JWT_SECRET: str = os.getenv("JWT_SECRET", "bizlens-ai-hackathon-super-secret-key-change-in-prod-2026")
        JWT_ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

        CHAIN_ID: int = 80002
        WEB3_PROVIDER_URI: str = os.getenv("WEB3_PROVIDER_URI", "https://rpc-amoy.polygon.technology")
        AMOY_FALLBACK_RPC: str = "https://polygon-amoy.drpc.org"
        CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
        BACKEND_WALLET_PRIVATE_KEY: str = os.getenv("BACKEND_WALLET_PRIVATE_KEY", "")

        UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024
        ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".pdf"]

        FREE_TIER_MONTHLY_SCAN_LIMIT: int = 50

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )
    settings = Settings()
else:
    class Settings(BaseModel):
        """Fallback configuration using BaseModel + os.getenv."""
        PROJECT_NAME: str = "BizLens AI"
        VERSION: str = "1.0.0"
        API_V1_STR: str = "/api"
        PORT: int = int(os.getenv("PORT", "8000"))

        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        GEMINI_MODEL: str = "gemini-2.5-flash"
        GEMINI_TIMEOUT_SECONDS: int = 30
        GEMINI_MAX_RETRIES: int = 3

        DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bizlens.db")

        JWT_SECRET: str = os.getenv("JWT_SECRET", "bizlens-ai-hackathon-super-secret-key-change-in-prod-2026")
        JWT_ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

        CHAIN_ID: int = 80002
        WEB3_PROVIDER_URI: str = os.getenv("WEB3_PROVIDER_URI", "https://rpc-amoy.polygon.technology")
        AMOY_FALLBACK_RPC: str = "https://polygon-amoy.drpc.org"
        CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
        BACKEND_WALLET_PRIVATE_KEY: str = os.getenv("BACKEND_WALLET_PRIVATE_KEY", "")

        UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
        MAX_FILE_SIZE_BYTES: int = 15 * 1024 * 1024
        ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".pdf"]

        FREE_TIER_MONTHLY_SCAN_LIMIT: int = 50

    settings = Settings()
