import os
import asyncio
import uuid
import json

from admin_retail_agent.agent import admin_agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from google.genai import types




async def agent_query_and_response(query: str, agent: LlmAgent) -> str:
    APP="retail_agent"
    USER_ID=str(uuid.uuid4())
    SESSION_ID=str(uuid.uuid4())

    # buat session service
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # buat runner
    runner = Runner(
        app_name=APP,
        agent=agent,
        session_service=session_service,
    )

    print(f"\n>>> User Message: {query}")
    user_message = types.Content(role="user", parts=[types.Part.from_text(text=query)])
    agent_response = ""

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=user_message,
    ):
        # Tampilkan tool call jika ada
        if event.get_function_calls():
            for tool_call in event.get_function_calls():
                tool_name = tool_call.name
                tool_args = tool_call.args
                print(f"\n<<< Tool Call:\n  Name : {tool_name}\n  Args : {json.dumps(tool_args, indent=2, ensure_ascii=False)}")
        # Tampilkan tool response jika ada
        if event.get_function_responses():
            for tool_response in event.get_function_responses():
                tool_name = tool_response.name
                result_dict = tool_response.response
                print(f"\n>>> Tool Response:\n  Name   : {tool_name}\n  Result : {json.dumps(result_dict, indent=2, ensure_ascii=False)}")
        # Tampilkan final response jika ada
        if event.is_final_response():
            if event.content and event.content.parts:
                agent_response = event.content.parts[0].text
                print(f"\n>>> Final Response {agent.name}: {agent_response}")

async def main():
    print("#------- Start Agent Retail -------#")
    print("\nKetik './menu' untuk melihat command singkat.")
    while True:
        query = input("\n<<< User Input: ")
        end = ["exit", "quit", "keluar", "q"]
        command = query.lower().strip()
        if command in end:
            print("\n<<< Exit")
            break
        if command == "./list/tools":
            prompt_result_list_tools = (
                "Tolong tampilkan daftar tools yang tersedia beserta penjelasan singkat fungsinya untuk admin retail."
            )
            await agent_query_and_response(prompt_result_list_tools, agent_retail)
            continue
        if command == "./list/tipe_produk":
            prompt_result_list_tipe_produk = (
                "Tolong tampilkan semua tipe produk yang tersedia di toko beserta penjelasan singkatnya."
            )
            await agent_query_and_response(prompt_result_list_tipe_produk, agent_retail)
            continue
        if command == "./menu":
            print("\n<<< Menu:")
            print("# Command singkat:")
            print("\n**Command tanpa umum yang bisa dijalankan oleh user**:")
            print(" ./list/tools = menampilkan daftar tools agent AI beserta penjelasan singkatnya")
            print(" ./list/tipe_produk = menampilkan semua tipe produk yang tersedia di toko")
            print(" exit/quit/keluar/q = keluar dari program")
            print("\n**Command yang hanya bisa dijalankan oleh admin setelah memasukan kredinsial**:")
            print(" ./add <tipe_produk> | <nama_produk> | <harga_enceran>")
            print(" ./update <tipe_produk> | <nama_produk> | <harga_enceran_baru>")
            print(" ./change <tipe_produk> | <nama_produk_lama> | <nama_produk_baru>")
            print(" ./delete <tipe_produk> | <nama_produk>")
            continue

        admin_tools = ["./add", "./delete", "./update", "./change"]
        if any(command.startswith(tool) for tool in admin_tools):
            print("\n[!] Akses admin diperlukan. Silakan masukkan kredensial Anda.")
            nama_lengkap = input("Nama lengkap: ").strip().lower()
            email = input("Email: ").strip().lower()
            password = input("Password: ").strip()
            if (
                nama_lengkap == "faishal bhitex"
                and email == "faishalbhitexretail@gmail.com"
                and password == "muhammadf@isha11"
            ):
                try:
                    if command.startswith("./add"):
                        # ./add <tipe_produk> | <nama_produk> | <harga_enceran>
                        _, params = query.split(" ", 1)
                        tipe_produk, nama_produk, harga_enceran = [x.strip() for x in params.split("|")]
                        prompt = f"Tambahkan produk '{nama_produk}' dengan harga {harga_enceran} ke tipe produk '{tipe_produk}'."
                        await agent_query_and_response(prompt, agent_retail)
                        continue
                    if command.startswith("./update"):
                        # ./update <tipe_produk> | <nama_produk> | <harga_enceran_baru>
                        _, params = query.split(" ", 1)
                        tipe_produk, nama_produk, harga_enceran_baru = [x.strip() for x in params.split("|")]
                        prompt = f"Update harga produk '{nama_produk}' pada tipe produk '{tipe_produk}' menjadi {harga_enceran_baru}."
                        await agent_query_and_response(prompt, agent_retail)
                        continue
                    if command.startswith("./delete"):
                        # ./delete <tipe_produk> | <nama_produk>
                        _, params = query.split(" ", 1)
                        tipe_produk, nama_produk = [x.strip() for x in params.split("|")]
                        prompt = f"Hapus produk '{nama_produk}' dari tipe produk '{tipe_produk}'."
                        await agent_query_and_response(prompt, agent_retail)
                        continue
                    if command.startswith("./change"):
                        # ./change <tipe_produk> | <nama_produk_lama> | <nama_produk_baru>
                        _, params = query.split(" ", 1)
                        tipe_produk, nama_produk_lama, nama_produk_baru = [x.strip() for x in params.split("|")]
                        prompt = f"Ganti nama produk '{nama_produk_lama}' menjadi '{nama_produk_baru}' pada tipe produk '{tipe_produk}'."
                        await agent_query_and_response(prompt, agent_retail)
                        continue
                except Exception:
                    print("Format command salah. Silakan cek kembali. Contoh: ./add jenis rokok | la bold | 17000")
                    print("Silahkan ketik './menu' untuk melihat contoh command yang benar-nya.")
                    continue
            else:
                print("Akses ditolak. Anda tidak memiliki hak untuk menggunakan tools ini karena bukan owner/admin retail yang terdaftar.")
                continue
        # Jika bukan command khusus, teruskan ke agent
        await agent_query_and_response(query, agent_retail)
    print("#------- End Agent Retail -------#")

if __name__ == "__main__":
    asyncio.run(main())