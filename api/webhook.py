import logging
import os
import random

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from fastapi import FastAPI, HTTPException, Request
from pydantic import ValidationError

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]  # токен задаётся в Vercel → Environment Variables
WEBHOOK_PATH = "/api/webhook"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

PEOPLE = {
    "behbudiy": {
        "name": "Mahmudxo‘ja Behbudiy",
        "bio": (
            "Jadid ma’rifatparvari, dramaturg va publitsist. "
            "U yangi usul maktablari va matbuot rivojiga hissa qo‘shgan. "
            "“Padarkush” dramasi uning mashhur asarlaridan biridir."
        ),
    },
    "avloniy": {
        "name": "Abdulla Avloniy",
        "bio": (
            "Ma’rifatparvar shoir, pedagog va jamoat arbobi. "
            "Yangi usul maktablarini tashkil etish hamda ta’limni rivojlantirish "
            "bilan shug‘ullangan. “Turkiy Guliston yoxud axloq” asari mashhur."
        ),
    },
    "fitrat": {
        "name": "Abdurauf Fitrat",
        "bio": (
            "Jadid adabiyotining yirik vakili, yozuvchi, olim va dramaturg. "
            "Uning ijodida ma’rifat, milliy uyg‘onish va jamiyat taraqqiyoti "
            "mavzulari muhim o‘rin tutadi."
        ),
    },
    "cholpon": {
        "name": "Abdulhamid Cho‘lpon",
        "bio": (
            "Shoir, yozuvchi, dramaturg va tarjimon. O‘zbek adabiyoti rivojiga "
            "katta hissa qo‘shgan; “Kecha va kunduz” romani bilan tanilgan."
        ),
    },
}

QUIZ = {
    "avloniy": {
        "question": "“Turkiy Guliston yoxud axloq” asarini kim yozgan?",
        "options": ["Abdulla Avloniy", "Mahmudxo‘ja Behbudiy", "Abdurauf Fitrat"],
        "answer": 0,
        "note": "Bu asar Abdulla Avloniyning tarbiya va axloq mavzusidagi mashhur asaridir.",
    },
    "behbudiy": {
        "question": "“Padarkush” dramasining muallifi kim?",
        "options": ["Abdulhamid Cho‘lpon", "Mahmudxo‘ja Behbudiy", "Abdulla Avloniy"],
        "answer": 1,
        "note": "“Padarkush” Mahmudxo‘ja Behbudiy qalamiga mansub drama.",
    },
    "jadid": {
        "question": "Jadid ma’rifatparvarlari faoliyatining muhim yo‘nalishi qaysi edi?",
        "options": ["Ta’lim va ma’rifatni rivojlantirish", "Faqat savdoni kengaytirish", "Faqat harbiy yurishlar"],
        "answer": 0,
        "note": "Jadidlar yangi usuldagi ta’lim va ma’rifat orqali jamiyatni rivojlantirishga intilgan.",
    },
}


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Jadidlar", callback_data="people")],
            [InlineKeyboardButton(text="🧠 Viktorina", callback_data="quiz")],
            [InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about")],
        ]
    )


def people_menu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=person["name"], callback_data=f"person:{key}")]
        for key, person in PEOPLE.items()
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu")]
        ]
    )


def quiz_keyboard(question_key: str) -> InlineKeyboardMarkup:
    question = QUIZ[question_key]
    buttons = [
        [
            InlineKeyboardButton(
                text=option,
                callback_data=f"answer:{question_key}:{index}",
            )
        ]
        for index, option in enumerate(question["options"])
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show_menu(message: Message, greeting: str = "") -> None:
    text = f"{greeting}\n\n" if greeting else ""
    text += "Jadidlar tarixi botiga xush kelibsiz! Bo‘limni tanlang:"
    await message.answer(text, reply_markup=main_menu())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    full_name = html.quote(message.from_user.full_name)
    await show_menu(message, f"Assalomu alaykum, {full_name}! 👋")


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "Bo‘limlarni ko‘rish uchun /start buyrug‘ini yuboring. "
        "Jadidlar bo‘limida qisqa tarjimai hollar, viktorinada esa "
        "bilimingizni sinash uchun savollar bor."
    )


@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "Jadidlar tarixi botiga xush kelibsiz! Bo‘limni tanlang:",
            reply_markup=main_menu(),
        )


@dp.callback_query(F.data == "people")
async def people_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "Ma’lumot olish uchun jadid nomini tanlang:",
            reply_markup=people_menu(),
        )


@dp.callback_query(F.data.startswith("person:"))
async def person_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    person_key = (callback.data or "").partition(":")[2]
    person = PEOPLE.get(person_key)
    if person is None:
        await callback.message.edit_text("Bu ma’lumot topilmadi.", reply_markup=back_to_menu())
        return

    await callback.message.edit_text(
        f"<b>{person['name']}</b>\n\n{person['bio']}",
        reply_markup=back_to_menu(),
    )


@dp.callback_query(F.data == "quiz")
async def quiz_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    question_key = random.choice(list(QUIZ))
    await callback.message.edit_text(
        f"🧠 <b>Viktorina</b>\n\n{QUIZ[question_key]['question']}",
        reply_markup=quiz_keyboard(question_key),
    )


@dp.callback_query(F.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    _, question_key, answer_text = (callback.data or "").split(":", maxsplit=2)
    question = QUIZ.get(question_key)
    if question is None or not answer_text.isdigit():
        await callback.answer("Javobni tekshirib bo‘lmadi.", show_alert=True)
        return

    is_correct = int(answer_text) == question["answer"]
    result = "✅ To‘g‘ri!" if is_correct else "❌ Bu safar xato."
    await callback.answer("To‘g‘ri!" if is_correct else "Yana urinib ko‘ring!")
    await callback.message.edit_text(
        f"{result}\n\n{question['note']}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Yana savol", callback_data="quiz")],
                [InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu")],
            ]
        ),
    )


@dp.callback_query(F.data == "about")
async def about_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "Bu bot jadid ma’rifatparvarlari va ularning merosi haqida "
            "qisqa ma’lumot beradi. Viktorina orqali bilimingizni ham sinab ko‘ring.",
            reply_markup=back_to_menu(),
        )


app = FastAPI()


@app.post(WEBHOOK_PATH)
@app.post("/webhook")
async def handle_webhook(request: Request) -> dict[str, bool]:
    try:
        payload = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    try:
        update = Update.model_validate(payload, context={"bot": bot})
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="Invalid Telegram update") from exc

    await dp.feed_update(bot, update)
    return {"ok": True}