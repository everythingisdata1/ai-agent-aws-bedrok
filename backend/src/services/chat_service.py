import json
import logging
import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from backend.src.config.app_config import get_agent_config
from backend.src.services.conversation_service import load_conversation, save_conversation
from backend.src.services.personality_service import read_personality

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

app = FastAPI(title="Server_V2", version="1.0.0")

agent_conf = get_agent_config()

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment variables.")
    raise EnvironmentError("OPENAI_API_KEY is required to run the server.")

client = OpenAI(api_key=OPENAI_API_KEY)


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


@app.get("/")
def greeting():
    return {"message": "Hello from Server_V2!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(f"Session ID: {session_id} | Message: {request.message}")

        conversation = load_conversation(session_id)

        messages = [{"role": "system", "content": read_personality(agent_conf)},
                    *conversation,
                    {"role": "user", "content": request.message}]

        response = client.chat.completions.create(model="gpt-4o-mini",
                                                  messages=messages,
                                                  max_completion_tokens=150)

        assistant_message = (response.choices[0].message.content or "No Response Generated").strip()

        conversation.extend([{"role": "user", "content": request.message},
                             {"role": "assistant", "content": assistant_message}])

        save_conversation(session_id, conversation)

        logger.info(f"Response: {assistant_message} | Session ID: {session_id}")

        return ChatResponse(response=assistant_message, session_id=session_id)

    except Exception as e:
        logger.exception("Chat API failed")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/sessions")
def list_of_sessions():
    sessions = []

    for file in agent_conf.local_data_dir.glob("*.json"):
        session_id = file.stem

        logger.info(
            f"Processing session: {session_id} | File: {file}"
        )

        try:
            conversation = json.loads(
                file.read_text(encoding="utf-8")
            )

            if conversation:
                sessions.append({
                    "session_id": session_id,
                    "message_count": len(conversation),
                    "last_message": conversation[-1]["content"]
                })

        except Exception as e:
            logger.error(
                f"Failed to read session {session_id}: {e}"
            )

    return {"sessions": sessions}
