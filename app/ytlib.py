import os
import time

from yt_dlp import YoutubeDL

from assist import new_id, now


def download_audio(url, task_id, folder, proxy=None):
    stt = now(True)
    retries = 3

    # Check if file was already downloaded
    filepath = f"{folder}/{task_id}.m4a"

    """
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return filepath, "unknown"
    """

    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": f"{folder}/{task_id}.m4a",
        "bypass_geoblock": True,
        "quiet": True,
        "noplaylist": True,
        "geo_bypass": True,  #
        #        "no_warnings": True,
        #        "ignoreerrors": True,
        #        "nooverwrites": True,
        #        "writethumbnail": True,
    }
    if proxy:
        ydl_opts["proxy"] = proxy

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
    stream_url = "https://www.youtube.com/live/Dv1s15JAAsM?si=BhvL3NUIuhxoEDQx"
    p, t = download_audio(stream_url, new_id(), "./audios", proxy=None)
    print(p, t)
