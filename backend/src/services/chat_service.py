import logging
import uuid

from fastapi import HTTPException
from openai import OpenAI

from backend.src.config.app_config import AgentConfig
from backend.src.model import ChatRequest, ChatResponse
from backend.src.services.conversation_service import ConversationService

log = logging.getLogger(__name__)
from backend.src.services.personality_service import read_personality


class ChatService:
    def __init__(self, agent_conf):
        log.info(f"Initializing ChatService with provided agent configuration. {id(self)}")
        self.agent_conf: AgentConfig = agent_conf
        self.conversation_services = ConversationService(agent_conf)
        self.client = OpenAI(api_key=self.agent_conf.openai_api_key)

    def chat(self, request: ChatRequest):
        try:
            session_id = request.session_id or str(uuid.uuid4())

            log.info(f"Session ID: {session_id} | Message: {request.message}")

            conversation = self.conversation_services.load_conversation(session_id)

            messages = [{"role": "system", "content": read_personality(self.agent_conf)},
                        *conversation,
                        {"role": "user", "content": request.message}]

            response = self.client.chat.completions.create(model="gpt-4o-mini",
                                                           messages=messages,
                                                           max_completion_tokens=150)

            assistant_message = (response.choices[0].message.content or "No Response Generated").strip()

            conversation.extend([{"role": "user", "content": request.message},
                                 {"role": "assistant", "content": assistant_message}])

            self.conversation_services.save_conversation(session_id, conversation)

            log.info(f"Response: {assistant_message} | Session ID: {session_id}")

            return ChatResponse(response=assistant_message, session_id=session_id)

        except Exception as e:
            log.exception("Chat API failed")
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
