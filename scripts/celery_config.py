from celery import Celery
from celery.schedules import crontab, timedelta
from celery.signals import worker_ready

from tgmediabot.envs import REDIS_URL

print("using redis at", REDIS_URL)
celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)
celery_app.autodiscover_tasks(["worker"])


celery_app.conf.update(result_expires=3600, worker_concurrency=4)
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
celery_app.conf.timezone = "UTC"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]


@celery_app.on_after_configure.connect
def run_new_tasks(sender, **kwargs):
    print("Running process_new_tasks")
    sender.send_task("worker.process_new_tasks")
