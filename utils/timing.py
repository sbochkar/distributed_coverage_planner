"""Helper functions for logging timing."""
from functools import wraps
from time import time

from log_utils import get_logger


def time_execution(f):
    logger = get_logger("timing")

    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        logger.info('func:%r took: %2.4f sec', f.__name__, te - ts)
        return result
    return wrap
