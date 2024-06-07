# getting ENV variables
import os

from dotenv import load_dotenv

load_dotenv()

AUDIO_PATH = "./audios"
if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)

MAX_FILE_SIZE = 48 * 1024 * 1024  # 48 MB
DURATION_STR = "00:50:00"  # 50 minutes
FFMPEG_TIMEOUT = 60  # 60 seconds

TG_TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
if not TG_TOKEN:
    raise ValueError("No TG_TOKEN set in .env")
if not ADMIN_ID:
    raise ValueError("No ADMIN_ID set in .env")


USAGE_TIMEDELTA_HOURS = int(os.getenv("USAGE_TIMEDELTA_HOURS", 24))
USAGE_PERIODIC_LIMIT = int(os.getenv("USAGE_PERIODIC_LIMIT", 10))


POSTGRES_URL = os.getenv("POSTGRES_URL")
if not POSTGRES_URL:
    raise ValueError("No POSTGRES_URL set in .env")

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("No REDIS_URL set in .env")

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
if not REDIS_PASSWORD:
    raise ValueError("No REDIS_PASSWORD set in .env")


USE_PROXY = os.getenv("USE_PROXY", "")
if USE_PROXY:
    USE_PROXY = USE_PROXY.strip().upper()
    print("Using proxies param:", USE_PROXY)

LOCAL_PROXY_URL = os.getenv("LOCAL_PROXY_URL", "http://localhost:8888")
print("Local proxy url:", LOCAL_PROXY_URL)


ENV = os.getenv("ENV", "PROD")
if ENV.lower() == "dev":
    print("Running in dev mode")
    POSTGRES_URL = "sqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/0"
else:
    print("Running in PROD mode:", ENV)


PAY_LINK = os.getenv("PAY_LINK", "")
if not PAY_LINK:
    raise ValueError("No PAY_LINK set in .env")

print(".env read successfully")
