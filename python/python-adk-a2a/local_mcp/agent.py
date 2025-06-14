from pathlib import Path

from google.adk.agents import LlmAgent
from .custom_adk_mcp import CustomMCPToolset as MCPToolset, StdioServerParameters

from .prompt import DB_MCP_PROMPT

# IMPORTANT: Dynamically compute the absolute path to your server.py script
#PATH_TO_YOUR_MCP_SERVER_SCRIPT = str((Path(__file__).parent / "server.py").resolve())
PATH_TO_YOUR_MCP_SERVER_SCRIPT = 'C://Users//User//python-adk-a2a//local_mcp//server.py'

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="db_mcp_client_agent",
    instruction=DB_MCP_PROMPT,
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="python",  # Changed from "python3" to "python" for Windows
                args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT],
            )
            # tool_filter=['list_tables'] # Optional: ensure only specific tools are loaded
        )
    ],
)

# Prepare toolset mcp when not using adk web
toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",  # Changed from "python3" to "python" for Windows
        args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT],
    ),
    tool_filter=["list_tables", "query_table"]  # Optional: filter specific tools
)