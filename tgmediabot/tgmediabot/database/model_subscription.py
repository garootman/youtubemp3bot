import random
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


class Subscription(Base):
    __tablename__ = "subscriptions"  # PK - increment id
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        nullable=False,
        default=new_int,
    )
    user_id = Column(BigInteger, nullable=False)
    start_date = Column(DateTime, default=utcnow, nullable=False)
    end_date = Column(DateTime, default=utcnow, nullable=False)
    package_type = Column(String(20), default="", nullable=False)

    def __repr__(self):
        return f"<{self.ended} subscription {self.id} for {self.user_id} from {self.start_date} end date {self.end_date} package {self.package_type}>"

    def __str__(self):
        return f"{self.ended} subscription {self.id} for {self.user_id} from {self.start_date} end date {self.end_date} package {self.package_type}"

    @property
    def ended(self):
        return self.end_date < utcnow()
