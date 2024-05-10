import re

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


def download_audio(video_id, path):
    url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(url)
    title = yt.title
    yt.streams.get_audio_only().download(path, filename=video_id + ".mp3")
    return title, f"{path}/{video_id}.mp3"
