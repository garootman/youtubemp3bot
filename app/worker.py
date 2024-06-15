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
    if not task or not task.media_id:
        print(f"Task {task_id} not found, or no media_id")
        return

    title, channel, duration, countries_yes, countries_no = yt_client.get_full_info(
        task.media_id
    )
    if not title:
        print(f"Video not found or not available: {task.media_id}")
        task.status = "NOTFOUND"
        taskman.update_task(task)
        send_msg(chat_id=task.chat_id, text="Video not found or not available")
        return

    task.title = title
    task.channel = channel
    task.duration = duration
    task.countries_yes = ",".join(countries_yes)
    task.countries_no = ",".join(countries_no)
    taskman.update_task(task)

    task = taskman.get_task_by_id(task_id)

    user_is_paid = pws.get_user_subscription(task.user_id)

    if not user_is_paid and duration > FREE_MINUTES_MAX * 60:
        send_msg(
            chat_id=task.chat_id,
            text="Video is over 30 minutes, /subscribe to download!",
        )
        task.status = "TOOLONG"
        taskman.update_task(task)
        return

    proxy_url = proxy_mgr.get_checked_proxy_by_countries(countries_yes, countries_no)
    print("Using proxy: ", proxy_url)

    file_name = os.path.join(AUDIO_PATH, f"{task_id}.m4a")
    filesize = download_audio(task.url, file_name, proxy=proxy_url)
    if not filesize:
        task.status = "ERROR"
        taskman.update_task(task)
        send_msg(
            chat_id=task.chat_id, text="Error downloading audio, please try again later"
        )
        send_msg(chat_id=ADMIN_ID, text=f"Error at task {task_id}")
        return

    local_files, std, err = split_audio(
        file_name, DURATION_STR, MAX_FILE_SIZE, FFMPEG_TIMEOUT
    )
    if not local_files:
        task.status = "ERROR"
        taskman.update_task(task)
        send_msg(
            chat_id=task.chat_id, text="Error downloading audio, please try again later"
        )
        send_msg(
            chat_id=ADMIN_ID, text=f"Error splitting task {task_id}: \n\n{err}\n\n{std}"
        )
        return

    x = mass_send_audio(task.chat_id, local_files, "FILE", title)
    if not x:
        task.status = "ERROR"
        taskman.update_task(task)
        send_msg(
            chat_id=task.chat_id, text="Error downloading audio, please try again later"
        )
        send_msg(chat_id=ADMIN_ID, text=f"Error sending msg for task {task_id}")
        return

    task.status = "COMPLETE"
    task.tg_file_id = ",".join([str(i.audio.file_id) for i in x if i])
    task.filesize = filesize
    task.countries_yes = ",".join(countries_yes)
    task.countries_no = ",".join(countries_no)
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
    task_id = "3c02a029"
    process_task(task_id)

"""
