""" Code for asyncronous telegram bot on python
replies to start with "hello world" message
gets user messages, extracts anything looking like youtube links
extracts video id, checks if video is available
lookups for id in mp3 folder, if not found downloads video
converts video to mp3
sends mp3 file to user
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from envs import ADMIN_ID, AUDIO_PATH, TG_TOKEN
from models import SessionLocal, Task
from worker import process_task
from ytlib import extract_urls, universal_check_link

hello_msg = "Hello, {}! This bot is designed to download youtube videos and send them to you as mp3 files. To get started, send me a youtube link."
no_yt_links = "No youtube links found in the message"
doing_job = "Processing video..."


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(hello_msg.format(message.from_user.full_name))


@dp.message()
async def msg_handler(message: Message) -> None:
    links = extract_urls(message.text)
    yt_ids = [
        universal_check_link(link) for link in links if universal_check_link(link)
    ]
    if not yt_ids:
        await message.reply(no_yt_links)
        return
    video_id = yt_ids[0]
    # add a task to database
    db = SessionLocal()
    task = Task(user_id=message.from_user.id, yt_id=video_id, msg_text=message.text)
    db.add(task)
    db.commit()
    process_task.delay(task.id)
    print(f"Task {task.id} added, yt_id: {video_id}")
    return


async def main() -> None:
    from aiogram.client.default import DefaultBotProperties

    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("runnning bot...")
    asyncio.run(main())
