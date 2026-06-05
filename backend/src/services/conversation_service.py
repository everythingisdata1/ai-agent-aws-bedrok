import json
import logging
from typing import Dict, TypeAlias

from backend.src.config.app_config import AgentConfig
from backend.src.config.memory_loader import get_file, save_file

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

Messages: TypeAlias = Dict[str, str]
Conversation: TypeAlias = list[Messages]


class ConversationService:
    MAX_MESSAGES = 50

    def __init__(self, agent_conf: AgentConfig):
        self.agent_conf: AgentConfig = agent_conf

    @staticmethod
    def _get_file_name(session_id: str) -> str:
        return f"conversation_{session_id}.json"

    def load_conversation(self, session_id: str) -> Conversation:
        log.info(f"Loading conversation for session :: {session_id}.")
        file_path = get_file(self._get_file_name(session_id),
                             self.agent_conf)

        if not file_path.exists():
            return []
        try:
            return json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON for session {session_id}: {e}")
            return []

        except OSError as e:
            log.error(f"Failed to read session {session_id}: {e}")
            return []

    def save_conversation(self, session_id: str, messages: list[Dict[str, str]]) -> None:
        log.info(f"Saving conversation for session {session_id}.")
        save_file(self._get_file_name(session_id),
                  json.dumps(
                      messages[-self.MAX_MESSAGES:],
                      ensure_ascii=False,
                      indent=4
                  ),
                  self.agent_conf)
