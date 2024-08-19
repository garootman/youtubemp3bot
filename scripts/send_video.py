from telebot import TeleBot

from tgmediabot.envs import ADMIN_ID, TG_TOKEN

bot = TeleBot(TG_TOKEN)
# file_id = "BAACAgIAAxkBAAIFgWbDWQkJiWDaxukZqaVs3-wpiEXTAAI2XgACQIoZSpnyz2zYKF15NQQ"
tt_file_id = 5341441747027253583

user_id = 5257529889
main_user_id = 62408647

# bot.send_video(user_id, file_id, caption="test")


def get_file_by_id(file_id):
    file = bot.get_file(file_id)
    # save file locally
    with open("downloads/test.txt", "wb") as f:
        f.write(bot.download_file(file.file_path).content)
    return file


# bot.send_document(main_user_id, tt_file_id, caption="test forwarding", visible_file_name="test.txt")

file = get_file_by_id(tt_file_id)
