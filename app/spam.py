# separate file for sending results to user
import asyncio
import os
import sys
import time

from envs import (
    ADMIN_ID,
    AUDIO_PATH,
    DURATION_STR,
    FFMPEG_TIMEOUT,
    MAX_FILE_SIZE,
    TG_TOKEN,
)
from telebot import TeleBot

bot = TeleBot(TG_TOKEN)

from taskmanager import TaskManager

taskman = TaskManager()

tg_message_txt = """Hi 👋 bot admin here! Some updates here:
1. Now works for stream records too
2. Files are now named after YT videos
3. Fixed some bugs 

Please let me know if you have any issues using /feedback command."""


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
    send_upd_messages(ids, tg_message_txt, only_admin=ADMIN_ONLY)
