import json
import logging
from typing import Dict, TypeAlias

from src.config.app_config import AgentConfig
from src.config.file_loader import FileLoader

log = logging.getLogger(__name__)

Message: TypeAlias = Dict[str, str]
Conversation: TypeAlias = list[Message]


class ConversationService:
    """
    Handles loading and saving conversation history.
    """

    MAX_MESSAGES = 50

    def __init__(self, agent_conf: AgentConfig):
        self.agent_conf = agent_conf
        self.file_service = FileLoader(agent_conf)

    def load_conversation(self, session_id: str) -> Conversation:
        log.info("Loading conversation | session_id=%s", session_id, )

        content = self.file_service.get_file(session_id)

        if content is None:
            log.info("No conversation found | session_id=%s", session_id, )
            return []
        try:
            conversation: Conversation = json.loads(content)
            log.info("Conversation loaded | session_id=%s | messages=%s", session_id, len(conversation), )

            return conversation
        except json.JSONDecodeError:
            log.exception("Invalid conversation JSON | session_id=%s", session_id, )
            return []

    def save_conversation(self, session_id: str, messages: Conversation, ) -> None:

        log.info("Saving conversation | session_id=%s | messages=%s", session_id, len(messages), )

        self.file_service.save(session_id,
                               json.dumps(messages[-self.MAX_MESSAGES:],
                                          ensure_ascii=False,
                                          indent=2,
                                          ), )

        log.info("Conversation saved successfully | session_id=%s", session_id, )
