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


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(20), primary_key=True, index=True, default=new_id)
    user_id = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    status = Column(String(20), default="NEW", nullable=False)
    url = Column(TEXT, default="", nullable=False)

    platform = Column(String(20), default="")
    media_type = Column(String(20), default="")
    media_id = Column(String(20), default="")
    countries_yes = Column(TEXT, default="")
    countries_no = Column(TEXT, default="")
    title = Column(String(256), default="")
    channel = Column(String(256), default="")
    duration = Column(Integer, default=0)
    filesize = Column(BigInteger, default=0)
    mode = Column(String(20), default="")

    error = Column(TEXT, default="")
    repeat = Column(Boolean, default=False)
    tg_file_id = Column(TEXT, default="")
    limits = Column(Integer, default=1)
    priority = Column(Integer, default=0)

    def __repr__(self):
        return f"<Task {self.id} {self.status} {self.url}>"

    def __str__(self):
        return f"Task: {self.id} {self.status} from {self.updated_at}: url {self.url}, media_id: {self.media_id}"
