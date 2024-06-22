import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tgmediabot.chatmanager import ChatManager
from tgmediabot.database import Base, Chat

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal
Base.metadata.create_all(engine)


chatman = ChatManager()


def test_chat_manager():
    """
    bump_noban(self, user_id, message=None):
    ban_chat(self, user_id, message=None):
    check_ban(self, chat_id):
    """
    chat_id = 123
    # initially NOT banned
    assert not chatman.check_ban(chat_id)

    # ban chat
    chatman.ban_chat(chat_id)
    assert chatman.check_ban(chat_id)

    # unban chat
    chatman.bump_noban(chat_id)
    assert not chatman.check_ban(chat_id)


if __name__ == "__main__":
    test_chat_manager()
    print("all tests passed")
