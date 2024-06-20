import os

import pytest

from medialib import download_audio

proxy = None
# rickroll url
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
folder = "test_audio"
file_name = os.path.join(folder, "test.m4a")


def test_prepare():
    # make folder if not exists
    if not os.path.exists("test_audio"):
        os.makedirs("test_audio")


def test_download_audio():
    filesize = download_audio(url, file_name, proxy=proxy)
    print("File size: ", filesize)
    assert os.path.exists(file_name)
    assert filesize > 1 * 1024 * 1024  # 1 MB


def test_bad_url():
    # catch exception for yt_dlp.utils.DownloadError
    x = download_audio(
        "https://www.youtube.com/watch?v=ZZZZZZZZZZZ", file_name, proxy=proxy
    )
    assert x == 0


if __name__ == "__main__":
    test_prepare()
    test_download_audio()
    test_bad_url()
