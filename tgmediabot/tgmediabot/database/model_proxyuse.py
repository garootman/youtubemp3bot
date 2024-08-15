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


def new_int():
    return random.randint(0, 1000000)


class ProxyUse(Base):
    # model to save proxy usage facts, 1 row per use
    __tablename__ = "proxyuse"
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        default=new_int,
    )
    proxy = Column(String(256), default="", nullable=False)
    use_type = Column(String(20), default="", nullable=False)
    task_id = Column(String(20), default="", nullable=False)  # FK
    url = Column(TEXT, default="", nullable=False)
    speed = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    success = Column(Boolean, default=False)
    error = Column(TEXT, default="")

    def __repr__(self):
        return f"<ProxyUse {self.proxy} for {self.url} at {self.updated_at}: {self.success}>"

    def __str__(self):
        return f"ProxyUse: {self.proxy} for {self.url} at {self.updated_at}: {self.success}"
