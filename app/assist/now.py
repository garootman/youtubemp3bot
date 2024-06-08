from datetime import datetime, timedelta, timezone


def utcnow(microseconds=False):
    if not microseconds:
        return datetime.utcnow().replace(microsecond=0)
    return datetime.utcnow()


def now(microseconds=False):
    nn = int(datetime.utcnow().timestamp() * 1000)
    if not microseconds:
        return nn // 1000 * 1000
    return nn
