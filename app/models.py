import os
from contextlib import contextmanager

from assist import new_id, plainstring, utcnow
from envs import POSTGRES_URL
from sqlalchemy import (
    TEXT,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import Session, declarative_base, sessionmaker, validates

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(20), primary_key=True, index=True, default=new_id)
    user_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    status = Column(String(20), default="NEW")
    yt_id = Column(String(20), nullable=False)
    yt_title = Column(String(256), default="")
    yt_duration = Column(BigInteger, default=0)
    tg_file_id = Column(TEXT, default="")
    url = Column(TEXT, default="")
    error = Column(TEXT, default="")
    msg_text = Column(TEXT, default="")
    repeat = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Task {self.id} {self.status} {self.yt_id}>"

    def __str__(self):
        return f"TG Task: {self.id} {self.status} from {self.updated_at}: tyid {self.yt_id}, msg: {plainstring(self.msg_text)}"


class Payment(Base):
    # a class to store payment details
    # payment consists of a  payment_id, user_id, amount_usd, status, method, created_at, valid_till, updated_at, comment
    __tablename__ = "payments"
    id = Column(String(20), primary_key=True, index=True, default=new_id)
    user_id = Column(BigInteger, nullable=False)
    amount_usd = Column(Float, nullable=False)
    status = Column(String(20), default="PAID")
    method = Column(String(20), default="")
    created_at = Column(DateTime, default=utcnow, nullable=False)
    valid_till = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    comment = Column(TEXT, default="")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = next(get_db())
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


Base.metadata.create_all(bind=engine)
print("DB + tables created successfully at", POSTGRES_URL)
