import logging
from datetime import datetime, timedelta

from tgmediabot.database import MediaInfo, Task
from tgmediabot.modelmanager import ModelManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TaskManager(ModelManager):
    # class to work with DB model Task
    # includes methods to make all operations with Task

    def create_task(self, user_id, chat_id, url, priority):
        logger.debug(
            f"Creating task for user {user_id}, chat {chat_id}, url {url}, priority {priority}"
        )
        with self._session() as db:
            task = Task(
                user_id=user_id,
                chat_id=chat_id,
                url=url,
                priority=priority,
            )
            db.add(task)
            db.commit()
            task_id = task.id
            logger.info(f"Task {task_id} added, url: {url}")

        return self.get_task_by_id(task_id)

    def create_media_info(
        self,
        task_id,
        url,
        platform,
        media_type,
        media_id,
        countries_yes,
        countries_no,
        title,
        channel,
        duration,
        filesize,
    ):
        """
        id = Column(String(20), primary_key=True, index=True, default=new_id)
        task_id = Column(String(20), nullable=False)
        url = Column(String(256), default="")
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

        islive = Column(Boolean, default=False)

        """
        logger.debug(f"Creating media_info for task {task_id}")

        with self._session() as db:
            media_info = MediaInfo(
                task_id=task_id,
                url=url,
                platform=platform,
                media_type=media_type,
                media_id=media_id,
                countries_yes=countries_yes,
                countries_no=countries_no,
                title=title,
                channel=channel,
                duration=duration,
                filesize=filesize,
            )
            db.add(media_info)
            db.commit()
            media_info_id = media_info.id
            db.expunge(media_info)
            logger.info(f"MediaInfo {media_info_id} added for task {task_id}")

        return media_info_id

    def get_task_medias(self, task_id):
        with self._session() as db:
            medias = db.query(MediaInfo).filter(MediaInfo.task_id == task_id).all()
            # expunge
            for media in medias:
                db.expunge(media)
            return medias

    def update_media_info(self, media_info):
        with self._session() as db:
            merged_media_info = db.merge(media_info)
            db.commit()
            logger.info(f"MediaInfo {merged_media_info.id} merged and updated")
            # return merged_media_info free from session
            db.expunge(merged_media_info)
            return merged_media_info

    def get_media_objects(self, task_id):
        # returns all media objects for a task
        with self._session() as db:
            medias = db.query(MediaInfo).filter(MediaInfo.task_id == task_id).all()
            db.expunge_all()
            return medias

    def get_current_queue(self, priority):
        # returns tasks with status NEW or PROCESSING
        with self._session() as db:
            tasks = (
                db.query(Task)
                .filter(Task.status.in_(["NEW", "PROCESSING"]))
                .filter(Task.priority <= priority)
                .all()
            )
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
            # return merged_task free from session
            db.expunge(merged_task)
            return merged_task
