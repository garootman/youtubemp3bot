import inspect
import logging
import time
import traceback
from functools import wraps

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def retry(max_retries=3, delay=1, outfunc=logger.error):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    arg_dict = dict(zip(inspect.getfullargspec(func)[0], args))
                    arg_dict = {k: repr(v)[:100] for k, v in arg_dict.items()}
                    msg = f"Got an error doing {func.__name__}:"
                    msg += f"\nParams were: {arg_dict}"
                    msg += f"\nFull traceback: {traceback.format_exc()}"
                    msg += f"\nRetry {_+1}/{max_retries} in {delay} seconds, "
                    outfunc(msg)
                    last_exception = e
                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator
