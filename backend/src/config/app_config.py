from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic.v1 import BaseSettings


class AgentConfig(BaseSettings):
    app_env: Literal["local", "cloud"] = "local"
    openai_api_key: str
    bucket_name: str = "ai_assistant_agent"

    class Config:
        env_file = r"E:\AI\AIProduction\twin-app\backend\.env"
        env_file_encoding = "utf-8"

    @property
    def local_data_dir(self) -> Path:
        return Path(__file__).resolve().parents[3] / "memory_data"

@lru_cache
def get_agent_config() -> AgentConfig:
    return AgentConfig()