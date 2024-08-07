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
import time
from datetime import timedelta

from tgmediabot.assist import extract_platform, extract_youtube_info, retry, utcnow
from tgmediabot.database import Task
from tgmediabot.envs import (
    ADMIN_ID,
    AUDIO_PATH,
    FFMPEG_TIMEOUT,
    FREE_MINUTES_MAX,
    GOOGLE_API_KEY,
    MAX_FILE_SIZE,
    PROXY_TOKEN,
    TG_TOKEN,
)
from tgmediabot.medialib import (
    YouTubeAPIClient,
    download_audio,
    fix_file_name,
    get_media_info,
    select_quality_format,
)
from tgmediabot.paywall import PayWallManager
from tgmediabot.proxies import ProxyRevolver
from tgmediabot.splitter import (
    convert_audio,
    delete_files_by_chunk,
    delete_small_files,
    get_chunk_duration_str,
    split_audio,
)
from tgmediabot.taskmanager import TaskManager
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
        
        
    @retry()
    def enrich_task(self, ignore_status=False):
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
    
        islive = False
        error = ""
        media_type, media_id = "", ""
        if platform == "youtube":
            media_type, media_id = extract_youtube_info(self.task.url)
            title, channel, duration, countries_yes, countries_no, islive = (
                self.ytclient.get_full_info(media_id)
            )
            if islive:
                error = "Video is live and cannot be downloaded"
                logger.error(error)
        else:
            ytproxy = self.proxyman.get_checked_proxy_by_countries(["US"], [])
            video_info = get_media_info(self.task.url, proxy=ytproxy)
            if not video_info or video_info.get("error"):
                error = video_info.get("error", "Unknown error")
                logger.error(f"Error getting video info: {error}")
            title = video_info.get("title")
            channel = video_info.get("uploader")
            duration = int(video_info.get("duration", 0))
            countries_yes = []
            countries_no = []
            
        task.platform = platform
        task.media_type = media_type
        task.media_id = media_id
        task.title = title
        task.channel = channel
        task.duration = duration
        task.countries_yes = ",".join(countries_yes)
        task.countries_no = ",".join(countries_no)
        task.error = error
        if error:
            task.status = "ERROR"
        else:
            task.status = "HASINFO"
        task = self.taskman.update_task(task)
        logger.info(f"Task {self.task_id} enriched with video info")
        self.task = task
        return task
        

    @retry()
    def download_media(self, url, proxy_url, file_name, platform, audio_format):
            stt = time.perf_counter()
            resdict = download_audio(
                url,
                file_name,
                proxy=proxy_url,
                platform=platform, 
                mediaformat=audio_format
            )
            duration = time.perf_counter() - stt
            size = os.path.getsize(file_name) if os.path.exists(file_name) else 0
            self.proxyman.save_proxy_use(
                proxy=proxy_url,
                use_type="download_audio",
                task_id=self.task_id,
                url=self.task.url,
                speed=size / duration if duration > 0 else 0,
                success=True if not resdict.get("error") else False,
                error=resdict.get("error"),
            )
            
            if not resdict or resdict.get("error"):
                logger.error(
                    f"Error downloading audio: {resdict.get('error', 'Unknown error')}"
                )
                return None

            return fix_file_name(file_name, self.task_id)





    def process(self, cleanup=True):
        # returns all the fucking results!
        # success or not
        # files info: filenames, sizes, duration
        # tg info: tg_file_id, message ids,
        # media-info: title, author | channel, duration,
        # countries-yes, no
        # error

        if self.task.status != "NEW":
            logger.error(f"Task {self.task_id} is not NEW!")
            return

        self.task.status = "PROCESSING"
        self.taskman.update_task(self.task)
        self.task = self.taskman.get_task_by_id(self.task_id)
        taskfolder = os.path.join(AUDIO_PATH, self.task_id)
        # create folder if not exists
        if os.path.exists(taskfolder):
            os.rmdir(taskfolder)
        os.mkdir(taskfolder)
        file_name = os.path.join(taskfolder, f"{self.task_id}.m4a")

        proxy_url = self.proxyman.get_checked_proxy_by_countries(
            self.task.countries_yes, self.task.countries_no
        )        
        logger.info(f"Using proxy: {proxy_url}")
        audio_format = {}
        """
        mediaformat = select_quality_format(video_info.get("formats"))
        if not mediaformat:
            mediaformat = {}
        audio_format = mediaformat.get("format_id")
        logger.info(f"Selected format: {audio_format}")
        """
        
        file_name = self.download_media(
            self.task.url, proxy_url, file_name, audio_format, self.task.platform
        )
        
        filesize = os.path.getsize(file_name) if os.path.exists(file_name) else 0

        if not filesize:
            logger.error(
                f"Error downloading audio: Not downloaded properly, file size is 0"
            )
            self.task.status = "ERROR"
            self.task.error = "Not downloaded properly"
            self.taskman.update_task(self.task)
            send_msg(
                chat_id=self.task.chat_id, text="Error downloading audio, please try again later"
            )
            logger.info(
                f"Task {self.task_id} not complete: error downloading audio, got 0 bytes in files"
            )
            logger.debug(f"file_name: {file_name}")
            return

        dursec_str = get_chunk_duration_str(duration, filesize, MAX_FILE_SIZE)
        file_name_mp3, err_to_mp3 = convert_audio(file_name, FFMPEG_TIMEOUT)
        if file_name_mp3:
            file_name = file_name_mp3
            filesize = os.path.getsize(file_name) if os.path.exists(file_name) else 0
            logger.info(f"Converted to mp3: {file_name}")
        else:
            logger.error(f"Error converting to mp3: {err_to_mp3}")

        local_files, std, err = split_audio(
            file_name, dursec_str, MAX_FILE_SIZE, FFMPEG_TIMEOUT
        )
        logger.info(f"Split audio: {local_files}")
        if not local_files:
            logger.error(f"Error splitting audio: {err}")
            self.task.status = "ERROR"
            self.taskman.update_task(self.task)
            send_msg(
                chat_id=self.task.chat_id, text="Error downloading audio, please try again later"
            )
            send_msg(
                chat_id=ADMIN_ID, text=f"Error splitting task {self.task_id}: \n\n{err}\n\n{std}"
            )
            logger.info(f"Task {self.task_id} not complete: error splitting audio")
            return

        fulltitle = f"{title} - {channel}"
        x = mass_send_audio(self.task.chat_id, local_files, "FILE", fulltitle)
        if not x:
            logger.error(f"Error sending messages for task {self.task_id}")
            self.task.status = "ERROR"
            self.taskman.update_task(self.task)
            send_msg(
                chat_id=self.task.chat_id, text="Error downloading audio, please try again later"
            )
            send_msg(chat_id=ADMIN_ID, text=f"Error sending msg for task {self.task_id}")
            logger.info(f"Task {self.task_id} not complete: error sending messages")
            return

        self.task.status = "COMPLETE"
        self.task.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
        self.task.filesize = filesize
        self.task.countries_yes = ",".join(countries_yes)
        self.task.countries_no = ",".join(countries_no)
        self.taskman.update_task(self.task)
        logger.info(f"Task {self.task_id} complete with status {self.task.status}")
        if cleanup:
            _ = delete_files_by_chunk(AUDIO_PATH, self.task_id)
            logger.info(f"Deleted files for task {self.task_id}")
            


