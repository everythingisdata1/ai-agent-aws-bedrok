import os
import uuid
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

# Load environment variables

load_dotenv(override=True)

# Validate OpenAI API Key

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY:", ("****" + OPENAI_API_KEY[-4:] if OPENAI_API_KEY else "Not) Found"))

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is missing"
    )

# FastAPI App

app = FastAPI(title="Conversational AI API",
              description="API for conversational AI applications",
              version="1.0.0", )

# CORS Configuration

cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(CORSMiddleware,
                   allow_origins=cors_origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"], )

# OpenAI Client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


# Load Personality Prompt


def load_personality():
    try:
        with open("../data/summary.txt", "r", encoding="utf-8", ) as f:
            return f.read().strip()

    except FileNotFoundError:
        return ("You are a helpful AI assistant.")


PERSONALITY = load_personality()


# Request Model
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


# Response Model
class ChatResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


# Root Endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Conversational AI API!"}


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Chat Endpoint

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:

        # Generate session id if missing
        session_id = (request.session_id or str(uuid.uuid4()))

        # Build messages
        messages = [{"role": "system", "content": PERSONALITY, },
                    {"role": "user", "content": request.message, }]

        # OpenAI Request
        response = (client.chat.completions.create(model="gpt-4o-mini",
                                                   messages=messages,
                                                          max_tokens=150,
                                                          temperature=0.2)
                    )

        ai_response = response.choices[0].message.content

        return ChatResponse(response=(ai_response.strip() if ai_response else "No response generated."),
                            session_id=session_id)

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


# Run App


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, )
