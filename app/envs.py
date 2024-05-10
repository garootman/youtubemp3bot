# getting ENV variables
import os

from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv("TG_TOKEN")
print("TG_TOKEN", TG_TOKEN)

ADMIN_ID = os.getenv("ADMIN_ID")
print("ADMIN_ID", ADMIN_ID)


AUDIO_PATH = "./audios"

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)
