import uuid
from datetime import datetime, timedelta


def new_id():
    return str(uuid.uuid4())[:8]


def utcnow(microseconds=False):
    if not microseconds:
        return datetime.now().replace(microsecond=0)
    return datetime.now()


def now(microseconds=False):
    # returns utctimestamp INT
    nn = int(datetime.now().timestamp() * 1000)
    if not microseconds:
        return nn // 1000 * 1000
    return nn


def plainstring(msg, maxlen=30):
    msg = (
        str(msg)
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
        .replace("  ", " ")
        .strip()
    )
    if len(msg) > maxlen:
        return msg[:maxlen] + "..."
    return msg


if __name__ == "__main__":
    print(new_id())
    print(utcnow())
    print(plainstring("Hello, world!"))
