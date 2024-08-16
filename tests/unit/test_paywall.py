from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tgmediabot.assist import utcnow
from tgmediabot.database import Base, Subscription, Task
from tgmediabot.paywall import PayWallManager
from tgmediabot.taskmanager import TaskManager

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal
Base.metadata.create_all(engine)
pwm = PayWallManager(db)
taskmanager = TaskManager(db)


"""
buy_premium(self, user_id, package_type):
def get_user_premium_sub(self, user_id):
def calc_daily_usage(self, user_id):
def check_daily_limit_left(self, user_id):
def calc_task_limits(duration_seconds, format):
"""


def test_paywall():
    now_plus_day = utcnow() + timedelta(days=1)
    now_minus_day = utcnow() - timedelta(days=1)
    user_id = 1234
    # test that user has 20 limits left
    # assert NOT premium
    assert pwm.get_user_premium_sub(user_id) is None
    assert pwm.check_daily_limit_left(user_id) == 20

    # add a task to the user, check that limits are reduced
    task = taskmanager.create_task(
        user_id=user_id, chat_id=user_id, url="NO URL", priority=0
    )

    assert pwm.check_daily_limit_left(user_id) == 20

    # make user a premium user
    pwm.buy_premium(user_id, "day")

    # assert premium
    assert pwm.get_user_premium_sub(user_id) is not None

    # assert limits left is 499
    assert pwm.check_daily_limit_left(user_id) == 500


if __name__ == "__main__":
    test_paywall()
    print("All tests passed!")
