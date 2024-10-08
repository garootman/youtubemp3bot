import logging
from contextlib import contextmanager
from datetime import timedelta

from tgmediabot.assist import utcnow
from tgmediabot.database import (
    Payment,
    SessionLocal,
    Subscription,
    Task,
    Transaction,
    User,
)
from tgmediabot.envs import USAGE_PERIODIC_LIMIT, USAGE_TIMEDELTA_HOURS
from tgmediabot.modelmanager import ModelManager

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UsageService(ModelManager):
    # class to handle the usage of the bot by user
    # works with the database to store and retrieve usage data

    def get_user_tasks_in_hours(self, user_id, hours):
        # returns quantity of completed tasks by user in the last N hours
        date_until = utcnow() - timedelta(hours=hours)
        with self._session() as db:
            user_tasks = (
                db.query(Task)
                .filter(Task.user_id == user_id)
                .filter(Task.status == "COMPLETE")
                .filter(Task.created_at > date_until)
                .all()
            )
            logger.debug(
                f"User {user_id} completed {len(user_tasks)} tasks in the last {hours} hours"
            )
            return len(user_tasks)


class PaywallService(ModelManager):
    # a class to handle the paywall. scenarios:
    # check if user is subscribed, and when the subscription ends
    # handle the payment process: create a payment, check if it's paid, etc
    # works with the database to store and retrieve payment data

    def get_user_subscription(self, user_id):
        # get the user's subscription end date
        # return the date or None if not found
        with self._session() as db:
            user_payment = (
                db.query(Payment)
                .filter(Payment.user_id == user_id)
                .filter(Payment.status == "PAID")
                .filter(Payment.valid_till > utcnow())
                .first()
            )
            if user_payment:
                logger.debug(f"User {user_id} has payments: {user_payment}")
                return user_payment.valid_till
            return None

    def create_payment(self, user_id, amount_usd, method, comment, valid_till):
        # create a payment record
        # return the payment_id
        with self._session() as db:
            new_payment = Payment(
                user_id=user_id,
                amount_usd=amount_usd,
                method=method,
                comment=comment,
                valid_till=valid_till,
            )
            db.add(new_payment)
            db.flush()
            db.expunge(new_payment)
            return new_payment.id

    def approve_payment(self, payment_id):
        # approve a payment
        # set the status to PAID
        with self._session() as db:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                payment.status = "PAID"
                db.commit()
                return True
            return False

    def delete_payment(self, payment_id):
        # delete a payment - really just marks it as deleted
        # set the status to DELETED
        with self._session() as db:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if payment:
                payment.status = "DELETED"
                db.commit()
                return True
            return False


class AccessControlService(PaywallService, UsageService):
    # a class to handle access control
    # check if user has access to the bot
    # works with the database to store and retrieve access data

    def __init__(
        self,
        db=SessionLocal,
        hours_limit=USAGE_TIMEDELTA_HOURS,
        tasks_limit=USAGE_PERIODIC_LIMIT,
    ):
        self._sessionlocal = db
        self.hours_limit = hours_limit
        self.tasks_limit = tasks_limit
        logger.info(
            f"AccessControlService initialized with db and limits: {tasks_limit} tasks in {hours_limit} hours"
        )

    def check_access(self, user_id):
        # check if user has access
        # return True if user has access
        # return False if user has no access
        # return None if user is not found
        logger.info(f"Checking access for user {user_id}")
        if self.get_user_subscription(user_id):
            logger.info(f"User {user_id} has a valid subscription")
            return True
        if self.get_user_tasks_in_hours(user_id, self.hours_limit) >= self.tasks_limit:
            logger.info(
                f"User {user_id} has reached the limit of {self.tasks_limit} tasks in {self.hours_limit} hours"
            )
            return False
        return True
