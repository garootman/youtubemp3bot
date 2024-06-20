from contextlib import contextmanager

from database import SessionLocal


class ModelManager:
    # basic class to work with database models

    def __init__(self, db=SessionLocal):
        self._sessionlocal = db

    @contextmanager
    def _session(self):
        session = self._sessionlocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
