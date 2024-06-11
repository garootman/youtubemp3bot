from database import SessionLocal, Task


class TaskManager:
    # class to wor with DB model Task
    # includes methods to make all operations with Task

    def __init__(self, db=SessionLocal()):
        self.db = db
        ct = self.db.query(Task).count()
        print("TaskManager created, total tasks: ", ct)

    def create_task(self, user_id, chat_id, url, platform, media_type, media_id):
        # create new task
        task = Task(
            user_id=user_id,
            chat_id=chat_id,
            url=url,
            platform=platform,
            media_type=media_type,
            media_id=media_id,
        )
        self.db.add(task)
        self.db.commit()
        print(f"Task {task.id} added, url: {url}")
        return task

    def get_task_by_id(self, task_id):
        # get task by id
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_unique_user_ids(self):
        # get all unique user_ids from tasks
        return self.db.query(Task.user_id).distinct().all()

    def count_all(self):
        # count all tasks
        return self.db.query(Task).count()

    def get_new_tasks(self):
        # get all tasks with status new
        return self.db.query(Task).filter(Task.status == "NEW").all()

    def lookup_task_by_media(self, platform, media_type, media_id):
        # find task with same platform, media_type, media_id
        # that is complete and has a tg_file_id
        # select one with the latest timestamp in updated_at
        task = (
            self.db.query(Task)
            .filter(
                Task.platform == platform,
                Task.media_type == media_type,
                Task.media_id == media_id,
                Task.status == "COMPLETE",
            )
            .order_by(Task.updated_at.desc())
            .first()
        )
        return task

    def update_task(self, task):
        # update task
        self.db.add(task)
        self.db.commit()
        print(f"Task {task.id} updated")
