from telebot import TeleBot

from envs import ADMIN_ID, AUDIO_PATH, TG_TOKEN

bot = TeleBot(TG_TOKEN)

filename = AUDIO_PATH + "/jdS9sY983rU.mp3"

x = bot.send_audio(
    chat_id=ADMIN_ID,
    audio=open(filename, "rb"),
    caption="Caption description",
    title="filename.mp3",
)

print(x.audio.file_id)
