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


def extract_platform(url):
    platform_patterns = {
        "youtube": re.compile(
            r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)", re.IGNORECASE
        ),
        "facebook": re.compile(r"(?:https?://)?(?:www\.)?facebook\.com", re.IGNORECASE),
        "instagram": re.compile(
            r"(?:https?://)?(?:www\.)?instagram\.com", re.IGNORECASE
        ),
        "tiktok": re.compile(r"(?:https?://)?(?:www\.)?tiktok\.com", re.IGNORECASE),
        "twitter": re.compile(r"(?:https?://)?(?:www\.)?twitter\.com", re.IGNORECASE),
        "twitch": re.compile(r"(?:https?://)?(?:www\.)?twitch\.tv", re.IGNORECASE),
        "vimeo": re.compile(r"(?:https?://)?(?:www\.)?vimeo\.com", re.IGNORECASE),
        "dailymotion": re.compile(
            r"(?:https?://)?(?:www\.)?dailymotion\.com", re.IGNORECASE
        ),
        "soundcloud": re.compile(
            r"(?:https?://)?(?:www\.)?soundcloud\.com", re.IGNORECASE
        ),
    }

    for platform, pattern in platform_patterns.items():
        if pattern.match(url):
            return platform
    return None
