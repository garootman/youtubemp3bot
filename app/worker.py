# separate file for sending results to user
import asyncio
import os
import time

from celery_config import celery_app
from envs import (
    ADMIN_ID,
    AUDIO_PATH,
    DURATION_STR,
    FFMPEG_TIMEOUT,
    MAX_FILE_SIZE,
    PROXY_URL,
    TG_TOKEN,
)
from models import SessionLocal, Task
from mp3lib import split_audio
from telebot import TeleBot
from telebot.types import InputMediaAudio
from ytlib import download_audio

bot = TeleBot(TG_TOKEN)


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
            sent_messages = bot.send_media_group(chat_id=chat_id, media=media)
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


def cleanup_files(audio_folder):
    # deletes all m4a files in audio_folder
    for file in os.listdir(audio_folder):
        if file.lower().endswith("m4a"):
            filepath = os.path.join(audio_folder, file)
            os.remove(filepath)


@celery_app.task
def process_task(task_id: str):
    print("called with task id", task_id)

    task = read_new_task(task_id)
    if not task:  # or task.status != "NEW":
        print("No task found or task is not new")
        return
    # file_name = AUDIO_PATH + task.yt_id + ".mp3"
    done_task = lookup_same_url(task.url)

    x = []
    dlmsg = None
    error = ""
    title = "unknown"

    if done_task:
        print(f"Found same yt_id in DB: task_id={done_task.id}")
        # caption = caption_template.format(done_task.yt_title)
        # title = done_task.yt_title
        x = mass_send_audio(
            task.user_id, done_task.tg_file_id.split(","), "MEDIA", done_task.yt_title
        )

    # list corresponding files in AUDIO_PATH, if they are less than MAX_FILE_SIZE
    """
    local_files = [
        os.path.join(AUDIO_PATH, file)
        for file in os.listdir(AUDIO_PATH)
        if file.startswith(task.yt_id)
        and os.path.getsize(os.path.join(AUDIO_PATH, file)) <= MAX_FILE_SIZE
    ]
    
    if not x and done_task and local_files:
        print(
            f"Sending {len(local_files)} audio files from disk for yt_id: {task.yt_id}"
        )
        x = []
        x = mass_send_audio(task.user_id, local_files, "FILE")
    """

    dlmsg = bot.send_message(
        chat_id=task.user_id,
        text="Downloading video. For large files it may take a while, please wait.",
    )

    if not x:
        print(f"Downloading audio for url: {task.url}")
        try:
            file_name, title = download_audio(task.url, task_id, AUDIO_PATH, PROXY_URL)

            local_files, std, err = split_audio(
                file_name, DURATION_STR, MAX_FILE_SIZE, FFMPEG_TIMEOUT, False
            )
            if err:
                raise ValueError(f"Error splitting files: {err}")
            print("Split done")
            x = mass_send_audio(task.user_id, local_files, "FILE", title)

            print("DONE!")
        except Exception as e:
            error = f"Error sending voice by downloading: {e}"
            print(error)

    if dlmsg:
        delete_messages(task.user_id, [dlmsg])

    if x:
        file_media_ids = ",".join([str(i.audio.file_id) for i in x if i])
        task.status = "COMPLETE"
        task.tg_file_id = file_media_ids
        task.yt_title = title
    else:
        task.status = "ERROR"
        bot.send_message(
            chat_id=task.user_id, text="Error sending voice, try again later"
        )
        bot.send_message(
            chat_id=ADMIN_ID, text=f"Error sending msg for task {task_id}: {error}"
        )

    # save updated task to DB
    task.error = error
    db = SessionLocal()
    db.add(task)
    db.commit()
    db.close()
    cleanup_files(AUDIO_PATH)


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


if __name__ == "__main__":
    celery_app.worker_main(
        argv=["worker", "--loglevel=info", "--concurrency=2", "--events"]
    )


if __name__ == "__somefun__":
    # read task_id from command line
    import sys

    task_id = sys.argv[1] if len(sys.argv) > 1 else None
    if not task_id:
        print("No task_id provided, but i have these failed tasks:")
        all_tasks = get_failed_tasks()
        for t in all_tasks:
            print(f"Task {t.id} created at {t.created_at}")
        sys.exit(1)

    process_task(task_id)
