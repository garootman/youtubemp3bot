import pytest

from tgmediabot.envs import GOOGLE_API_KEY
from tgmediabot.medialib import YouTubeAPIClient

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


def test_get_playlist_info():
    plid = "PLyy-7U8Nf9Sq9L5lF-W9eRtH9cPsw7fBi"
    links = yt.get_playlist_media_links(plid)
    assert links
    assert isinstance(links, list)
    assert len(links) > 5


if __name__ == "__main__":
    test_full_info()
    test_restricted_info()
    test_missing_video()
