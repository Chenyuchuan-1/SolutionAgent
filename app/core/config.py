from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_text_model: str = "gpt-5.5"
    openai_text_url: str = ""
    deepseek_summary_base_url: str = "https://api.gpugeek.com/v1"
    deepseek_summary_model: str = "Vendor3/DeepSeek-V4-Flash"
    openai_image_model: str = "gpt-image-2"
    openai_image_url: str = ""
    openai_image_edit_url: str = ""
    openai_image_api_key: str = ""
    openai_image_auth_enabled: bool = False
    openai_image_include_size: bool = False
    openai_image_response_format: str = ""
    tavily_api_key: str = ""
    exa_api_key: str = ""
    exa_search_type: str = "auto"
    exa_num_results: int = 10
    exa_content_mode: str = "highlights"
    brave_api_key: str = ""
    serpapi_api_key: str = ""
    searxng_endpoint: str = ""
    storage_root: Path = Path("storage/runs")
    default_image_size: str = "1536x1024"
    default_image_quality: str = "high"
    image_generation_concurrency: int = 3
    mock_image_fallback: bool = False
    request_timeout: float = 20.0
    mineru_mcp_url: str = "https://mineru.net/api/v4/extract/task"
    mineru_api_token: str = ""
    mineru_model_version: str = "vlm"
    mineru_language: str = "ch"
    mineru_enable_formula: bool = True
    mineru_enable_table: bool = True
    mineru_is_ocr: bool = False
    mineru_timeout: float = 600.0
    mineru_poll_interval: float = 5.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    return settings
