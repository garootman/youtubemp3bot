import os

from yt_dlp import YoutubeDL

from .yt_dlp_options import DOWNLOAD_OPTIONS


def get_media_info(url, proxy=None):
    ydl_opts = DOWNLOAD_OPTIONS["getinfo"]
    if proxy:
        ydl_opts["proxy"] = proxy
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except Exception as e:
            return {"error": str(e)}


def download_audio(url, filepath, proxy=None, platform="youtube", mediaformat=None):
    if not platform or platform not in DOWNLOAD_OPTIONS:
        ydl_opts = DOWNLOAD_OPTIONS["default"].copy()
        print(f"Unknown platform {platform}, using default options: default")
    else:
        ydl_opts = DOWNLOAD_OPTIONS[platform].copy()
        print(f"Using platform {platform} options")

    ydl_opts["outtmpl"] = filepath
    if proxy:
        ydl_opts["proxy"] = proxy

    if mediaformat:
        ydl_opts["format"] = mediaformat

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            return info_dict
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return {"error": str(e)}
