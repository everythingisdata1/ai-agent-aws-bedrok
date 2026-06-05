import logging

print("main.py loaded", __name__)
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.config.app_config import get_agent_config
from src.model import ChatResponse, ChatRequest
from src.services import chat_service

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

agentService = chat_service.ChatService(agent_conf)


@app.get("/")
def greeting():
    return {"message": "Hello from Server_V2!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    print("Received chat request:", request)
    return agentService.chat(request)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main:app", port=8000, host="0.0.0.0")
