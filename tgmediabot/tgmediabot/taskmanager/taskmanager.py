import logging
from datetime import datetime, timedelta

from tgmediabot.database import Task
from tgmediabot.modelmanager import ModelManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaskManager(ModelManager):
    # class to work with DB model Task
    # includes methods to make all operations with Task
    
    def create_task(
        self, user_id, chat_id, url, platform="", media_type="", media_id=""
    ):
        logger.debug(
            f"Creating task for user {user_id}, chat {chat_id}, url {url}, platform {platform}, media_type {media_type}, media_id {media_id}"
        )
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
            db.commit()
            task_id = task.id
            logger.info(f"Task {task_id} added, url: {url}")

        return self.get_task_by_id(task_id)
    
    def get_current_queue(self):
        # returns tasks with status NEW or PROCESSING
        with self._session() as db:
            tasks = db.query(Task).filter(Task.status.in_(["NEW", "PROCESSING"])).all()
            return tasks

    def get_task_by_id(self, task_id):
        if not task_id:
            logger.error("No task_id provided")
            return None
        with self._session() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                db.expunge(task)  # Detach the task from the session
                return task
            return None

    def get_unique_user_ids(self):
        ids = []
        with self._session() as db:
            tasks_ids = db.query(Task.user_id).distinct().all()
        for task_id in tasks_ids:
            ids.append(task_id[0])
        return ids

    def count_all(self):
        with self._session() as db:
            return db.query(Task).count()

    def get_new_task_ids(self, hours_back=3):
        ret_ids = []
        with self._session() as db:
            new_tasks = (
                db.query(Task).filter(Task.status.in_(["NEW", "PROCESSING"])).all()
            )
            for task in new_tasks:
                if task.created_at > datetime.utcnow() - timedelta(hours=hours_back):
                    ret_ids.append(task.id)
        return ret_ids

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

    """
        def check_duplicate_task(self, chat_id, url):
            is_duplicate = False
            with self._session() as db:
                task = db.query(Task).filter(Task.chat_id == chat_id, Task.url == url).first()
                if task:
                    is_duplicate = True
            return is_duplicate
    """

    def update_task(self, task):
        with self._session() as db:
            merged_task = db.merge(task)
            db.commit()
            logger.info(f"Task {merged_task.id} merged and updated")
