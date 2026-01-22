from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseModel):
    provider: str = "local"
    local_path: str = "./data/artifacts"
    s3_bucket: str | None = None
    s3_endpoint: str | None = None


class DatabaseSettings(BaseModel):
    url: str = "sqlite:///./data/metadata.db"


class AuthSettings(BaseModel):
    enabled: bool = True
    api_key: str = "dev-key"


class LimitsSettings(BaseModel):
    max_upload_bytes: int = 10 * 1024 * 1024
    max_pages: int = 300
    max_text_length: int = 1_000_000


class ObservabilitySettings(BaseModel):
    otlp_endpoint: str | None = None
    service_name: str = "vectorless-rag-service"
    json_logs: bool = True


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VRS_", env_nested_delimiter="__")

    env: str = "dev"
    storage: StorageSettings = Field(default_factory=StorageSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    limits: LimitsSettings = Field(default_factory=LimitsSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    enable_llm_navigation: bool = False
    request_timeout_seconds: int = 30


settings = Settings()
