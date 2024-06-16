def select_quality_format(formats, min_br=90, max_br=200):
    # first try to get 128kbps audio only
    if not formats or not isinstance(formats, list):
        return {}
    ao128 = next(
        (f for f in formats if f.get("abr") == 128 and f.get("acodec") != "none"), None
    )
    if ao128:
        return ao128
    # try to find the best audio format in the given range
    audio_formats = [f for f in formats if f.get("abr") and f.get("acodec") != "none"]
    if audio_formats:
        audio_formats.sort(key=lambda f: f.get("abr", 0))
        audios_in_range = [f for f in audio_formats if min_br <= f["abr"] <= max_br]
        if audios_in_range:
            return min(audios_in_range, key=lambda f: f["abr"])
        # if no audio in the range, get the best audio format
        return audio_formats[-1]
    return {}


all_urls = [
    "https://vk.com/feed?w=story-41944327_456240213%2Fdiscover",  # not working now - bad browser
    "https://vk.com/clip-213584752_456239257",
    "https://live.vkplay.ru/metallicheskayagora/record/56523d2a-88f0-416a-901e-279e589d97bc/records",
    "https://www.tiktok.com/@giorgigogochuriepatajur/video/7353736876680809729?is_from_webapp=1&sender_device=pc",
    "https://www.tiktok.com/@22gradusi/video/7361462184049741074?is_from_webapp=1&sender_device=pc",
    "https://l.likee.video/v/suJwv6",
    "https://vimeo.com/956764043",  # not working now
    "https://x.com/NevskyAlexandr/status/1801889206894998006",
    "https://vk.com/video-110135406_456243143",
    "https://ok.ru/video/6652061092578",
    "https://vk.com/audio506644832_456274494_7f1b2655d85afdfcf0",  # not working now - https://vk.com/badbrowser.php
    "https://001.l0rdfilm.info/50740-poslednij-drakon-2024.html",
    "https://ok.ru/video/7772972518062",
]
