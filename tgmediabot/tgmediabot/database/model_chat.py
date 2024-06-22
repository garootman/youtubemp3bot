import sys

from sqlalchemy import (
    TEXT,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from .db_config import Base

sys.path.append("..")

from tgmediabot.assist import new_id, plainstring, utcnow


class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(BigInteger, primary_key=True, index=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    banned = Column(Boolean, default=False)
    admin_banned = Column(Boolean, default=False)
    username = Column(String(256), default="")
    full_name = Column(String(256), default="")
    message_json = Column(TEXT, default="")

    def __repr__(self):
        return f"Chat: {self.chat_id} {self.full_name} {self.username}"

    def __str__(self):
        return f"Chat: {self.chat_id} {self.full_name} {self.username}, banned: {self.banned} admin_banned: {self.admin_banned}"
