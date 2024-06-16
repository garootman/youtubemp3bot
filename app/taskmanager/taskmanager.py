from contextlib import contextmanager

from database import SessionLocal, Task
from sqlalchemy.orm import sessionmaker


class TaskManager:
    # class to work with DB model Task
    # includes methods to make all operations with Task

    def __init__(self, db=SessionLocal):
        self._sessionlocal = db
        ct = self.count_all()
        print("TaskManager created, total tasks: ", ct)

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

    def create_task(
        self, user_id, chat_id, url, platform="", media_type="", media_id=""
    ):
        with self._session() as db:
            task = Task(
                user_id=user_id,
                chat_id=chat_id,
                url=url,
                platform=platform,
                media_type=media_type,
                media_id=media_id,
            )
            db.add(task)
            db.flush()  # Ensure the task ID is populated
            db.expunge(task)
            print(f"Task {task.id} added, url: {url}")
            return task
        # return self.get_task_by_id(task_id)

    def get_task_by_id(self, task_id):
        with self._session() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                db.expunge(task)  # Detach the task from the session
            return task

    def get_unique_user_ids(self):
        with self._session() as db:
            return db.query(Task.user_id).distinct().all()

    def count_all(self):
        with self._session() as db:
            return db.query(Task).count()

    def get_new_tasks(self):
        with self._session() as db:
            all_tasks = db.query(Task).filter(Task.status == "NEW").all()
            for task in all_tasks:
                db.expunge(task)
            return all_tasks

    def lookup_task_by_media(self, platform, media_type, media_id):
        # find task with same platform, media_type, media_id
        # that is complete and has a tg_file_id
        # select one with the latest timestamp in updated_at
        with self._session() as db:
            task = (
                db.query(Task)
                .filter(
                    Task.platform == platform,
                    Task.media_type == media_type,
                    Task.media_id == media_id,
                    Task.status == "COMPLETE",
                )
                .order_by(Task.updated_at.desc())
                .first()
            )
            if task:
                db.expunge(task)
            return task

    def update_task(self, task):
        with self._session() as db:
            db.add(task)
            print(f"Task {task.id} updated")
