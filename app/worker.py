# separate file for sending results to user
import asyncio
import os

from celery_config import celery_app
from envs import ADMIN_ID, AUDIO_PATH, TG_TOKEN
from models import SessionLocal, Task
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


@celery_app.task
def process_task(task_id: str):
    print("called with task id", task_id)

    task = read_new_task(task_id)
    if not task or task.status != "NEW":
        print("No task found or task is not new")
        return
    file_name = AUDIO_PATH + task.yt_id + ".mp3"
    done_task = lookup_same_ytid(task.yt_id)

    x = None
    error = ""
    if done_task:
        print(f"Found same yt_id in DB: task_id={done_task.id}")
        # caption = caption_template.format(done_task.yt_title)
        title = done_task.yt_title
        try:
            # send_audio or send_voice
            x = bot.send_audio(
                chat_id=task.user_id,
                audio=done_task.tg_file_id,
                # caption=caption,
                title=done_task.yt_title[:64] + ".mp3",
            )

        except Exception as e:
            error = f"Error sending voice by media id: {e}"
            print(error)

    if not x and done_task and os.path.isfile(file_name):
        # try to send the audio file mp3 from disk
        # check if mp3 file exists
        print(f"Sending audio file from disk: {file_name}")
        # file_object = types.FSInputFile(file_name)
        # file_object = open(file_name, "rb")
        try:
            x = bot.send_audio(
                chat_id=task.user_id,
                audio=open(file_name, "rb"),
                # caption=caption,
                title=done_task.yt_title[:64] + ".mp3",
            )

        except Exception as e:
            error = f"Error sending voice by file: {e}"
            print(error)

    if not x:
        print(f"Downloading audio for yt_id: {task.yt_id}")
        try:
            title, file_name = download_audio(task.yt_id, AUDIO_PATH)
            # caption = caption_template.format(title)
            x = bot.send_audio(
                chat_id=task.user_id,
                audio=open(file_name, "rb"),
                title=title[:64] + ".mp3",
            )  # caption=caption
            print("DONE!")
        except Exception as e:
            error = f"Error sending voice by downloading: {e}"
            print(error)

    if x:
        task.status = "COMPLETE"
        task.tg_file_id = x.audio.file_id
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

