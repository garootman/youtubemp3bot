"""
- [ ] Не делать задачи забанившим юзерам
ссылки вида music.youtube.com НЕ воспринимаются как площадка ютуб - проверить, написать тест
Общая логика процессинга “ссылки“ на медиа-объект
предусмотреть загрузку видео, как вариант
Обрабатывать недоступность прокси - заменой например. или ютуб зажмотил ссылку.
Скорость: лимиты на каждое действие, сообщения юзеру “осталось столько-то. “fix slow download speed - with proxy speed?
Мультилогика в зависимости от источника: 
форматы
прокси
???
Переписать форматы аудио извлечения
Обработать ошибку с  пустыми файлами - когда нечего отправлять
вернуть подбор видоса по айдишнику телеги (обрабатывать дубли - как раньше!)
убрать дубли видео для юзера
mp3 meta info - to file by ffmpeg
Работать внутри ПАПКИ, чистить по завершению
"""

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
)
from tgmediabot.database import Task
from tgmediabot.envs import ADMIN_ID, AUDIO_PATH, FFMPEG_TIMEOUT, MAX_FILE_SIZE
from tgmediabot.medialib import download_audio, fix_file_name, get_media_info

# from tgmediabot.paywall import PayWallManager
# from tgmediabot.proxies import ProxyRevolver
from tgmediabot.splitter import convert_audio  # delete_files_by_chunk,
from tgmediabot.splitter import get_resolution, split_media

# from tgmediabot.taskmanager import TaskManager
from tgmediabot.telelib import delete_messages, mass_send_audio, send_msg

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)


class TaskProcessor:
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
    def enrich_task(self, ignore_status=False, max_urls=20):
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
        else:
            links = [self.task.url]
        islive = False
        error = ""
        media_type, media_id = "", ""

        for url in links[:max_urls]:
            if platform == "youtube":
                media_type, media_id = extract_youtube_info(url)
                title, channel, duration, countries_yes, countries_no, islive = (
                    self.ytclient.get_full_info(media_id)
                )
                # logger.debug(f"Countries: {countries_yes} ({type(countries_yes)}), {countries_no} ({type(countries_no)})")
                if islive:
                    error = "Video is live and cannot be downloaded"
                    logger.error(error)
            else:
                # ytproxy = self.proxyman.get_checked_proxy_by_countries(["US"], [])
                ytproxy = None
                video_info = get_media_info(self.task.url, proxy=ytproxy)
                if not video_info or video_info.get("error"):
                    error = video_info.get("error", "Unknown error")
                    logger.error(f"Error getting video info: {error}")
                title = video_info.get("title")
                channel = video_info.get("uploader")
                duration = int(video_info.get("duration", 0))
                countries_yes = []
                countries_no = []

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
            )

        if error:
            task.status = "ERROR"
        else:
            task.status = "HASINFO"
        task = self.taskman.update_task(task)
        logger.info(f"Task {self.task_id} enriched with video info")
        self.task = task
        return task

    @retry()
    def download_media(self, url, proxy_url, file_name, platform, media):
        stt = time.perf_counter()
        resdict = download_audio(
            url, file_name, proxy=proxy_url, platform=platform, media=media
        )
        duration = time.perf_counter() - stt
        size = os.path.getsize(file_name) if os.path.exists(file_name) else 0
        self.proxyman.save_proxy_use(
            proxy=proxy_url,
            use_type="download_audio",
            task_id=self.task_id,
            url=url,
            speed=size / duration if duration > 0 else 0,
            success=True if not resdict.get("error") else False,
            error=resdict.get("error"),
        )

        if not resdict or resdict.get("error"):
            logger.error(
                f"Error downloading audio: {resdict.get('error', 'Unknown error')}"
            )
            return None, resdict.get("error")

        file_name = fix_file_name(file_name, self.task_id)
        return file_name, None

    def process(self, cleanup=True, ignore_status=False):
        # returns all the fucking results!
        # success or not
        # files info: filenames, sizes, duration
        # tg info: tg_file_id, message ids,
        # media-info: title, author | channel, duration,
        # countries-yes, no
        # error

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
        if self.task.format == "mp3":
            ext = "mp3"
            format_type = "audio"
        elif self.task.format == "m4a":
            ext = "m4a"
            format_type = "audio"
        else:
            ext = "mp4"
            format_type = "video"

        logger.info(f"Using proxy: {proxy_url}")

        for media in media_objects:
            width, height = 0, 0
            file_name = os.path.join(taskfolder, f"{media.id}.{ext}")
            # download_media(url, proxy_url, file_name, platform, media):
            file_name, dl_error = self.download_media(
                media.url, proxy_url, file_name, media.platform, self.task.format
            )
            if not file_name or not os.path.exists(file_name):
                filesize = 0
            else:
                filesize = os.path.getsize(file_name)

            if not filesize:
                logger.error(
                    f"Error downloading audio: Not downloaded properly, file size is 0"
                )
                self.task.status = "ERROR"
                self.task.error = "Not downloaded properly"
                if dl_error:
                    self.task.error += f": {dl_error}"
                self.taskman.update_task(self.task)
                send_msg(
                    chat_id=self.task.chat_id,
                    text="Error downloading audio, please try again later",
                )
                logger.info(
                    f"Task {self.task_id} not complete: error downloading audio, got 0 bytes in files"
                )
                logger.debug(f"file_name: {file_name}")
                return

            if self.task.format == "mp3":
                mp3_file_name, err_to_mp3 = convert_audio(file_name, FFMPEG_TIMEOUT)
                mp3_file_size = (
                    os.path.getsize(mp3_file_name)
                    if os.path.exists(mp3_file_name)
                    else 0
                )
                if filesize:
                    logger.info(f"Converted to mp3: {file_name}")
                    file_name = mp3_file_name
                    filesize = mp3_file_size
                else:
                    logger.error(f"Error converting to mp3: {err_to_mp3}")

            local_files, std, err = split_media(
                file_name, media.duration, MAX_FILE_SIZE
            )
            logger.info(f"Split audio: {local_files}")
            if not local_files:
                logger.error(f"Error splitting audio: {err}")
                self.task.status = "ERROR"
                self.taskman.update_task(self.task)
                send_msg(
                    chat_id=self.task.chat_id,
                    text="Error downloading audio, please try again later",
                )
                send_msg(
                    chat_id=ADMIN_ID,
                    text=f"Error splitting task {self.task_id}: \n\n{err}\n\n{std}",
                )
                logger.info(f"Task {self.task_id} not complete: error splitting audio")
                return

            fulltitle = f"[{self.task.format}] {media.title} - {media.channel}"
            if format_type == "video":
                width, height = get_resolution(file_name, FFMPEG_TIMEOUT)
            x = mass_send_audio(
                self.task.chat_id,
                local_files,
                "FILE",
                fulltitle,
                format_type,
                width,
                height,
            )
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
                #                send_msg(
                #                    chat_id=ADMIN_ID, text=f"Error sending msg for task {self.task_id}"
                #                )
                logger.info(f"Task {self.task_id} not complete: error sending messages")
                media.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
                media.filesize = filesize
                self.taskman.update_media_info(media)

        self.task.status = "COMPLETE"
        # self.task.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
        # self.task.filesize = filesize
        # self.task.countries_yes = ",".join(countries_yes)
        # self.task.countries_no = ",".join(countries_no)
        self.taskman.update_task(self.task)
        logger.info(f"Task {self.task_id} complete with status {self.task.status}")
        if cleanup:
            shutil.rmtree(taskfolder)
            logger.info(f"Deleted files for task {self.task_id}")
