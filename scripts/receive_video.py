""" Code for asyncronous telegram bot on python
replies to start with "hello world" message
gets user messages, extracts anything looking like youtube links
extracts video id, checks if video is available
lookups for id in mp3 folder, if not found downloads video
converts video to mp3
sends mp3 file to user
"""

import logging

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from worker import enrich_tp_task, process_task

from tgmediabot.assist import (
    extract_platform,
    extract_urls,
    extract_youtube_info,
    utcnow,
)
from tgmediabot.chatmanager import ChatManager
from tgmediabot.database import Base, SessionLocal, create_db, engine, session_scope
from tgmediabot.envs import (
    ADMIN_ID,
    OWNER_ID,
    PAY_LINK,
    TG_TOKEN,
    USAGE_PERIODIC_LIMIT,
    USAGE_TIMEDELTA_HOURS,
)
from tgmediabot.paywall import PayWallManager
from tgmediabot.taskmanager import TaskManager
from tgmediabot.taskprocessor import TaskProcessor

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

db = SessionLocal
create_db()

taskman = TaskManager(db)
chatman = ChatManager(db)
payman = PayWallManager(db)


hello_msg = "Hello, {}! This bot is designed to download youtube videos and send them to you as mp3 files. To get started, send me a youtube link."
no_yt_links = "No youtube links found in the message"
doing_job = "Processing video..."
feedback_msg = "Your next message will be sent to the feedback chat admin."
feedback_done = "Feedback sent to admin chat"
usage_exceeded = (
    "Sorry, you have reached the limit of {} uses per {} hours.\nYou can buy a monthly subscription to get unlimited uses here:\n"
    + PAY_LINK
    + "\n\nAlso, please use my Hamster Kombat code: https://t.me/hamstEr_kombat_bot/start?startapp=kentId62408647"
)
task_added = "Task added\nYou have {} uses left in this {} hours period."
unlimited_until = "You have unlimited uses, expires in {}"

form_router = Router()


@form_router.message(F.document)
async def process_inbound_document(message: Message) -> None:
    print(f"Received a message with document: {message}")
    msg = f"File ID is {message.document.file_id}"
    await message.answer(msg)


@form_router.message(F.video)
async def process_inbound_file(message: Message) -> None:
    print(f"Received a message with video: {message}")
    msg = f"Video file ID is {message.video.file_id}"
    await message.answer(msg)


async def main() -> None:
    from aiogram.client.default import DefaultBotProperties

    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    logger.info("Starting bot")
    asyncio.run(main())
