from datetime import timedelta

from assist import utcnow
from database import Payment, SessionLocal, Task
from envs import USAGE_PERIODIC_LIMIT, USAGE_TIMEDELTA_HOURS


class UsageService:
    # class to handle the usage of the bot by user
    # works with the database to store and retrieve usage data
    def __init__(self, db=SessionLocal()):
        self.db = db
        print("UsageService initialized with db")

    def get_user_tasks_in_hours(self, user_id, hours):
        # returns quantity of completed tasks by user in the last N hours
        date_until = utcnow() - timedelta(hours=hours)
        user_tasks = (
            self.db.query(Task)
            .filter(Task.user_id == user_id)
            .filter(Task.status == "COMPLETE")
            .filter(Task.created_at > date_until)
            .all()
        )
        return len(user_tasks)


class PaywallService:
    # a class to handle the paywall. scenarios:
    # check if user is subscribed, and when the subscription ends
    # handle the payment process: create a payment, check if it's paid, etc
    # works with the database to store and retrieve payment data

    def __init__(self, db=SessionLocal()):
        self.db = db
        print("PaywallService initialized with db")

    def get_user_subscription(self, user_id):
        # get the user's subscription end date
        # return the date or None if not found
        users_payments = (
            self.db.query(Payment)
            .filter(Payment.user_id == user_id)
            .filter(Payment.status == "PAID")
            .filter(Payment.valid_till > utcnow())
            .all()
        )
        return max([p.valid_till for p in users_payments], default=None)

    def create_payment(self, user_id, amount_usd, method, comment, valid_till):
        # create a payment record
        # return the payment_id
        new_payment = Payment(
            user_id=user_id,
            amount_usd=amount_usd,
            method=method,
            comment=comment,
            valid_till=valid_till,
        )
        self.db.add(new_payment)
        self.db.commit()
        return new_payment.id

    def approve_payment(self, payment_id):
        # approve a payment
        # set the status to PAID
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.status = "PAID"
            self.db.commit()
            return True
        return False

    def delete_payment(self, payment_id):
        # delete a payment - really just marks it as deleted
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.status = "DELETED"
            self.db.commit()
            return True


class AccessControlService(PaywallService, UsageService):
    # a class to handle access control
    # check if user has access to the bot
    # works with the database to store and retrieve access data

    def __init__(
        self,
        db=SessionLocal(),
        hours_limit=USAGE_TIMEDELTA_HOURS,
        tasks_limit=USAGE_PERIODIC_LIMIT,
    ):
        self.db = db
        self.hours_limit = hours_limit
        self.tasks_limit = tasks_limit
        print(
            f"AccessControlService initialized with db and limits: {tasks_limit} tasks in {hours_limit} hours"
        )

    def check_access(self, user_id):
        # check if user has access
        # return True if user has access
        # return False if user has no access
        # return None if user is not found
        if self.get_user_subscription(user_id):
            return True
        if self.get_user_tasks_in_hours(user_id, self.hours_limit) >= self.tasks_limit:
            return False
        return True
