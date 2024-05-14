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
    TG_TOKEN,
)
from models import SessionLocal, Task
from mp3lib import split_mp4_audio
from telebot import TeleBot
from ytlib import download_audio

bot = TeleBot(TG_TOKEN)


def read_new_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    return task


def lookup_same_ytid(yt_id):
    # find task with same yt_id, that is complete and has a tg_file_id
    # select one with the latest timestamp in updated_at
    db = SessionLocal()
    task = (
        db.query(Task)
        .filter(Task.yt_id == yt_id, Task.status == "COMPLETE", Task.tg_file_id != "")
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


def mass_send_audio(chat_id, audio_list, title, mode):
    sent = []
    for i, audio in enumerate(audio_list):
        try:
            tit = (f"{title[:32]}_{i+1}.mp4",)
            audio_object = audio if mode == "MEDIA" else open(audio, "rb")
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
        sent = None
    return sent


@celery_app.task
def process_task(task_id: str):
    print("called with task id", task_id)

    task = read_new_task(task_id)
    if not task:  # or task.status != "NEW":
        print("No task found or task is not new")
        return
    # file_name = AUDIO_PATH + task.yt_id + ".mp3"
    done_task = lookup_same_ytid(task.yt_id)

    x = None
    dlmsg = None
    error = ""

    if done_task:
        print(f"Found same yt_id in DB: task_id={done_task.id}")
        # caption = caption_template.format(done_task.yt_title)
        title = done_task.yt_title
        x = mass_send_audio(
            task.user_id, done_task.tg_file_id.split(","), title, "MEDIA"
        )

    # list corresponding files in AUDIO_PATH, if they are less than MAX_FILE_SIZE
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
        x = mass_send_audio(task.user_id, local_files, done_task.yt_title, "FILE")

    dlmsg = bot.send_message(
        chat_id=task.user_id,
        text="Downloading video. For large files it may take a while, please wait.",
    )

    if not x:
        print(f"Downloading audio for yt_id: {task.yt_id}")
        try:
            title, file_name, duration = download_audio(task.yt_id, AUDIO_PATH)

            local_files, std, err = split_mp4_audio(
                file_name, DURATION_STR, MAX_FILE_SIZE, FFMPEG_TIMEOUT, False
            )
            if err:
                raise ValueError(f"Error splitting files: {err}")
            print("Split done")
            x = mass_send_audio(task.user_id, local_files, title, "FILE")

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

    # save updated task to DB
    task.error = error
    db = SessionLocal()
    db.add(task)
    db.commit()
    db.close()


if __name__ == "__main__":
    taskid = "64f48666"
    process_task(taskid)
