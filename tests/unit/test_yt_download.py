import os

import pytest

from tgmediabot.medialib import download_audio

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
    resdict = download_audio(url, file_name, proxy=proxy)
    assert resdict is not None


def test_bad_url():
    # catch exception for yt_dlp.utils.DownloadError
    resdict = download_audio(
        "https://www.youtube.com/watch?v=ZZZZZZZZZZZ", file_name, proxy=proxy
    )
    assert resdict["error"]


if __name__ == "__main__":
    test_prepare()
    test_download_audio()
    test_bad_url()
