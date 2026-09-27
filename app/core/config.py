from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # Application
    # ==========================
    APP_NAME: str = "KWARIHUB"
    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str

    # ==========================
    # Authentication
    # ==========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ==========================
    # File Upload
    # ==========================
    STORAGE_PATH: str = "storage"
    PRODUCT_IMAGE_PATH: str = "storage/products"
    AVATAR_PATH: str = "storage/avatars"

    # ==========================
    # Email
    # ==========================
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "KWARIHUB"

    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # ==========================
    # Celery
    # ==========================
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/0"

    # ==========================
    # Monnify Payment Gateway
    # ==========================
    MONNIFY_BASE_URL: str = "https://sandbox.monnify.com"
    MONNIFY_API_KEY: str
    MONNIFY_SECRET_KEY: str
    MONNIFY_CONTRACT_CODE: str

    # ==========================
    # Payment
    # ==========================
    PAYMENT_PROVIDER: str = "MONNIFY"
    PAYMENT_EXPIRY_MINUTES: int = 30
    CURRENCY: str = "NGN"

    # ==========================
    # Frontend
    # ==========================
    FRONTEND_URL: str = "http://localhost:3000"

    # ==========================
    # Redis
    # ==========================
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # ==========================
    # Settings
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()