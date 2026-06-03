import json
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)



app = FastAPI(title="Server_V2", version="1.0.0")

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")

client = OpenAI(api_key=OPENAI_API_KEY)


def read_personality() -> str:
    personality_file = BASE_DIR / "summery.txt"

    if not personality_file.exists():
        return "You are a helpful AI assistant."

    return personality_file.read_text(encoding="utf-8").strip()


PERSONALITY = read_personality()


def get_conversation_file(session_id: str) -> Path:
    return MEMORY_DIR / f"{session_id}.json"


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

        logger.info(
            f"Session ID: {session_id} | Message: {request.message}"
        )

        conversation = load_conversation(session_id)

        messages = [
            {"role": "system", "content": PERSONALITY},
            *conversation,
            {"role": "user", "content": request.message},
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_completion_tokens=150
        )

        assistant_message = response.choices[0].message.content

        conversation.extend([
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": assistant_message}
        ])

        save_conversation(session_id, conversation)

        logger.info(
            f"Response: {assistant_message} | Session ID: {session_id}"
        )

        return ChatResponse(
            response=assistant_message,
            session_id=session_id
        )

    except Exception as e:
        logger.exception("Chat API failed")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.post("/sessions")
def list_of_sessions():
    sessions = []

    for file in MEMORY_DIR.glob("*.json"):
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
