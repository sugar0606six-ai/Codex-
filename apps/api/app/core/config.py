from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WestMonth Amazon Opportunity Cloud"
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/westmonth_amazon"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 720
    openai_api_key: str | None = None
    amazon_data_provider: str = "stub"
    rainforest_api_key: str | None = None
    rainforest_base_url: str = "https://api.rainforestapi.com/request"
    rainforest_max_results: int = 5
    admin_email: str = "admin@westmonth.local"
    admin_password: str = "ChangeMe123!"
    skill_catalog_tool_path: str = "app/skills/westmonth-catalog-analyzer/scripts/catalog_tool.py"
    enable_live_sources: bool = False
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
