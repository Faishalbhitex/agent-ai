import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from .tools import (
    get_harga_dagang,
    get_list_tipe_produk,
    update_harga_dagang,
    change_nama_produk,
    add_produk,
    get_nama_produk,
    get_list_type_produk_nama_dan_harga,
    delete_produk
)
from .prompt import PROMPT_ADMIN_AGENT

load_dotenv()

llm = os.getenv("GEMINI_MODEL")

admin_agent = LlmAgent(
    model=llm,
    name="retail_admin_agent",
    description="Agent untuk mengelola data retail",
    instruction=PROMPT_ADMIN_AGENT,
    tools=[
        get_harga_dagang,
        get_list_tipe_produk,
        update_harga_dagang,
        change_nama_produk,
        add_produk,
        get_nama_produk,
        get_list_type_produk_nama_dan_harga,
        delete_produk
    ],
)


root_agent = admin_agent