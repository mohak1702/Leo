from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.tools.computer import open_application

app = FastAPI(
    title="LEO Backend",
    version="0.1.0",
)

# Allow the LEO desktop frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CommandRequest(BaseModel):
    command: str


@app.get("/")
def root():
    return {
        "name": "LEO",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/command")
def handle_command(request: CommandRequest):
    command = request.command.strip()

    normalized_command = command.lower()

    if normalized_command in [
        "open calculator",
        "launch calculator",
        "start calculator",
    ]:
        result = open_application("Calculator")

        return {
            **result,
            "command": command,
        }

    return {
        "success": True,
        "command": command,
        "message": f'LEO received: "{command}"',
        "status": "completed",
    }