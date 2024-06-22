from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tgmediabot.assist import utcnow
from tgmediabot.database import Base, Payment
from tgmediabot.paywall import PaywallService

engine = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal
Base.metadata.create_all(engine)
pws = PaywallService(db)


def test_paywall():
    now_plus_day = utcnow() + timedelta(days=1)
    now_minus_day = utcnow() - timedelta(days=1)
    user_id = 1234
    # check that get_user_subscription returns None
    assert pws.get_user_subscription(user_id) == None
    # create a payment for 1 day from now
    payment_id = pws.create_payment(user_id, 1, "test", "test", now_plus_day)
    # check that get_user_subscription returns None as the payment is not approved
    assert pws.get_user_subscription(user_id) == None
    # approve the payment
    pws.approve_payment(payment_id)
    # check that get_user_subscription returns the date of the payment
    assert pws.get_user_subscription(user_id) == now_plus_day
    # delete the payment
    pws.delete_payment(payment_id)
    # check that get_user_subscription returns None
    assert pws.get_user_subscription(user_id) == None
    # create a payment for 1 day ago
    payment_id = pws.create_payment(user_id, 1, "test", "test", now_minus_day)
    # check that get_user_subscription returns None as the payment is expired
    assert pws.get_user_subscription(user_id) == None
    # delete the payment
    pws.delete_payment(payment_id)
    # check that get_user_subscription returns None
    assert pws.get_user_subscription(user_id) == None


if __name__ == "__main__":
    test_paywall()
    print("All tests passed!")
