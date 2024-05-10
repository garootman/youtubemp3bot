# code for asyncronous telegram bot on python
# replies to start with "hello world" message
# gets user messages, extracts anything looking like youtube links
# extracts video id, checks if video is available
# lookups for id in mp3 folder, if not found downloads video
# converts video to mp3
# sends mp3 file to user

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from envs import ADMIN_ID, AUDIO_PATH, TG_TOKEN
from messages import doing_job, hello_msg, no_yt_links
from ytlib import download_audio, extract_urls, universal_check_link

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
    audio_file = f"{AUDIO_PATH}/{video_id}.mp3"
    # find corresponding mp3 file in AUDIO_PATH
    if os.path.exists(audio_file):
        # send audio file as a file, not audio
        # await message.reply_audio(audio_file)
        file = types.FSInputFile(audio_file)  # , filename=pseduo_name)
        await message.answer_document(file)
        return
    # download video
    await message.reply(doing_job)
    try:
        vid_title, audio_file = download_audio(video_id, AUDIO_PATH)
    except Exception as e:
        await message.reply(f"Error downloading video: {str(e)}")
        return

    file = types.FSInputFile(audio_file, filename=vid_title + ".mp3")
    await message.answer_document(file)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("runnning bot...")
    asyncio.run(main())
