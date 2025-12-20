import time
import requests
from infra.settings import RETRIES, RETRY_BASE_DELAY


def retry_request(fn, retries=RETRIES, base_delay=RETRY_BASE_DELAY):
    for attempt in range(retries + 1):
        try:
            return fn()
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(base_delay * (2 ** attempt))
    return None