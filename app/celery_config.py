from celery import Celery
from celery.schedules import crontab, timedelta
from celery.signals import worker_ready
from envs import REDIS_URL

celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)
celery_app.autodiscover_tasks(["worker"])


# Optional configuration, see the application user guide.
celery_app.conf.update(result_expires=3600, worker_concurrency=10)


@celery_app.on_after_configure.connect
def run_restart_errors(sender, **kwargs):
    print("Running run_restart_errors")
    sender.send_task("worker.rerun_failed_tasks")
