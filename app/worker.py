# separate file for sending results to user
import asyncio

from aiogram import Bot, types

from celery_config import celery_app
from envs import ADMIN_ID, AUDIO_PATH, TG_TOKEN
from models import SessionLocal, Task

bot = Bot(token=TG_TOKEN)


def read_new_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    db.close()
    return task


def lookup_same_ytid(yt_id):
    # find task with same yt_id, that is complete and has a tg_file_id
    db = SessionLocal()
    task = (
        db.query(Task)
        .filter(Task.yt_id == yt_id, Task.status == "COMPLETE", Task.tg_file_id != "")
        .first()
    )
    db.close()
    return task


@celery_app.task
async def process_task(task_id: str):
    # read task from DB
    task = read_new_task(task_id)
    done_task = lookup_same_ytid(task.yt_id)
    chat_id = task.chat_id
    if not task:
        print("No task found")
        return
    if done_task:
        media_id = done_task.tg_file_id
        x = await bot.send_voice(chat_id=chat_id, voice=media_id, caption=caption)
        # send user existing media or file

    filename = AUDIO_PATH + task.yt_id + ".mp3"
    file = types.FSInputFile(file_name)
    x = await bot.send_voice(chat_id=chat_id, voice=file, caption=caption)
    media_id = x.voice.file_id
    task.status = "COMPLETE"
    task.error = ""
    task.tg_file_id = media_id
    db = SessionLocal()
    db.commit()
    db.close()


if __name__ == "__main__":
    # asyncio.run(send_audio_to_admin())
    test_media_id = (
        "AwACAgIAAxkDAANoZj6dOPSxT9K1SccNip4JDpJLPwQAAhlDAAKqG_hJQn-WowABJN7WNQQ"
    )
    asyncio.run(resend_audio_to_user(test_media_id, ADMIN_ID, "Test message"))
    # new_task = read_new_task()
