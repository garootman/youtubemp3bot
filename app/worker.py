# separate file for sending results to user
import os
import time
from datetime import timedelta

from assist import retry, utcnow
from celery_config import celery_app
from database import Payment, Task
from envs import (
    ADMIN_ID,
    AUDIO_PATH,
    DURATION_STR,
    FFMPEG_TIMEOUT,
    FREE_MINUTES_MAX,
    GOOGLE_API_KEY,
    MAX_FILE_SIZE,
    PROXY_TOKEN,
    TG_TOKEN,
)
from medialib import YouTubeAPIClient, download_audio
from paywall import PaywallService
from proxies import ProxyRevolver
from splitter import delete_files_by_chunk, delete_small_files, split_audio
from sqlalchemy import or_
from taskmanager import TaskManager
from telelib import delete_messages, mass_send_audio, send_msg

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)


proxy_mgr = ProxyRevolver(PROXY_TOKEN)
yt_client = YouTubeAPIClient(GOOGLE_API_KEY)
taskman = TaskManager()
pws = PaywallService()


@celery_app.task
def process_task(task_id: str, cleanup=True):
    print("Worker called with task id", task_id)
    task = taskman.get_task_by_id(task_id)
    done_task = taskman.lookup_task_by_media(
        task.platform, task.media_type, task.media_id
    )

    x = []
    dlmsg = None
    error = ""
    title = "unknown"
    channel = "unknown"
    duration = 0
    filesize = 0
    repeat = False
    countries_yes = []
    countries_no = []

    if done_task:
        print(f"Found same media in DB: task_id={done_task.id}")
        x = mass_send_audio(
            task.chat_id, done_task.tg_file_id.split(","), "MEDIA", done_task.title
        )
        if x:
            repeat = True
            title = done_task.title
            channel = done_task.channel
            duration = done_task.duration
            countries_yes = done_task.countries_yes
            countries_no = done_task.countries_no
            filesize = done_task.filesize

    if not x:
        title, channel, duration = None, None, 0
        dlmsg = send_msg(
            chat_id=task.chat_id,
            text="Downloading video. For large files it may take a while, please wait.",
        )

        print(
            f"Downloading audio for url: {task.url}, type: {task.media_type}, id: {task.media_id}, platform: {task.platform}"
        )
        try:
            title, channel, duration, countries_yes, countries_no = (
                yt_client.get_full_info(task.media_id)
            )
            print(
                f"Got title: {title}, channel: {channel}, duration: {duration}, countries_yes: {countries_yes}, countries_no: {countries_no}"
            )

            task.title = title
            task.channel = channel
            task.duration = duration
            task.countries_yes = ",".join(countries_yes)
            task.countries_no = ",".join(countries_no)
            taskman.update_task(task)

            if not title:
                raise ValueError("Video not found or not available")

            user_is_paid = pws.get_user_subscription(task.user_id)
            print(f"User is paid: {user_is_paid}")
            # olny paid users can download files longer than 30 minutes
            if not user_is_paid and duration > FREE_MINUTES_MAX * 60:
                send_msg(
                    chat_id=task.chat_id,
                    text="Video is over 30 minutes, /subscribe to download!",
                )
                task.status = "TOOLONG"
                taskman.update_task(task)
                return

            proxy_url = proxy_mgr.get_checked_proxy_by_countries(
                countries_yes, countries_no
            )
            print("Using proxy: ", proxy_url)

            file_name = os.path.join(AUDIO_PATH, f"{task_id}.m4a")

            filesize = download_audio(task.url, file_name, proxy=proxy_url)
            if not filesize:
                msg = f"Error downloading audio, file size is 0. Proxy was: {proxy_url}, countries_yes: {countries_yes}, countries_no: {countries_no}"
                raise ValueError(msg)
            size_mb = round(filesize / 1024 / 1024, 2)
            print("Downloaded with size: ", size_mb, "MB to file: ", file_name)
            # file_name, title, duration = download_audio(
            #    task.url, task_id, AUDIO_PATH, proxy_url
            # )

            local_files, std, err = split_audio(
                file_name, DURATION_STR, MAX_FILE_SIZE, FFMPEG_TIMEOUT
            )
            if err:
                raise ValueError(f"Error splitting files: {err}")
            x = mass_send_audio(task.chat_id, local_files, "FILE", title)

            print("DONE!")
        except Exception as e:
            error = f"Error sending voice by downloading: {e}"
            print(error)

    if dlmsg:
        delete_messages(task.chat_id, [dlmsg])

    if x:
        file_media_ids = ",".join([str(i.audio.file_id) for i in x if i])
        task.status = "COMPLETE"
        task.tg_file_id = file_media_ids
        task.duration = duration
        task.repeat = repeat
        task.title = title
        task.channel = channel
        task.filesize = filesize
        task.countries_yes = ",".join(countries_yes)
        task.countries_no = ",".join(countries_no)

    else:
        task.status = "ERROR"
        send_msg(chat_id=task.chat_id, text="Error sending voice, try again later")
        send_msg(
            chat_id=ADMIN_ID, text=f"Error sending msg for task {task_id}: {error}"
        )

    task.error = error
    taskman.update_task(task)

    if cleanup:
        _ = delete_files_by_chunk(AUDIO_PATH, task_id)


@celery_app.task
def process_new_tasks():
    new_tasks = taskman.get_new_tasks()
    print("Processing new tasks. Got ", len(new_tasks), "total tasks")
    for task in new_tasks:
        print(f"Processing task {task.id} as of {task.created_at}")
        time.sleep(1)
        process_task(task.id)


if __name__ == "__main__":
    celery_app.worker_main(
        argv=["worker", "--loglevel=info", "--concurrency=2", "--events"]
    )


"""
if __name__ == "__main__":
    # run task with task_id
    task_id = "909884c2"
    process_task(task_id)

"""
