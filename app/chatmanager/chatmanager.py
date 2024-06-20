import json

from database import Chat
from modelmanager import ModelManager


class ChatManager(ModelManager):
    """
    # class to manage user chat data

    class Chat(Base):
        __tablename__ = "chats"
        chat_id = Column(BigInteger, primary_key=True, index=True)
        updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
        banned = Column(Boolean, default=False)
        username = Column(String(256), default="")
        full_name = Column(String(256), default="")
        message_json = Column(TEXT, default="")
    """

    def _update_chat(self, chat):
        with self._session() as db:
            merged_chat = db.merge(chat)
            db.commit()
            print(f"Chat {merged_chat.chat_id} merged and updated")

    def bump_noban(self, user_id, message=None):
        chat = self._get_any_chat_obj(user_id, message)
        chat.banned = False
        print(f"Bumping chat {chat.chat_id}, banned: {chat.banned}")
        self._update_chat(chat)

    def ban_chat(self, user_id, message=None):
        chat = self._get_any_chat_obj(user_id, message)
        chat.banned = True
        self._update_chat(chat)

    def check_ban(self, chat_id):
        # checks if chat has a banned flag in the db
        chat = self._get_chat_by_id(chat_id)
        if chat:
            return chat.banned
        return False

    def _message_to_chat(self, message):
        json_str = message.json()
        json_str_dict = json.loads(json_str)
        json_str_dict_formatted = json.dumps(
            json_str_dict, indent=4, default=str, ensure_ascii=False
        )
        new_chat_object = Chat(
            chat_id=message.chat.id,
            username=message.chat.username,
            full_name=message.chat.full_name,
            message_json=json_str_dict_formatted,
        )
        return new_chat_object

    def _makeup_chat(self, chat_id):
        # makes a new chat object from chat_id and thin air
        new_chat_object = Chat(
            chat_id=chat_id, username="", full_name="", message_json=""
        )
        return new_chat_object

    def _get_any_chat_obj(self, chat_id, message=None):
        print ("SKIPPING CHAT FROM MESSAGE FOR NOW")
        message=None
        if message:
            print("Chat from message")
            return self._message_to_chat(message)
        else:
            chat = self._get_chat_by_id(chat_id)
            if chat:
                print("Chat from db")
                return chat
            else:
                print("Chat from thin air")
                return self._makeup_chat(chat_id)
            # return self._get_chat_by_id(chat_id) or self._makeup_chat(chat_id)

    def _get_chat_by_id(self, chat_id):
        with self._session() as db:
            chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
            if chat:
                db.expunge(chat)
                return chat
