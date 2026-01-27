import time
import requests
from infra.settings import RETRIES, RETRY_BASE_DELAY


class OnlineEngineUnavailable(RuntimeError):
    """Raised when the online engine cannot be reached after retries."""


def retry_request(fn, retries=RETRIES, base_delay=RETRY_BASE_DELAY):
    last_exc = None

    for attempt in range(retries + 1):
        try:
            return fn()
        except requests.RequestException as e:
            last_exc = e
            if attempt == retries:
                break
            time.sleep(base_delay * (2 ** attempt))

    # Raise ONE clean error instead of traceback spam
    raise OnlineEngineUnavailable("Online engine unreachable") from last_exc

