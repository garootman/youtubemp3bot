import json

from tgmediabot.database import Chat
from tgmediabot.modelmanager import ModelManager


class ChatManager(ModelManager):

    def _update_chat(self, chat):
        with self._session() as db:
            merged_chat = db.merge(chat)
            db.commit()
            print(f"Chat {merged_chat.chat_id} merged and updated")

    def bump_noban(self, user_id, message_dict={}):
        chat = self._get_any_chat_obj(user_id, message_dict)
        chat.banned = False
        print(f"Bumping chat {chat.chat_id}, banned: {chat.banned}")
        self._update_chat(chat)

    def ban_chat(self, user_id, message_dict={}):
        chat = self._get_any_chat_obj(user_id, message_dict)
        chat.banned = True
        self._update_chat(chat)

    def check_ban(self, chat_id):
        # checks if chat has a banned flag in the db
        chat = self._get_chat_by_id(chat_id)
        if chat:
            return chat.banned
        return False

    def _message_to_chat(self, message_dict: dict):
        # makes a new chat object from a message_dict
        chat_dict = message_dict.get("chat", {})
        new_chat_object = Chat(
            chat_id=chat_dict.get("id", 0),
            username=chat_dict.get("username"),
            full_name=message_dict.get("full_name", ""),
            message_json=json.dumps(
                message_dict, default=str, ensure_ascii=False, indent=4
            ),
        )
        return new_chat_object

    def _makeup_chat(self, chat_id):
        # makes a new chat object from chat_id and thin air
        new_chat_object = Chat(
            chat_id=chat_id, username="", full_name="", message_json="{}"
        )
        return new_chat_object

    def _get_any_chat_obj(self, chat_id, message_dict={}):
        chat = None
        if message_dict:
            chat = self._message_to_chat(message_dict)
        else:
            chat = self._get_chat_by_id(chat_id)
            if not chat:
                chat = self._makeup_chat(chat_id)
        return chat

    def _get_chat_by_id(self, chat_id):
        with self._session() as db:
            chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                db.expunge(chat)
                return chat
