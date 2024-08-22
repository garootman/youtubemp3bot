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


class MediaInfo(Base):
    __tablename__ = "mediainfo"
    id = Column(String(20), primary_key=True, index=True, default=new_id)
    task_id = Column(String(20), nullable=False)
    url = Column(String(256), default="")
    updated_at = Column(DateTime, default=utcnow, nullable=False)

    platform = Column(String(20), default="")
    media_type = Column(String(20), default="")
    media_id = Column(String(20), default="")
    countries_yes = Column(TEXT, default="")
    countries_no = Column(TEXT, default="")
    title = Column(String(256), default="")
    channel = Column(String(256), default="")
    duration = Column(Integer, default=0)
    filesize = Column(BigInteger, default=0)

    error = Column(TEXT, default="")
    tg_file_id = Column(TEXT, default="")
    formats_json = Column(TEXT, default="")

    islive = Column(Boolean, default=False)

    def __repr__(self):
        return f"<MediaInfo {self.id} {self.media_id} {self.title}>"

    def __str__(self):
        return f"{self.media_id} {self.url}: {self.channel} - {self.title}, duration {self.duration} seconds"
