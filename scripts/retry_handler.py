import time
import logging
from functools import wraps

logger = logging.getLogger('RetryHandler')

class TransientError(Exception):
    pass

class AuthError(Exception):
    pass

def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except AuthError:
                    logger.error('Authentication error — human intervention required')
                    raise
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f'All {max_attempts} attempts failed: {e}')
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f'Attempt {attempt+1} failed ({e}), retrying in {delay}s')
                    time.sleep(delay)
        return wrapper
    return decorator