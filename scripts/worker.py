# separate file for sending results to user
import logging
import os
import time
from datetime import timedelta

from celery_config import celery_app

from tgmediabot.assist import extract_platform, extract_youtube_info, retry, utcnow
from tgmediabot.chatmanager import ChatManager
from tgmediabot.database import Payment, Task
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
from tgmediabot.paywall import PaywallService
from tgmediabot.proxies import ProxyRevolver
from tgmediabot.splitter import (
    delete_files_by_chunk,
    delete_small_files,
    get_chunk_duration_str,
    split_audio,
)
from tgmediabot.taskmanager import TaskManager
from tgmediabot.telelib import delete_messages, mass_send_audio, send_msg

# from tgmediabot.database import SessionLocal
# db = SessionLocal


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)


proxy_mgr = ProxyRevolver(PROXY_TOKEN)
yt_client = YouTubeAPIClient(GOOGLE_API_KEY)

taskman = TaskManager()
pws = PaywallService()
chatman = ChatManager()


@celery_app.task
def process_task(task_id: str, cleanup=True):
    logger.info(f"Worker called with task id {task_id}")
    task = taskman.get_task_by_id(task_id)

    if not task:
        logger.error(f"Task {task_id} not found!")
        return

    logger.debug(f"Task: {task}")

    if task.status != "NEW":
        logger.error(f"Task {task_id} is not NEW!")
        return

    task.status = "PROCESSING"
    taskman.update_task(task)
    task = taskman.get_task_by_id(task_id)

    chat_id = task.chat_id
    platform = extract_platform(task.url)
    task.platform = platform
    if platform == "youtube":
        video_info = {}
        media_type, media_id = extract_youtube_info(task.url)
        title, channel, duration, countries_yes, countries_no, islive = (
            yt_client.get_full_info(media_id)
        )
        proxy_url = proxy_mgr.get_checked_proxy_by_countries(
            countries_yes, countries_no
        )
        if not title:
            logger.error(f"Video not found or not available: {task.url}")
            task.status = "NOTFOUND"
            taskman.update_task(task)
            send_msg(chat_id=chat_id, text="Video not found or not available")
            logger.info(f"Task {task_id} not complete: video not found")
            return
        if islive:
            # end task if live stream
            logger.error(f"Video is live: {task.url}")
            task.status = "ISLIVE"
            taskman.update_task(task)
            send_msg(chat_id=chat_id, text="Video is live, cannot download")
            logger.info(f"Task {task_id} not complete: video is live")
            return

    else:
        logger.info(f"Platform not youtube: {task.url}")
        video_info = get_media_info(task.url)
        error = video_info.get("error")
        if not video_info or error:
            if not error:
                error = "Unknown error"
            logger.error(f"Error getting video info: {error}")
            task.status = "ERROR"
            task.error = error
            taskman.update_task(task)
            send_msg(chat_id=chat_id, text="Error getting video info")
            logger.info(f"Task {task_id} not complete: error getting video info")
            return

        title = video_info.get("title")
        channel = video_info.get("uploader")
        duration = int(video_info.get("duration", 0))
        countries_yes = []
        countries_no = []
        proxy_url = None

    logger.info(
        f"Got video info: {title} - {channel} - {duration} - {countries_yes} - {countries_no}"
    )
    logger.info(f"Using proxy: {proxy_url}")
    task.title = title
    task.channel = channel
    task.duration = duration
    task.countries_yes = ",".join(countries_yes)
    task.countries_no = ",".join(countries_no)
    taskman.update_task(task)
    task = taskman.get_task_by_id(task_id)
    logger.info(f"Task {task_id} updated with video info")

    """
        user_is_paid = pws.get_user_subscription(task.user_id)

        if not user_is_paid and duration > FREE_MINUTES_MAX * 60:
            send_msg(
                chat_id=chat_id,
                text="Video is over 30 minutes, /subscribe to download!",
            )
            task.status = "TOOLONG"
            taskman.update_task(task)
            return
    """

    if duration > FREE_MINUTES_MAX * 60:
        send_msg(
            chat_id=chat_id,
            text=f"Video is over {FREE_MINUTES_MAX} minutes, please try another video",
        )
        task.status = "TOOLONG"
        taskman.update_task(task)
        logger.info(f"Task {task_id} not complete: video is too long")
        return

    file_name = os.path.join(AUDIO_PATH, f"{task_id}.m4a")

    mediaformat = select_quality_format(video_info.get("formats"))
    if not mediaformat:
        mediaformat = {}
    logger.info(f"Selected format: {mediaformat}")
    resdict = download_audio(
        task.url,
        file_name,
        proxy=proxy_url,
        platform=platform,
        mediaformat=mediaformat.get("format_id"),
    )
    if not resdict or resdict.get("error"):
        logger.error(
            f"Error downloading audio: {resdict.get('error', 'Unknown error')}"
        )
        task.status = "ERROR"
        task.error = resdict.get("error", "Unknown error")
        taskman.update_task(task)
        send_msg(
            chat_id=chat_id, text="Error downloading audio, please try again later"
        )
        logger.info(f"Task {task_id} not complete: error downloading audio")
        return

    file_name = fix_file_name(file_name, task_id)
    filesize = os.path.getsize(file_name) if os.path.exists(file_name) else 0

    if not filesize:
        logger.error(
            f"Error downloading audio: Not downloaded properly, file size is 0"
        )
        task.status = "ERROR"
        task.error = "Not downloaded properly"
        taskman.update_task(task)
        send_msg(
            chat_id=chat_id, text="Error downloading audio, please try again later"
        )
        logger.info(
            f"Task {task_id} not complete: error downloading audio, got 0 bytes in files"
        )
        logger.debug(f"file_name: {file_name}")
        return

    dursec_str = get_chunk_duration_str(duration, filesize, MAX_FILE_SIZE)
    local_files, std, err = split_audio(
        file_name, dursec_str, MAX_FILE_SIZE, FFMPEG_TIMEOUT
    )
    logger.info(f"Split audio: {local_files}")
    if not local_files:
        logger.error(f"Error splitting audio: {err}")
        task.status = "ERROR"
        taskman.update_task(task)
        send_msg(
            chat_id=chat_id, text="Error downloading audio, please try again later"
        )
        send_msg(
            chat_id=ADMIN_ID, text=f"Error splitting task {task_id}: \n\n{err}\n\n{std}"
        )
        logger.info(f"Task {task_id} not complete: error splitting audio")
        return

    fulltitle = f"{title} - {channel}"
    x = mass_send_audio(chat_id, local_files, "FILE", fulltitle)
    if not x:
        logger.error(f"Error sending messages for task {task_id}")
        task.status = "ERROR"
        taskman.update_task(task)
        send_msg(
            chat_id=chat_id, text="Error downloading audio, please try again later"
        )
        send_msg(chat_id=ADMIN_ID, text=f"Error sending msg for task {task_id}")
        logger.info(f"Task {task_id} not complete: error sending messages")
        return

    task.status = "COMPLETE"
    task.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
    task.filesize = filesize
    task.countries_yes = ",".join(countries_yes)
    task.countries_no = ",".join(countries_no)
    taskman.update_task(task)
    chatman.bump_noban(chat_id)
    logger.info(f"Task {task_id} complete with status {task.status}")
    if cleanup:
        _ = delete_files_by_chunk(AUDIO_PATH, task_id)
        logger.info(f"Deleted files for task {task_id}")


@celery_app.task
def process_new_tasks():
    new_task_ids = taskman.get_new_task_ids()
    msg = f"(Re-)processing {len(new_task_ids)} new tasks: {new_task_ids[:5]}..."
    logger.info(msg)
    for tid in new_task_ids:
        task = taskman.get_task_by_id(tid)
        task.status = "NEW"
        taskman.update_task(task)
        process_task.delay(tid, cleanup=True)
        logger.info(f"Added '{tid}' as of {task.created_at} to queue")


if __name__ == "__main__":
    # Runs celery. To add beat scheduler, add -B flag
    celery_app.worker_main(
        argv=["worker", "--loglevel=info", "--concurrency=1", "--events"]
    )


"""
if __name__ == "__main__":
    # run task with task_id
    task_id = "83159c65"
    process_task(task_id)
    
"""
