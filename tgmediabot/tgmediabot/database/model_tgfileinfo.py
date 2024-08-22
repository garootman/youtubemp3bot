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

import random

from tgmediabot.assist import new_id, plainstring, utcnow


def new_int():
    return random.randint(0, 1000000)


class TgMediaInfo(Base):
    # model to save proxy usage facts, 1 row per use
    __tablename__ = "tgmediainfo"
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        default=new_int,
    )
    remote_task_id = Column(String(20), default="", nullable=False)
    file_id = Column(String(256), default="", nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    success = Column(Boolean, default=False)
    error = Column(TEXT, default="")

    def __repr__(self):
        return f"<TgMediaInfo {self.file_id} for {self.remote_task_id} at {self.updated_at}: {self.success}>"

    def __str__(self):
        return f"TgMediaInfo: {self.file_id} for {self.remote_task_id} at {self.updated_at}: {self.success}"
