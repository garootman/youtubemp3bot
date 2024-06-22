import pytest

from tgmediabot.assist import extract_platform, extract_urls, extract_youtube_info


def test_extract_urls():
    urls = extract_urls("https://www.youtube.com/watch?v=12345")
    assert urls == ["https://www.youtube.com/watch?v=12345"]
    text_with_urls = "https://www.youtube.com/watch?v=12345 and HASDKJSHL https://www.youtube.com/watch?v=67890"
    urls = extract_urls(text_with_urls)
    assert urls == [
        "https://www.youtube.com/watch?v=12345",
        "https://www.youtube.com/watch?v=67890",
    ]


def test_get_yt_info():
    rickroll_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    media_type, media_id = extract_youtube_info(rickroll_url)
    assert media_type == "video"
    assert media_id == "dQw4w9WgXcQ"

    shorts_url = "https://www.youtube.com/shorts/MTxNJCbpRIk"
    media_type, media_id = extract_youtube_info(shorts_url)
    assert media_type == "short"
    assert media_id == "MTxNJCbpRIk"

    live_url = "https://www.youtube.com/live/dQw4w9WgXcQ"
    media_type, media_id = extract_youtube_info(live_url)
    assert media_type == "live"
    assert media_id == "dQw4w9WgXcQ"

    invalid_url = "https://www.youtube.com/watch?v="
    media_type, media_id = extract_youtube_info(invalid_url)
    print(media_type, media_id)
    assert media_type is None
    assert media_id is None


def test_extract_platform():
    youtube_url = "https://www.youtube.com/watch?v=12345"
    assert extract_platform(youtube_url) == "youtube"

    facebook_url = "https://www.facebook.com/watch?v=12345"
    assert extract_platform(facebook_url) == "facebook"

    instagram_url = "https://www.instagram.com/watch?v=12345"
    assert extract_platform(instagram_url) == "instagram"

    tiktok_url = "https://www.tiktok.com/watch?v=12345"
    assert extract_platform(tiktok_url) == "tiktok"

    twitter_url = "https://www.twitter.com/watch?v=12345"
    assert extract_platform(twitter_url) == "twitter"

    twitch_url = "https://www.twitch.tv/watch?v=12345"
    assert extract_platform(twitch_url) == "twitch"

    vimeo_url = "https://www.vimeo.com/watch?v=12345"
    assert extract_platform(vimeo_url) == "vimeo"

    invalid_url = "https://www.example.com/watch?v=12345"
    assert extract_platform(invalid_url) == "unknown"


if __name__ == "__main__":
    test_extract_urls()
    test_get_yt_info()
    test_extract_platform()
    print("All tests passed!")
