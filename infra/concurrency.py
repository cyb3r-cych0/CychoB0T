import threading
from infra.settings import OFFLINE_BACKEND
from infra.metrics import metrics


class ConcurrencyLimiter:
    def __init__(self, max_concurrent: int):
        if OFFLINE_BACKEND == "embedded":
            max_concurrent = 1

        self._sem = threading.Semaphore(max_concurrent)
        self._inflight = 0

    def __enter__(self):
        if not self._sem.acquire(blocking=False):
            metrics.inc("offline_model_busy")
            metrics.inc("offline_requests_rejected")
            raise RuntimeError("model_busy")

        self._inflight += 1
        metrics.set("offline_inflight", self._inflight)
        metrics.inc("offline_requests_total")
        return self

    def __exit__(self, exc_type, exc, tb):
        self._inflight -= 1
        metrics.set("offline_inflight", self._inflight)
        self._sem.release()


