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
def send_video(*args, **kwargs):
    # universdal fnc to wrap send msg
    logger.debug(f"Sending videos: {args}, {kwargs}")
    msg = bot.send_video(*args, **kwargs)
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


def mass_send_audio(
    chat_id, audio_list, mode, title, format_type="audio", width=0, height=0
):
    if not format_type:
        format_type = "audio"
    sent = []
    logger.debug(
        f"Sending {len(audio_list)} {format_type} files to {chat_id} with mode {mode}:\n{audio_list}"
    )
    for i, audio in enumerate(audio_list):
        if len(audio_list) > 1:
            tit = f"{title}_{i+1}"
        else:
            tit = f"{title}"

        if mode == "MEDIA":
            audio_object = InputMediaAudio(media=audio)
            if format_type == "audio":
                xi = send_audio(chat_id=chat_id, audio=audio_object, caption=tit)
            else:
                xi = send_video(
                    chat_id=chat_id,
                    video=audio_object,
                    caption=tit,
                    width=width,
                    height=height,
                )

        elif mode == "FILE":
            if os.path.exists(audio):
                filesize = os.path.getsize(audio)
                logger.debug(f"Sending to {chat_id} file {audio} with size {filesize}")
                with open(audio, "rb") as audio_object:
                    if format_type == "audio":
                        xi = send_audio(
                            chat_id=chat_id, audio=audio_object, caption=tit
                        )
                    else:
                        xi = send_video(
                            chat_id=chat_id,
                            video=audio_object,
                            caption=tit,
                            width=width,
                            height=height,
                            timeout=60,
                        )

                # audio_object = open(audio, "rb")
            else:
                logger.error(f"File {audio} does not exist!")
                sent.append(None)
                continue
        # if there is more than one audio file, add index to title

        if xi:
            logger.info(
                f"Sent {format_type} chunk {i} of {len(audio_list)} to {chat_id}, sleeping 1 sec."
            )
            time.sleep(1)
        else:
            logger.error(f"Error sending {format_type} by {mode}")
            xi = None
        sent.append(xi)
    if not all(sent):
        logger.error(f"Not all data was sent to chat {chat_id} with mode {mode}")
        delete_messages(chat_id, sent)
        sent = []
    return sent
