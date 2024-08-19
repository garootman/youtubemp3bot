from envs import API_HASH, API_ID, BOTNAME
from telethon import TelegramClient

client = TelegramClient("admin", API_ID, API_HASH)


async def upload_file(file_path):
    await client.start()
    file_name = file_path.split("/")[-1]
    task_id = file_name.split(".")[0]
    sent_message = await client.send_file(BOTNAME, file_path, caption=task_id)
    file_id = sent_message.media.document.id
    return file_id
