from datetime import datetime, timedelta

import pytest
from database import Base, Task
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from taskmanager import TaskManager

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal
Base.metadata.create_all(engine)
taskman = TaskManager(db)


def test_taskmanager_new_task():
    task = taskman.create_task(1, 1, "url", "platform", "media_type", "media_id")

    assert taskman.count_all() == 1
    
    task_id = task.id
    
    task = taskman.get_task_by_id(task.id)
    
    assert task.user_id == 1
    assert task.chat_id == 1
    assert task.url == "url"
    assert task.platform == "platform"
    assert task.media_type == "media_type"
    assert task.media_id == "media_id"
    assert task.status == "NEW"
    

    # check lookup by media is none
    lookedup_task = taskman.lookup_task_by_media("platform", "media_type", "media_id")
    assert not lookedup_task  # as no task is complete

    # test get_new_tasks
    new_tasks = taskman.get_new_tasks()
    assert len(new_tasks) == 1
    
    # test update_task
    task.status = "COMPLETE"
    
    taskman.update_task(task)
    task = taskman.get_task_by_id(task_id)
    assert task.status == "COMPLETE"
    
    # make sure there are no new tasks
    new_tasks = taskman.get_new_tasks()
    assert len(new_tasks) == 0
    
    # check lookup by media is NOT none
    lookedup_task = taskman.lookup_task_by_media("platform", "media_type", "media_id")
    assert lookedup_task  # as task is complete
    assert lookedup_task.status == "COMPLETE"
    assert lookedup_task.id == task.id


if __name__ == "__main__":
    test_taskmanager_new_task()
    print("All tests passed")
