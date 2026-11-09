import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_PATH = "/api/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==== ЗДЕСЬ ВАША ЛОГИКА ИЗ main.py ====
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    await message.answer("Привет! Бот работает на Vercel 🚀")

@dp.message()
async def echo(message: Message):
    await message.answer(message.text)
# ======================================

def create_app():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    return app

app = create_app()