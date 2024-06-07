""" Code for asyncronous telegram bot on python
replies to start with "hello world" message
gets user messages, extracts anything looking like youtube links
extracts video id, checks if video is available
lookups for id in mp3 folder, if not found downloads video
converts video to mp3
sends mp3 file to user
"""

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from assist import extract_urls, universal_check_link, utcnow
from envs import (
    ADMIN_ID,
    AUDIO_PATH,
    PAY_LINK,
    TG_TOKEN,
    USAGE_PERIODIC_LIMIT,
    USAGE_TIMEDELTA_HOURS,
)
from models import SessionLocal, Task, get_db, session_scope
from worker import get_user_subscribed, get_user_usage, process_task

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


class BotState(StatesGroup):
    waiting_for_feedback = State()
    waiting_for_payment = State()


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(hello_msg.format(message.from_user.full_name))


@form_router.message(Command("feedback"))
async def feedback_command_handler(message: Message, state: FSMContext) -> None:
    await message.answer(feedback_msg)
    # await FeedbackState.waiting_for_feedback.set()
    await state.set_state(BotState.waiting_for_feedback)


@form_router.message(Command("cancel"))
async def delete_chat_history(message: Message, state: FSMContext) -> None:
    # a command to delete chat history
    await state.clear()
    # await message.answer("Will clear chat history")


@form_router.message(Command("subscribe"))
async def payment_command_handler(message: Message, state: FSMContext) -> None:
    # gives a link to make payment
    # switches to payment state
    msg = (
        "You can make a payment here: "
        + PAY_LINK
        + "\n\nAfter subscribing, send a screenshot of the payment here."
    )
    await message.answer(msg)
    await state.set_state(BotState.waiting_for_payment)


@form_router.message(BotState.waiting_for_payment)
async def payment_message_handler(message: Message, state: FSMContext) -> None:
    # await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.forward(ADMIN_ID)
    await message.answer(
        "Your message was forwarded to the admin chat, await for confirmation. Usually takes 1-2 hours."
    )
    await state.clear()


@form_router.message(BotState.waiting_for_feedback)
async def feedback_message_handler(message: Message, state: FSMContext) -> None:
    # await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.forward(ADMIN_ID)
    await message.answer(feedback_done)
    await state.clear()


@form_router.message()
async def msg_handler(message: Message) -> None:
    links = extract_urls(message.text)
    if not links:
        await message.reply(no_yt_links)
        return
    url = links[0]
    if not universal_check_link(url):
        await message.reply(no_yt_links)
        return

    user_usage = get_user_usage(message.from_user.id, USAGE_TIMEDELTA_HOURS)
    unlimit = False
    subscribed_until = get_user_subscribed(message.from_user.id)
    if subscribed_until:
        print(f"User {message.from_user.id} is subscribed until {subscribed_until}")
        unlimit = subscribed_until > utcnow()

    if len(user_usage) >= USAGE_PERIODIC_LIMIT and not unlimit:
        await message.answer(
            usage_exceeded.format(USAGE_PERIODIC_LIMIT, USAGE_TIMEDELTA_HOURS)
        )
        return

    db = SessionLocal()
    task = Task(
        user_id=message.from_user.id, msg_text=message.text, url=url, yt_id="no_yt_id"
    )
    db.add(task)
    db.commit()
    process_task.delay(task.id)
    print(f"Task {task.id} added, url: {url}")
    db.close()

    if unlimit:
        expires_in = subscribed_until - utcnow()
        await message.answer(unlimited_until.format(expires_in))

    else:
        await message.answer(
            task_added.format(
                USAGE_PERIODIC_LIMIT - len(user_usage), USAGE_TIMEDELTA_HOURS
            )
        )

    return


async def main() -> None:
    from aiogram.client.default import DefaultBotProperties

    bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print("runnning bot...")
    asyncio.run(main())
