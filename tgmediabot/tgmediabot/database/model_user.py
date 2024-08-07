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


class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, index=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    balance = Column(Integer, default=0)
    username = Column(String(256), default="")
    full_name = Column(String(256), default="")
    
    def __repr__(self):
        return f"User: {self.id} {self.full_name} {self.username} with balance: {self.balance} ⭐️"
    
    def __str__(self):
        return f"User: {self.id} {self.full_name} ({self.balance} ⭐️) {self.username}"