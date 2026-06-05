import logging
import uuid

from fastapi import HTTPException
from openai import OpenAI
from src.config.app_config import AgentConfig
from src.model import ChatRequest, ChatResponse
from src.services.conversation_service import ConversationService
from src.services.personality_service import read_personality

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class ChatService:

    def __init__(self, agent_conf: AgentConfig):
        log.info("Initializing ChatService | instance_id=%s", id(self), )
        self.agent_conf = agent_conf
        self.conversation_services = ConversationService(agent_conf)
        self.client = OpenAI(api_key=self.agent_conf.openai_api_key)

    def chat(self, request: ChatRequest) -> ChatResponse:
        log.info("Received request | instance_id=%s | session_id=%s | message=%s", id(self), request.session_id,
                 request.message, )

        try:
            session_id = request.session_id or str(uuid.uuid4())
            log.info("Loading conversation | session_id=%s", session_id)

            conversation = self.conversation_services.load_conversation(session_id) or []

            messages = [{"role": "system", "content": read_personality(self.agent_conf), },
                        *conversation,
                        {"role": "user", "content": request.message, }, ]
            log.info("Calling OpenAI API | session_id=%s | message_count=%s", session_id, len(messages), )

            response = self.client.chat.completions.create(model="gpt-4o-mini",
                                                           messages=messages,
                                                           max_completion_tokens=150, )

            assistant_message = (response.choices[0].message.content or "No Response Generated").strip()

            conversation.extend([{"role": "user", "content": request.message},
                                 {"role": "assistant", "content": assistant_message}, ])

            log.info("Saving conversation | session_id=%s", session_id)

            self.conversation_services.save_conversation(session_id=session_id,
                                                         conversation=conversation, )

            log.info("Response generated | session_id=%s | response_length=%s", session_id, len(assistant_message), )

            return ChatResponse(response=assistant_message, session_id=session_id, )

        except Exception as ex:
            log.exception("Chat request failed | session_id=%s", request.session_id, )

            raise HTTPException(status_code=500, detail=f"Error: {str(ex)}", ) from ex
