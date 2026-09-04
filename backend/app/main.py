from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.agent.agent import Agent


app = FastAPI(
    title="LEO Backend",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str


agent = Agent()


@app.get("/")
def root():
    return {
        "name": "LEO",
        "status": "online",
        "version": "0.2.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "agent": "local",
        "model": "llama3.2",
    }


@app.post("/command")
def handle_command(request: CommandRequest):
    command = request.command.strip()

    if not command:
        return {
            "success": False,
            "error": "Command cannot be empty.",
        }

    return agent.run(command)