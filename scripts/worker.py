# separate file for sending results to user
import logging

from celery_config import celery_app

from tgmediabot.envs import GOOGLE_API_KEY, PROXY_TOKEN
from tgmediabot.medialib import YouTubeAPIClient
from tgmediabot.paywall import PayWallManager
from tgmediabot.proxies import ProxyRevolver
from tgmediabot.taskmanager import TaskManager
from tgmediabot.taskprocessor import RemoteTaskProcessor

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


proxy_mgr = ProxyRevolver(PROXY_TOKEN)
taskman = TaskManager()
pwm = PayWallManager()


ytapi_proxy = proxy_mgr.get_checked_proxy_by_countries(["US"], [])
yt_client = YouTubeAPIClient(GOOGLE_API_KEY, ytapi_proxy)


@celery_app.task
def process_task(task_id: str, cleanup=True):
    task_processor = RemoteTaskProcessor(
        task_id=task_id,
        proxymanager=proxy_mgr,
        taskmanager=taskman,
        ytclient=yt_client,
        payman=pwm,
    )

    result = task_processor.process(cleanup)
    return result


# @celery_app.task
def enrich_tp_task(task_id: str, premium: bool = False):
    task_processor = RemoteTaskProcessor(
        task_id=task_id,
        proxymanager=proxy_mgr,
        taskmanager=taskman,
        ytclient=yt_client,
        payman=pwm,
    )

    result = task_processor.enrich_task(ignore_status=True, premium=premium)
    return result


@celery_app.task
def process_new_tasks():
    new_task_ids = taskman.get_new_task_ids()
    msg = f"(Re-)processing {len(new_task_ids)} new tasks: {new_task_ids[:5]}..."
    logger.info(msg)
    for tid in new_task_ids:
        task = taskman.get_task_by_id(tid)
        task.status = "NEW"
        taskman.update_task(task)
        process_task.delay(tid, cleanup=True)
        logger.info(f"Added '{tid}' as of {task.created_at} to queue")


if __name__ == "__main__":
    # Runs celery. To add beat scheduler, add -B flag
    celery_app.worker_main(
        argv=["worker", "--loglevel=info", "--concurrency=1", "--events"]
    )


"""

if __name__ == "__main__":
    task_id = "67c392791c26"

    task_processor = RemoteTaskProcessor(
        task_id=task_id,
        proxymanager=proxy_mgr,
        taskmanager=taskman,
        ytclient=yt_client,
        payman=pwm,
    )
    result = task_processor.process(cleanup=False, ignore_status=True)
    print(result)

"""
