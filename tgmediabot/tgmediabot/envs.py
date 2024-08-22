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

MAX_FILE_SIZE = 40 * 1024 * 1024  # 48 MB
FFMPEG_TIMEOUT = 60  # 60 seconds

TG_TOKEN = os.getenv("TG_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
OWNER_ID = os.getenv("OWNER_ID")
AGENT_ID = os.getenv("AGENT_ID")

assert TG_TOKEN, "No TG_TOKEN set in .env"
assert ADMIN_ID, "No ADMIN_ID set in .env"
assert OWNER_ID, "No OWNER_ID set in .env"
assert AGENT_ID, "No AGENT_ID set in .env"


USAGE_TIMEDELTA_HOURS = int(os.getenv("USAGE_TIMEDELTA_HOURS", 24))
USAGE_PERIODIC_LIMIT = int(os.getenv("USAGE_PERIODIC_LIMIT", 10))


POSTGRES_URL = os.getenv("POSTGRES_URL")
assert POSTGRES_URL, "No POSTGRES_URL set in .env"


REDIS_URL = os.getenv("REDIS_URL")
assert REDIS_URL, "No REDIS_URL set in .env"


REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
assert REDIS_PASSWORD, "No REDIS_PASSWORD set in .env"


PROXY_TOKEN = os.getenv("PROXY_TOKEN")
assert PROXY_TOKEN, "No PROXY_TOKEN set in .env"


ENV = os.getenv("ENV", "PROD")
if ENV.lower() == "dev":
    logger.warning("Running in DEV mode")
    POSTGRES_URL = "sqlite:///./test.db"
    REDIS_URL = "redis://localhost:6379/0"
else:
    logger.warning("Running in PROD mode")


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
assert GOOGLE_API_KEY, "No GOOGLE_API_KEY set in .env"

PAY_LINK = os.getenv("PAY_LINK", "")
assert PAY_LINK, "No PAY_LINK set in .env"


MEDIASERVER_IP = os.getenv("MEDIASERVER_IP")
MEDIASERVER_PORT = os.getenv("MEDIASERVER_PORT")
MEDIASERVER_USER = os.getenv("MEDIASERVER_USER")
MEDIASERVER_PASSWORD = os.getenv("MEDIASERVER_PASSWORD")

assert MEDIASERVER_IP, "No MEDIASERVER_IP set in .env"
assert MEDIASERVER_PORT, "No MEDIASERVER_PORT set in .env"
assert MEDIASERVER_USER, "No MEDIASERVER_USER set in .env"
assert MEDIASERVER_PASSWORD, "No MEDIASERVER_PASSWORD set in .env"


logger.info(".env read successfully")
