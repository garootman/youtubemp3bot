import os
import re

from assist import now
from pytube import YouTube


def extract_urls(text):
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
    yt = YouTube(url)
    title = yt.title
    video_duration = yt.length
    yt.streams.get_audio_only().download(folder, filename=video_id + ".mp4")
    filepath = f"{folder}/{video_id}.mp4"
    print(
        f"Downloaded in {now(True) - stt} ms: '{title[:20]}...' to {filepath}, size {round(os.path.getsize(filepath)/1024/1024,2)} MB"
    )
    return title, filepath, video_duration
