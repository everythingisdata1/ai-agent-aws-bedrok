from backend.src.config.app_config import AgentConfig
from backend.src.config.memory_loader import get_file


def read_personality(agent_conf: AgentConfig) -> str:
    personality_file = get_file(f"summary.txt", agent_conf)

    if not personality_file.exists():
        return "You are a helpful AI assistant."

    return personality_file.read_text(encoding="utf-8").strip()
