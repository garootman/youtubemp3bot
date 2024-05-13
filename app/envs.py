# getting ENV variables
import os

from dotenv import load_dotenv

load_dotenv()

AUDIO_PATH = "./audios"
if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)

MAX_FILE_SIZE = 48 * 1024 * 1024  # 48 MB
DURATION_STR = "00:50:00"  # 50 minutes

TG_TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
if not TG_TOKEN:
    raise ValueError("No TG_TOKEN set in .env")
if not ADMIN_ID:
    raise ValueError("No ADMIN_ID set in .env")


REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("No REDIS_URL set in .env")

POSTGRES_URL = os.getenv("POSTGRES_URL")
if not POSTGRES_URL:
    raise ValueError("No POSTGRES_URL set in .env")

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("No REDIS_URL set in .env")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
if not REDIS_PASSWORD:
    raise ValueError("No REDIS_PASSWORD set in .env")


ENV = os.getenv("ENV", "PROD")
if ENV.lower() == "dev":
    print("Running in dev mode")
    POSTGRES_URL = "sqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/0"

elif ENV.lower() == "test":
    print("Running in TEST mode")
    POSTGRES_URL = "postgresql://postgres:postgres@localhost:22432/tgytmp3"
    REDIS_URL = "redis://:XP9Dg3BhtJ@localhost:22379/1"
else:
    print("Running in PROD mode:", ENV)


print(".env read successfully")
