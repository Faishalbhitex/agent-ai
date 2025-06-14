
import uuid
from dotenv import load_dotenv
import logging

from mcp_agent.agent import root_agent, toolset
from local_mcp.agent import root_agent as local_agent_mcp, toolset
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

# Ignore warnings from ADK and Gemini APIs
logging.getLogger("google.adk.runners").setLevel(logging.ERROR)
logging.getLogger("google_genai.types").setLevel(logging.ERROR)


load_dotenv()


async def query_agent_mcp(query: str, agent: LlmAgent) -> dict:
    APP_NAME = "local_mcp_agent"
    USER_ID = str(uuid.uuid4())
    SESSION_ID = str(uuid.uuid4())
    print(f"\n<<< User Query: {query}")
    session_service= InMemorySessionService()
    artifact_service = InMemoryArtifactService()

    session = await session_service.create_session(
        state={},
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        artifact_service=artifact_service,
        session_service=session_service
    )

    content = types.Content(role='user', parts=[types.Part.from_text(text=query)])
    final_response = ""
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    ):
        if event.get_function_calls():
            tool_call = event.get_function_calls()
            for call in tool_call:
                print(f"\n>>> Tool call: {call.name}\n Args: {call.args}")
        if event.get_function_responses():
            tool_resp = event.get_function_responses()
            for resp in tool_resp:
                tool_name = resp.name
                result = resp.response
                print(f"\n<<< Tool response:{tool_name} -> Result: {result}")
        if event.is_final_response():
            if event.content and event.content.parts:
                # Ensure we have content and parts before accessing
                final_response = event.content.parts[0].text
    
    print(f"\n<<< Agent: {final_response}")
    print("\n>>> Closing MCP server connection...")
    await toolset.close()
    print("\n<<< Cleanup complete.")

async def main():
    exit = ['quit', 'exit', 'q']
    while True:
        query = input("\nEnter your query for the MCP agent: ")
        if query.lower() in exit:
            print("Exiting the MCP agent.")
            break
        #await query_agent_mcp(query, root_agent)
        await query_agent_mcp(query, local_agent_mcp)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())