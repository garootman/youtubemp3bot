import logging

import isodate
import requests

from tgmediabot.assist import drilldown

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class YouTubeAPIClient:
    def __init__(self, api_key, proxy=None, timeout=5):
        logger.debug(f"Initializing YouTube API client with key {api_key[:5]}...")
        self.__api_key = api_key
        self.__timeout = timeout
        msg = "YouTube API client initialized successfully!"
        if proxy:
            msg += f" Using proxy {proxy}"
            self.__proxies = {"http": proxy, "https": proxy}
        else:
            self.__proxies = None
        selftest = self.self_test_apikey()
        if not selftest:
            logger.critical("API key is invalid")
            raise Exception("API key is invalid")

        logger.info(msg)

    @property
    def proxy(self):
        return self.__proxies["http"]

    def self_test_apikey(self):
        # test if api key is valid - using API ping
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=dQw4w9WgXcQ&key={self.__api_key}"
        response = requests.get(req_url, proxies=self.__proxies, timeout=self.__timeout)
        if response.status_code == 200:
            return True
        return False

    def get_video_metadata(self, video_id):
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={self.__api_key}"
        response = requests.get(req_url, proxies=self.__proxies, timeout=self.__timeout)
        if response.status_code == 200:
            return response.json()
        logger.info(
            f"Got response {response.status_code} from YT API for video {video_id}"
        )
        logger.debug(f"Response text: {response.text}")
        return {}

    def get_video_snippet(self, video_id):
        # gets video general info - title, channel, etc
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={self.__api_key}"
        response = requests.get(req_url, proxies=self.__proxies, timeout=self.__timeout)
        if response.status_code == 200:
            return response.json()
        logger.info(
            f"Got response {response.status_code} from YT API for video {video_id}"
        )
        logger.debug(f"Response text: {response.text}")
        return {}

    def get_playlist_media_links(self, playlist_id, raise_on_error=False):
        # gets all media links from playlist
        # use next page token to get all links, limit is MAX_PLAYLIST_ITEMS
        base_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        videos = []
        next_page_token = None
        logger.info(f"Getting YouTube playlist {playlist_id} media links")
        used_next_page_tokens = []

        while True:
            if next_page_token in used_next_page_tokens:
                break
            if next_page_token:
                used_next_page_tokens.append(next_page_token)
            params = {
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": 50,
                "pageToken": next_page_token,
                "key": self.__api_key,
            }

            response = requests.get(
                base_url, params=params, proxies=self.__proxies, timeout=self.__timeout
            )
            if response.status_code != 200:
                msg = f"Got response {response.status_code} from YT API for playlist {playlist_id}\n{response.text}"
                logger.error(msg)
                if raise_on_error:
                    print(response.text)
                    raise Exception(
                        f"Got response {response.status_code} from YT API for playlist {playlist_id}: {response.text}"
                    )
                break
            data = response.json()

            for item in data["items"]:
                video_id = drilldown(item, ["snippet", "resourceId", "videoId"])
                if not video_id:
                    logger.error(f"Video ID not found in playlist item {item}")
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                videos.append(video_url)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        return videos

    def get_video_duration(self, metadata_dict) -> int:
        # returns video duration in int seconds
        duration_str = drilldown(
            metadata_dict, ["items", 0, "contentDetails", "duration"]
        )
        if not duration_str:
            return 0
        return int(isodate.parse_duration(duration_str).total_seconds())

    def get_stream_live(self, snippet):
        # returns True if stream is live
        liveness = []
        for snip in snippet["items"]:
            if "snippet" in snip:
                if snip["snippet"].get("liveBroadcastContent", "").lower() == "live":
                    logger.info("Stream is live!")
                    return True
        return False

    def get_video_countries_avail(self, metadata_dict):
        avail = drilldown(
            metadata_dict,
            ["items", 0, "contentDetails", "regionRestriction", "allowed"],
        )
        if not avail or avail == "{}":
            return []

        return avail

    def get_video_countries_blocked(self, metadata_dict):
        # returns a list of countries where video is blocked
        blocked = drilldown(
            metadata_dict,
            ["items", 0, "contentDetails", "regionRestriction", "blocked"],
        )
        if not blocked:
            return []
        return blocked

    def get_video_title(self, snippet_dict):
        tit = drilldown(snippet_dict, ["items", 0, "snippet", "title"])
        return tit

    def get_video_channel(self, snippet_dict):
        chan = drilldown(snippet_dict, ["items", 0, "snippet", "channelTitle"])
        return chan

    def get_video_channel_id(self, snippet_dict):
        chan_id = drilldown(snippet_dict, ["items", 0, "snippet", "channelId"])
        return chan_id

    def get_full_info(self, video_id):
        # get all info about video
        metadata = self.get_video_metadata(video_id)
        snippet = self.get_video_snippet(video_id)
        if not (metadata and snippet):
            logger.error(f"Video {video_id} has no metadata or snipper")
            logger.debug(f"Snippet was {snippet}")
            logger.debug(f"Metadata was {metadata}")
            return "", "", 0, [], [], False

        title = self.get_video_title(snippet)
        channel = self.get_video_channel(snippet)
        duration = self.get_video_duration(metadata)
        countries_yes = self.get_video_countries_avail(metadata)
        countries_no = self.get_video_countries_blocked(metadata)
        live = self.get_stream_live(snippet)
        return title, channel, duration, countries_yes, countries_no, live
