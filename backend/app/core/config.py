from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    app_name: str = Field(
        default="MusicGraph API",
        validation_alias="MUSICGRAPH_APP_NAME",
    )
    debug: bool = Field(
        default=True,
        validation_alias="MUSICGRAPH_DEBUG",
    )
    api_prefix: str = Field(
        default="/api",
        validation_alias="MUSICGRAPH_API_PREFIX",
    )
    use_mock_data: bool = Field(
        default=True,
        validation_alias="MUSICGRAPH_USE_MOCK_DATA",
    )
    cors_origins: str = Field(
        default="http://localhost:5173",
        validation_alias="MUSICGRAPH_CORS_ORIGINS",
    )

    neo4j_uri: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_NEO4J_URI",
    )
    neo4j_username: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_NEO4J_USERNAME",
    )
    neo4j_password: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_NEO4J_PASSWORD",
    )
    neo4j_database: str = Field(
        default="neo4j",
        validation_alias="MUSICGRAPH_NEO4J_DATABASE",
    )
    llm_provider: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_LLM_PROVIDER",
    )
    llm_api_key: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_LLM_API_KEY",
    )
    llm_base_url: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_LLM_BASE_URL",
    )
    llm_model: str | None = Field(
        default=None,
        validation_alias="MUSICGRAPH_LLM_MODEL",
    )

    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env", REPO_ROOT / ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
