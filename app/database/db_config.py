import os
from contextlib import contextmanager

from envs import POSTGRES_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker, validates

# add 2 folders up to import envs
# import sys
# sys.path.append("..")


engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


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


def create_db():
    Base.metadata.create_all(bind=engine)
    print("DB + tables created successfully at", POSTGRES_URL)

create_db()