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
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from worker import process_task
from aiogram.utils.keyboard import InlineKeyboardBuilder
  

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
    AUDIO_PATH,
    PAY_LINK,
    TG_TOKEN,
    USAGE_PERIODIC_LIMIT,
    USAGE_TIMEDELTA_HOURS,
)
from tgmediabot.paywall import AccessControlService
from tgmediabot.taskmanager import TaskManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


db = SessionLocal
create_db()
# Base.metadata.create_all(bind=engine)


uacs = AccessControlService(db, USAGE_TIMEDELTA_HOURS, USAGE_PERIODIC_LIMIT)
taskman = TaskManager(db)
chatman = ChatManager(db)


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


def bump(message: Message) -> None:
    logger.info(f"Bumping chat for chat id {message.chat.id}")
    logger.debug(f"Bumping chat with message {message}")
    message_dict = message.dict()
    message_dict["full_name"] = message.from_user.full_name
    chatman.bump_noban(message.chat.id, message_dict=message_dict)
    logger.info("Finished bumping chat with message")


class BotState(StatesGroup):
    waiting_for_feedback = State()
    waiting_for_payment = State()


@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    bump(message)
    await message.answer(hello_msg.format(message.from_user.full_name))
    logger.info(f"User {message.from_user.full_name} started the bot")


@form_router.message(Command("feedback"))
async def feedback_command_handler(message: Message, state: FSMContext) -> None:
    await message.answer(feedback_msg)
    # await FeedbackState.waiting_for_feedback.set()
    bump(message)
    await state.set_state(BotState.waiting_for_feedback)
    logger.info(f"User {message.from_user.full_name} is sending feedback")


@form_router.message(Command("thanks"))
async def thanks_command_handler(message: Message, state: FSMContext) -> None:
    bump(message)
    with open("thanks_msg.txt", "r") as f:
        thanks_msg = f.read()
    await message.answer(thanks_msg, parse_mode=ParseMode.MARKDOWN)
    # await FeedbackState.waiting_for_feedback.set()
    logger.info(f"User {message.from_user.full_name} said thanks")
    
@form_router.message(Command("donate"))
async def donta_start_handler(message: Message, state: FSMContext) -> None:
    builder = InlineKeyboardBuilder()  
    builder.button(text=f"Оплатить 1 ⭐️", pay=True)  
    keyb = builder.as_markup()
    prices = [LabeledPrice(label="XTR", amount=1)]  

    
    
    await message.answer_invoice(  
        title="Поддержка канала",  
        description="Поддержать канал на 1 звёзд!",  
        prices=prices,  
        provider_token="",  
        payload="channel_support",  
        currency="XTR",  
        reply_markup=keyb,  
    )
    
@form_router.pre_checkout_query(F.invoice_payload == "channel_support")
async def pre_checkout_query(query: PreCheckoutQuery) -> None:
    # if your product is available for sale,
    # confirm that you are ready to accept payment
    await query.answer(ok=True)
    logger.info(f"Pre checkout query OK: {query}")
    
@form_router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot) -> None:
    """
    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer("Thanks. Your payment has been refunded.")
    """
    await message.answer("Thanks. Your payment has been received!")

@form_router.message(Command("stars"))
async def check_star_balance(message: Message, bot: Bot) -> None:
    bot_star_txns = await bot.get_star_transactions()
    logger.info(f"Bot star transactions: {bot_star_txns}")
    
    


"""
@form_router.message(Command("cancel"))
async def delete_chat_history(message: Message, state: FSMContext) -> None:
    await state.clear()


@form_router.message(Command("subscribe"))
async def payment_command_handler(message: Message, state: FSMContext) -> None:
    # gives a link to make payment
    # switches to payment state
    bump(message)
    msg = (
        "You can make a payment here: "
        + PAY_LINK
        + "\n\nAfter subscribing, send a screenshot of the payment here."
    )
    await message.answer(msg)
    await state.set_state(BotState.waiting_for_payment)
    logger.info(
        f"User {message.from_user.id}: {message.from_user.full_name} is subscribing"
    )


@form_router.message(BotState.waiting_for_payment)
async def payment_message_handler(message: Message, state: FSMContext) -> None:
    # await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    await message.forward(ADMIN_ID)
    await message.answer(
        "Your message was forwarded to the admin chat, await for confirmation. Usually takes 1-2 hours."
    )
    await state.clear()
    logger.info(
        f"User {message.from_user.id}: {message.from_user.full_name} sent payment"
    )
"""


@form_router.message(BotState.waiting_for_feedback)
async def feedback_message_handler(message: Message, state: FSMContext) -> None:
    # await bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    logger.info(f"Forwarding message to admin chat")
    logger.debug(f"Message: {message}")
    await message.forward(ADMIN_ID)
    await message.answer(feedback_done)
    await state.clear()
    logger.info(
        f"User {message.from_user.id}: {message.from_user.full_name} sent feedback"
    )


@form_router.message()
async def msg_handler(message: Message) -> None:
    logger.info(f"Processing message")
    logger.debug(f"Message: {message}")
    bump(message)
    links = extract_urls(message.text)
    if not links:
        await message.reply(no_yt_links)
        logger.info("No youtube links found in the message, returning")
        return
    url = links[0]
    logger.info(f"Extracted url: {url}")
    task = taskman.create_task(
        user_id=message.from_user.id, chat_id=message.chat.id, url=url
    )
    queue_len = len(taskman.get_current_queue())
    logger.info(f"Created task {task.id}, current queue length: {queue_len}")

    nt = process_task.delay(task.id)
    logger.info(f"Task {task.id} sent to work queue: {nt}")
    msg = f"Task added to queue, position: {queue_len}"
    await message.answer(msg)

    """
    platform = extract_platform(url)
    if platform != "youtube":
        await message.reply("Only YouTube links are supported")
        return
    media_type, media_id = extract_youtube_info(url)

    if not media_type:
        await message.reply("Failed to extract video ID from the link")
        return
    

    access = uacs.check_access(message.from_user.id)

    if not access:
        await message.answer(
            usage_exceeded.format(USAGE_PERIODIC_LIMIT, USAGE_TIMEDELTA_HOURS)
        )
        return
    
    

    paid_till = uacs.get_user_subscription(message.from_user.id)

    if paid_till:
        expires_in = paid_till - utcnow()
        await message.answer(unlimited_until.format(expires_in))

    else:
        user_usage = USAGE_PERIODIC_LIMIT - uacs.get_user_tasks_in_hours(
            message.from_user.id, USAGE_TIMEDELTA_HOURS
        )
        await message.answer(task_added.format(user_usage, USAGE_TIMEDELTA_HOURS))

    return
    """


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
