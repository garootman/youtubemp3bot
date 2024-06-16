DOWNLOAD_OPTIONS = {}
DOWNLOAD_OPTIONS["getinfo"] = {
    "quiet": True,
    "no_warnings": True,
    "no_color": True,
    "skip_download": True,
    "geo_bypass": True,
    "noplaylist": True,
    "prefer-free-formats": True,
    # set browser emulate mozila
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Mode": "navigate",
    },
}


DOWNLOAD_OPTIONS["youtube"] = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "outtmpl": "",
    # "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}


DOWNLOAD_OPTIONS["tiktok"] = {
    "outtmpl": "",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }
    ],
}


DOWNLOAD_OPTIONS["vk"] = {
    "format": "worstaudio",
    "outtmpl": "",
    # "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}

DOWNLOAD_OPTIONS["ok"] = {
    "format": "worst",
    "outtmpl": "",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }
    ],
}


DOWNLOAD_OPTIONS["default"] = {
    "format": "worst",
    "outtmpl": "",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "192",
        }
    ],
}
