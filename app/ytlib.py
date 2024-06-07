import os
import time

from assist import new_id, now
from retry import retry
from yt_dlp import YoutubeDL
from ytdlp_config import DOWNLOAD_OPTIONS, GETINFO_OPTIONS


@retry()
def get_video_info(url):
    with YoutubeDL(GETINFO_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        return info


@retry()
def download_audio(url, task_id, folder, proxy=None):
    stt = now(True)
    filepath = f"{folder}/{task_id}.m4a"

    ydl_opts = DOWNLOAD_OPTIONS.copy()
    ydl_opts["outtmpl"] = filepath
    if proxy:
        ydl_opts["proxy"] = proxy

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        title = f"{info_dict.get('uploader', 'Unknown')}: {info_dict.get('title', 'Unknown')}"
        duration = int(info_dict.get("duration", 0))
        print(
            f"Downloaded in {now(True) - stt} ms: '{title[:20]}...' to {filepath}, size {round(os.path.getsize(filepath)/1024/1024, 2)} MB"
        )
        return filepath, title, duration


if __name__ == "__main__":
    # Test the download_audio function + duration
    from envs import PROXY_URL

    stream_url = "https://www.youtube.com/live/Dv1s15JAAsM?si=BhvL3NUIuhxoEDQx"
    p, t, d = download_audio(stream_url, new_id(), "./audios", proxy=PROXY_URL)
    print(p, t, d)
