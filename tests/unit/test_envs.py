import pytest


def test_get_env():
    from tgmediabot.envs import (
        ADMIN_ID,
        AUDIO_PATH,
        ENV,
        FFMPEG_TIMEOUT,
        GOOGLE_API_KEY,
        MAX_FILE_SIZE,
        PAY_LINK,
        POSTGRES_URL,
        PROXY_TOKEN,
        REDIS_PASSWORD,
        REDIS_URL,
        TG_TOKEN,
        USAGE_PERIODIC_LIMIT,
        USAGE_TIMEDELTA_HOURS,
    )


if __name__ == "__main__":
    test_get_env()
    print("Everything passed")
