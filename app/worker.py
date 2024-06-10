# separate file for sending results to user
import os
import time
from datetime import timedelta

from assist import retry, utcnow
from celery_config import celery_app
from database import Payment, SessionLocal, Task
from envs import (
    ADMIN_ID,
    AUDIO_PATH,
    DURATION_STR,
    FFMPEG_TIMEOUT,
    GOOGLE_API_KEY,
    LOCAL_PROXY_URL,
    MAX_FILE_SIZE,
    TG_TOKEN,
    USE_PROXY,
)
from medialib import YouTubeAPIClient, download_audio
from proxies import ProxyRevolver
from splitter import delete_files_by_chunk, delete_small_files, split_audio
from sqlalchemy import or_
from telebot import TeleBot
from telebot.types import InputMediaAudio

if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)


def get_proxies():
    if USE_PROXY == "LOCALHOST":
        return [LOCAL_PROXY_URL]
    elif USE_PROXY:
        if os.path.exists(USE_PROXY):
            with open(USE_PROXY) as f:
                return f.readlines()
        else:
            print(f"Proxy file {USE_PROXY} not found")

    return []


proxy_mgr = ProxyRevolver(get_proxies())
bot = TeleBot(TG_TOKEN)
yt_client = YouTubeAPIClient(GOOGLE_API_KEY)


def read_new_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    return task


def get_failed_tasks():
    db = SessionLocal()
    # get all tasks with status error
    tasks = db.query(Task).filter(Task.status == "ERROR").all()
    db.close()
    return tasks


def get_new_tasks():
    db = SessionLocal()
    # get all tasks with status new
    tasks = db.query(Task).filter(Task.status == "NEW").all()
    db.close()
    return tasks


@retry()
def send_msg(*args, **kwargs):
    # universdal fnc to wrap send msg
    return bot.send_message(*args, **kwargs)


def lookup_same_url(url):
    # find task with same yt_id, that is complete and has a tg_file_id
    # select one with the latest timestamp in updated_at
    db = SessionLocal()
    task = (
        db.query(Task)
        .filter(Task.url == url, Task.status == "COMPLETE", Task.tg_file_id != "")
        .order_by(Task.updated_at.desc())
        .first()
    )
    db.close()
    return task


def lookup_same_media(paltform, media_type, media_id):
    # find task with same paltform, media_type, media_id
    # that is complete and has a tg_file_id
    # select one with the latest timestamp in updated_at
    db = SessionLocal()
    task = (
        db.query(Task)
        .filter(
            Task.paltform == paltform,
            Task.media_type == media_type,
            Task.media_id == media_id,
            Task.status == "COMPLETE",
        )
        .order_by(Task.updated_at.desc())
        .first()
    )
    db.close()
    return task


def delete_messages(chat_id, msg_batch):
    for msg in msg_batch:
        if msg:
            try:
                bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception as e:
                print(f"Error deleting message: {e}")
                pass


def mass_send_audio_album(chat_id, audio_list, mode):
    sent = []

    # Разбиваем аудиофайлы на части по 10 штук
    for i in range(0, len(audio_list), 10):
        audio_chunk = audio_list[i : i + 10]
        media = []

        for j, audio in enumerate(audio_chunk):
            try:
                audio_object = audio if mode == "MEDIA" else open(audio, "rb")
                media.append(InputMediaAudio(media=audio_object))  # , caption=tit))

            except Exception as e:
                error = f"Error preparing audio for sending: {e}"
                print(error)
                media.append(None)

        try:
            # sent_messages = bot.send_media_group(chat_id=chat_id, media=media)
            sent_messages = send_msg(chat_id=chat_id, media=media)
            sent.extend(sent_messages)
            time.sleep(1)
        except Exception as e:
            error = f"Error sending media group: {e}"
            print(error)
            sent.extend([None] * len(media))

    if not all(sent):
        print(f"Not all data was sent to chat {chat_id} with mode {mode}")
        delete_messages(chat_id, sent)
        sent = []

    return sent


def mass_send_audio(chat_id, audio_list, mode, title):
    sent = []
    for i, audio in enumerate(audio_list):
        try:
            audio_object = audio if mode == "MEDIA" else open(audio, "rb")
            tit = f"{title}_{i+1}.m4a"
            xi = bot.send_audio(
                chat_id=chat_id,
                audio=audio_object,
                title=tit,
            )
            print(
                f"Sent audio chunk {i} of {len(audio_list)} to {chat_id}, sleeping 1 sec."
            )
            time.sleep(1)

        except Exception as e:
            error = f"Error sending voice by {mode}: {e}"
            print(error)
            xi = None
        sent.append(xi)
    if not all(sent):
        print(f"Not all data was sent to chat {chat_id} with mode {mode}")
        delete_messages(chat_id, sent)
        sent = []
    return sent


@celery_app.task
def process_task(task_id: str, cleanup=True):
    print("Worker called with task id", task_id)
    task = read_new_task(task_id)
    done_task = lookup_same_media(task.paltform, task.media_type, task.media_id)

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
            f"Downloading audio for url: {task.url}, type: {task.media_type}, id: {task.media_id}, platform: {task.paltform}"
        )
        try:
            title, channel, duration, countries_yes, countries_no = (
                yt_client.get_full_info(task.media_id)
            )
            print(
                f"Got title: {title}, channel: {channel}, duration: {duration}, countries_yes: {countries_yes}, countries_no: {countries_no}"
            )

            if not title:
                raise ValueError("Video not found or not available")

            proxy_url = proxy_mgr.get_checked_proxy_by_countries(
                countries_yes, countries_no
            )
            print("Using proxy: ", proxy_url)

            file_name = os.path.join(AUDIO_PATH, f"{task_id}.m4a")

            filesize = download_audio(task.url, file_name, proxy=None)
            if not filesize:
                raise ValueError("Error downloading audio, file size is 0")
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
        task.yt_duration = duration
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
    db = SessionLocal()
    db.add(task)
    db.commit()
    db.close()
    if cleanup:
        x = delete_files_by_chunk(AUDIO_PATH, task_id)
        print(f"Deleted {x} files for task {task_id}")


@celery_app.task
def rerun_failed_tasks():
    error_tasks = get_failed_tasks()
    print("Re-running failed tasks. Got ", len(error_tasks), "total tasks")
    for task in error_tasks:
        print(
            f"Re-running task {task.id} as of {task.created_at}, error was: {task.error}"
        )
        time.sleep(1)
        # rocess_task(task.id)


@celery_app.task
def process_new_tasks():
    new_tasks = get_new_tasks()
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
    task_id = "2fa4a642"
    process_task(task_id)
"""
