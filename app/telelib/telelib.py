import time

from assist import retry
from envs import TG_TOKEN
from telebot import TeleBot
from telebot.types import InputMediaAudio

bot = TeleBot(TG_TOKEN)


@retry()
def send_msg(*args, **kwargs):
    # universdal fnc to wrap send msg
    return bot.send_message(*args, **kwargs)


@retry()
def send_audio(*args, **kwargs):
    # universdal fnc to wrap send msg
    return bot.send_audio(*args, **kwargs)


@retry()
def delete_messages(chat_id, msg_batch):
    for msg in msg_batch:
        if msg:
            try:
                bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception as e:
                print(f"Error deleting message: {e}")
                return False
    return True


def mass_send_audio(chat_id, audio_list, mode, title):
    sent = []
    for i, audio in enumerate(audio_list):
        audio_object = audio if mode == "MEDIA" else open(audio, "rb")
        # if there is more than one audio file, add index to title
        if len(audio_list) > 1:
            tit = f"{title}_{i+1}.m4a"
        else:
            tit = f"{title}.m4a"
        xi = send_audio(
            chat_id=chat_id,
            audio=audio_object,
            title=tit,
        )
        if xi:
            print(
                f"Sent audio chunk {i} of {len(audio_list)} to {chat_id}, sleeping 1 sec."
            )
            time.sleep(1)
        else:
            error = f"Error sending voice by {mode}: {e}"
            print(error)
            xi = None
        sent.append(xi)
    if not all(sent):
        print(f"Not all data was sent to chat {chat_id} with mode {mode}")
        delete_messages(chat_id, sent)
        sent = []
    return sent
