import logging

from src.config.app_config import AgentConfig
from src.config.file_loader import FileLoader

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def read_personality(agent_conf: AgentConfig) -> str:
    file_loader = FileLoader(agent_conf)

    content = file_loader.load_by_name("summary.txt")

    return content.strip() if content else "DEFAULT_PERSONALITY"
