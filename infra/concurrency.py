import threading
from fastapi import HTTPException

class ConcurrencyLimiter:
    def __init__(self, max_concurrent: int):
        self.sema = threading.Semaphore(max_concurrent)

    def __enter__(self):
        if not self.sema.acquire(blocking=False):
            raise HTTPException(status_code=503, detail="Server busy")
        return self

    def __exit__(self, exc_type, exc, tb):
        self.sema.release()
