import os

from yt_dlp import YoutubeDL


def download_audio(url, filepath, proxy=None):

    DOWNLOAD_OPTIONS = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": "",
        # "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,
        "prefer-free-formats": True,
    }

    ydl_opts = DOWNLOAD_OPTIONS.copy()
    ydl_opts["outtmpl"] = filepath
    if proxy:
        ydl_opts["proxy"] = proxy

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            return os.path.getsize(filepath)
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return 0
