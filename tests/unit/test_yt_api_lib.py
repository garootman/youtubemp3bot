import pytest

from tgmediabot.envs import GOOGLE_API_KEY, PROXY_TOKEN
from tgmediabot.medialib import YouTubeAPIClient

yt_client = YouTubeAPIClient(
    GOOGLE_API_KEY, "http://2dh5uiDTSX:vxQCr3xYC9Pbg46@103.47.52.201:8243"
)


yt = YouTubeAPIClient(GOOGLE_API_KEY)


def test_full_info():

    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    title, channel, duration, countries_yes, countries_no, islive = yt.get_full_info(
        video_id
    )
    assert "astley" in title.lower()
    assert "astley" in channel.lower()
    assert duration > 100


def test_restricted_info():
    video_id = "cH9AcFlbZco"  # some restricted
    title, channel, duration, countries_yes, countries_no, islive = yt.get_full_info(
        video_id
    )
    assert countries_no


def test_missing_video():
    video_id = "ZZZZZZZZZZZ"  # some restricted
    title, channel, duration, countries_yes, countries_no, islive = yt.get_full_info(
        video_id
    )
    assert not title
    assert not channel
    assert not duration
    assert not countries_yes
    assert not countries_no


if __name__ == "__main__":
    test_full_info()
    test_restricted_info()
    test_missing_video()
