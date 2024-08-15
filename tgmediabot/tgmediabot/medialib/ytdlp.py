import logging
import os

from yt_dlp import YoutubeDL

from .yt_dlp_options import DOWNLOAD_OPTIONS

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_media_info(url, proxy=None):
    logger.info(f"Getting media info for {url}")
    ydl_opts = DOWNLOAD_OPTIONS["getinfo"]
    if proxy:
        logger.info(f"Using proxy {proxy}")
        ydl_opts["proxy"] = proxy
    logger.debug(f"Using options: {ydl_opts}")
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            logger.debug(f"Got info for {url}: {info}")
            return info
        except Exception as e:
            logger.error(f"Error getting info for {url}: {e}")
            return {"error": str(e)}


def download_audio(url, filepath, proxy=None, platform="youtube", media="m4a"):
    mediaformat = f"{platform}_{media}"
    logger.info(f"Downloading media from {url} to {filepath} with format {mediaformat}")
    logger.debug(f"Platform: {platform}, format: {mediaformat}, proxy: {proxy}")
    if not mediaformat or mediaformat not in DOWNLOAD_OPTIONS:
        ydl_opts = DOWNLOAD_OPTIONS["default"].copy()
        logger.info(f"Unknown platform {mediaformat}, using default options: default")
    else:
        ydl_opts = DOWNLOAD_OPTIONS[mediaformat].copy()
        logger.info(f"Using platform {mediaformat} options")

    ydl_opts["outtmpl"] = filepath
    if proxy:
        ydl_opts["proxy"] = proxy
    else:
        ydl_opts.pop("proxy", None)

    # if mediaformat:
    #    ydl_opts["format"] = mediaformat

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            filesize_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)
            logger.info(f"Downloaded {filesize_mb} MB of {url} to {filepath}")
            return info_dict
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return {"error": str(e)}
