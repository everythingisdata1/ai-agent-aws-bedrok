import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from backend.src.config.app_config import get_agent_config
from backend.src.config.memory_loader import get_file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

agent_conf = get_agent_config()


def get_conversation_file(session_id: str) -> Path:
    return get_file(f"{session_id}.json", agent_conf)


def load_conversation(session_id: str) -> list:
    file_path = get_conversation_file(session_id)

    logger.info(f"Loading conversation from: {file_path}")
    if not file_path.exists():
        return []
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load conversation {session_id}: {e}")
        return []


def save_conversation(session_id: str, conversation: list) -> None:
    file_path = get_conversation_file(session_id)
    file_path.write_text(
        json.dumps(conversation, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )
