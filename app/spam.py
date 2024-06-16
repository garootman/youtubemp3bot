# separate file for sending results to user
import asyncio
import os
import random
import sys
import time

from envs import ADMIN_ID, TG_TOKEN
from telebot import TeleBot

bot = TeleBot(TG_TOKEN)

from taskmanager import TaskManager

taskman = TaskManager()

tg_message_txt = """Hi 👋 bot admin here with updates:
1. Now it is not only YouTube, but also TikTok, OK, VK and some other sites - feel free to try!
2. Dayly downloads are unlimited now
3. maximum video duration is now 4 hours

go ahead and try: https://vk.com/search/video?q=rickroll&z=video281711238_456240128

Feel free to leave your /feedback"""


def send_upd_messages(ids, tg_message_txt, only_admin=True):
    sent = 0
    errors = 0
    if only_admin:
        print("Sending to admin only")
        ids = [ADMIN_ID]

    for user_tg_id in ids:
        if not user_tg_id:
            continue
        try:
            bot.send_message(chat_id=user_tg_id, text=tg_message_txt)
            time.sleep(5)
            print(f"Sent message to {user_tg_id}")
            sent += 1
        except Exception as e:
            errors += 1
            print(f"Error sending message to {user_tg_id}: {e}")

    print(f"Sent {sent} messages total, {errors} errors.")


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
