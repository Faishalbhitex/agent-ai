from dotenv import load_dotenv
import os

from google.adk.agents import LlmAgent
from .prompt import instruction_system_sql
from .tools import AVAILABLE_TOOLS 
from google.genai import types

load_dotenv(dotenv_path="retail_agent_sql/.env")

llm = os.getenv("GEMINI_MODEL")

retail_faishal_agent_sql = LlmAgent(
    name="retail_faishal_agent_sql",
    model=llm,
    description="""
    AI Agent untuk manajemen database retail Faishal Bhitex. Membantu owner Shal mengelola inventory, produk, dan analisis bisnis melalui operasi database yang cepat dan efisien.
    """,
    instruction=instruction_system_sql(),
    tools=AVAILABLE_TOOLS,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.2,
    )
)

root_agent = retail_faishal_agent_sql