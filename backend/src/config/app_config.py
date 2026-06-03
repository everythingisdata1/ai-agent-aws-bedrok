import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class AgentConfig(BaseModel):
    env: Literal["local", "cloud"] = os.getenv("APP_ENV", "local")

    @property
    def local_data_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def bucket_name(self) -> str:
        return "ai_assistant_agent"


@lru_cache
def get_agent_config() -> AgentConfig:
    return AgentConfig()
