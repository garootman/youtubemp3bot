import os
import time

from assist import now
from yt_dlp import YoutubeDL


def download_audio(video_id, folder):
    stt = now(True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    retries = 3

    # Check if file was already downloaded
    filepath = f"{folder}/{video_id}.m4a"
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return filepath, "unknown"

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": f"{folder}/{video_id}.m4a",
    }

    while retries > 0:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = f"{info_dict.get('uploader', 'Unknown')}: {info_dict.get('title', 'Unknown')}"
                print(
                    f"Downloaded in {now(True) - stt} ms: '{title[:20]}...' to {filepath}, size {round(os.path.getsize(filepath)/1024/1024, 2)} MB"
                )
                return filepath, title
        except Exception as e:
            msg = f"Error downloading {url}: {e}"
            print(msg)
            retries -= 1
            time.sleep(1)
    raise Exception(f"Failed to download {url}: {msg}")


if __name__ == "__main__":
    # Test the download_audio function
    restricted_video_url = "https://www.youtube.com/watch?v=Q_cZcXXWpIk"
    x = YouTube(restricted_video_url, use_oauth=True, allow_oauth_cache=True)
    print(dir(x))
    print(x.title)
    # download_audio("dQw4w9WgXcQ", "downloads")
