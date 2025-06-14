import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agents.engine import _run_agent, create_agent
from .agents.schema import ChatRequest, ChatResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the MCP Agent API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/status")
async def status():
    return {"status": "running", "version": "1.0.0"}

@app.post("/chat")
async def chat_agent(chat: ChatRequest) -> ChatResponse:
    """
    Endpoint to chat with the MCP agent.
    Accepts a query and returns tool calls, tool responses, and agent response.
    """
    # Create the agent if it doesn't exist
    agent = create_agent()
    response = await _run_agent(chat.query, chat.session_id or str(uuid.uuid4()), agent)
    if not response:
        raise HTTPException(status_code=500, detail="Failed to get a response from the agent.")
    return response
