from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from assist import utcnow
from database import Base, Payment, Task
from paywall import AccessControlService

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ses = SessionLocal
Base.metadata.create_all(engine)

uacs = AccessControlService(ses, 1, 1)  # 1 hour, 1 task limit
db = ses()


def test_access_control():
    user_id = 1234
    time_30_min_ago = utcnow() - timedelta(minutes=30)
    # test that check_access returns True
    assert uacs.check_access(user_id) == True
    # add a task 30 minutes ago
    new_task = Task(
        user_id=user_id, chat_id=123, status="COMPLETE", media_id="ABCDERFGASD"
    )
    new_task.created_at = time_30_min_ago
    db.add(new_task)
    db.commit()
    # test that check_access returns False - as the task is within the 1 hour window
    assert uacs.check_access(user_id) == False
    # add a payment for the user
    new_payment = Payment(
        user_id=user_id,
        amount_usd=10,
        method="paypal",
        comment="test",
        valid_till=utcnow() + timedelta(days=30),
    )
    db.add(new_payment)
    db.commit()
    # test that check_access returns False as payment is not paid
    assert uacs.check_access(user_id) == False
    # approve the payment
    new_payment.status = "PAID"
    db.add(new_payment)
    db.commit()
    # test that check_access returns True
    assert uacs.check_access(user_id) == True


if __name__ == "__main__":
    test_access_control()
    print("Everything passed")
