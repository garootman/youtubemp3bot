import re
import uuid
from datetime import datetime, timedelta


def new_id():
    return str(uuid.uuid4())[:8]


def utcnow(microseconds=False):
    if not microseconds:
        return datetime.now().replace(microsecond=0)
    return datetime.now()


def now(microseconds=False):
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


def extract_urls(text):
    if not text:
        return []
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = re.findall(url_pattern, text)
    return urls


def universal_check_link(link):
    # Regular expressions for different YouTube URL formats
    regexes = [
        r"http(?:s?)://(?:www\.)?youtube\.com/watch\?v=",
        r"http(?:s?)://(?:www\.)?youtube\.com/embed/",
        r"http(?:s?)://(?:www\.)?youtube\.com/v/",
        r"http(?:s?)://(?:www\.)?youtube\.com/live/",
        #        r"http(?:s?)://(?:www\.)?youtube\.com/playlist\?list=",
        # palylists are excluded by now
        r"http(?:s?)://(?:www\.)?youtube\.com/shorts/",
        r"http(?:s?)://(?:www\.)?youtube\.com/channel/",
        r"http(?:s?)://(?:www\.)?youtube\.com/user/",
        r"http(?:s?)://(?:www\.)?youtube\.com/c/",
        r"http(?:s?)://(?:www\.)?youtube\.com/@",
        r"http(?:s?)://(?:www\.)?youtube\.com/music/",
        r"http(?:s?)://youtu\.be/",
    ]
    for regex in regexes:
        match = re.match(regex, link)
        if match:
            return True
    return False
