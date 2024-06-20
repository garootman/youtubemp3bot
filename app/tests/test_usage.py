from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from assist import utcnow
from database import Base, Payment, Task
from paywall import UsageService

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(engine)
ses = SessionLocal

usage_service = UsageService(ses)
user_id = 1234
chat_id = 5678
media_id = "ABCDEFG"

db = ses()


def test_usage():
    # check that get_user_tasks_in_hours returns 0
    assert usage_service.get_user_tasks_in_hours(user_id, 1) == 0
    # create a task for the user, NOT complete
    new_task = Task(user_id=user_id, chat_id=chat_id, status="NEW", media_id=media_id)
    db.add(new_task)
    db.commit()
    # check that get_user_tasks_in_hours returns 0 as the task is not complete
    assert usage_service.get_user_tasks_in_hours(user_id, 1) == 0
    # complete the task
    new_task.status = "COMPLETE"
    db.add(new_task)
    db.commit()
    # check that get_user_tasks_in_hours returns 1
    new_task_count = usage_service.get_user_tasks_in_hours(user_id, 1)
    print("NTC", new_task_count)
    assert new_task_count == 1
    # add task with created_at 2 hours ago, which is outside the 1 hour window
    new_task = Task(user_id=user_id, chat_id=chat_id, status="COMPLETE")
    new_task.created_at = utcnow() - timedelta(hours=2)
    db.add(new_task)
    # check that get_user_tasks_in_hours returns 1
    assert usage_service.get_user_tasks_in_hours(user_id, 1) == 1


if __name__ == "__main__":
    test_usage()
    print("Everything passed")
