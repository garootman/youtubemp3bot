import os
import re
import time

from assist import now
from pytube import YouTube
from yt_dlp import YoutubeDL


def extract_urls(text):
    if not text:
        return []
    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = re.findall(url_pattern, text)
    return urls


def universal_check_link(link):
    # Regular expressions for different YouTube URL formats
    regexes = [
        r"http(?:s?):\/\/(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
        r"http(?:s?):\/\/youtu\.be\/([^?]+)",
        r"http(?:s?):\/\/(?:www\.)?youtube\.com\/embed\/([^?]+)",
        r"http(?:s?):\/\/(?:www\.)?youtube\.com\/v\/([^?]+)",
        r"http(?:s?):\/\/(?:www\.)?youtube\.com\/playlist\?list=([^&]+)",
        r"http(?:s?):\/\/(?:www\.)?youtube\.com\/music\?list=([^&]+)",
        r"http(?:s?):\/\/music\.youtube\.com\/watch\?v=([^&]+)",
        r"http(?:s?):\/\/music\.youtube\.com\/playlist\?list=([^&]+)",
    ]

    for regex in regexes:
        match = re.match(regex, link)
        if match:
            return match.group(1)

    return None


def download_audio(video_id, folder):
    stt = now(True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    retries = 3

    # Check if file was already downloaded
    filepath = f"{folder}/{video_id}.mp4"
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return filepath, "unknown"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{folder}/{video_id}.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    while retries > 0:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = f"{info_dict.get('uploader', 'Unknown')}: {info_dict.get('title', 'Unknown')}"
                temp_filepath = f"{folder}/{video_id}.mp3"
                os.rename(temp_filepath, filepath)
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


def download_audio_pytube(video_id, folder):
    stt = now(True)
    url = f"https://www.youtube.com/watch?v={video_id}"
    retries = 3

    # check if file was already downloaded
    # if yes, return the path
    filepath = f"{folder}/{video_id}.mp4"
    if os.path.exists(filepath):
        print(f"File already exists: {filepath}")
        return filepath, "unknown"  # , None

    while retries > 0:
        try:
            yt = YouTube(url)  # , use_oauth = True , allow_oauth_cache = True)
            title = str(yt.author) + ": " + str(yt.title)
            # video_duration = yt.length
            yt.streams.get_audio_only().download(folder, filename=video_id + ".temp")
            os.rename(f"{folder}/{video_id}.temp", f"{folder}/{video_id}.mp4")
            print(
                f"Downloaded in {now(True) - stt} ms: '{title[:20]}...' to {filepath}, size {round(os.path.getsize(filepath)/1024/1024,2)} MB"
            )
            return filepath, title  # , video_duration
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
