from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

load_dotenv(dotenv_path='hello_agent/.env')

root_agent = LlmAgent(
    name="agent_kaltim",
    model="gemini-2.0-flash",
    description="agent mencari informasi dan berita di kalimantan timur.",
    instruction="Anda adalah asisten yang membantu mencari informasi dan berita terkini di Kalimantan Timur. Gunakan alat pencarian 'google_search' untuk menemukan informasi yang relevan.",
    tools=[google_search]
)