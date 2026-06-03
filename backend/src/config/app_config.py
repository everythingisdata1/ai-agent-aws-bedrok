from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class AgentConfig(BaseModel):
    env: Literal["Local", "Cloud"] = "Cloud"

    def memory(self):
        if self.env == "local":
            BASE_DIR = Path(__file__).resolve().parent
            MEMORY_DIR = BASE_DIR / "memory"
            MEMORY_DIR.mkdir(exist_ok=True)
            return MEMORY_DIR
        else:
            s3_bucket = ""
            return s3_bucket


@lru_cache
def get_agent_config():
    return AgentConfig
