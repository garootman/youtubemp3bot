import isodate
import requests

from assist import drilldown


class YouTubeAPIClient:
    # class to work with YT API
    # gets video metadata and other technical info
    def __init__(self, api_key):
        self.__api_key = api_key
        selftest = self.self_test_apikey()
        if not selftest:
            raise Exception("API key is invalid")
        print("YouTube API client initialized successfully!")

    def self_test_apikey(self):
        # test if api key is valid - using API ping
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id=dQw4w9WgXcQ&key={self.__api_key}"
        response = requests.get(req_url)
        if response.status_code == 200:
            return True
        return False

    def get_video_metadata(self, video_id):
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={self.__api_key}"
        response = requests.get(req_url)
        if response.status_code == 200:
            return response.json()
        return {}

    def get_video_snippet(self, vide_id):
        # gets video general info - title, channel, etc
        req_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={vide_id}&key={self.__api_key}"
        response = requests.get(req_url)
        if response.status_code == 200:
            return response.json()

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
                    return True
        return False

    def get_video_countries_avail(self, metadata_dict):
        avail = drilldown(
            metadata_dict,
            ["items", 0, "contentDetails", "regionRestriction", "allowed"],
        )
        if not avail:
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

    def get_full_info(self, video_id):
        # get all info about video
        metadata = self.get_video_metadata(video_id)
        snippet = self.get_video_snippet(video_id)
        title = self.get_video_title(snippet)
        channel = self.get_video_channel(snippet)
        duration = self.get_video_duration(metadata)
        countries_yes = self.get_video_countries_avail(metadata)
        countries_no = self.get_video_countries_blocked(metadata)
        live = self.get_stream_live(snippet)
        return title, channel, duration, countries_yes, countries_no, live
