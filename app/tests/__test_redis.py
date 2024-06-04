import sys

sys.path.append("../")

import pytest
from envs import REDIS_PASSWORD, REDIS_URL


def __test_redis_connection():
    import redis

    # r = redis.StrictRedis.from_url(REDIS_URL, password=REDIS_PASSWORD)
    r = redis.StrictRedis.from_url("redis://localhost:6379/0")

    assert r.ping() == True
    print("OK")


if __name__ == "__main__":
    __test_redis_connection()
