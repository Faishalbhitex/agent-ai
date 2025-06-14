from pydantic import BaseModel
from typing import Optional, List

class ToolCall(BaseModel):
    tool_name: str
    args: dict

class ToolResponse(BaseModel):
    tool_name: str
    results: dict

class AgentResponse(BaseModel):
    response: str

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    tool_calls: Optional[list[ToolCall]] = None
    tool_responses: Optional[list[ToolResponse]] = None
    response:  Optional[AgentResponse] = None
