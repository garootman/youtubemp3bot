import re


def extract_urls(text):
    if not text:
        return []
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = re.findall(url_pattern, text)
    return urls


def extract_youtube_info(url):
    youtube_patterns = {
        "video": re.compile(
            r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:watch\?v=|embed/|v/)|youtu\.be/)([^"&?/ ]{11})',
            re.IGNORECASE,
        ),
        "short": re.compile(
            r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([^"&?/ ]{11})', re.IGNORECASE
        ),
        "live": re.compile(
            r'(?:https?://)?(?:www\.)?youtube\.com/live/([^"&?/ ]{11})', re.IGNORECASE
        ),
    }

    for media_type, pattern in youtube_patterns.items():
        match = pattern.match(url)
        if match:
            return media_type, match.group(1)
    return None, None


def extract_plyalist_id(url):
    # returns youtube playlist id from url
    # also should work with all possible youtube playlist urls
    # with music, with short, with embed, etc, also with post-url params
    patterns = [
        re.compile(
            r"https?://(?:www\.)?(?:music\.)?(?:m\.)?youtube\.com/playlist\?list=([A-Za-z0-9_-]+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:https?://)?(?:www\.)?(?:music\.youtube\.com|youtube\.com|m\.youtube\.com|youtu\.be)/(?:playlist\?list=|embed/videoseries\?list=|watch\?v=)([A-Za-z0-9_-]+)",
            re.IGNORECASE,
        ),
    ]
    for pattern in patterns:
        match = pattern.search(url)
        if match:
            return match.group(1)
    return None


def extract_platform(url):
    platform_patterns = {
        "youtube": re.compile(
            r"(?:https?://)?(?:www\.)?(?:music\.youtube\.com|youtube\.com|youtu\.be)(?!/playlist\?list=[A-Za-z0-9_-]+)",
            re.IGNORECASE,
        ),
        "yt_playlist": re.compile(
            r"https?://(?:www\.)?(?:music\.)?youtube\.com/playlist\?list=[A-Za-z0-9_-]+",
            re.IGNORECASE,
        ),
        "facebook": re.compile(r"(?:https?://)?(?:www\.)?facebook\.com", re.IGNORECASE),
        "instagram": re.compile(
            r"(?:https?://)?(?:www\.)?instagram\.com", re.IGNORECASE
        ),
        "tiktok": re.compile(r"(?:https?://)?(?:www\.)?tiktok\.com", re.IGNORECASE),
        "twitter": re.compile(r"(?:https?://)?(?:www\.)?twitter\.com", re.IGNORECASE),
        "twitch": re.compile(r"(?:https?://)?(?:www\.)?twitch\.tv", re.IGNORECASE),
        "vimeo": re.compile(r"(?:https?://)?(?:www\.)?vimeo\.com", re.IGNORECASE),
        "vk": re.compile(r"(?:https?://)?(?:www\.)?vk\.com", re.IGNORECASE),
        "ok": re.compile(r"(?:https?://)?(?:www\.)?ok\.ru", re.IGNORECASE),
    }

    for platform, pattern in platform_patterns.items():
        if pattern.match(url):
            return platform
    return "unknown"
