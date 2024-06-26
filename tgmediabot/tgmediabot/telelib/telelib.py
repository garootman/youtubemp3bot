import os
import time

from telebot import TeleBot
from telebot.types import InputMediaAudio

from tgmediabot.assist import retry
from tgmediabot.envs import TG_TOKEN

bot = TeleBot(TG_TOKEN)

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@retry()
def send_msg(*args, **kwargs):
    # universdal fnc to wrap send msg
    logger.debug(f"Sending message: {args}, {kwargs}")
    return bot.send_message(*args, **kwargs)


@retry()
def send_audio(*args, **kwargs):
    # universdal fnc to wrap send msg
    logger.debug(f"Sending audio: {args}, {kwargs}")
    msg = bot.send_audio(*args, **kwargs)
    return msg


@retry()
def delete_messages(chat_id, msg_batch):
    logger.debug(f"Deleting messages: {msg_batch}")
    for msg in msg_batch:
        if msg:
            try:
                bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception as e:
                logger.error(f"Error deleting message: {e}")
                return False
    return True


def mass_send_audio(chat_id, audio_list, mode, title):
    sent = []
    logger.debug(
        f"Sending {len(audio_list)} audio files to {chat_id} with mode {mode}:\n{audio_list}"
    )
    for i, audio in enumerate(audio_list):
        if mode == "MEDIA":
            audio_object = InputMediaAudio(media=audio)
        elif mode == "FILE":
            if os.path.exists(audio):
                audio_object = open(audio, "rb")
            else:
                logger.error(f"File {audio} does not exist!")
                sent.append(None)
                continue
        # if there is more than one audio file, add index to title
        if len(audio_list) > 1:
            tit = f"{title}_{i+1}"
        else:
            tit = f"{title}"
        xi = send_audio(
            chat_id=chat_id,
            audio=audio_object,
            caption=tit,
        )
        if xi:
            logger.info(
                f"Sent audio chunk {i} of {len(audio_list)} to {chat_id}, sleeping 1 sec."
            )
            time.sleep(1)
        else:
            logger.error(f"Error sending voice by {mode}")
            xi = None
        sent.append(xi)
    if not all(sent):
        logger.error("Not all data was sent to chat {chat_id} with mode {mode}")
        delete_messages(chat_id, sent)
        sent = []
    return sent
