DOWNLOAD_OPTIONS = {}
DOWNLOAD_OPTIONS["getinfo"] = {
    "quiet": True,
    "no_warnings": True,
    "no_color": True,
    "skip_download": True,
    "geo_bypass": True,
    "noplaylist": True,
    "prefer-free-formats": True,
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Sec-Fetch-Mode": "navigate",
    },
}


DOWNLOAD_OPTIONS["youtube_m4a"] = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "outtmpl": "",
    # "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}

DOWNLOAD_OPTIONS["youtube_mp3"] = {
    "format": "bestaudio[ext=m4a]/bestaudio",
    "outtmpl": "",
    # "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}

DOWNLOAD_OPTIONS["youtube_360"] = {
    # "format": "bestvideo[height<=360]+bestaudio/best[height<=360]", # 360p
    # vcodec:h264[vext=mp4][height<=360],aext:m4a
    # "format": "vcodec:h264[height<=360]+bestaudio/best[height<=360]", # 360p
    "format": "134+140",
    # "format": "18",
    "outtmpl": "",
    # "quiet": True,
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}

DOWNLOAD_OPTIONS["youtube_720"] = {
    "format": "bestvideo[ext=mp4][vcodec^=avc1][height<=720]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
    # "format": "bestvideo[ext=webm][vcodec^=vp9][height<=720]+bestaudio[ext=webm]/bestvideo[vcodec^=vp9][height<=720]+bestaudio/best",
    "outtmpl": "",
    "noplaylist": True,
    "geo_bypass": True,
    "prefer-free-formats": True,
}


DOWNLOAD_OPTIONS["youtube_1080"] = {
    "format": "bestvideo[ext=mp4][vcodec^=avc1][height<=1080]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
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
