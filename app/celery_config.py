from celery import Celery
from envs import REDIS_URL

celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)
celery_app.autodiscover_tasks(["worker"])


# Optional configuration, see the application user guide.
celery_app.conf.update(result_expires=3600, worker_concurrency=10)
