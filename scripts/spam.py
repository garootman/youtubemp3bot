# separate file for sending results to user
import asyncio
import os
import random
import sys
import time

from telebot import TeleBot
from telebot.apihelper import ApiException

from tgmediabot.envs import ADMIN_ID, TG_TOKEN

bot = TeleBot(TG_TOKEN)

from tgmediabot.chatmanager import ChatManager
from tgmediabot.taskmanager import TaskManager

taskman = TaskManager()
chatman = ChatManager()

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

with open("text_spam.txt", "r") as myfile:
    tg_message_txt = myfile.read()


def send_upd_messages(ids, tg_message_txt, only_admin=True):
    sent = 0
    errors = 0
    if only_admin:
        logger.info("Sending to admin only")
        ids = [ADMIN_ID]
    logger.info(f"Sending to {len(ids)} users")
    for user_tg_id in ids:
        if not user_tg_id:
            continue
        try:
            bot.send_message(
                chat_id=user_tg_id, text=tg_message_txt, parse_mode="Markdown"
            )
            time.sleep(5)
            logger.info(f"Sent message to {user_tg_id}")
            sent += 1
            chatman.bump_noban(user_tg_id)
        except Exception as e:
            errors += 1
            logger.info(f"Error sending message to {user_tg_id}: {e}")
            if "bot was blocked" in str(e).lower():
                chatman.ban_chat(user_tg_id)

    logger.info(f"Sent {sent} messages total, {errors} errors.")


if __name__ == "__main__":
    # get GO_SEND parameter from command line
    # if GO_SEND is True, send messages to all users
    # if GO_SEND is False, send message only to admin
    GO_SEND = False
    if len(sys.argv) > 1:
        GO_SEND = sys.argv[1].lower() == "true"
    ADMIN_ONLY = not GO_SEND

    ids = taskman.get_unique_user_ids()
    # shuffle ids
    isd = random.sample(ids, len(ids))
    send_upd_messages(ids, tg_message_txt, only_admin=ADMIN_ONLY)
