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
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, InlineKeyboardButton
from worker import process_task, enrich_task
from tgmediabot.taskprocessor import TaskProcessor

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
    PAY_LINK,
    TG_TOKEN,
    USAGE_PERIODIC_LIMIT,
    USAGE_TIMEDELTA_HOURS,
)

from tgmediabot.paywall import PayWallManager
from tgmediabot.taskmanager import TaskManager

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


def bump(message: Message) -> None:
    logger.info(f"Bumping chat for chat id {message.chat.id}")
    logger.debug(f"Bumping chat with message {message}")
    message_dict = message.dict()
    message_dict["full_name"] = message.from_user.full_name
    chatman.bump_noban(message.chat.id, message_dict=message_dict)
    logger.info("Finished bumping chat with message")


class BotState(StatesGroup):
    waiting_for_feedback = State()
    

@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    bump(message)
    await message.answer(hello_msg.format(message.from_user.full_name))
    logger.info(f"User {message.from_user.full_name} started the bot")


@form_router.message(Command("feedback"))
async def feedback_command_handler(message: Message, state: FSMContext) -> None:
    await message.answer(feedback_msg)
    bump(message)
    await state.set_state(BotState.waiting_for_feedback)
    logger.info(f"User {message.from_user.full_name} is sending feedback")


@form_router.message(Command("thanks"))
async def thanks_command_handler(message: Message, state: FSMContext) -> None:
    bump(message)
    with open("thanks_msg.txt", "r") as f:
        thanks_msg = f.read()
    await message.answer(thanks_msg, parse_mode=ParseMode.MARKDOWN)
    logger.info(f"User {message.from_user.full_name} said thanks")
    
    
    
@form_router.message(Command("limits"))
async def limits_command_handler(message: Message, state: FSMContext) -> None:
    # check user current premium status, and limits left
    premium = payman.get_user_premium_sub(message.from_user.id)
    limits = payman.check_daily_limit_left(message.from_user.id)
    free = "free" if not premium else "premium"
    msg = f"You use {free} version. Limits left: {limits}"
    
    if premium:
        msg += f"\nPremium expires in {premium.end_date}"
    else:
        msg += "\nIf you want more, get /premium !"
    await message.reply(msg)
        
    

    
@form_router.message(Command("premium"))
async def premium_msg_handler(message: Message, state: FSMContext) -> None:
    
    # check user current premium status
    # if IS premium, return message with current premium status and expiration date + limits
    
    premium = payman.get_user_premium_sub(message.from_user.id)
    limits = payman.check_daily_limit_left(message.from_user.id)

    if premium:
        msg = f"Your premium access expires in {premium.end_date}. Limits left: {limits}"
        await message.reply(msg)
        return
    
    
    # if NOT premium, return message with premium packages
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Day: 1⭐️", callback_data="premium_day")
    builder.button(text="Week: 7⭐️", callback_data="premium_week")
    builder.button(text="Month: 30⭐️", callback_data="premium_month")
    markup = builder.as_markup()
    await message.reply("Choose your premium package:", reply_markup=markup)    
   
    
#@form_router.callback_query(text_startswith="premium_")
@form_router.callback_query(F.data.startswith("premium_"))
async def premium_day_callback(call: CallbackQuery, state: FSMContext) -> None:
    if call.data == "premium_day":
        title = "Premium Access - 1 Day"
        description = "Get access to premium features for 1 day."
        price = 1
    elif call.data == "premium_week":
        title = "Premium Access - 1 Week"
        description = "Get access to premium features for 1 week."
        price = 7
    elif call.data == "premium_month":
        title = "Premium Access - 1 Month"
        description = "Get access to premium features for 1 month."
        price = 30
        
    builder = InlineKeyboardBuilder()
    builder.button(text=f"Pay {price} ⭐️", pay=True)
    prices = [LabeledPrice(label="XTR", amount=price)]

    await call.message.answer_invoice(
        title=title,
        description=description,
        prices=prices,  
        provider_token="",  
        payload= "premium_access",
        currency="XTR",  
        reply_markup=builder.as_markup(),  
    )

    
@form_router.pre_checkout_query(F.invoice_payload == "premium_access")
async def pre_checkout_query(query: PreCheckoutQuery) -> None:
    # if your product is available for sale,
    # confirm that you are ready to accept payment
    await query.answer(ok=True)
    logger.info(f"Pre checkout query OK: {query}")
    
    
@form_router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot) -> None:
    # add premium access to user, based of amount paid
    
    await bot.refund_star_payment(
        user_id=message.from_user.id,
        telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
    )
    await message.answer("Thanks. Your payment has been refunded.")

    amount = message.successful_payment.total_amount
    if amount == 1:
        pack = "day"
    elif amount == 7:
        pack = "week"
    elif amount == 30:
        pack = "month"
    prem_end = payman.buy_premium(user_id=message.from_user.id, package_type=pack)
    msg = f"Thanks. You have purchased {pack} premium access. Expires in {prem_end}.\nYou can check it with /limits command."
    await message.answer(msg)

    # notify admin about new premium user
    await bot.send_message(ADMIN_ID, f"New premium user: @{message.from_user.username}, paid {amount} stars for {pack} package.")
    



@form_router.message(Command("stars"))
async def check_star_balance(message: Message, bot: Bot) -> None:
    bot_star_txns = await bot.get_star_transactions()
    logger.info(f"Bot star transactions: {bot_star_txns}")
    


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
    
    user_limits = payman.check_daily_limit_left(message.from_user.id)
    user_premium = payman.get_user_premium_sub(message.from_user.id)
    
    if user_limits <= 0 and not user_premium:
        msg = f"You spent all your daily limits. Get premium access to continue, or wait a little - we share 20 free uses every day."
        await message.reply(msg)
        return
    
    url = links[0]

    
    # {"m4a": 1, "mp3": 2, "360": 3, "720": 4, "1080": 5}
    logger.info(f"Extracted url: {url}")
    task = taskman.create_task(
        user_id=message.from_user.id, chat_id=message.chat.id, url=url
    )
    
    # user_limits = payman.check_daily_limit_left(message.from_user.id)
    user_premium = payman.get_user_premium_sub(message.from_user.id)
    priority = 0 if user_premium else 1
    queue_len = len(taskman.get_current_queue())
    logger.info(f"Created task {task.id}, current queue length: {queue_len}")
    
    # start a celery task 'process_task' with task id and priority
    #nt = process_task.apply_async(args=[task.id], priority=priority)
    rich_task = enrich_task.delay(task.id)
    rich_dict = rich_task.__dict__
    msg = f"Got task data: {rich_dict}"
    await message.answer(msg)

    
    #nt = process_task.delay(task.id, priority=priority)
    
    #logger.info(f"Task {task.id} sent to work queue: {nt}")
    #msg = f"Task added to queue, position: {queue_len}"
    #await message.answer(msg)




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
