"""
Rate Limiting (Industry-Grade, Offline-Safe)
Goal:
- Prevent abuse per API key without external services.

Design choices (locked):
- In-memory rate limiter
- Per API key
- Sliding window
- Fail fast with 429 Too Many Requests
- Logged violations

Policy (Simple, Sensible Defaults)
- Limit: 30 requests / minute / API key
- Window: 60 seconds
- Scope: /chat only
- (We’ll make this configurable later.)
"""
import time
import threading
from collections import defaultdict, deque
from fastapi import HTTPException
from infra.settings import WINDOW_SECONDS, MAX_REQUESTS, BURST_WINDOW_SEC, MAX_BURST

_LOCK = threading.Lock()

# per API key
_REQUESTS = defaultdict(deque)

# policy
WINDOW_SECONDS = WINDOW_SECONDS
MAX_REQUESTS = MAX_REQUESTS
BURST_WINDOW = BURST_WINDOW_SEC
MAX_BURST = MAX_BURST


def rate_limit(api_key: str):
    now = time.time()

    with _LOCK:
        q = _REQUESTS[api_key]

        # drop old entries (main window)
        while q and now - q[0] > WINDOW_SECONDS:
            q.popleft()

        # throughput limit
        if len(q) >= MAX_REQUESTS:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # burst limit
        burst_count = 0
        for ts in reversed(q):
            if now - ts <= BURST_WINDOW:
                burst_count += 1
            else:
                break

        if burst_count >= MAX_BURST:
            raise HTTPException(status_code=429, detail="Burst limit exceeded")

        q.append(now)
