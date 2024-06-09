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

from assist import new_id, plainstring, utcnow


class Payment(Base):
    # a class to store payment details
    # payment consists of a  payment_id, user_id, amount_usd, status, method, created_at, valid_till, updated_at, comment
    __tablename__ = "payments"
    id = Column(String(20), primary_key=True, index=True, default=new_id)
    user_id = Column(BigInteger, nullable=False)
    amount_usd = Column(Float, nullable=False)
    status = Column(String(20), default="NEW")
    method = Column(String(20), default="")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    valid_till = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    comment = Column(TEXT, default="")
