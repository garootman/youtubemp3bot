# getting ENV variables
import logging
import os

from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


load_dotenv()

AUDIO_PATH = "./audio"

MAX_FILE_SIZE = 48 * 1024 * 1024  # 48 MB
FFMPEG_TIMEOUT = 60  # 60 seconds
FREE_MINUTES_MAX = 4 * 60  # 4 hours

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


PROXY_TOKEN = os.getenv("PROXY_TOKEN")
if not PROXY_TOKEN:
    raise ValueError("No PROXY_TOKEN set in .env")

ENV = os.getenv("ENV", "PROD")
if ENV.lower() == "dev":
    logger.warning("Running in DEV mode")
    POSTGRES_URL = "sqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/0"
else:
    logger.warning("Running in PROD mode")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("No GOOGLE_API_KEY set in .env")


PAY_LINK = os.getenv("PAY_LINK", "")
if not PAY_LINK:
    raise ValueError("No PAY_LINK set in .env")

logger.info(".env read successfully")
