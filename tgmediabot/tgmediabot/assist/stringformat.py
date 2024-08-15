import uuid


def new_id(l=12):
    s = str(uuid.uuid4())
    s = s.replace("-", "").replace("_", "")
    return s[:l]


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
