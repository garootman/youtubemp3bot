import uuid
from datetime import datetime, timedelta


def new_id():
    return str(uuid.uuid4())[:8]


def utcnow(microseconds=False):
    if not microseconds:
        return datetime.now().replace(microsecond=0)
    return datetime.now()


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
