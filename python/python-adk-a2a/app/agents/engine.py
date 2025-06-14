from dotenv import load_dotenv
import uuid
import logging

from local_mcp.agent import root_agent as local_agent_mcp, toolset
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

from app.agents.schema import ChatResponse, ToolCall, ToolResponse, AgentResponse

# Ignore warnings from ADK and Gemini APIs
logging.getLogger("google.adk.runners").setLevel(logging.ERROR)
logging.getLogger("google_genai.types").setLevel(logging.ERROR)

load_dotenv()

async def _run_agent(query: str, session_id: str, agent: LlmAgent) -> ChatResponse:
    APP_NAME = "local_mcp_agent"
    USER_ID = str(uuid.uuid4())

    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
    )
    if not session:
        session = await session_service.create_session(
            state={},
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id,
        )
    
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        artifact_service=artifact_service,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part.from_text(text=query)])

    chat_response = ChatResponse()
    tool_calls = []
    tool_responses = []
    agent_response = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content
    ):
        if event.get_function_calls():
            for tool_call in event.get_function_calls():
                tool_calls.append(ToolCall(
                    tool_name=tool_call.name,
                    args=tool_call.args
                ))
        if event.get_function_responses():
            for tool_resp in event.get_function_responses():
                tool_responses.append(ToolResponse(
                    tool_name=tool_resp.name,
                    results=tool_resp.response
                ))
        if event.is_final_response():
            if event.content and event.content.parts:
                agent_response = AgentResponse(response=event.content.parts[0].text)
        
    chat_response.tool_calls = tool_calls if tool_calls else None
    chat_response.tool_responses = tool_responses if tool_responses else None
    chat_response.response = agent_response 

    return chat_response

def create_agent():
    """
    Create and return the local MCP agent.
    This function is used to initialize the agent for use in the API.
    """
    return local_agent_mcp  # or any other agent you want to create