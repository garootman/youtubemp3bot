from tgmediabot.assist import utcnow, get_logger
from tgmediabot.modelmanager import ModelManager
from tgmediabot.database import User, Subscription, Task

from datetime import timedelta, datetime
import math

logger = get_logger(__name__)


class PayWallManager(ModelManager):

    DAILY_LIMITS_FREE = 20  # daily limit for free users
    DAILY_LIMITS_PREMIUM = 500  # daily limit for premium users
    PREMIUM_DAYS = {"day": 1, "week": 7, "month": 30}
    FORMAT_LIMITS = {"m4a": 1, "mp3": 2, "360": 3, "720": 4, "1080": 5}

    def buy_premium(self, user_id, package_type, start_date=None):
        if not start_date:
            start_date = utcnow()
        expiry_date = start_date + timedelta(days=self.PREMIUM_DAYS[package_type])
        with self._session() as db:
            new_subscription = Subscription(
                user_id=user_id, start_date=start_date, end_date=expiry_date, package_type=package_type
            )
            db.add(new_subscription)
            db.commit()
            logger.info(
                f"User {user_id} purchased '{package_type}' package until {expiry_date}"
            )
            return new_subscription.end_date

    def get_user_premium_sub(self, user_id):
        with self._session() as db:
            user_sub = (
                db.query(Subscription)
                .filter(Subscription.user_id == user_id)
                .filter(Subscription.end_date >= utcnow())
                .first()
            )
            db.expunge_all()
            return user_sub

    def calc_daily_usage(self, user_id):
        with self._session() as db:
            # find all tasks for the user, that were created within 24 hours
            # filter only tasks in statuses COMPLETE, NEW, PROCESSING
            user_tasks = (
                db.query(Task)
                .filter(Task.user_id == user_id)
                .filter(Task.created_at >= utcnow() - timedelta(hours=24))
                .filter(Task.status.in_(["COMPLETE", "NEW", "PROCESSING"]))
                .all()
            )
            limits = sum(task.limits for task in user_tasks)
        
        logger.debug(
            f"Within 24 hours user {user_id} has {len(user_tasks)} chargable tasks with total limits {limits}"
        )
        return limits

    def check_daily_limit_left(self, user_id):
        user_sub = self.get_user_premium_sub(user_id)
        daily_limit = self.DAILY_LIMITS_PREMIUM if user_sub else self.DAILY_LIMITS_FREE
        daily_usage = self.calc_daily_usage(user_id)
        daily_limit_left = daily_limit - daily_usage
        logger.debug(f"User {user_id} has {daily_limit_left} limits left for today")
        return daily_limit_left

    @staticmethod
    def calc_task_limits(duration_seconds, format):
        # split audio into 10 min chunks, ceil(duration/600)
        n_10min_chunks = math.ceil(duration_seconds / 600)
        format_multiplier = PayWallManager.FORMAT_LIMITS[format]
        return n_10min_chunks * format_multiplier

    def check_task_limits(self, user_id, duration_seconds, format):
        task_limits = self.calc_task_limits(duration_seconds, format)
        daily_limit_left = self.check_daily_limit_left(user_id)
        return daily_limit_left >= task_limits
