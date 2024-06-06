import inspect
import time
import traceback
from functools import wraps

from assist import now


def retry(max_retries=3, delay=1, outfunc=print, raise_exception=True):
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
                    msg = f"{str(now(True))} Got an error doing {func.__name__}:"
                    msg += f"\nParams were: {arg_dict}"
                    msg += f"\nFull traceback: {traceback.format_exc()}"
                    msg += f"\nRetry {_+1}/{max_retries} in {delay} seconds, "
                    outfunc(msg)
                    last_exception = e
                    time.sleep(delay)
            if raise_exception:
                raise last_exception

        return wrapper

    return decorator
