import json
import logging
import os
import shutil
import time
from datetime import timedelta

from tgmediabot.assist import (
    extract_platform,
    extract_plyalist_id,
    extract_youtube_info,
    retry,
    utcnow,
)
from tgmediabot.database import Task
from tgmediabot.envs import ADMIN_ID, AUDIO_PATH, FFMPEG_TIMEOUT, MAX_FILE_SIZE
from tgmediabot.medialib import (
    check_download_status,
    download_media_remote,
    fix_file_name,
    get_media_info_remote,
    send_to_telegram,
)

# from tgmediabot.paywall import PayWallManager
# from tgmediabot.proxies import ProxyRevolver
from tgmediabot.splitter import convert_audio  # delete_files_by_chunk,
from tgmediabot.splitter import get_resolution, split_media

# from tgmediabot.taskmanager import TaskManager
from tgmediabot.telelib import delete_messages, mass_send_audio, resend_media, send_msg

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)

# create_tgfile_info
# update_tgfile_info
# get_tgfile_info


class RemoteTaskProcessor:

    max_urls = 20

    def __init__(self, proxymanager, taskmanager, ytclient, payman, task_id=None):
        self.proxyman = proxymanager
        self.taskman = taskmanager
        self.ytclient = ytclient
        self.payman = payman
        self.task_id = task_id
        self.task = self.taskman.get_task_by_id(task_id)
        if not self.task:
            raise ValueError(f"Task {self.task_id} not found!")
        logger.info(f"TaskProcessor initialized with task id {self.task_id}")

    # @retry()
    def enrich_task(self, ignore_status=False, premium=False):
        logger.info(f"Enriching task {self.task_id}")
        task = self.taskman.get_task_by_id(self.task_id)
        if not task:
            raise ValueError(f"Task {self.task_id} not found!")
        if task.status != "NEW" and not ignore_status:
            logger.error(f"Task {self.task_id} is not NEW!")
            return
        task.status = "ENRICHING"
        task = self.taskman.update_task(task)
        platform = extract_platform(task.url)
        logger.info(f"Enriching task {self.task_id} with platform {platform}")

        if platform == "yt_playlist":
            plid = extract_plyalist_id(task.url)
            links = self.ytclient.get_playlist_media_links(plid, raise_on_error=False)
            platform = "youtube"
            if not premium:
                links = [links[0]]
            else:
                links = links[: self.max_urls]
        else:
            links = [self.task.url]
        islive = False
        error = ""
        media_type, media_id = "", ""

        for url in links:

            if platform == "youtube":
                media_type, media_id = extract_youtube_info(url)
                #                title, channel, duration, countries_yes, countries_no, islive = (
                _, _, _, countries_yes, countries_no, islive = (
                    self.ytclient.get_full_info(media_id)
                )
                if islive:
                    error = "Video is live and cannot be downloaded"
                    logger.error(error)
            else:
                countries_yes, countries_no, islive = [], [], False

            proxy = self.proxyman.get_checked_proxy_by_countries(
                countries_yes, countries_no
            )
            video_info = get_media_info_remote(url, proxy=proxy)
            if not video_info or video_info.get("error"):
                error = video_info.get("error", "Unknown error")
                logger.error(f"Error getting video info: {error}")
            title = video_info.get("title")
            channel = video_info.get("uploader")
            duration = int(video_info.get("duration", 0))
            formats_json = video_info.get("formats")
            formats_json = json.dumps(formats_json) if formats_json else ""
            if not formats_json:
                error = "No formats found"
                logger.error(error)
                break

            self.taskman.create_media_info(
                task_id=self.task_id,
                platform=platform,
                url=url,
                media_type=media_type,
                media_id=media_id,
                countries_yes=",".join(countries_yes),
                countries_no=",".join(countries_no),
                title=title,
                channel=channel,
                duration=duration,
                filesize=0,
                formats_json=formats_json,
            )

        if error:
            task.status = "ERROR"
        else:
            task.status = "HASINFO"
        task = self.taskman.update_task(task)
        logger.info(f"Task {self.task_id} enriched with video info")
        self.task = task
        return task

    def process(self, cleanup=True, ignore_status=False, media_timeout=10 * 60):
        if self.task.status != "TO_PROCESS" and not ignore_status:
            logger.error(f"Task {self.task_id} is not in TO_PROCESS status!")
            return
        media_objects = self.taskman.get_media_objects(self.task_id)
        if not media_objects:
            logger.error(f"Task {self.task_id} has NO media objects!")
            return

        self.task.status = "PROCESSING"
        self.task = self.taskman.update_task(self.task)
        taskfolder = os.path.join(AUDIO_PATH, self.task_id)
        # if os.path.exists(taskfolder):
        # shutil.rmtree(taskfolder)
        proxy_url = self.proxyman.get_checked_proxy_by_countries(
            media_objects[0].countries_yes, media_objects[0].countries_no
        )

        logger.info(f"Using proxy: {proxy_url}")
        totalsize = 0
        for media in media_objects:
            # 1. remote send command to START DOWNLOAD
            #   - POST /ytdlp-download with params: url, proxy, format
            #   - response: {"status": (success), task_id": remote_download_task_id}

            remote_task_id = download_media_remote(
                media.url, self.task.format, proxy_url
            )

            # 2. remote check status of download
            #   - GET /ytdlp-status/{task_id}
            #   - response: {"status": (success), "filename": filename, "filesize": filesize}

            file_dict = check_download_status(remote_task_id)
            logger.info(f"File dict: {file_dict}")
            if "error" in file_dict:
                msg = f"Error downloading audio: {file_dict['error']}"
                logger.error(msg)
                self.task.error = msg
                send_msg(
                    chat_id=self.task.chat_id,
                    text="Error downloading audio, please try again later",
                )
                continue

            remote_filename = file_dict.get("filename")
            filesize = int(file_dict.get("filesize"))
            totalsize += filesize

            # exceptions will be described later
            # 3. Once it is downloaded and NOT temp, send it to user
            #  - POST /upload-to-telegram with params: file_name from step 2
            #  - response: {"status": (success), filesize in bytes

            s = send_to_telegram(remote_task_id)

            # 4. Start checking taskmanager for tgmediaobject, if it was uploaded
            #  - taskman.get_tgfile_info with remote_download_task_id
            #  - once we have TgMediaInfo object, we can send its .file_id to user
            # 5. send message to user with file_id

            dtt = utcnow()  # returns datetime.datetime
            while utcnow() - dtt < timedelta(seconds=media_timeout):
                tgupload = self.taskman.get_tgfile_info(remote_task_id)
                if tgupload and tgupload.file_id:
                    tg_file_id = tgupload.file_id
                    break
                time.sleep(5)

            media.tg_file_id = tg_file_id

            fulltitle = f"[{self.task.format}] {media.title} - {media.channel}"
            x = resend_media(self.task.chat_id, tg_file_id, fulltitle, self.task.format)

            if not x:
                msg = f"Error sending messages for task {self.task_id}"
                logger.error(msg)
                self.task.status = "ERROR"
                self.task.error = msg
                self.taskman.update_task(self.task)
                send_msg(
                    chat_id=self.task.chat_id,
                    text="Error downloading audio, please try again later",
                )
                logger.info(f"Task {self.task_id} not complete: error sending messages")
                media.tg_file_id = tg_file_id
                self.taskman.update_media_info(media)

        self.task.status = "COMPLETE"
        # self.task.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
        self.task.filesize = totalsize
        # self.task.countries_yes = ",".join(countries_yes)
        # self.task.countries_no = ",".join(countries_no)
        self.taskman.update_task(self.task)
        logger.info(f"Task {self.task_id} complete with status {self.task.status}")
        if cleanup:
            logger.debug(f"Nothing to delete, lol")
