import os
import aiohttp
from aiohttp import web

BOT_TOKEN = os.environ["BOT_TOKEN"]
API = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def handle(request):
    update = await request.json()
    message = update.get("message")
    if message and "text" in message:
        chat_id = message["chat"]["id"]
        async with aiohttp.ClientSession() as session:
            await session.post(f"{API}/sendMessage",
                json={"chat_id": chat_id, "text": message["text"]})
    return web.Response(text="ok")

app = web.Application()
app.router.add_post("/", handle)